"""
工单图片识别与去重逻辑：
- 跟踪追踪像素(很小)直接跳过
- 同一张图片在>=RECUR_THRESHOLD个不同工单里出现过，视为各公司的签名/名片图片，自动拉黑跳过
- 每个工单只处理一次（按图片hash记录在 uploaded_images.json），更新工单时不会重复识别/重复上传
"""
import hashlib
import json
import os

import nextop_api

MIN_IMAGE_BYTES = 3000          # 小于此大小视为追踪像素/无意义图片，跳过
RECUR_THRESHOLD = 3             # 同一图片出现在>=N个不同工单里，自动视为名片/签名图片

# 邮件正文里的头像/表情/占位图，不是真附件（且常下载失败）。命中即在下载前跳过。
SKIP_URL_SUBSTRINGS = (
    "default-avatar",   # Zendesk 默认头像占位图 (/images/YYYY/default-avatar-NN.png)
    "gravatar",         # Gravatar 头像
    "/emoji/", "/emojis/",
    "spacer.gif", "spacer.png", "pixel.gif",
)

HASH_STATS_FILE = "image_hashes.json"      # {hash: [ticket_no, ...]}
UPLOADED_CACHE_FILE = "uploaded_images.json"  # {ticket_no: [hash, ...]}
BLOCKLIST_FILE = "card_blocklist.json"     # [hash, ...] 手动确认过的名片/签名图，永久跳过
TOKEN_HASH_FILE = "token_hash.json"        # {file_token: hash} 上传记录


def _load(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_blocklist():
    if os.path.exists(BLOCKLIST_FILE):
        with open(BLOCKLIST_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_token_hash(token: str, h: str):
    """上传时记录 file_token → hash 映射"""
    data = _load(TOKEN_HASH_FILE) or {}
    data[token] = h
    _save(TOKEN_HASH_FILE, data)


def load_token_hash() -> dict:
    return _load(TOKEN_HASH_FILE) or {}


def add_to_blocklist(hashes):
    """手动把确认是名片/签名图的hash加入永久黑名单"""
    current = load_blocklist()
    current.update(hashes)
    with open(BLOCKLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(current), f, ensure_ascii=False, indent=2)


def collect_new_images(reference_no, messages):
    """
    扫描工单消息里的图片，跳过已处理过的、追踪像素、以及跨工单重复出现的名片/签名图。
    返回本次需要新上传的图片列表：[{"hash":..., "bytes":..., "content_type":..., "name":...}]
    名片/签名图/追踪像素会立即记入已处理缓存（它们本就不需要上传）。
    真正需要上传的图片【不会】在这里标记为已处理 —— 必须等上传确认成功后调用 mark_uploaded()，
    避免上传失败（如权限错误）却被误判为"已处理"导致以后不再重试。
    """
    hash_stats = _load(HASH_STATS_FILE)
    uploaded_cache = _load(UPLOADED_CACHE_FILE)
    blocklist = load_blocklist()
    already_done = set(uploaded_cache.get(reference_no, []))

    to_upload = []
    seen_in_this_run = set()

    for m in messages:
        sources = [(url, None) for url in m.get("image_urls", [])]
        for att in m.get("file_attachments", []):
            sources.append((None, att))

        for url, att in sources:
            if url is not None and any(s in url.lower() for s in SKIP_URL_SUBSTRINGS):
                continue  # 头像/表情/占位图，直接跳过，不下载
            try:
                if url is not None:
                    content, content_type = nextop_api.download_image(url)
                    name_hint = None
                else:
                    record = nextop_api.get_file_link(att["id"])
                    link = record.get("link")
                    if not link:
                        continue
                    content, content_type = nextop_api.download_image(link)
                    name_hint = att.get("file_name")
            except Exception as e:
                print(f"  图片下载失败: {e}")
                continue

            h = hashlib.sha256(content).hexdigest()
            if h in seen_in_this_run:
                continue
            seen_in_this_run.add(h)

            tickets_seen = hash_stats.setdefault(h, [])
            if reference_no not in tickets_seen:
                tickets_seen.append(reference_no)

            if h in already_done:
                continue  # 之前已经处理过这张图（无论是否上传），跳过避免重复

            is_signature_or_card = len(tickets_seen) >= RECUR_THRESHOLD or h in blocklist
            too_small = len(content) < MIN_IMAGE_BYTES

            if not is_signature_or_card and not too_small:
                if name_hint:
                    name = name_hint
                else:
                    ext = (content_type.split("/")[-1] if content_type else "png").split(";")[0]
                    name = f"{reference_no}_{h[:8]}.{ext}"
                to_upload.append({
                    "hash": h,
                    "bytes": content,
                    "content_type": content_type or "image/png",
                    "name": name,
                })
            else:
                # 名片/签名/追踪像素：不需要上传，直接标记为已处理
                already_done.add(h)

    uploaded_cache[reference_no] = sorted(already_done)
    _save(HASH_STATS_FILE, hash_stats)
    _save(UPLOADED_CACHE_FILE, uploaded_cache)

    return to_upload


def mark_uploaded(reference_no, hashes):
    """上传成功后调用，把hash正式记入已处理缓存"""
    if not hashes:
        return
    uploaded_cache = _load(UPLOADED_CACHE_FILE)
    already_done = set(uploaded_cache.get(reference_no, []))
    already_done.update(hashes)
    uploaded_cache[reference_no] = sorted(already_done)
    _save(UPLOADED_CACHE_FILE, uploaded_cache)

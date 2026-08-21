import time
import random
import hashlib
import json
import requests
from bs4 import BeautifulSoup
import config

BASE = "https://api.nextop.com"


def _headers(extra=None):
    if not all((config.NEXTOP_AUTH, config.NEXTOP_COOKIE, config.NEXTOP_SATOKEN)):
        raise NextopAuthRequired("Nextop credentials are not configured.")
    ts = str(int(time.time() * 1000))
    h = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "authorization": config.NEXTOP_AUTH,
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://saas.nextop.com",
        "referer": "https://saas.nextop.com/",
        "satoken": config.NEXTOP_SATOKEN,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "x-ca-language": "zh_CN",
        "x-ca-reqid": f"0.{random.random()}-{ts}",
        "x-ca-reqtime": ts,
    }
    if extra:
        h.update(extra)
    return h


def _cookies():
    jar = {}
    for part in config.NEXTOP_COOKIE.split(";"):
        k, v = part.strip().split("=", 1)
        jar[k] = v
    return jar


SESSION_EXPIRED_CODES = {"A00998", "A00997"}
SUCCESS_CODES = {"000000", 0, "0", None}


class NextopAuthRequired(RuntimeError):
    """Existing local session cannot be refreshed without new browser input."""

class NextopResponseError(RuntimeError):
    """Nextop replied, but the envelope cannot safely be treated as ticket data."""

class NextopLookupEmpty(NextopResponseError):
    """A successful exact-lookup request returned no matching record."""

class NextopParseError(NextopResponseError):
    """Expected ticket/message response structure was absent."""


def _post(url, payload):
    r = requests.post(url, json=payload, headers=_headers(), cookies=_cookies())
    if r.status_code in (401, 403):
        raise NextopAuthRequired("Nextop authentication expired or invalid.")
    r.raise_for_status()
    data = r.json()
    if data.get("code") in SESSION_EXPIRED_CODES:
        raise NextopAuthRequired("Nextop authentication expired or invalid.")
    if data.get("code") not in SUCCESS_CODES:
        raise NextopResponseError("Nextop request returned an unsuccessful response.")
    return data


def _get(url, params):
    r = requests.get(url, params=params, headers=_headers(), cookies=_cookies())
    if r.status_code in (401, 403):
        raise NextopAuthRequired("Nextop authentication expired or invalid.")
    r.raise_for_status()
    data = r.json()
    if data.get("code") in SESSION_EXPIRED_CODES:
        raise NextopAuthRequired("Nextop authentication expired or invalid.")
    if data.get("code") not in SUCCESS_CODES:
        raise NextopResponseError("Nextop request returned an unsuccessful response.")
    return data


def refresh_session_from_pageorder_request(pageorder_request):
    """Refresh from the browser's copied PageOrders request (cURL form).

    The endpoint name ``pageOrders`` is not itself a credential.  This accepts
    the existing manual fallback format without storing the pasted request.
    """
    import update_token
    auth, cookie_str, satoken = update_token.parse_curl(str(pageorder_request or ""))
    update_token.persist(auth, cookie_str, satoken)
    config.NEXTOP_AUTH = auth
    config.NEXTOP_COOKIE = cookie_str
    config.NEXTOP_SATOKEN = satoken


def search_tickets(keyword, search_by="content", size=10):
    """关键词搜索工单
    search_by: 'content'(工单内容), 'title'(工单标题), 'email'(客户邮箱)
    """
    payload = {
        "assignStatus": "", "brandIds": [], "categoryIds": [], "ccUserIds": [],
        "createStartTime": "", "createEndTime": "", "createIds": [],
        "current": 1, "size": size, "total": 0,
        "filterId": "", "labelIds": [], "orderField": "0", "orderType": "0",
        "outerAddresses": keyword if search_by == "email" else "",
        "outerIds": [], "priorities": [], "receiveMailAddrs": [],
        "remark": "", "repairOrderNo": "", "replyStartTime": "", "replyEndTime": "",
        "serviceGroupIds": [], "serviceUserIds": [], "sources": [], "status": [],
        "templateIds": [],
        "title": keyword if search_by in ("title", "content") else "",
        "type": "", "updateEndTime": "", "updateStartTime": "",
        "updateTime": "",
        "defaultSelectVal": search_by if search_by in ("title", "content") else "title",
        "serviceGroup": [], "createTime": "",
        "name": "", "filterName": "", "selectInputType": "content",
        "isOrderFilterForm": True, "language": "zh"
    }
    data = _post(f"{BASE}/ticketOrder/wOrder/pageOrders", payload)
    return data.get("data", {}).get("records", [])


def find_ticket_by_no(repair_order_no):
    """通过工单号搜索，返回工单基础信息（含 id）"""
    payload = {
        "assignStatus": "", "brandIds": [], "categoryIds": [], "ccUserIds": [],
        "createStartTime": "", "createEndTime": "", "createIds": [],
        "current": 1, "size": 20, "total": 0,
        "filterId": "", "labelIds": [], "orderField": "0", "orderType": "0",
        "outerAddresses": "", "outerIds": [], "priorities": [], "receiveMailAddrs": [],
        "remark": "", "repairOrderNo": repair_order_no, "replyStartTime": "", "replyEndTime": "",
        "serviceGroupIds": [], "serviceUserIds": [], "sources": [], "status": [],
        "templateIds": [], "title": "", "type": "", "updateEndTime": "", "updateStartTime": "",
        "updateTime": "", "defaultSelectVal": "title", "serviceGroup": [], "createTime": "",
        "name": "", "filterName": "", "selectInputType": "content",
        "isOrderFilterForm": True, "language": "zh"
    }
    data = _post(f"{BASE}/ticketOrder/wOrder/pageOrders", payload)
    body = data.get("data")
    if not isinstance(body, dict) or not isinstance(body.get("records"), list):
        raise NextopParseError("Ticket lookup response has no records list.")
    records = body["records"]
    if not records:
        raise NextopLookupEmpty("Ticket lookup returned no exact record.")
    for rec in records:
        if rec.get("repairOrderNo") == repair_order_no:
            return rec
    raise NextopResponseError("Ticket lookup returned records without an exact ticket number.")


def get_basic_info(ticket_id):
    data = _get(f"{BASE}/ticketOrder/wOrder/workbench/basicInfo", {"id": ticket_id})
    if not isinstance(data.get("data"), dict):
        raise NextopParseError("Ticket detail response has no data object.")
    return data["data"]


def _message_list(data):
    body = data.get("data")
    if isinstance(body, list): return body, None
    if isinstance(body, dict):
        for key in ("records", "list", "items"):
            if isinstance(body.get(key), list): return body[key], body
    raise NextopParseError("Ticket messages response has no message list.")

def _message_key(message):
    key = message.get("id") or message.get("messageId")
    if key: return str(key)
    identity = {name: message.get(name) for name in ("sendTime", "createTime", "senderType", "senderName", "senderAddr", "content", "subject")}
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()

def get_messages(ticket_id, size=100):
    """Read and normalize the conversation endpoint; paginate only when its envelope declares a total."""
    params = {"id": ticket_id, "size": size, "current": 1}
    first = _get(f"{BASE}/ticketOrder/wOrder/workbench/messages", params)
    messages, envelope = _message_list(first)
    total = envelope.get("total") if envelope else None
    try: total = int(total)
    except (TypeError, ValueError): total = len(messages)
    current = 2
    while envelope and len(messages) < total and current <= 100:
        page = _get(f"{BASE}/ticketOrder/wOrder/workbench/messages", {"id": ticket_id, "size": size, "current": current})
        extra, _ = _message_list(page)
        if not extra: break
        messages.extend(extra); current += 1
    deduped = {}
    for message in messages:
        deduped.setdefault(_message_key(message), message)
    return sorted(deduped.values(), key=lambda item: (item.get("sendTime") or item.get("createTime") or 0, str(item.get("id") or item.get("messageId") or "")))


def html_to_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # 去掉引用块（转发/回复历史）、图片、样式
    for tag in soup.find_all(["blockquote", "img", "style"]):
        tag.decompose()
    text = soup.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def extract_image_urls(html):
    """提取消息HTML里的图片URL（在html_to_text去图之前调用）"""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):
            urls.append(src)
    return urls


def download_image(url):
    """下载工单附件图片（复用Nextop鉴权）"""
    r = requests.get(url, headers=_headers(), cookies=_cookies(), timeout=30)
    r.raise_for_status()
    return r.content, r.headers.get("content-type", "")


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic")
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")
LOG_FILE_EXTENSIONS = (".log", ".txt", ".csv", ".zip", ".rar", ".7z")


def get_file_link(file_id):
    """通过文件id查询附件的真实下载直链（飞书/网页里点开附件时调用的接口）"""
    data = _get(f"{BASE}/file/fileRecord/{file_id}", {})
    return data.get("data", {})


def get_message_file_attachments(message):
    """Return safe attachment metadata; downloading and vision remain separate read-only phases."""
    files = message.get("files") or []
    result = []
    for f in files:
        name = str(f.get("fileName") or "")
        lower = name.lower()
        kind = ("image" if lower.endswith(IMAGE_EXTENSIONS) else
                "video" if lower.endswith(VIDEO_EXTENSIONS) else
                "file" if lower.endswith(LOG_FILE_EXTENSIONS) else "other")
        result.append({"id": f.get("id"), "file_name": name, "kind": kind})
    return result


MSG_CONTENT_LIMIT = 3000  # 每条消息正文最多传给 AI 的字符数


def get_ticket_full(repair_order_no):
    ticket = find_ticket_by_no(repair_order_no)
    ticket_id = ticket["id"]
    basic = get_basic_info(ticket_id)
    messages = get_messages(ticket_id)
    cleaned_messages, attachment_counts = [], {"image": 0, "video": 0, "file": 0, "other": 0}
    for m in messages:
        raw_html = m.get("content")
        image_urls = extract_image_urls(raw_html)
        file_attachments = get_message_file_attachments(m)
        for attachment in file_attachments: attachment_counts[attachment["kind"]] += 1
        attachment_counts["image"] += len(image_urls)
        content = html_to_text(raw_html)
        if len(content) > MSG_CONTENT_LIMIT:
            content = content[:MSG_CONTENT_LIMIT] + "\n...[truncated]"
        cleaned_messages.append({
            "id": _message_key(m),
            "sender": m.get("senderAddr") or m.get("senderName"),
            "senderName": m.get("senderName"),
            "senderType": m.get("senderType"),  # 1=客户来信, 2=客服回复
            # Preserve role/direction hints for service-side reply classification.
            "senderRole": m.get("senderRole") or m.get("role"),
            "authorType": m.get("authorType"),
            "direction": m.get("direction") or m.get("messageDirection"),
            "isSystem": bool(m.get("isSystem") or m.get("systemMessage")),
            "time": m.get("sendTime"),
            "subject": m.get("subject"),
            "content": content,
            "image_urls": image_urls,
            "file_attachments": file_attachments,
        })
    return {
        "list_info": ticket,
        "basic": basic,
        "messages": cleaned_messages,
        "attachment_counts": attachment_counts,
    }


if __name__ == "__main__":
    import sys
    import json
    no = sys.argv[1] if len(sys.argv) > 1 else "E193328"
    full = get_ticket_full(no)
    with open(f"ticket_{no}.json", "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=2)
    print(f"saved to ticket_{no}.json")

"""新工单标签与字段自动填充引擎（供 main.py 调用）：
- 一级/二级标签：实时读标签定义表 + DeepSeek 归类
- 硬件逻辑/回复模板：按二级查 fields_cache.json（随包发的字段库）
- 案例数：实时统计（写入后刷新同类工单，保持一致）
"""
import os, json, requests, time
import feishu_api, config

WIKI_TOKEN = "J98gwFrl8iG5yqkOCUZcEDaGn2c"   # 标签定义表所在 wiki
TAG_TABLE = "tblkmOOvjsaFVz7K"                # 一级/二级/三级 定义表
# 标签归类是"从清单里选一个"的结构化任务，默认用快模型 flash 提速
_MODEL = getattr(config, "DEEPSEEK_MODEL_FAST", None) or "deepseek-v4-flash"
_FIELDS_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fields_cache.json")
_KW = "三级标签（关键词/别名/错误代码）"


def _gt(v):
    if isinstance(v, list):
        if v and isinstance(v[0], dict) and "text" in v[0]:
            return "".join(s.get("text", "") for s in v if isinstance(s, dict))
        return ", ".join(str(x) for x in v)
    if isinstance(v, dict):
        return v.get("text") or v.get("name") or ""
    return str(v) if v is not None else ""


_tax = None
_prompt = None
_lib = None


def _taxonomy():
    global _tax
    if _tax is None:
        base = f"/open-apis/bitable/v1/apps/{WIKI_TOKEN}/tables/{TAG_TABLE}/records/search"
        rows, page = [], None
        while True:
            params = {"page_size": 500}
            if page:
                params["page_token"] = page
            d = feishu_api._request("POST", base, params=params, json={})["data"]
            rows += d.get("items", [])
            if not d.get("has_more") or not d.get("page_token"):
                break
            page = d["page_token"]
        _tax = [{"l1": _gt(r["fields"].get("一级标签")), "l2": _gt(r["fields"].get("二级标签")),
                 "kw": _gt(r["fields"].get(_KW))} for r in rows]
        _tax = [x for x in _tax if x["l1"] and x["l2"]]
    return _tax


def _build_prompt():
    global _prompt
    if _prompt is None:
        from collections import OrderedDict
        g = OrderedDict()
        for x in _taxonomy():
            g.setdefault(x["l1"], []).append((x["l2"], x["kw"]))
        t = ""
        for l1, items in g.items():
            t += f"【{l1}】\n"
            for l2, kw in items:
                t += f"  {l2} : {kw}\n"
        _prompt = ("你是Mammotion（割草机器人）售后工单分类助手。下面是标签体系："
                   "【一级问题】换行缩进「二级问题 : 关键词/别名/错误代码信号」。\n"
                   "根据工单内容（故障现象、错误码、描述），选出最匹配的【二级问题】，只输出二级问题原文；"
                   "判不出、或不是设备故障（纯备件料号咨询等按其对应二级；实在没有就空）就输出空字符串。\n\n"
                   + t + "\n输出JSON: {\"l2\":\"<二级问题原文或空>\"}\n"
                   "规则：①错误码是强信号，工单错误码出现在某二级信号里就优先选它；②其次按现象关键词；"
                   "③只能输出上面列出的二级原文；④一个工单选一个最主要的。")
    return _prompt


def _field_lib():
    global _lib
    if _lib is None:
        _lib = json.load(open(_FIELDS_CACHE, encoding="utf-8")) if os.path.exists(_FIELDS_CACHE) else {}
    return _lib


def classify(text, retries=4):
    """返回 (一级, 二级)；判不出返回 ('','')"""
    import time as _time
    l2map = {x["l2"]: x["l1"] for x in _taxonomy()}
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.post(config.DEEPSEEK_BASE_URL + "/chat/completions",
                headers={"Authorization": "Bearer " + config.DEEPSEEK_API_KEY, "Content-Type": "application/json"},
                json={"model": _MODEL, "messages": [{"role": "system", "content": _build_prompt()},
                      {"role": "user", "content": text[:2500]}],
                      "response_format": {"type": "json_object"}, "temperature": 0.1},
                # (连接超时, 读取超时)：线路抽风快速失败重试，正常生成给足 90s
                timeout=(20, 90))
            r.raise_for_status()
            l2 = json.loads(r.json()["choices"][0]["message"]["content"]).get("l2", "").strip()
            return (l2map.get(l2, ""), l2) if l2 in l2map else ("", "")
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                _time.sleep(2 ** attempt)
    print(f"  标签分类失败（{retries}次）: {last_err}")
    return ("", "")


def apply_lib(fields, l1, l2):
    """用已算好的 (一级,二级) 给 fields 补上标签 + 硬件逻辑/回复模板/SOP。返回二级。"""
    if not l2:
        return None
    fields["一级标签"] = l1
    fields["二级标签"] = l2
    lib = _field_lib().get(l2, {})
    if lib.get("hw"):
        fields["硬件逻辑与原因解析"] = lib["hw"]
    if lib.get("en"):
        fields["解决方案回复模板(EN)"] = lib["en"]
    if lib.get("sop"):          # 按二级的 SOP，覆盖按 PIE Issue Type 的旧 SOP
        fields["SOP"] = lib["sop"]
    return l2


def enrich(fields, text):
    """一步：分类 + 补字段（串行）。main.py 用并行版本时改调 classify + apply_lib。"""
    return apply_lib(fields, *classify(text))


def refresh_case_count(l2, expected_record_id=None, max_attempts=3):
    """Authoritatively recount one L2 group with bounded create visibility retry."""
    if not l2:
        return {"success": True, "count": None, "record_seen": True, "updated": 0}
    base = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/search"
    def query():
        items, page = [], None
        while True:
            params = {"page_size": 500}
            if page:
                params["page_token"] = page
            body = {"field_names": ["案例数"], "filter": {"conjunction": "and", "conditions": [{"field_name": "二级标签", "operator": "is", "value": [l2]}]}}
            d = feishu_api._request("POST", base, params=params, json=body).get("data", {})
            items += d.get("items", [])
            if not d.get("has_more") or not d.get("page_token"):
                return items
            page = d["page_token"]

    items = []
    for attempt in range(max(1, min(max_attempts, 3))):
        items = query()
        if not expected_record_id or any(item.get("record_id") == expected_record_id for item in items):
            break
        if attempt < min(max_attempts, 3) - 1:
            time.sleep((0.35, 0.9)[attempt])
    record_seen = not expected_record_id or any(item.get("record_id") == expected_record_id for item in items)
    if not record_seen:
        return {"success": False, "count": None, "record_seen": False, "updated": 0, "warning": "created record not yet visible"}
    n = len(items)
    # Only write stale records; the count is derived from the filtered ITR set.
    stale = [it["record_id"] for it in items if it.get("fields", {}).get("案例数") != n]
    for rid in stale:
        response = feishu_api.update_record(rid, {"案例数": n})
        if response.get("code") != 0:
            return {"success": False, "count": n, "record_seen": True, "updated": len(stale), "warning": "case count write rejected"}
    verified = query()
    consistent = len(verified) == n and all(item.get("fields", {}).get("案例数") == n for item in verified)
    return {"success": consistent, "count": n, "record_seen": True, "updated": len(stale), "warning": None if consistent else "case count verification pending"}


def reconcile_case_counts():
    """Low-frequency authoritative repair for external deletes/edits.

    This is intentionally separate from normal GUI work. It reads every
    surviving record, derives counts from the current table, writes stale rows
    only, then verifies the result. It never uses +/- arithmetic.
    """
    started = time.time()
    records = feishu_api.get_all_records(["二级标签", "案例数"])
    groups = {}
    for record in records:
        fields = record.get("fields", {})
        l2 = feishu_api.normalize_field_value(fields.get("二级标签"))
        l2 = str(l2 or "").strip()
        if l2:
            groups.setdefault(l2, []).append(record)
    stale = []
    for l2, members in groups.items():
        expected = len(members)
        stale.extend((member.get("record_id"), expected) for member in members if member.get("fields", {}).get("案例数") != expected)
    updated = 0
    for record_id, expected in stale:
        response = feishu_api.update_record(record_id, {"案例数": expected})
        if response.get("code") != 0:
            return {"success": False, "records_scanned": len(records), "labels_counted": len(groups), "stale_rows": len(stale), "updated_rows": updated, "verify_result": "not_run", "elapsed_seconds": round(time.time() - started, 3)}
        updated += 1
    verified = feishu_api.get_all_records(["二级标签", "案例数"])
    verified_groups = {}
    for record in verified:
        fields = record.get("fields", {})
        l2 = str(feishu_api.normalize_field_value(fields.get("二级标签")) or "").strip()
        if l2:
            verified_groups.setdefault(l2, []).append(record)
    consistent = all(all(item.get("fields", {}).get("案例数") == len(items) for item in items) for items in verified_groups.values())
    return {"success": consistent, "records_scanned": len(records), "labels_counted": len(groups), "stale_rows": len(stale), "updated_rows": updated, "verify_result": "pass" if consistent else "fail", "elapsed_seconds": round(time.time() - started, 3)}

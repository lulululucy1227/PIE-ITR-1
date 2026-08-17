import re
import time
import requests
import config

BASE = "https://open.feishu.cn"
_AUTH_ERROR_CODES = {99991663, 99991661, 99991677, 99991668}


def _safe_feishu_message(message):
    """Keep technical diagnostics while excluding likely submitted values."""
    text = re.sub(r"\s+", " ", str(message or "")).strip()
    if re.search(r"(?i)\b(value|content|description|solution|case history|record data)\b", text):
        return "Feishu rejected submitted field data."
    text = re.sub(r"(['\"]).*?\1", "[redacted]", text)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[redacted-email]", text)
    return text[:240] or "Feishu rejected the operation."


def _with_operation(response, operation):
    """Expose only safe response diagnostics; never request payload or headers."""
    result = dict(response or {})
    result["operation"] = operation
    result["http_status"] = result.get("http_status")
    result["feishu_code"] = result.get("code")
    result["feishu_msg"] = _safe_feishu_message(result.get("msg"))
    result.pop("raw", None)
    return result


def is_network_error(exc):
    return isinstance(exc, requests.exceptions.RequestException)


def _read_config_text():
    with open("config.py", "r", encoding="utf-8") as f:
        return f.read()


def _write_config_text(text):
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(text)


def _persist_tokens(access_token, refresh_token):
    text = _read_config_text()
    text = re.sub(r'FEISHU_USER_ACCESS_TOKEN = ".*?"',
                   f'FEISHU_USER_ACCESS_TOKEN = "{access_token}"', text)
    text = re.sub(r'FEISHU_USER_REFRESH_TOKEN = ".*?"',
                   f'FEISHU_USER_REFRESH_TOKEN = "{refresh_token}"', text)
    _write_config_text(text)
    config.FEISHU_USER_ACCESS_TOKEN = access_token
    config.FEISHU_USER_REFRESH_TOKEN = refresh_token


def _get_app_access_token():
    resp = requests.post(f"{BASE}/open-apis/auth/v3/app_access_token/internal",
                          json={"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET})
    resp.raise_for_status()
    return resp.json()["app_access_token"]


def refresh_user_token():
    """用 refresh_token 换取新的 access_token，并写回 config.py"""
    app_token = _get_app_access_token()
    resp = requests.post(
        f"{BASE}/open-apis/authen/v1/refresh_access_token",
        headers={"Authorization": f"Bearer {app_token}", "Content-Type": "application/json"},
        json={"grant_type": "refresh_token", "refresh_token": config.FEISHU_USER_REFRESH_TOKEN},
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"刷新飞书token失败: {data}")
    _persist_tokens(data["data"]["access_token"], data["data"]["refresh_token"])
    return config.FEISHU_USER_ACCESS_TOKEN


def _request(method, path, **kwargs):
    import time as _t
    url = f"{BASE}{path}"
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {config.FEISHU_USER_ACCESS_TOKEN}"
    headers["Content-Type"] = "application/json; charset=utf-8"
    kwargs.setdefault("timeout", 30)
    # 网络瞬断（SSL/连接重置）自动重试
    resp = None
    for attempt in range(4):
        try:
            resp = requests.request(method, url, headers=headers, **kwargs)
            break
        except requests.exceptions.RequestException as e:
            if attempt == 3:
                raise
            _t.sleep(1.5 * (attempt + 1))
    try:
        data = resp.json()
    except Exception:
        return {"code": -1, "msg": "Feishu returned a non-JSON response.", "http_status": resp.status_code}
    data["http_status"] = resp.status_code
    if data.get("code") in _AUTH_ERROR_CODES:
        # token 过期，刷新后重试一次
        refresh_user_token()
        headers["Authorization"] = f"Bearer {config.FEISHU_USER_ACCESS_TOKEN}"
        resp = requests.request(method, url, headers=headers, **kwargs)
        try:
            data = resp.json()
        except Exception:
            return {"code": -1, "msg": "Feishu returned a non-JSON response.", "http_status": resp.status_code}
        data["http_status"] = resp.status_code
    return data


def create_record(fields: dict):
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records"
    return _with_operation(_request("POST", path, json={"fields": fields}), "create_record")


def find_record(reference_no: str):
    """按 Reference No. 查找已有记录，返回 record_id 或 None"""
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/search"
    data = _request("POST", path, json={
        "filter": {
            "conjunction": "and",
            "conditions": [{
                "field_name": "Reference No.",
                "operator": "is",
                "value": [reference_no],
            }],
        },
        "page_size": 1,
    })
    items = data.get("data", {}).get("items", [])
    if items:
        return items[0]["record_id"]
    return None


def find_records_by_reference_exact(reference_no, field_names=None):
    """Read-only exact Reference No. lookup; never chooses a duplicate."""
    return _find_records_exact("Reference No.", reference_no, field_names)


def find_records_by_ticket_no_exact(ticket_no, field_names=None):
    """Read-only exact Ticket No. lookup; caller handles 0/1/many."""
    return _find_records_exact("Ticket No.", ticket_no, field_names)


def _find_records_exact(field_name, value, field_names=None):
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/search"
    data = _request("POST", path, params={"page_size": 100}, json={
        "field_names": list(field_names or []),
        "filter": {"conjunction": "and", "conditions": [{"field_name": field_name, "operator": "is", "value": [str(value or "").strip()]}]},
    })
    if data.get("code") != 0:
        raise RuntimeError("Feishu exact lookup failed.")
    return data.get("data", {}).get("items", [])


def update_record(record_id: str, fields: dict):
    """更新已有记录的指定字段"""
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/{record_id}"
    return _with_operation(_request("PUT", path, json={"fields": fields}), "update_record")


def get_record(record_id: str):
    """获取单条记录的所有字段"""
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/{record_id}"
    data = _request("GET", path)
    return data.get("data", {}).get("record", {})


def upload_attachment(file_bytes: bytes, file_name: str):
    """上传附件到多维表格，返回 file_token"""
    url = f"{BASE}/open-apis/drive/v1/medias/upload_all"
    headers = {"Authorization": f"Bearer {config.FEISHU_USER_ACCESS_TOKEN}"}
    form = {
        "file_name": (None, file_name),
        "parent_type": (None, "bitable_file"),
        "parent_node": (None, config.FEISHU_APP_TOKEN),
        "size": (None, str(len(file_bytes))),
        "file": (file_name, file_bytes),
    }
    resp = requests.post(url, headers=headers, files=form)
    data = resp.json()
    if data.get("code") in (99991663, 99991661, 99991677, 99991668):
        refresh_user_token()
        headers["Authorization"] = f"Bearer {config.FEISHU_USER_ACCESS_TOKEN}"
        resp = requests.post(url, headers=headers, files=form)
        data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"上传附件失败: {data}")
    return data["data"]["file_token"]


def download_attachment(file_token: str) -> bytes:
    """从飞书下载附件内容（用于计算hash）"""
    url = f"{BASE}/open-apis/drive/v1/medias/{file_token}/download"
    headers = {"Authorization": f"Bearer {config.FEISHU_USER_ACCESS_TOKEN}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code in (401, 403):
        refresh_user_token()
        headers["Authorization"] = f"Bearer {config.FEISHU_USER_ACCESS_TOKEN}"
        resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.content


_select_options_cache = {}


def get_select_field_options(field_name, use_cache=True):
    """读取指定单选/多选字段的实时选项名列表（去重保序）。
    优化：一次把所有字段的选项都缓存下来，避免每个字段各拉一次接口。"""
    if use_cache and field_name in _select_options_cache:
        return _select_options_cache[field_name]
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/fields"
    data = _request("GET", path, params={"page_size": 200})
    for f in data.get("data", {}).get("items", []):
        names, seen = [], set()
        for o in ((f.get("property") or {}).get("options", []) or []):
            n = o.get("name")
            if n and n not in seen:
                seen.add(n)
                names.append(n)
        _select_options_cache[f.get("field_name")] = names   # 一次缓存所有字段
    return _select_options_cache.get(field_name, [])


def get_table_fields_metadata():
    """Read ITR field metadata without creating or changing any field/record."""
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/fields"
    data = _request("GET", path, params={"page_size": 200})
    if data.get("code") != 0:
        raise RuntimeError("Feishu field metadata request failed.")
    return data.get("data", {}).get("items", [])


def get_records_sample(field_names, limit=10):
    """Read a bounded field-only sample for diagnostics; never writes records."""
    safe_limit = max(1, min(int(limit), 10))
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/search"
    data = _request(
        "POST",
        path,
        params={"page_size": safe_limit},
        json={"field_names": list(field_names or [])},
    )
    if data.get("code") != 0:
        raise RuntimeError("Feishu record sample request failed.")
    return data.get("data", {}).get("items", [])[:safe_limit]


def get_records_for_matching(field_names, limit=100):
    """Read a bounded ITR slice for legacy duplicate detection only."""
    safe_limit = min(max(int(limit), 1), 100)
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/search"
    data = _request("POST", path, params={"page_size": safe_limit}, json={"field_names": list(field_names or [])})
    if data.get("code") != 0:
        raise RuntimeError("Feishu matching-record request failed.")
    return data.get("data", {}).get("items", [])[:safe_limit]


def get_all_records(field_names=None):
    """获取表格所有记录，返回 list of {record_id, fields}"""
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/search"
    results = []
    page_token = None
    while True:
        # ⚠ records/search 的 page_size/page_token 必须放 URL 查询参数，放 body 会翻页失效导致死循环
        params = {"page_size": 500}
        if page_token:
            params["page_token"] = page_token
        body = {}
        if field_names:
            body["field_names"] = field_names
        data = _request("POST", path, params=params, json=body)
        d = data.get("data", {})
        results.extend(d.get("items", []))
        if not d.get("has_more") or not d.get("page_token"):
            break
        page_token = d["page_token"]
    return results


def find_records_by_reference_no(reference_no, field_names, limit=100):
    """Read a bounded same-source record set for manual-case candidate matching.

    This is deliberately read-only and does not page through the full ITR.
    Callers must still require an explicit user choice before any update.
    """
    path = f"/open-apis/bitable/v1/apps/{config.FEISHU_APP_TOKEN}/tables/{config.FEISHU_TABLE_ID}/records/search"
    data = _request("POST", path, params={"page_size": min(max(limit, 1), 100)}, json={
        "field_names": field_names,
        "filter": {
            "conjunction": "and",
            "conditions": [{
                "field_name": "Reference No.",
                "operator": "is",
                "value": [reference_no],
            }],
        },
    })
    return data.get("data", {}).get("items", [])


def _text_value(field_val):
    """统一提取飞书字段的文字值，兼容多行文本(list)、单选(dict)、普通字符串"""
    if isinstance(field_val, list):
        return "".join(
            seg.get("text", "") for seg in field_val if isinstance(seg, dict)
        )
    if isinstance(field_val, dict):
        # SingleSelect / 单选字段返回 {"text": "...", "value": "..."}
        return field_val.get("text") or field_val.get("value") or ""
    if isinstance(field_val, str):
        return field_val
    return ""


def normalize_field_value(field_val):
    """Normalize read-only Bitable values for future candidate display/matching.

    This helper intentionally has no write-side behavior.  It preserves the
    useful native Python shape: rich-text lists become text, multi-select
    string lists stay lists, date values stay numeric timestamps, and missing
    fields remain ``None``.
    """
    if field_val is None:
        return None
    if isinstance(field_val, str):
        return field_val
    if isinstance(field_val, (int, float)):
        return field_val
    if isinstance(field_val, dict):
        return field_val.get("text") or field_val.get("value") or field_val.get("name") or ""
    if isinstance(field_val, list):
        if not field_val:
            return []
        if all(isinstance(item, str) for item in field_val):
            return list(field_val)
        if all(isinstance(item, dict) for item in field_val):
            return "".join(item.get("text", "") for item in field_val)
        return list(field_val)
    return field_val

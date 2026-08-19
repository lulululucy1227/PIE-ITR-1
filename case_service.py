"""Reusable case orchestration for the NextopSync CLI and future GUI."""
import re
import threading
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
from time import perf_counter

import analyzer
import feishu_api
import field_options as fo
import images
import nextop_api
import settings
import tag_engine


FIELD_MAP = {
    "case_history": "Case History", "device_name": "Device name",
    "disti_dealer": "Disti/Dealer/Service Point", "model_type": "Model Type",
    "description": "Description", "pie_comment": "PIE-Comment",
    "solutions": "Solutions", "fault_symptom": "Fault Symptom",
    "error_code": "Error Code", "error_massages": "Error massages",
}
V2_MANAGED_FIELDS = tuple(FIELD_MAP.values()) + ("一级标签", "二级标签")
ITR_TODO_FIELD = "加入ITR待办"
MULTI_SELECT_FIELDS = {"Fault Symptom", "Error Code"}
_ALLOWED_OPTIONS = {"Fault Symptom": set(fo.FAULT_SYMPTOM), "Error Code": set(fo.ERROR_CODE)}
_CANDIDATE_FIELDS = ["Ticket No.", "Reference No.", "Disti/Dealer/Service Point", "Device name", "Model Type", "PIE-Comment", "Description", "Solutions", "Fault Symptom", "Error Code", "Replied Time-NEW", "Status", "Ticket Created Time", "案例数", "Case History", "一级标签", "二级标签", ITR_TODO_FIELD]
_CANDIDATE_LIMIT = 5
_RECENT_CANDIDATE_DAYS = 14
_MANUAL_SOURCES = {"whatsapp", "lark", "email"}
_record_write_locks, _record_lock_guard = set(), threading.Lock()

@contextmanager
def _record_write_guard(record_id):
    """Non-blocking authoritative lock for every existing-record write."""
    with _record_lock_guard:
        if record_id in _record_write_locks:
            yield False
            return
        _record_write_locks.add(record_id)
    try:
        yield True
    finally:
        with _record_lock_guard:
            _record_write_locks.discard(record_id)

def parse_case_history_for_display(history):
    blocks=[b.strip() for b in str(history or '').split('\n\n') if b.strip()]
    events=[]
    for block in blocks:
        first, _, content=block.partition('\n'); role='UNKNOWN'
        low=first.casefold()
        if 'pie' in low: role='PIE_REPLY'
        elif 'dealer' in low: role='DEALER'
        elif 'customer' in low: role='CUSTOMER'
        elif 'system' in low: role='SYSTEM'
        events.append({'timestamp': first if first.startswith('[') else None, 'role': role, 'content': content if content else block})
    return list(reversed(events))

def analyze_existing_case_for_inspector(case):
    return analyzer.analyze_case_for_inspector(case)

def translate_inspector_analysis_to_zh(analysis):
    return analyzer.translate_inspector_analysis_to_zh(analysis)


@dataclass
class ManualDraft:
    source: str
    raw_text: str = field(repr=False)
    new_block: str = field(repr=False)
    new_analysis: dict = field(repr=False)
    imported_ms: int
    manual_messages: list = field(default_factory=list, repr=False)
    tags: tuple = ("", "")


@dataclass
class PreparedNextopCase:
    """Read/analyze-only Nextop review object; it never writes Feishu."""
    ticket_no: str
    case_history: str = field(repr=False)
    analysis: dict = field(default_factory=dict, repr=False)
    fields: dict = field(default_factory=dict, repr=False)
    messages: list = field(default_factory=list, repr=False)
    list_info: dict = field(default_factory=dict, repr=False)
    existing_record_id: str | None = None
    existing_case: dict | None = None
    match_status: str = "NOT_FOUND"
    matches: list = field(default_factory=list)
    # ``exact`` means the target came from the stable Reference No. lookup;
    # ``legacy`` is an explicit user-confirmed structured-match target.
    # Commit uses this to recheck the right freshness contract without doing
    # another Nextop fetch or analyzer run.
    selected_match_kind: str | None = None
    can_create: bool = False
    can_update: bool = False
    context_pack: dict = field(default_factory=dict, repr=False)


@dataclass
class CaseEvidenceAttachment:
    """Future read-only image evidence contract; no OCR or writes in D2-D."""
    attachment_id: str | None = None
    source: str = ""
    mime_type: str = ""
    image_ref: str = ""
    caption: str = ""
    extracted_text: str = ""
    vision_summary: str = ""
    error_codes: list = field(default_factory=list)
    processed: bool = False


_WHATSAPP_CN_HEADER = re.compile(r"^\[(\d{1,2}):(\d{2}),\s*(\d{4})年(\d{1,2})月(\d{1,2})日\]\s*([^:]+):\s*(.*)$")
_WHATSAPP_HEADER = re.compile(r"^\[(\d{1,2})/(\d{1,2})/(\d{4}),\s*(\d{1,2}):(\d{2})\]\s*([^:]+):\s*(.*)$")


def parse_manual_messages(text):
    """Extract only reliable WhatsApp-style message boundaries/timestamps.

    Original Case History remains unchanged; these in-memory IDs support reply
    classification and are never written to Feishu.
    """
    messages, current = [], None
    for line in str(text or "").splitlines():
        cn, standard = _WHATSAPP_CN_HEADER.match(line), _WHATSAPP_HEADER.match(line)
        timestamp_ms = None
        if cn:
            hour, minute, year, month, day, _sender, content = cn.groups()
            timestamp_ms = int(datetime(int(year), int(month), int(day), int(hour), int(minute), tzinfo=timezone.utc).timestamp() * 1000)
        elif standard:
            day, month, year, hour, minute, _sender, content = standard.groups()
            timestamp_ms = int(datetime(int(year), int(month), int(day), int(hour), int(minute), tzinfo=timezone.utc).timestamp() * 1000)
        if cn or standard:
            if current: messages.append(current)
            current = {"id": len(messages) + 1, "timestamp_ms": timestamp_ms, "content": content.strip()}
        elif current:
            current["content"] = (current["content"] + "\n" + line).strip()
    if current: messages.append(current)
    messages = [item for item in messages if item["content"]]
    return messages or ([{"id": 1, "timestamp_ms": None, "content": str(text or "").strip()}] if str(text or "").strip() else [])


def _progress(callback, stage, message, success=None):
    if callback:
        callback(stage, message, success)


def _result(success, action, message, **extra):
    return {"success": success, "action": action, "message": message, **extra}


def _response_record_id(response):
    """Extract only the record identifier when the Feishu create response provides it."""
    data = response.get("data") or {}
    return (data.get("record") or {}).get("record_id") or data.get("record_id")


def _feishu_failure(response, action, message, **extra):
    """Return safe Feishu diagnostics without exposing a response or payload."""
    code = response.get("feishu_code", response.get("code"))
    http_status = response.get("http_status")
    safe_message = response.get("feishu_msg") or "Feishu rejected the operation."
    if http_status in (401, 403) or code in {99991663, 99991661, 99991677, 99991668}:
        category = "authorization"
    elif re.search(r"field|option|value|validation", safe_message, re.I):
        category = "field_validation"
    else:
        category = "feishu_api"
    return _result(False, action, message, error_type="feishu_api_error", operation=response.get("operation"), http_status=http_status, feishu_code=code, safe_message=safe_message, error_category=category, **extra)


def _exception_failure(exc, action, message, **extra):
    error_type = "network_error" if feishu_api.is_network_error(exc) else "python_error"
    safe_message = "Network request failed." if error_type == "network_error" else "Unexpected application error."
    return _result(False, action, message, error_type=error_type, safe_message=safe_message, **extra)


def _join(value):
    return ", ".join(str(item) for item in value) if isinstance(value, list) else str(value or "")


def _tag_text(analysis):
    parts = []
    for label, key in (("Model", "model_type"), ("Error code", "error_code"), ("Error message", "error_massages"), ("Fault symptom", "fault_symptom"), ("Description", "description"), ("PIE comment", "pie_comment")):
        if analysis.get(key):
            parts.append(f"{label}: {_join(analysis[key])}")
    return "\n".join(parts)


def _only_digits(value): return re.sub(r"[^\d]", "", value or "")


def _match_dealer_alias(*texts):
    blob = " ".join(str(text) for text in texts if text).lower()
    if not blob.strip(): return None
    digits = _only_digits(blob)
    aliases = dict(getattr(fo, "DEALER_ALIASES", {}))
    aliases.update(getattr(settings, "NEXTOP_DEALER_ALIASES", {}))
    for alias, dealer in aliases.items():
        normalized = alias.strip().lower()
        if normalized.startswith("+"):
            if _only_digits(normalized) and _only_digits(normalized) in digits: return dealer
        elif normalized and re.search(rf"(?<!\w){re.escape(normalized)}(?!\w)", blob): return dealer
    return None


_AUDITED_SINGLE_SELECTS = ("Disti/Dealer/Service Point", "Model Type", "一级标签", "二级标签", "Status")


def _audit_single(audit, field_name, value, options_query_success=None, exact_validation=None):
    if audit is None or field_name not in _AUDITED_SINGLE_SELECTS:
        return
    audit[field_name] = {
        "field_name": field_name,
        "python_type": type(value).__name__ if value is not None else "NoneType",
        "is_empty": value in (None, "", []),
        "live_options_query_success": options_query_success,
        "exact_validation_result": exact_validation,
    }
    if field_name == "Status":
        audit[field_name]["expected_enum"] = "Replied"


def _guard_select(fields, field_name, audit=None):
    value = fields.get(field_name)
    original_value = value
    if isinstance(value, list): value, fields[field_name] = (value[0] if value else ""), (value[0] if value else "")
    try: valid = set(feishu_api.get_select_field_options(field_name))
    except Exception:
        # A nonempty value not verified against live options must never be written.
        if value not in (None, "", []): fields[field_name] = None
        _audit_single(audit, field_name, fields.get(field_name), False, None)
        return
    if value in (None, "", []):
        _audit_single(audit, field_name, fields.get(field_name), True, None)
        return
    if value not in valid:
        fields[field_name] = None
        _audit_single(audit, field_name, None, True, False)
        return
    _audit_single(audit, field_name, value, True, True)


def _apply_dealer_alias(fields, *texts):
    dealer = _match_dealer_alias(*texts)
    if not dealer: return
    try: valid = set(feishu_api.get_select_field_options("Disti/Dealer/Service Point"))
    except Exception: valid = set()
    if valid and dealer in valid: fields["Disti/Dealer/Service Point"] = dealer


def _guard_dealer(fields, audit=None):
    value = fields.get("Disti/Dealer/Service Point")
    try: valid = set(feishu_api.get_select_field_options("Disti/Dealer/Service Point"))
    except Exception:
        if value: fields["Disti/Dealer/Service Point"] = None
        _audit_single(audit, "Disti/Dealer/Service Point", fields.get("Disti/Dealer/Service Point"), False, None)
        return
    if not value:
        _audit_single(audit, "Disti/Dealer/Service Point", value, True, None)
        return
    if value not in valid: fields["Disti/Dealer/Service Point"] = None
    _audit_single(audit, "Disti/Dealer/Service Point", fields.get("Disti/Dealer/Service Point"), True, value in valid)


def _wrap_field(name, value):
    if name not in MULTI_SELECT_FIELDS: return value or ""
    items = [str(x).strip() for x in (value if isinstance(value, list) else str(value or "").split(",")) if str(x).strip()]
    return [x for x in items if x in _ALLOWED_OPTIONS[name]]


def _guard_device_name(fields):
    """Never treat a product model option as a concrete device identifier."""
    device_name = str(fields.get("Device name") or "").strip()
    if not device_name:
        return
    model_type = str(fields.get("Model Type") or "").strip()
    if _normalized_text(device_name) == _normalized_text(model_type):
        fields["Device name"] = ""
        return
    try:
        model_options = feishu_api.get_select_field_options("Model Type")
    except Exception:
        return
    if _normalized_text(device_name) in {_normalized_text(option) for option in model_options}:
        fields["Device name"] = ""


def format_time(value):
    if value in (None, ""): return ""
    try:
        numeric = int(value) / 1000 if int(value) > 10_000_000_000 else int(value)
        return datetime.fromtimestamp(numeric, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OSError, OverflowError): return ""


def build_nextop_case_history(messages):
    blocks, pie_names = [], {name.lower() for name in settings.PIE_SENDERS}
    for message in messages:
        content = str(message.get("content") or "").strip()
        if not content: continue
        header, sender = [], str(message.get("senderName") or "").strip()
        if format_time(message.get("time")): header.append(format_time(message.get("time")))
        if message.get("senderType") == 2 and sender and sender.lower() in pie_names: header.append(f"PIE - {sender}")
        elif message.get("senderType") == 1 and sender: header.append(f"Agent - {sender}")
        elif sender: header.append(sender)
        blocks.append(("[" + "] [".join(header) + "]\n" if header else "") + content)
    return "\n\n".join(blocks)


def build_imported_case_history(source, text, imported_at=None):
    timestamp = imported_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"[Imported: {timestamp}] [{source}]\n{text.strip()}" if text.strip() else ""


def _apply_tags(fields, analysis, tags=None):
    l1, l2 = tags if tags is not None else tag_engine.classify(_tag_text(analysis))
    fields["一级标签"], fields["二级标签"] = l1 or "", l2 or ""


def build_v2_fields(case_history, analysis, dealer_context=(), single_select_audit=None, tags=None):
    fields = {"Case History": case_history}
    for key, name in FIELD_MAP.items():
        if key != "case_history": fields[name] = _wrap_field(name, analysis.get(key, ""))
    _apply_dealer_alias(fields, *dealer_context); _guard_dealer(fields, single_select_audit); _guard_select(fields, "Model Type", single_select_audit)
    _apply_tags(fields, analysis, tags); _guard_select(fields, "一级标签", single_select_audit); _guard_select(fields, "二级标签", single_select_audit)
    _guard_device_name(fields)
    for name in V2_MANAGED_FIELDS: fields.setdefault(name, [] if name in MULTI_SELECT_FIELDS else "")
    return fields


def sanitize_create_fields(fields):
    """Create records omit no-value fields; updates retain explicit clearing values."""
    return {
        name: value for name, value in fields.items()
        if value is not None
        and not (isinstance(value, str) and not value.strip())
        and not (isinstance(value, (list, tuple, set, dict)) and not value)
    }


def sanitize_update_fields(fields, single_select_audit=None):
    """Keep V2 stale clearing, but never send an illegal empty single select.

    Feishu accepts the established text/multi-select clear shapes already used
    by V2 (``""`` and ``[]``).  Empty single selects are omitted instead of
    being serialized as ``""``; the old value is safely retained when the API
    does not provide a verified clear representation.
    """
    payload = dict(fields)
    for name in _AUDITED_SINGLE_SELECTS:
        if name not in payload:
            continue
        value = payload[name]
        if value in (None, "", [], {}):
            payload.pop(name, None)
            if single_select_audit is not None:
                entry = single_select_audit.setdefault(name, {"field_name": name})
                entry.update({"action": "CLEAR_SKIPPED", "clear_strategy": "omit_unsupported_single_select", "python_type": type(value).__name__, "is_empty": True})
        elif not isinstance(value, str):
            payload.pop(name, None)
            if single_select_audit is not None:
                entry = single_select_audit.setdefault(name, {"field_name": name})
                entry.update({"action": "OMIT", "python_type": type(value).__name__, "is_empty": False})
        elif single_select_audit is not None:
            single_select_audit.setdefault(name, {"field_name": name}).update({"action": "SUBMIT", "python_type": "str", "is_empty": False})
    return payload


def finalize_update_single_select_audit(audit, payload):
    result = {}
    for name in _AUDITED_SINGLE_SELECTS:
        entry = dict((audit or {}).get(name, {}))
        entry.setdefault("field_name", name)
        entry.setdefault("action", "SUBMIT" if name in payload else "OMIT")
        entry.setdefault("python_type", type(payload.get(name)).__name__ if name in payload else "NoneType")
        entry.setdefault("is_empty", name not in payload)
        if name == "Status": entry["expected_enum"] = "Replied"
        result[name] = entry
    return result


def finalize_single_select_audit(audit, fields, payload):
    """Return only safe categories for the final create payload."""
    result = {}
    for field_name in _AUDITED_SINGLE_SELECTS:
        entry = dict((audit or {}).get(field_name, {}))
        value = fields.get(field_name)
        entry.update({
            "field_name": field_name,
            "submit_or_omit": "submit" if field_name in payload else "omit",
            "python_type": type(value).__name__ if value is not None else "NoneType",
            "is_empty": value in (None, "", []),
        })
        if field_name == "Status": entry["expected_enum"] = "Replied"
        result[field_name] = entry
    return result


def _is_nextop_support_reply(message):
    """Use Nextop role/direction metadata first; names are fallback only."""
    if message.get("isSystem"):
        return False
    role_data = " ".join(str(message.get(key) or "") for key in ("senderRole", "authorType", "direction")).casefold()
    if any(token in role_data for token in ("system", "bot", "customer", "dealer", "inbound")):
        return False
    if any(token in role_data for token in ("support", "agent", "internal", "staff", "pie", "outbound")):
        return True
    sender_type = str(message.get("senderType") or "").strip()
    if sender_type == "2":
        return True
    # Older payloads sometimes lack role metadata.  Known PIE identity is only
    # a conservative supporting signal, never the primary whitelist.
    return sender_type != "1" and str(message.get("senderName") or "").casefold() in {name.casefold() for name in settings.PIE_SENDERS}


def _nextop_reply_fields(messages):
    replies = [m for m in messages if _is_nextop_support_reply(m)]
    if not replies: return {}
    times = [int(m["time"]) for m in replies if m.get("time") not in (None, "")]
    result = {"Status": "Replied", "Total Replied": len(replies)}
    if times:
        result.update({"Replied Time-First": min(times), "Replied Time-NEW": max(times)})
    return result


def find_nextop_legacy_duplicates(analysis, limit=100):
    """Return only high-confidence legacy candidates; never auto-merge them."""
    records = feishu_api.get_records_for_matching(_CANDIDATE_FIELDS, limit=limit)
    new_device = _normalized_text(analysis.get("device_name"))
    new_errors = set(_as_list(analysis.get("error_code")))
    new_model = _normalized_text(analysis.get("model_type"))
    new_dealer = _normalized_text(analysis.get("disti_dealer"))
    new_symptoms = set(_as_list(analysis.get("fault_symptom")))
    matches = []
    for candidate in (candidate_from_record(record) for record in records):
        if not candidate.get("record_id"):
            continue
        device = bool(new_device and new_device == _normalized_text(candidate.get("device_name")))
        errors = bool(new_errors & set(_as_list(candidate.get("error_codes"))))
        model = bool(new_model and new_model == _normalized_text(candidate.get("model_type")))
        dealer = bool(new_dealer and new_dealer == _normalized_text(candidate.get("disti")))
        symptoms = bool(new_symptoms & set(_as_list(candidate.get("fault_symptom"))))
        corroborating = sum((errors, model, dealer, symptoms))
        # Device/SN needs corroboration; absent a device, require at least
        # three independent structured signals.  Text similarity alone is not
        # sufficient and is deliberately excluded from this safety gate.
        if (device and corroborating >= 1) or (not new_device and sum((errors, model, dealer, symptoms)) >= 3):
            candidate["duplicate_signals"] = {"device": device, "error": errors, "model": model, "dealer": dealer, "symptom": symptoms}
            matches.append(candidate)
    return sorted(matches, key=lambda item: (sum(item["duplicate_signals"].values()), item.get("replied_time_new") or 0), reverse=True)


def _refresh_case_counts(*secondary_tags, created_record_id=None, progress_callback=None):
    """Recount affected secondary-tag groups only after a successful ITR write."""
    reports, warnings = [], []
    for tag in {str(tag or "").strip() for tag in secondary_tags}:
        if tag:
            try:
                _progress(progress_callback, "refreshing_case_count", "Updating case count.")
                report = tag_engine.refresh_case_count(tag, expected_record_id=created_record_id)
                _progress(progress_callback, "verifying_case_count", "Checking case count.")
                reports.append(report or {})
                if report is not None and not report.get("success", False): warnings.append(tag)
            except Exception: warnings.append(tag)
    if warnings:
        _progress(progress_callback, "case_count_warning", "Case count refresh pending.", False)
    elif reports:
        _progress(progress_callback, "case_count_updated", "Case count updated.", True)
    return {"reports": reports, "warning": bool(warnings), "count": next((r.get("count") for r in reports if r.get("count") is not None), None)}


def _manual_reply_fields(manual_messages, support_reply_ids, new_support_reply_ids=None, existing_fields=None, imported_ms=None):
    support_ids = set(support_reply_ids or [])
    replies = [item for item in manual_messages if item["id"] in support_ids]
    if not replies: return {}
    result = {"Status": "Replied", "Total Replied": len(replies)}
    all_times = [item["timestamp_ms"] for item in replies if item.get("timestamp_ms")]
    new_ids = set(new_support_reply_ids or [])
    # The combined History is authoritative: NEW is never only this import's time.
    if all_times: result["Replied Time-NEW"] = max(all_times)
    elif new_ids and imported_ms is not None: result["Replied Time-NEW"] = imported_ms
    existing_first = feishu_api.normalize_field_value((existing_fields or {}).get("Replied Time-First"))
    if not existing_first and all_times: result["Replied Time-First"] = min(all_times)
    return result


def _manual_created_time(manual_messages, reply_fields, fallback_ms):
    """Case start time comes from the earliest reliable original message."""
    source_times = [item["timestamp_ms"] for item in manual_messages if item.get("timestamp_ms")]
    return min(source_times) if source_times else reply_fields.get("Replied Time-First") or fallback_ms


def _normalized_text(value): return re.sub(r"\s+", " ", str(value or "")).strip().casefold()
def _as_list(value): return value if isinstance(value, list) else []


def normalize_itr_todo(value):
    """Normalize the Checkbox representation before it reaches the GUI."""
    value = feishu_api.normalize_field_value(value)
    if isinstance(value, bool): return value
    if isinstance(value, (int, float)): return bool(value)
    if isinstance(value, str): return value.strip().casefold() in {"true", "1", "yes"}
    return False


def candidate_from_record(record):
    fields, value = record.get("fields", {}), feishu_api.normalize_field_value
    return {"record_id": record.get("record_id"), "ticket_no": value(fields.get("Ticket No.")), "reference_no": value(fields.get("Reference No.")), "disti": value(fields.get("Disti/Dealer/Service Point")), "device_name": value(fields.get("Device name")), "model_type": value(fields.get("Model Type")), "pie_comment": value(fields.get("PIE-Comment")), "description": value(fields.get("Description")), "solutions": value(fields.get("Solutions")), "fault_symptom": value(fields.get("Fault Symptom")), "error_codes": value(fields.get("Error Code")), "replied_time_first": value(fields.get("Replied Time-First")), "replied_time_new": value(fields.get("Replied Time-NEW")), "status": value(fields.get("Status")), "case_history": value(fields.get("Case History")), "first_level_tag": value(fields.get("一级标签")), "second_level_tag": value(fields.get("二级标签")), "ticket_created_time": value(fields.get("Ticket Created Time")), "case_count": value(fields.get("案例数")), "include_itr_todo": normalize_itr_todo(fields.get(ITR_TODO_FIELD))}


def score_candidate(new_analysis, candidate, now_ms):
    score, reasons = 0, []; new_device, old_device = _normalized_text(new_analysis.get("device_name")), _normalized_text(candidate.get("device_name")); device_match = bool(new_device and old_device and new_device == old_device)
    if device_match: score += 100; reasons.append("same device")
    overlap = set(_as_list(new_analysis.get("error_code"))) & set(_as_list(candidate.get("error_codes")))
    if overlap: score += 45 + 5 * (len(overlap) - 1); reasons.append("shared error code")
    if _normalized_text(new_analysis.get("disti_dealer")) and _normalized_text(new_analysis.get("disti_dealer")) == _normalized_text(candidate.get("disti")): score += 20; reasons.append("same dealer")
    new_model, old_model = _normalized_text(new_analysis.get("model_type")), _normalized_text(candidate.get("model_type"))
    if new_model and old_model:
        if new_model == old_model: score += 15; reasons.append("same model")
        else: score -= 30; reasons.append("model conflict")
    new_symptoms, old_symptoms = set(_as_list(new_analysis.get("fault_symptom"))), set(_as_list(candidate.get("fault_symptom")))
    if new_symptoms & old_symptoms: score += 10; reasons.append("shared symptom")
    elif new_symptoms and old_symptoms: score -= 5
    candidate_time = candidate.get("replied_time_new")
    if isinstance(candidate_time, (int, float)): score += max(0, int(_RECENT_CANDIDATE_DAYS - max(0, (now_ms - candidate_time) / 86_400_000)))
    new_text, old_text = _normalized_text(new_analysis.get("pie_comment") or new_analysis.get("description")), _normalized_text(candidate.get("pie_comment") or candidate.get("description"))
    if new_text and old_text: score += int(10 * SequenceMatcher(None, new_text[:500], old_text[:500]).ratio())
    return score, device_match or bool(overlap), reasons


def find_manual_candidates(source, new_analysis, now_ms, timings=None):
    started = perf_counter(); records = feishu_api.find_records_by_reference_no(source.upper(), _CANDIDATE_FIELDS); query_done = perf_counter(); cutoff = now_ms - _RECENT_CANDIDATE_DAYS * 86_400_000; ranked = []
    candidates = [candidate_from_record(record) for record in records]
    normalized_at = perf_counter()
    for candidate in candidates:
        if not candidate["record_id"]: continue
        score, strong, reasons = score_candidate(new_analysis, candidate, now_ms); candidate_time = candidate.get("replied_time_new"); recent = not isinstance(candidate_time, (int, float)) or candidate_time >= cutoff
        if (recent or strong) and score > 0: candidate.update(score=score, reasons=reasons); ranked.append(candidate)
    result = sorted(ranked, key=lambda item: (item["score"], item.get("replied_time_new") or 0), reverse=True)[:_CANDIDATE_LIMIT]
    if timings is not None:
        timings.update({"candidate_query": query_done - started, "candidate_normalization": normalized_at - query_done, "candidate_scoring_ranking": perf_counter() - normalized_at})
    return result


def append_manual_history(existing_history, new_block, raw_new_text):
    if _normalized_text(raw_new_text) and _normalized_text(raw_new_text) in _normalized_text(existing_history): return None
    return f"{str(existing_history or '').rstrip()}\n\n{new_block}".strip()


def build_notes_attachments(reference_no, messages, existing_record_id, progress_callback=None):
    new_images = images.collect_new_images(reference_no, messages)
    if not new_images: return None
    tokens, uploaded_hashes = [], []
    for image in new_images:
        try:
            token = feishu_api.upload_attachment(image["bytes"], image["name"]); tokens.append({"file_token": token}); images.save_token_hash(token, image["hash"]); uploaded_hashes.append(image["hash"])
        except Exception:
            _progress(progress_callback, "notes", "An image upload failed; other images continue.", False)
    images.mark_uploaded(reference_no, uploaded_hashes)
    if not tokens: return None
    existing_tokens = []
    if existing_record_id:
        record = feishu_api.get_record(existing_record_id); existing_tokens = [{"file_token": item["file_token"]} for item in record.get("fields", {}).get("Notes", []) if item.get("file_token")]
    return existing_tokens + tokens


def open_existing_case(identifier):
    """Read one ITR Case by exact Ticket No. or Reference No.; 0 AI, 0 write."""
    identifier = str(identifier or "").strip()
    finder = feishu_api.find_records_by_ticket_no_exact if identifier.upper().startswith("ITR-") else feishu_api.find_records_by_reference_exact
    records = finder(identifier, _CANDIDATE_FIELDS)
    matches = [candidate_from_record(record) for record in records]
    if not matches:
        return _result(False, "open_existing", "No exact ITR Case found.", match_status="NOT_FOUND", matches=[])
    if len(matches) != 1:
        return _result(False, "open_existing", "Multiple exact ITR Cases require selection.", match_status="MULTIPLE", matches=matches)
    return _result(True, "open_existing", "Existing Case loaded.", match_status="ONE", record_id=matches[0]["record_id"], case=matches[0], matches=matches)


def prepare_nextop_case(ticket_no, progress_callback=None, *, duplicate_decision=None, duplicate_record_id=None):
    """Fetch/analyze/review Nextop only.  This function never writes ITR."""
    ticket_no = str(ticket_no or "").strip()
    try:
        _progress(progress_callback, "matching", "Checking for an existing ITR Case.")
        existing = open_existing_case(ticket_no)
        if existing.get("match_status") == "MULTIPLE":
            return _result(False, "prepared_multiple", "Multiple exact ITR Cases require selection.", match_status="MULTIPLE", matches=existing["matches"])
        _progress(progress_callback, "nextop_fetch", "Fetching Nextop ticket.")
        ticket_data = nextop_api.get_ticket_full(ticket_no); messages = ticket_data["messages"]; history = build_nextop_case_history(messages)
        _progress(progress_callback, "analysis", "Analyzing Nextop Case for review.")
        analysis = analyzer.analyze_case_history(history); info = ticket_data["list_info"]
        dealer_context = (info.get("outerName"), info.get("outerAddress"), info.get("title")) + tuple(m.get("senderName") for m in messages if m.get("senderType") == 1)
        fields = build_v2_fields(history, analysis, dealer_context); fields.update({"Reference No.": ticket_no, "Ticket Created Time": info["createTime"]}); reply = _nextop_reply_fields(messages); _guard_select(reply, "Status"); fields.update(reply)
        existing_id = existing.get("record_id") if existing.get("match_status") == "ONE" else None
        existing_case = existing.get("case") if existing_id else None
        selected_match_kind = "exact" if existing_id else None
        if not existing_id:
            legacy_matches = find_nextop_legacy_duplicates(analysis)
            if legacy_matches and duplicate_decision not in {"update", "create"}:
                return _result(False, "possible_duplicate", "A possible existing Case requires confirmation.", ticket_no=ticket_no, possible_duplicate=True, duplicate_candidate=legacy_matches[0], error_type="possible_duplicate")
            if legacy_matches and duplicate_decision == "update":
                allowed_ids = {item.get("record_id") for item in legacy_matches}
                existing_id = duplicate_record_id if duplicate_record_id in allowed_ids else legacy_matches[0].get("record_id")
                existing_case = next((item for item in legacy_matches if item.get("record_id") == existing_id), None)
                selected_match_kind = "legacy"
        import context_service
        context_pack=context_service.build_context(ticket_no, fields, messages, history)
        prepared = PreparedNextopCase(ticket_no, history, analysis, fields, messages, info,
                                      existing_record_id=existing_id, existing_case=existing_case,
                                      match_status="ONE" if existing_id else "NOT_FOUND",
                                      matches=existing.get("matches", []), selected_match_kind=selected_match_kind,
                                      can_create=not bool(existing_id), can_update=bool(existing_id), context_pack=context_pack)
        _progress(progress_callback, "prepared", "Ready for review.", True)
        return _result(True, "prepared_existing" if existing_id else "prepared_new", "Nextop Case is ready for review.", prepared=prepared, case=existing_case or candidate_from_record({"record_id": None, "fields": fields}))
    except nextop_api.NextopAuthRequired as exc:
        missing = "not configured" in str(exc).lower()
        return _result(False, "prepare_nextop", "Nextop authentication is not configured." if missing else "Nextop authentication expired or invalid.", ticket_no=ticket_no, error_type="NEXTOP_CREDENTIALS_MISSING" if missing else "NEXTOP_AUTH_FAILED")
    except Exception as exc:
        return _exception_failure(exc, "prepare_nextop", "Nextop preparation failed.", ticket_no=ticket_no)


def _nextop_update_fields(fields, audit, include_itr_todo, todo_dirty):
    update_fields = {name: fields[name] for name in V2_MANAGED_FIELDS if fields[name] is not None}
    for name in ("Status", "Total Replied", "Replied Time-First", "Replied Time-NEW", "Notes"):
        if name in fields and fields[name] is not None:
            update_fields[name] = fields[name]
    update_fields = sanitize_update_fields(update_fields, audit)
    if todo_dirty:
        update_fields[ITR_TODO_FIELD] = bool(include_itr_todo)
    return update_fields


def _prepared_stale(ticket_no, record_id, kind):
    """Read-only target check immediately before a prepared write."""
    if kind != "exact":
        return None
    matches = feishu_api.find_records_by_reference_exact(ticket_no, _CANDIDATE_FIELDS)
    ids = {item.get("record_id") for item in matches if item.get("record_id")}
    if ids == {record_id}:
        return None
    return _result(False, "commit_prepared", "Prepared Case is stale; load it again before writing.",
                   ticket_no=ticket_no, record_id=record_id, error_type="prepared_stale")


def commit_prepared_nextop_case(prepared, progress_callback=None, *, include_itr_todo=False, todo_dirty=False):
    """Write an already prepared Nextop Case; never fetches or analyzes Nextop."""
    if not isinstance(prepared, PreparedNextopCase):
        return _result(False, "commit_prepared", "Invalid prepared Case.", error_type="invalid_prepared")
    if not prepared.fields or not prepared.case_history:
        return _result(False, "commit_prepared", "Prepared Case has no review data; load it again before writing.", ticket_no=prepared.ticket_no, error_type="invalid_prepared")
    guard = None
    try:
        fields = dict(prepared.fields)
        update_single_select_audit = {}
        existing_id = prepared.existing_record_id
        if existing_id:
            stale = _prepared_stale(prepared.ticket_no, existing_id, prepared.selected_match_kind)
            if stale:
                return stale
            guard = _record_write_guard(existing_id)
            if not guard.__enter__():
                return _result(False, "updated", "This case is being updated in another workspace.", record_id=existing_id, ticket_no=prepared.ticket_no, error_type="case_busy")
        else:
            _progress(progress_callback, "matching", "Final duplicate check before creation.")
            exact_matches = feishu_api.find_records_by_reference_exact(prepared.ticket_no, _CANDIDATE_FIELDS)
            if len(exact_matches) > 1:
                return _result(False, "commit_prepared", "Multiple exact ITR Cases require selection.", ticket_no=prepared.ticket_no, error_type="prepared_stale")
            if exact_matches:
                existing_id = exact_matches[0].get("record_id")
                guard = _record_write_guard(existing_id)
                if not guard.__enter__():
                    return _result(False, "updated", "This case is being updated in another workspace.", record_id=existing_id, ticket_no=prepared.ticket_no, error_type="case_busy")
        old_secondary_tag = None
        if existing_id:
            # Also makes an explicit legacy target fail safely if it vanished.
            latest = feishu_api.get_record(existing_id)
            old_secondary_tag = feishu_api.normalize_field_value((latest.get("fields") or {}).get("二级标签"))
        _progress(progress_callback, "notes", "Syncing Notes images.")
        notes = build_notes_attachments(prepared.ticket_no, prepared.messages, existing_id, progress_callback)
        if notes is not None:
            fields["Notes"] = notes
        if existing_id:
            update_fields = _nextop_update_fields(fields, update_single_select_audit, include_itr_todo, todo_dirty)
            update_single_select_audit = finalize_update_single_select_audit(update_single_select_audit, update_fields)
            _progress(progress_callback, "writing", "Updating existing ITR Case.")
            response, action, record_id = feishu_api.update_record(existing_id, update_fields), "updated", existing_id
        else:
            _progress(progress_callback, "writing", "Creating ITR Case.")
            fields[ITR_TODO_FIELD] = bool(include_itr_todo)
            response, action, record_id = feishu_api.create_record(sanitize_create_fields(fields)), "created", None
        if record_id is None:
            record_id = _response_record_id(response)
        success = response.get("code") == 0
        _progress(progress_callback, "complete", "Nextop sync completed." if success else "Nextop sync failed.", success)
        if not success:
            return _feishu_failure(response, action, "ITR synchronization failed.", record_id=record_id, ticket_no=prepared.ticket_no, single_select_audit=update_single_select_audit if action == "updated" else None)
        refresh = _refresh_case_counts(old_secondary_tag, fields.get("二级标签"), created_record_id=record_id if action == "created" else None, progress_callback=progress_callback)
        case = None
        if record_id:
            try:
                _progress(progress_callback, "readback", "Loading synchronized Case.")
                case = candidate_from_record(feishu_api.get_record(record_id))
            except Exception:
                refresh["warning"] = True
        return _result(True, action, "ITR record synchronized.", record_id=record_id, ticket_no=prepared.ticket_no, error_type=None, case=case, case_count=refresh.get("count"), case_count_refresh_warning=refresh["warning"], single_select_audit=update_single_select_audit if action == "updated" else None)
    except nextop_api.NextopAuthRequired:
        # A prepared commit does not call Nextop; retain a safe generic failure
        # in case an optional image helper reports this project exception.
        return _result(False, "commit_prepared", "Nextop authentication requires a PageOrder request.", ticket_no=prepared.ticket_no, error_type="nextop_auth_required")
    except Exception as exc:
        _progress(progress_callback, "failed", "Nextop sync failed.", False)
        return _exception_failure(exc, "commit_prepared", "Nextop synchronization failed.", ticket_no=prepared.ticket_no)
    finally:
        if guard is not None:
            guard.__exit__(*sys.exc_info())


def sync_nextop(ticket_no, progress_callback=None, *, include_itr_todo=False, todo_dirty=False, duplicate_decision=None, duplicate_record_id=None):
    prepared_result = prepare_nextop_case(ticket_no, progress_callback, duplicate_decision=duplicate_decision, duplicate_record_id=duplicate_record_id)
    if not prepared_result.get("success"):
        return prepared_result
    return commit_prepared_nextop_case(prepared_result["prepared"], progress_callback, include_itr_todo=include_itr_todo, todo_dirty=todo_dirty)


def refresh_nextop_session(pageorder_request, progress_callback=None):
    """GUI-safe, on-demand use of the existing browser-request fallback."""
    try:
        _progress(progress_callback, "nextop_authenticating", "Refreshing Nextop session.")
        nextop_api.refresh_session_from_pageorder_request(pageorder_request)
        _progress(progress_callback, "nextop_authenticated", "Nextop session refreshed.", True)
        return _result(True, "nextop_authenticated", "Nextop session refreshed.", error_type=None)
    except Exception:
        _progress(progress_callback, "nextop_auth_failed", "Nextop authentication failed.", False)
        return _result(False, "nextop_authenticated", "Nextop authentication refresh failed.", error_type="nextop_auth_failed")


def prepare_manual_submission(source, raw_text, progress_callback=None):
    source = str(source or "").lower().strip(); raw_text = str(raw_text or "").strip()
    if source not in _MANUAL_SOURCES: return _result(False, "prepare_manual", "Unsupported manual source.", error_type="invalid_source")
    if not raw_text: return _result(False, "prepare_manual", "No content entered.", source=source, error_type="empty_content")
    try:
        started = perf_counter(); now = datetime.now(timezone.utc); now_ms = int(now.timestamp() * 1000); new_block = build_imported_case_history(source, raw_text, now.strftime("%Y-%m-%d %H:%M UTC")); manual_messages = parse_manual_messages(raw_text)
        _progress(progress_callback, "analysis", "Analyzing imported content."); analysis_started = perf_counter(); analysis = analyzer.analyze_case_history(new_block, manual_messages=manual_messages); analysis_done = perf_counter()
        _progress(progress_callback, "classification", "Classifying case tags."); tags = tag_engine.classify(_tag_text(analysis))
        _progress(progress_callback, "candidates", "Finding possible related Cases."); timings = {"ai_analysis": analysis_done - analysis_started}; candidates = find_manual_candidates(source, analysis, now_ms, timings); timings["total_elapsed"] = perf_counter() - started; draft = ManualDraft(source, raw_text, new_block, analysis, now_ms, manual_messages, tags); _progress(progress_callback, "prepared", "Candidate review is ready.", True)
        return _result(True, "prepared", "Manual submission prepared.", source=source, draft=draft, candidates=candidates, timings=timings)
    except Exception as exc: return _result(False, "prepare_manual", "Manual submission preparation failed.", source=source, error_type=type(exc).__name__)


def create_manual_case(draft, progress_callback=None, *, include_itr_todo=False):
    try:
        _progress(progress_callback, "create", "Creating new manual Case."); single_select_audit = {}; fields = build_v2_fields(draft.new_block, draft.new_analysis, (draft.new_block,), single_select_audit, draft.tags); fields["Reference No."] = draft.source.upper(); fields[ITR_TODO_FIELD] = bool(include_itr_todo); reply_fields = _manual_reply_fields(draft.manual_messages, draft.new_analysis.get("support_reply_ids"), draft.new_analysis.get("support_reply_ids"), imported_ms=draft.imported_ms); _guard_select(reply_fields, "Status", single_select_audit); fields.update(reply_fields); fields["Ticket Created Time"] = _manual_created_time(draft.manual_messages, reply_fields, draft.imported_ms); payload = sanitize_create_fields(fields); single_select_audit = finalize_single_select_audit(single_select_audit, fields, payload); response = feishu_api.create_record(payload); success = response.get("code") == 0
        _progress(progress_callback, "complete", "Manual Case created." if success else "Manual Case creation failed.", success)
        if not success:
            return _feishu_failure(response, "created", "Manual Case creation failed.", source=draft.source, record_id=_response_record_id(response), single_select_audit=single_select_audit)
        record_id = _response_record_id(response); refresh = _refresh_case_counts(fields.get("二级标签"), created_record_id=record_id, progress_callback=progress_callback); created_case = None
        if record_id:
            _progress(progress_callback, "readback", "Loading created Case.")
            try: created_case = candidate_from_record(feishu_api.get_record(record_id))
            except Exception: refresh["warning"] = True
        return _result(True, "created", "Manual Case created.", source=draft.source, record_id=record_id, error_type=None, single_select_audit=single_select_audit, created_case=created_case, case_count=refresh.get("count"), case_count_refresh_warning=refresh["warning"], case_count_refresh=refresh)
    except Exception as exc: return _exception_failure(exc, "create_manual", "Manual Case creation failed.", source=getattr(draft, "source", None))


def update_manual_case(record_id, draft, progress_callback=None, *, include_itr_todo=None):
    guard = _record_write_guard(record_id)
    if not guard.__enter__():
        return _result(False, "updated", "This case is being updated in another workspace.", record_id=record_id, error_type="case_busy")
    try:
        _progress(progress_callback, "reload", "Reloading selected Case."); latest = feishu_api.get_record(record_id); latest_fields = latest.get("fields", {}); existing = feishu_api.normalize_field_value(latest_fields.get("Case History")) or ""; merged = append_manual_history(existing, draft.new_block, draft.raw_text)
        if merged is None: return _result(False, "duplicate_blocked", "This content may already be recorded; no update was made.", record_id=record_id, source=draft.source, duplicate_detected=True, error_type="duplicate")
        _progress(progress_callback, "analysis", "Analyzing complete Case History and classifying tags."); manual_messages = parse_manual_messages(merged); analysis = analyzer.analyze_case_history(merged, manual_messages=manual_messages); update_single_select_audit = {}; fields = build_v2_fields(merged, analysis, (merged,), update_single_select_audit); update_fields = {name: fields[name] for name in V2_MANAGED_FIELDS if fields[name] is not None}; old_secondary_tag = feishu_api.normalize_field_value(latest_fields.get("二级标签")); new_message_count = len(draft.manual_messages); new_message_ids = {item["id"] for item in manual_messages[-new_message_count:]} if new_message_count else set(); new_ids = new_message_ids & set(analysis.get("support_reply_ids", [])); reply_fields = _manual_reply_fields(manual_messages, analysis.get("support_reply_ids"), new_ids, latest_fields, imported_ms=draft.imported_ms); _guard_select(reply_fields, "Status", update_single_select_audit); update_fields.update({name: value for name, value in reply_fields.items() if value is not None}); update_fields = sanitize_update_fields(update_fields, update_single_select_audit)
        # This is a user-controlled Checkbox, intentionally outside V2 stale clearing.
        if include_itr_todo is not None:
            update_fields[ITR_TODO_FIELD] = bool(include_itr_todo)
        update_single_select_audit = finalize_update_single_select_audit(update_single_select_audit, update_fields); _progress(progress_callback, "writing", "Updating selected Case."); response = feishu_api.update_record(record_id, update_fields); success = response.get("code") == 0
        _progress(progress_callback, "complete", "Manual Case updated." if success else "Manual Case update failed.", success)
        if not success:
            return _feishu_failure(response, "updated", "Manual Case update failed.", record_id=record_id, source=draft.source, duplicate_detected=False, single_select_audit=update_single_select_audit)
        refresh = _refresh_case_counts(old_secondary_tag, fields.get("二级标签"), progress_callback=progress_callback)
        updated_case = None
        try: updated_case = candidate_from_record(feishu_api.get_record(record_id))
        except Exception: refresh["warning"] = True
        return _result(True, "updated", "Manual Case updated.", record_id=record_id, source=draft.source, duplicate_detected=False, error_type=None, updated_case=updated_case, case_count=refresh.get("count"), case_count_refresh_warning=refresh["warning"], case_count_refresh=refresh, single_select_audit=update_single_select_audit)
    except Exception as exc: return _exception_failure(exc, "update_manual", "Manual Case update failed.", record_id=record_id, source=getattr(draft, "source", None))
    finally:
        guard.__exit__(*sys.exc_info())

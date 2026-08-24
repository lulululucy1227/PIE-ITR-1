"""Reusable case orchestration for the NextopSync CLI and future GUI."""
import re
import threading
import sys
import hashlib
import json
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, replace
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
ITR_NFF_FIELD = "加入NFF"
ITR_ISSUE_OWNER_FIELD = "问题归属"
ITR_ISSUE_OWNER_OPTIONS = {"产品问题", "代理问题"}
NFF_EVIDENCE_LABELS = {
    "customer_issue": "Customer Original Issue",
    "functional_test": "Functional Test PDF report",
    "communication_check": "Communication Check PDF report",
    "automap_run": "AutoMap Run PDF report",
    "connect_checking": "Connect Checking screenshot",
    "latest_log": "latest log or confirmation that the uploaded log is the latest",
}


def nff_missing_evidence(evidence):
    """Return exact missing NFF evidence labels; never collapse to a count."""
    values = dict(evidence or {})
    return [label for key, label in NFF_EVIDENCE_LABELS.items() if not bool(values.get(key))]


def nff_reply_for_source(source, candidate, evidence):
    """Generate a missing-only, source-aware reply after evidence evaluation."""
    missing = nff_missing_evidence(evidence)
    if str(candidate or "").upper() == "NO":
        return "", missing
    if not missing:
        return "NFF evidence is complete. Manual NFF decision is required.", missing
    bullets = "\n".join(f"- {item}" for item in missing)
    if str(source or "").casefold() in {"whatsapp", "lark"}:
        return f"Please also provide:\n{bullets}", missing
    return f"Hello,\n\nPlease also provide:\n{bullets}\n\nBest regards,\nPIE Technical Support", missing
MULTI_SELECT_FIELDS = {"Fault Symptom", "Error Code"}
_ALLOWED_OPTIONS = {"Fault Symptom": set(fo.FAULT_SYMPTOM), "Error Code": set(fo.ERROR_CODE)}
_CANDIDATE_FIELDS = ["Ticket No.", "Reference No.", "Disti/Dealer/Service Point", "Device name", "Model Type", "PIE-Comment", "Description", "Solutions", "Fault Symptom", "Error Code", "Error massages", "Replied Time-First", "Replied Time-NEW", "Total Replied", "Status", "Ticket Created Time", "案例数", "Case History", "一级标签", "二级标签", ITR_TODO_FIELD, ITR_NFF_FIELD, ITR_ISSUE_OWNER_FIELD]
_PRESERVE_ON_EMPTY = {"Description", "Solutions", "PIE-Comment", "一级标签", "二级标签", "Error Code", "Error massages", "Model Type", "Case History", "Ticket Created Time", "Replied Time-First", "Replied Time-NEW", "Total Replied"}
_CANDIDATE_LIMIT = 5
_RECENT_CANDIDATE_DAYS = 14
_MANUAL_SOURCES = {"whatsapp", "lark", "email"}
_record_write_locks, _record_lock_guard = set(), threading.Lock()
_QUOTED_HISTORY_LINE = re.compile(r"^\s*(on .{0,100}wrote:|from:|sent:|to:|subject:|发件人[:：]|主题[:：]|>)", re.I)
_CLOSING_LINE = re.compile(r"^\s*(best regards|kind regards|thanks(?: and regards)?|thank you|sincerely|cheers|此致|敬礼|谢谢|祝好)\s*[,，.。!！]*\s*$", re.I)
_PARTNER_SIGNATURE = re.compile(r"^\s*=+\s*$|^\s*EMEA Partner Support", re.I)

# Governed, evidence-backed serial prefixes.  Do not infer a product from an
# unknown prefix: this registry is deliberately small and centrally maintained.
DEVICE_PREFIX_MODEL_MAP = {
    "LUBA-MB": "luba mini 2",
    "LUBA-VP": "luba 2x",
    "LUBA-VS": "luba 2",
    "YUKA-MVT": "yuka mini 2 800",
}

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


def reanalyze_prepared_nextop_case(prepared, human_guidance=""):
    """Rebuild one prepared Case from its stable snapshot and one new Inspector result.

    The returned PreparedNextopCase is the only payload accepted by Preview and
    Commit.  This prevents a guided re-analysis being displayed while an older
    field set is accidentally submitted.
    """
    if not isinstance(prepared, PreparedNextopCase):
        return _result(False, "reanalyze", "No prepared Nextop Case is available.", error_type="invalid_prepared")
    source = dict(prepared.analysis or {})
    source.update({
        "case_history": prepared.case_history,
        "description": prepared.fields.get("Description") or source.get("description") or "",
        "fault_symptom": prepared.fields.get("Fault Symptom") or source.get("fault_symptom") or [],
        "pie_comment": prepared.fields.get("PIE-Comment") or source.get("pie_comment") or "",
        "solutions": prepared.fields.get("Solutions") or source.get("solutions") or "",
        "model_type": prepared.fields.get("Model Type") or source.get("model_type") or "",
        "error_codes": prepared.fields.get("Error Code") or source.get("error_code") or [],
        "status": prepared.fields.get("Status") or source.get("status") or "",
        "context_pack": prepared.context_pack,
        "human_guidance": str(human_guidance or "").strip(),
    })
    analysis = analyzer.analyze_case_for_inspector(source)
    analysis_data = asdict(analysis)
    fields = dict(prepared.fields)
    # These are current Inspector-owned fields.  A blank current solution is
    # intentional and must replace an older disproven one.
    fields.update({
        "Case History": prepared.case_history,
        "Description": analysis_data["customer_description"],
        "PIE-Comment": analysis_data["ai_suggested_next_step"],
        "Solutions": analysis_data["solution"],
    })
    return _result(True, "reanalyze", "Case analysis is current.", prepared=replace(prepared, analysis=analysis_data, fields=fields), analysis=analysis)

def translate_inspector_analysis_to_zh(analysis):
    return analyzer.translate_inspector_analysis_to_zh(analysis)

def translate_text_to_zh(text):
    return analyzer.translate_text_to_zh(text)


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
class ManualIntakeDraft:
    """Source-neutral, uncreated manual intake.  It has no Feishu write path."""
    draft_key: str
    source: str
    raw_source_evidence: str = field(repr=False)
    normalized_analysis_input: str = field(repr=False)
    contact: str = ""
    partner_candidate: dict = field(default_factory=dict)
    partner_confirmed: str = ""
    country: str = ""
    device: str = ""
    model: str = ""
    serial_number: str = ""
    session_notes: str = ""
    attachment_metadata: list = field(default_factory=list)
    source_timestamp: str = ""
    case_history_append: str = field(repr=False, default="")
    analysis: dict = field(default_factory=dict, repr=False)
    tags: tuple = ("", "")
    device_evidence: dict = field(default_factory=dict)
    image_evidence: list = field(default_factory=list)
    reply_suppressed: bool = False


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
    ticket_version: str = ""
    fetched_at: str = ""
    message_fingerprint: str = ""
    latest_message_id: str = ""
    latest_message_timestamp: object = None
    latest_sender_role: str = "UNKNOWN"
    attachment_counts: dict = field(default_factory=dict)
    model_resolution: dict = field(default_factory=dict)
    partner_resolution: dict = field(default_factory=dict)


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
            current = {"id": len(messages) + 1, "timestamp_ms": timestamp_ms,
                       "sender": _sender.strip(), "content": content.strip()}
        elif current:
            current["content"] = (current["content"] + "\n" + line).strip()
    if current: messages.append(current)
    messages = [item for item in messages if item["content"]]
    return messages or ([{"id": 1, "timestamp_ms": None, "sender": "", "content": str(text or "").strip()}] if str(text or "").strip() else [])


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

def _normalize_device_prefix(value):
    """Normalize only formatting, never product semantics."""
    return re.sub(r"[-_\s]+", "-", str(value or "").strip()).upper()


def resolve_model(device_name, explicit_model=""):
    """Resolve a known serial prefix; unknown and conflicts stay reviewable."""
    normalized = _normalize_device_prefix(device_name)
    match = next(((prefix, model) for prefix, model in
                  sorted(DEVICE_PREFIX_MODEL_MAP.items(), key=lambda item: len(item[0]), reverse=True)
                  if normalized.startswith(prefix)), None)
    prefix, mapped = match if match else ("", "")
    explicit = str(explicit_model or "").strip()
    if explicit and mapped and _normalized_text(explicit) != _normalized_text(mapped):
        return {"status": "MODEL_CONFLICT", "model": explicit, "explicit_model": explicit,
                "prefix_model": mapped, "matched_prefix": prefix}
    if explicit:
        return {"status": "EXPLICIT", "model": explicit, "matched_prefix": prefix}
    if mapped:
        return {"status": "PREFIX_MATCH", "model": mapped, "matched_prefix": prefix}
    return {"status": "UNKNOWN", "model": "", "matched_prefix": ""}


def _model_from_device_name(device_name):
    return resolve_model(device_name).get("model", "")


_DEVICE_TOKEN = re.compile(r"\b(?:LUBA|YUKA)[-_][A-Z0-9-]{4,}\b", re.I)


def _device_tokens(value):
    return [_normalize_device_prefix(item) for item in _DEVICE_TOKEN.findall(str(value or ""))]


def _structured_device_tokens(value):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).casefold()
            if any(token in lowered for token in ("device", "serial", "machine", "product")):
                found.extend(_device_tokens(item))
            if isinstance(item, (dict, list, tuple)):
                found.extend(_structured_device_tokens(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_structured_device_tokens(item))
    return found


def extract_ticket_device(ticket_data):
    """Choose only a deterministic device token, preserving disagreements."""
    info = dict((ticket_data or {}).get("list_info") or {})
    basic = dict((ticket_data or {}).get("basic") or {})
    messages = list((ticket_data or {}).get("messages") or [])
    grouped = [
        ("structured", _structured_device_tokens(basic) + _structured_device_tokens(info)),
        ("title", _device_tokens(info.get("title") or info.get("subject"))),
        ("message", [token for message in messages for token in _device_tokens(message.get("content"))]),
    ]
    candidates = [(source, token) for source, tokens in grouped for token in tokens]
    unique = list(dict.fromkeys(token for _source, token in candidates))
    if len(unique) > 1:
        return {"status": "DEVICE_CONFLICT", "device_name": "", "candidates": unique}
    if unique:
        source = next(source for source, token in candidates if token == unique[0])
        return {"status": source.upper(), "device_name": unique[0], "candidates": unique}
    return {"status": "UNRESOLVED", "device_name": "", "candidates": []}


def format_time(value):
    if value in (None, ""): return ""
    try:
        numeric = int(value) / 1000 if int(value) > 10_000_000_000 else int(value)
        return datetime.fromtimestamp(numeric, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OSError, OverflowError): return ""


def build_nextop_case_history(messages):
    blocks, pie_names = [], {name.lower() for name in settings.PIE_SENDERS}
    seen = set()
    ordered = sorted(messages or [], key=lambda item: (item.get("time") or 0, str(item.get("id") or item.get("messageId") or "")))
    for message in ordered:
        identity = str(message.get("id") or message.get("messageId") or hashlib.sha256(json.dumps({key: message.get(key) for key in ("time", "senderType", "senderName", "content")}, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest())
        if identity in seen: continue
        seen.add(identity)
        content = _clean_nextop_message_content(message.get("content"))
        if not content: continue
        header, sender = [], str(message.get("senderName") or "").strip()
        if format_time(message.get("time")): header.append(format_time(message.get("time")))
        if message.get("senderType") == 2 and sender and sender.lower() in pie_names: header.append(f"PIE - {sender}")
        elif message.get("senderType") == 1 and sender: header.append(f"Agent - {sender}")
        elif sender: header.append(sender)
        blocks.append(("[" + "] [".join(header) + "]\n" if header else "") + content)
    return "\n\n".join(blocks)

def _clean_nextop_message_content(content):
    """Keep current technical evidence while removing quoted mail chains and repeated signatures."""
    lines = str(content or "").replace("\r\n", "\n").splitlines()
    kept = []
    for line in lines:
        if _QUOTED_HISTORY_LINE.match(line) or _PARTNER_SIGNATURE.match(line): break
        kept.append(line.rstrip())
        if _CLOSING_LINE.match(line): break
    text = "\n".join(kept).strip()
    return re.sub(r"\n{3,}", "\n\n", text)

def _message_fingerprint(messages):
    """Stable, local-only freshness token.  It never contains ticket content."""
    payload = [{key: item.get(key) for key in ("id", "time", "senderType", "senderRole", "authorType", "direction", "senderName", "content", "subject")}
               for item in (messages or [])]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:16]

def _ticket_version(messages, list_info=None):
    metadata = {key: (list_info or {}).get(key) for key in ("id", "repairOrderNo", "title", "outerName", "outerAddress", "createTime", "status", "updateTime")}
    return hashlib.sha256(json.dumps({"messages": _message_fingerprint(messages), "metadata": metadata}, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:16]

def _message_role(message):
    if _is_nextop_support_reply(message): return "PIE"
    role_data = " ".join(str(message.get(key) or "") for key in ("senderRole", "authorType", "direction")).casefold()
    if str(message.get("senderType") or "") == "1" or any(token in role_data for token in ("customer", "dealer", "inbound", "agent")):
        return "AGENT"
    return "UNKNOWN"

def _latest_message_info(messages):
    latest = (messages or [])[-1] if messages else {}
    return {"latest_message_id": str(latest.get("id") or latest.get("messageId") or ""), "latest_message_timestamp": latest.get("time"), "latest_sender_role": _message_role(latest)}

def _refresh_failure(ticket_no, exc):
    if isinstance(exc, nextop_api.NextopAuthRequired):
        missing = "not configured" in str(exc).lower()
        return _result(False, "refresh_nextop", "Nextop authentication is not configured." if missing else "Nextop authentication expired or invalid.", ticket_no=ticket_no, error_type="NEXTOP_CREDENTIALS_MISSING" if missing else "NEXTOP_AUTH_FAILED", stage="nextop_fetch")
    return _result(False, "refresh_nextop", "Latest Nextop state could not be verified.", ticket_no=ticket_no, error_type="NEXTOP_REFRESH_ERROR", stage="nextop_fetch")

def refresh_latest_nextop_case(prepared):
    """Read latest Nextop state and return a safe delta; never writes Feishu or Nextop."""
    if not isinstance(prepared, PreparedNextopCase):
        return _result(False, "refresh_nextop", "No prepared Nextop Case is available.", error_type="invalid_prepared")
    try:
        ticket = nextop_api.get_ticket_full(prepared.ticket_no)
        messages, info = ticket["messages"], ticket["list_info"]
        version = _ticket_version(messages, info)
        message_fingerprint = _message_fingerprint(messages)
        latest = _latest_message_info(messages)
    except Exception as exc:
        return _refresh_failure(prepared.ticket_no, exc)
    if version == prepared.ticket_version:
        return _result(True, "refresh_nextop", "Refresh complete.", ticket_no=prepared.ticket_no, change_type="NO_CHANGE", prepared=prepared, ticket_version=version, message_fingerprint=message_fingerprint, **latest)
    if message_fingerprint == (prepared.message_fingerprint or _message_fingerprint(prepared.messages)):
        history = build_nextop_case_history(messages)
        fields = build_v2_fields(history, prepared.analysis, (info.get("outerName"), info.get("outerAddress"), info.get("title")))
        reply = _nextop_reply_fields(messages); _guard_select(reply, "Status"); fields.update(_preserve_reply_count(reply, prepared.fields.get("Total Replied")))
        import context_service
        refreshed = PreparedNextopCase(prepared.ticket_no, history, prepared.analysis, fields, messages, info,
            prepared.existing_record_id, prepared.existing_case, prepared.match_status, prepared.matches,
            prepared.selected_match_kind, prepared.can_create, prepared.can_update,
            context_service.build_context(prepared.ticket_no, fields, messages, history), version,
            datetime.now(timezone.utc).isoformat(), message_fingerprint=message_fingerprint, attachment_counts=dict(ticket.get("attachment_counts") or {}), model_resolution=dict(fields.get("_model_resolution") or {}), partner_resolution=dict(fields.get("_partner_resolution") or {}), **latest)
        return _result(True, "refresh_nextop", "Ticket metadata synced.", ticket_no=prepared.ticket_no, change_type="METADATA_CHANGED", prepared=refreshed, ticket_version=version, message_fingerprint=message_fingerprint, **latest)
    if latest["latest_sender_role"] == "PIE":
        history = build_nextop_case_history(messages)
        fields = build_v2_fields(history, prepared.analysis, (info.get("outerName"), info.get("outerAddress"), info.get("title")))
        reply = _nextop_reply_fields(messages); _guard_select(reply, "Status"); fields.update(_preserve_reply_count(reply, prepared.fields.get("Total Replied")))
        import context_service
        refreshed = PreparedNextopCase(prepared.ticket_no, history, prepared.analysis, fields, messages, info,
            prepared.existing_record_id, prepared.existing_case, prepared.match_status, prepared.matches,
            prepared.selected_match_kind, prepared.can_create, prepared.can_update,
            context_service.build_context(prepared.ticket_no, fields, messages, history), version,
            datetime.now(timezone.utc).isoformat(), message_fingerprint=message_fingerprint, attachment_counts=dict(ticket.get("attachment_counts") or {}), model_resolution=dict(fields.get("_model_resolution") or {}), partner_resolution=dict(fields.get("_partner_resolution") or {}), **latest)
        return _result(True, "refresh_nextop", "Latest PIE reply synced. Waiting for agent reply.", ticket_no=prepared.ticket_no, change_type="NEW_PIE_MESSAGE", prepared=refreshed, ticket_version=version, message_fingerprint=message_fingerprint, **latest)
    refreshed = prepare_nextop_case(prepared.ticket_no, ticket_data=ticket)
    if not refreshed.get("success"):
        return refreshed
    change = "NEW_AGENT_MESSAGE" if latest["latest_sender_role"] == "AGENT" else "NEW_UNKNOWN_MESSAGE"
    message = "New agent message received — analysis refreshed." if change == "NEW_AGENT_MESSAGE" else "New message sender is unknown — review and analysis refreshed."
    return _result(True, "refresh_nextop", message, ticket_no=prepared.ticket_no, change_type=change, prepared=refreshed["prepared"], ticket_version=refreshed["prepared"].ticket_version, requires_reanalyze=True, **_latest_message_info(refreshed["prepared"].messages))


def build_imported_case_history(source, text, imported_at=None):
    timestamp = imported_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"[Imported: {timestamp}] [{source}]\n{text.strip()}" if text.strip() else ""


def _apply_tags(fields, analysis, tags=None):
    l1, l2 = tags if tags is not None else tag_engine.classify(_tag_text(analysis))
    fields["一级标签"], fields["二级标签"] = l1 or "", l2 or ""
    fields["_classification"] = {
        "status": "RESOLVED" if l1 and l2 else "UNRESOLVED",
        "reason": "No legal exact ITR tag mapping was returned." if not (l1 and l2) else "",
    }


def build_v2_fields(case_history, analysis, dealer_context=(), single_select_audit=None, tags=None):
    fields = {"Case History": case_history}
    for key, name in FIELD_MAP.items():
        if key != "case_history": fields[name] = _wrap_field(name, analysis.get(key, ""))
    resolution = resolve_model(fields.get("Device name"), fields.get("Model Type"))
    if not fields.get("Model Type"):
        fields["Model Type"] = resolution["model"]
    # Transient evidence for the local review/analyzer only; it is not a
    # Feishu-managed field and is removed before any write boundary.
    fields["_model_resolution"] = resolution
    _apply_dealer_alias(fields, *dealer_context); _guard_dealer(fields, single_select_audit); _guard_select(fields, "Model Type", single_select_audit)
    fields["_partner_resolution"] = {"status": "RESOLVED" if fields.get("Disti/Dealer/Service Point") else "UNRESOLVED", "partner": fields.get("Disti/Dealer/Service Point") or ""}
    _apply_tags(fields, analysis, tags); _guard_select(fields, "一级标签", single_select_audit); _guard_select(fields, "二级标签", single_select_audit)
    _guard_device_name(fields)
    for name in V2_MANAGED_FIELDS: fields.setdefault(name, [] if name in MULTI_SELECT_FIELDS else "")
    return fields


def sanitize_create_fields(fields):
    """Create records omit no-value fields; updates retain explicit clearing values."""
    return {
        name: value for name, value in fields.items()
        if not str(name).startswith("_")
        and value is not None
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


def _preserve_reply_count(fields, floor):
    """Never lower a known ITR reply total when a Nextop snapshot is partial."""
    try:
        known = int(str(floor or "").strip())
    except (TypeError, ValueError):
        return fields
    current = int(fields.get("Total Replied") or 0)
    if known > current:
        fields["Total Replied"] = known
    return fields


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
    return {"record_id": record.get("record_id"), "ticket_no": value(fields.get("Ticket No.")), "reference_no": value(fields.get("Reference No.")), "disti": value(fields.get("Disti/Dealer/Service Point")), "device_name": value(fields.get("Device name")), "model_type": value(fields.get("Model Type")), "pie_comment": value(fields.get("PIE-Comment")), "description": value(fields.get("Description")), "solutions": value(fields.get("Solutions")), "fault_symptom": value(fields.get("Fault Symptom")), "error_codes": value(fields.get("Error Code")), "replied_time_first": value(fields.get("Replied Time-First")), "replied_time_new": value(fields.get("Replied Time-NEW")), "total_replied": value(fields.get("Total Replied")), "status": value(fields.get("Status")), "case_history": value(fields.get("Case History")), "first_level_tag": value(fields.get("一级标签")), "second_level_tag": value(fields.get("二级标签")), "ticket_created_time": value(fields.get("Ticket Created Time")), "case_count": value(fields.get("案例数")), "nff": normalize_itr_todo(fields.get(ITR_NFF_FIELD)), "issue_owner": value(fields.get(ITR_ISSUE_OWNER_FIELD)), "include_itr_todo": normalize_itr_todo(fields.get(ITR_TODO_FIELD))}


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


def prepare_nextop_case(ticket_no, progress_callback=None, *, duplicate_decision=None, duplicate_record_id=None, ticket_data=None):
    """Fetch/analyze/review Nextop only.  This function never writes ITR."""
    ticket_no = str(ticket_no or "").strip()
    stage = "duplicate_lookup"
    try:
        _progress(progress_callback, "matching", "Checking for an existing ITR Case.")
        existing = open_existing_case(ticket_no)
        if existing.get("match_status") == "MULTIPLE":
            return _result(False, "prepared_multiple", "Multiple exact ITR Cases require selection.", match_status="MULTIPLE", matches=existing["matches"])
        stage = "nextop_fetch"; _progress(progress_callback, "nextop_fetch", "Fetching Nextop ticket.")
        ticket_data = ticket_data or nextop_api.get_ticket_full(ticket_no); messages = ticket_data["messages"]; history = build_nextop_case_history(messages)
        stage = "analyze"; _progress(progress_callback, "analysis", "Analyzing Nextop Case for review.")
        analysis = analyzer.analyze_case_history(history); info = ticket_data["list_info"]
        device_resolution = extract_ticket_device(ticket_data)
        if not analysis.get("device_name") and device_resolution["status"] not in {"DEVICE_CONFLICT", "UNRESOLVED"}:
            analysis["device_name"] = device_resolution["device_name"]
        stage = "prepare_fields"; dealer_context = (info.get("outerName"), info.get("outerAddress"), info.get("title")) + tuple(m.get("senderName") for m in messages if m.get("senderType") == 1)
        fields = build_v2_fields(history, analysis, dealer_context); fields["_device_resolution"] = device_resolution; fields.update({"Reference No.": ticket_no, "Ticket Created Time": info["createTime"]}); reply = _nextop_reply_fields(messages); _guard_select(reply, "Status"); fields.update(reply)
        existing_id = existing.get("record_id") if existing.get("match_status") == "ONE" else None
        existing_case = existing.get("case") if existing_id else None
        _preserve_reply_count(fields, (existing_case or {}).get("total_replied"))
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
        stage = "context_build"; import context_service
        context_pack=context_service.build_context(ticket_no, fields, messages, history)
        prepared = PreparedNextopCase(ticket_no, history, analysis, fields, messages, info,
                                      existing_record_id=existing_id, existing_case=existing_case,
                                      match_status="ONE" if existing_id else "NOT_FOUND",
                                      matches=existing.get("matches", []), selected_match_kind=selected_match_kind,
                                        can_create=not bool(existing_id), can_update=bool(existing_id), context_pack=context_pack,
                                        ticket_version=_ticket_version(messages, info), fetched_at=datetime.now(timezone.utc).isoformat(),
                                        message_fingerprint=_message_fingerprint(messages), attachment_counts=dict(ticket_data.get("attachment_counts") or {}), model_resolution=dict(fields.get("_model_resolution") or {}), partner_resolution=dict(fields.get("_partner_resolution") or {}), **_latest_message_info(messages))
        _progress(progress_callback, "prepared", "Ready for review.", True)
        return _result(True, "prepared_existing" if existing_id else "prepared_new", "Nextop Case is ready for review.", prepared=prepared, case=existing_case or candidate_from_record({"record_id": None, "fields": fields}))
    except nextop_api.NextopAuthRequired as exc:
        missing = "not configured" in str(exc).lower()
        return _result(False, "prepare_nextop", "Nextop authentication is not configured." if missing else "Nextop authentication expired or invalid.", ticket_no=ticket_no, error_type="NEXTOP_CREDENTIALS_MISSING" if missing else "NEXTOP_AUTH_FAILED", stage="nextop_fetch")
    except feishu_api.FeishuAuthRequired as exc:
        cause = str(exc).lower()
        if "refresh token" in cause:
            message = "Feishu refresh authorization is missing. Refresh the Feishu user authorization in the local configuration."
        elif "expired" in cause or "invalid" in cause:
            message = "Feishu user authorization has expired or is invalid. Refresh the local Feishu authorization."
        elif "app or table" in cause:
            message = "Feishu ITR app or table configuration is missing."
        elif "app credentials" in cause:
            message = "Feishu app credentials are missing."
        else:
            message = "Feishu read credentials or table configuration is missing."
        return _result(False, "prepare_nextop", message, ticket_no=ticket_no, error_type="FEISHU_CREDENTIALS_MISSING", stage=stage)
    except feishu_api.FeishuReadError as exc:
        detail = f"Feishu code: {exc.code}" if exc.code not in (None, "") else None
        return _result(False, "prepare_nextop", f"Feishu duplicate lookup failed: {exc.message}", ticket_no=ticket_no, error_type="FEISHU_LOOKUP_ERROR", stage=stage, detail=detail)
    except Exception as exc:
        if isinstance(exc, nextop_api.NextopLookupEmpty):
            return _result(False, "prepare_nextop", "Ticket lookup returned no exact result; verify Nextop scope or ticket number.", ticket_no=ticket_no, error_type="NEXTOP_LOOKUP_EMPTY", stage="ticket_search")
        if isinstance(exc, nextop_api.NextopParseError):
            return _result(False, "prepare_nextop", "Nextop returned an unexpected ticket response.", ticket_no=ticket_no, error_type="NEXTOP_PARSE_ERROR", stage="nextop_fetch")
        if isinstance(exc, nextop_api.NextopResponseError):
            return _result(False, "prepare_nextop", "Nextop ticket lookup could not be confirmed.", ticket_no=ticket_no, error_type="NEXTOP_RESPONSE_ERROR", stage="nextop_fetch")
        codes={"duplicate_lookup":"FEISHU_LOOKUP_ERROR","context_build":"CONTEXT_BUILD_ERROR","analyze":"ANALYZE_ERROR","prepare_fields":"PREPARATION_ERROR","nextop_fetch":"NEXTOP_REQUEST_ERROR"}
        messages={"duplicate_lookup":"Preparation failed at Feishu duplicate lookup.","context_build":"Preparation failed while building context.","analyze":"Ticket loaded, but analysis failed.","prepare_fields":"Preparation failed while preparing ticket fields.","nextop_fetch":"Nextop ticket request failed."}
        return _result(False, "prepare_nextop", messages.get(stage,"Preparation failed."), ticket_no=ticket_no, error_type=codes.get(stage,"PREPARATION_ERROR"), stage=stage)


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


def _issue_owner_for_submit(value, dirty):
    """Validate an explicit human ownership choice; untouched values preserve ITR."""
    if not dirty:
        return None
    value = str(value or "").strip()
    if not value:
        return None
    try:
        options = set(feishu_api.get_select_field_options(ITR_ISSUE_OWNER_FIELD))
    except Exception:
        return False
    return value if value in options else False


def _has_payload_value(value):
    return value not in (None, "", [], {}, "—", "undefined")


def _non_destructive_update_fields(update_fields):
    """VALID NEW VALUE > EXISTING VALUE > EMPTY: omit empty overwrite attempts."""
    return {name: value for name, value in update_fields.items() if name not in _PRESERVE_ON_EMPTY or _has_payload_value(value)}


def prepare_commit_preview(prepared):
    """Return the exact effective fields a later Commit would submit; read-only."""
    freshness = refresh_latest_nextop_case(prepared)
    if not freshness.get("success") or freshness.get("change_type") != "NO_CHANGE":
        return _result(False, "preview", "ITR Preview is blocked until the latest Nextop state is current.", error_type="NEXTOP_TICKET_STALE", prepared=freshness.get("prepared"))
    current = freshness["prepared"]
    fields = dict(current.fields)
    if current.existing_record_id:
        existing = feishu_api.get_record(current.existing_record_id).get("fields") or {}
        for name in _PRESERVE_ON_EMPTY:
            if not _has_payload_value(fields.get(name)) and _has_payload_value(existing.get(name)):
                fields[name] = existing[name]
    return _result(True, "preview", "ITR Preview is current.", prepared=replace(current, fields=fields))


def commit_prepared_nextop_case(prepared, progress_callback=None, *, include_itr_todo=False, todo_dirty=False, nff_value=False, nff_dirty=False, issue_owner_value=None, issue_owner_dirty=False):
    """Write an already prepared Nextop Case; never fetches or analyzes Nextop."""
    if not isinstance(prepared, PreparedNextopCase):
        return _result(False, "commit_prepared", "Invalid prepared Case.", error_type="invalid_prepared")
    if not prepared.fields or not prepared.case_history:
        return _result(False, "commit_prepared", "Prepared Case has no review data; load it again before writing.", ticket_no=prepared.ticket_no, error_type="invalid_prepared")
    freshness = refresh_latest_nextop_case(prepared)
    if not freshness.get("success"):
        return _result(False, "commit_prepared", "Latest Nextop state could not be verified; ITR Commit is blocked.", ticket_no=prepared.ticket_no, error_type=freshness.get("error_type") or "NEXTOP_REFRESH_ERROR", stage=freshness.get("stage"))
    if freshness.get("change_type") != "NO_CHANGE":
        return _result(False, "commit_prepared", "Ticket has changed since ITR preparation. Please review the latest messages.", ticket_no=prepared.ticket_no, error_type="NEXTOP_TICKET_STALE", latest_change=freshness.get("change_type"), prepared=freshness.get("prepared"))
    selected_owner = _issue_owner_for_submit(issue_owner_value, issue_owner_dirty)
    if selected_owner is False:
        return _result(False, "commit_prepared", "Issue ownership could not be validated against the current ITR schema.", ticket_no=prepared.ticket_no, error_type="issue_owner_invalid")
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
            update_fields = _non_destructive_update_fields(update_fields)
            if nff_dirty:
                update_fields[ITR_NFF_FIELD] = bool(nff_value)
            if selected_owner:
                update_fields[ITR_ISSUE_OWNER_FIELD] = selected_owner
            update_single_select_audit = finalize_update_single_select_audit(update_single_select_audit, update_fields)
            _progress(progress_callback, "writing", "Updating existing ITR Case.")
            response, action, record_id = feishu_api.update_record(existing_id, update_fields), "updated", existing_id
        else:
            _progress(progress_callback, "writing", "Creating ITR Case.")
            fields[ITR_TODO_FIELD] = bool(include_itr_todo)
            fields[ITR_NFF_FIELD] = bool(nff_value)
            if selected_owner:
                fields[ITR_ISSUE_OWNER_FIELD] = selected_owner
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


def _manual_source_timestamp(messages):
    values = [item.get("timestamp_ms") for item in messages if item.get("timestamp_ms")]
    if not values:
        return ""
    return datetime.fromtimestamp(min(values) / 1000, timezone.utc).isoformat()


def build_manual_source_block(source, raw_source_evidence, *, contact="", source_timestamp=""):
    """Preserve original evidence; processing time is intentionally not recorded as source time."""
    lines = [f"[Source: {str(source or '').strip()}]"]
    if source_timestamp:
        lines.append(f"[Source timestamp: {source_timestamp}]")
    if str(contact or "").strip():
        lines.append(f"[Contact: {str(contact).strip()}]")
    return "\n".join(lines + [str(raw_source_evidence or "").strip()]).strip()


_MODEL_FAMILY_TOKEN = re.compile(r"^(?:luba|yuka)(?:mini)?[\s_-]*\d+(?:[\s_-]*x)?$", re.I)
_SERIAL_LABEL = re.compile(r"\b(?:serial(?:\s+number)?|s/?n)\s*[:#-]?\s*([A-Z0-9][A-Z0-9_-]{4,})\b", re.I)
_ERROR_CODE_TOKEN = re.compile(r"\b(?:E|ERR(?:OR)?[- ]?)[A-Z0-9]{2,}\b", re.I)


def is_valid_manual_serial(value):
    """Reject model names (notably LUBA 2 X) before they reach a draft."""
    text = str(value or "").strip()
    compact = re.sub(r"[\s_-]+", "", text).casefold()
    if not text or _MODEL_FAMILY_TOKEN.fullmatch(text) or compact in {"luba2x", "luba3", "luba2", "lubamini2", "yukamini2"}:
        return False
    return bool(re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{4,}", text, re.I))


def _manual_evidence(raw_text, supplied_device="", supplied_model="", supplied_serial="", image_evidence=None):
    raw_devices = list(dict.fromkeys(_device_tokens(raw_text)))
    images = [item for item in (image_evidence or []) if isinstance(item, dict)]
    image_devices = list(dict.fromkeys(_normalize_device_prefix(value)
                                       for item in images for value in (item.get("device_candidates") or [])
                                       if _device_tokens(value)))
    image_models = list(dict.fromkeys(str(value).strip() for item in images for value in (item.get("model_candidates") or []) if str(value).strip()))
    explicit_device = _normalize_device_prefix(supplied_device) if _device_tokens(supplied_device) else ""
    candidates = list(dict.fromkeys(([explicit_device] if explicit_device else []) + raw_devices + image_devices))
    source = "MANUAL_CONFIRMED" if explicit_device else ("RAW_EXPLICIT" if len(raw_devices) == 1 else ("IMAGE_CANDIDATE" if len(image_devices) == 1 else ""))
    # A single model-approved image candidate is useful case evidence. It is
    # still marked for human confirmation before any ITR write.
    chosen = explicit_device or (raw_devices[0] if len(raw_devices) == 1 else (image_devices[0] if len(image_devices) == 1 else ""))
    serials = list(dict.fromkeys(_SERIAL_LABEL.findall(str(raw_text or ""))))
    serials += [str(value).strip() for item in images for value in (item.get("serial_candidates") or [])]
    serials = [item for item in serials if is_valid_manual_serial(item)]
    requested_serial = str(supplied_serial or "").strip()
    serial = requested_serial if is_valid_manual_serial(requested_serial) else (serials[0] if len(set(serials)) == 1 else "")
    resolution = resolve_model(chosen, supplied_model)
    known_model = resolution.get("model") or ""
    model_conflict = bool(known_model and image_models and any(_normalized_text(item) != _normalized_text(known_model) for item in image_models))
    image_errors = list(dict.fromkeys(str(value).strip() for item in images for value in (item.get("error_codes") or []) if str(value).strip()))
    image_messages = list(dict.fromkeys(str(value).strip() for item in images for value in (item.get("error_messages") or []) if str(value).strip()))
    technical_facts = [fact for item in images for fact in (item.get("technical_facts") or []) if isinstance(fact, dict) and str(fact.get("label") or "").strip() and str(fact.get("value") or "").strip()]
    return {
        "device_name": chosen, "device_candidates": candidates,
        "device_status": source or ("MULTIPLE_CANDIDATES" if len(candidates) > 1 else "UNRESOLVED"),
        "image_confirmation_required": bool((image_devices or image_models or image_errors or image_messages) and not (explicit_device or supplied_model or requested_serial)),
        "model_resolution": resolution, "model_candidates": list(dict.fromkeys(([known_model] if known_model else []) + image_models)), "model_conflict": model_conflict,
        "serial_number": serial,
        "serial_status": "VALID" if serial else ("REJECTED_MODEL_FAMILY" if requested_serial else "UNRESOLVED"),
        "error_code_candidates": list(dict.fromkeys(_ERROR_CODE_TOKEN.findall(str(raw_text or "")) + image_errors)),
        "error_message_candidates": image_messages,
        "technical_facts": technical_facts,
    }


def _manual_support_reply_ids(messages):
    """Return only evidence-backed manual support messages."""
    aliases = {str(name).casefold() for name in settings.PIE_SENDERS}
    ids = []
    for item in messages or []:
        sender = str(item.get("sender") or "").strip().casefold()
        tokens = set(re.findall(r"[a-z0-9]+", sender))
        if sender and (bool(tokens & aliases) or any(token in sender for token in ("pie", "support", "mammotion"))):
            ids.append(item["id"])
    return ids


def _manual_reply_statistics(messages):
    """Derive workload metrics from imported source evidence only."""
    support_ids = _manual_support_reply_ids(messages)
    replies = [item for item in messages or [] if item.get("id") in set(support_ids)]
    timestamps = [item.get("timestamp_ms") for item in replies if item.get("timestamp_ms")]
    if not replies or len(timestamps) != len(replies):
        return {"status": "NEEDS_CONFIRMATION", "support_reply_ids": support_ids,
                "message": "Reply statistics need confirmation", "fields": {}}
    return {"status": "DERIVED", "support_reply_ids": support_ids,
            "fields": {"Total Replied": len(replies), "Replied Time-First": min(timestamps), "Replied Time-NEW": max(timestamps)}}


def _actionable_manual_guidance(value):
    """Keep a case summary out of PIE Guidance."""
    text = str(value or "").strip()
    action = re.compile(r"\b(?:ask|request|confirm|verify|check|collect|provide|test|replace|restart|update|inspect)\b|请|确认|检查|收集|提供|测试|更换|重启|更新|核实", re.I)
    return text if text and action.search(text) else ""


def _validated_repair_actions(actions, raw_text):
    """Reject recommendations, questions, and negated repair history."""
    source = str(raw_text or "").casefold()
    accepted = []
    for value in actions or []:
        action = str(value or "").strip()
        low = action.casefold()
        if not action or action.endswith("?") or re.match(r"(?:please|ask|request|recommend|建议|请)\b", low):
            continue
        if any(token in low for token in ("replaced", "changed", "更换", "替换")):
            if re.search(r"(?:not|never|未|没有|没有被|尚未)\s+(?:been\s+)?(?:replaced|changed|更换|替换)", source):
                continue
        accepted.append(action)
    return list(dict.fromkeys(accepted))


def _manual_reply(analysis, source, messages):
    support_ids = set(analysis.get("support_reply_ids") or [])
    if messages and messages[-1].get("id") in support_ids:
        return "", True
    issue = str(analysis.get("description") or "").strip()
    if not issue:
        return "", False
    if str(source).casefold() in {"whatsapp", "lark"}:
        return "Thank you for the update. We have recorded the information provided and will continue the review.", False
    return "Hello,\n\nThank you for the update. We have recorded the information provided and will continue the review.\n\nBest regards,\nPIE Technical Support", False


def prepare_manual_intake(payload):
    """Prepare/analyze a manual source without any Feishu create or update."""
    from intake import normalize_case
    import partner_resolver
    payload = dict(payload or {})
    source = str(payload.get("source") or "").strip().casefold()
    raw = str(payload.get("raw_source_evidence") or "").strip()
    if source not in _MANUAL_SOURCES:
        return _result(False, "prepare_manual_intake", "Unsupported manual source.", error_type="invalid_source")
    if not raw:
        return _result(False, "prepare_manual_intake", "Paste the original conversation before analyzing.", error_type="empty_content")
    try:
        normalized = normalize_case(source, raw, str(payload.get("source_reference") or ""))
        manual_messages = parse_manual_messages(raw)
        source_timestamp = _manual_source_timestamp(manual_messages)
        contact = str(payload.get("contact") or "").strip()
        partner_confirmed = str(payload.get("partner_confirmed") or "").strip()
        try:
            partner_candidate = partner_resolver.resolve_partner(partner_resolver.load_partner_records_readonly(), explicit_partner=partner_confirmed, contact=contact)
        except Exception:
            partner_candidate = {"status": "UNKNOWN", "partner": "", "code": "", "country": "", "reason": "partner_source_unavailable", "candidates": []}
        case_history = build_manual_source_block(source, raw, contact=contact, source_timestamp=source_timestamp)
        analysis = analyzer.analyze_case_history(case_history, manual_messages=manual_messages)
        attachments = list(payload.get("attachments") or [])
        image_evidence = analyzer.analyze_manual_images(attachments) if any(str(item.get("type") or "").startswith("image/") for item in attachments if isinstance(item, dict)) else []
        evidence = _manual_evidence(raw, payload.get("device") or "", payload.get("model") or "", payload.get("serial_number") or "", image_evidence)
        device = evidence["device_name"]
        if device:
            analysis["device_name"] = device
        if str(payload.get("model") or "").strip():
            analysis["model_type"] = str(payload.get("model")).strip()
        elif evidence["model_resolution"].get("model") and not analysis.get("model_type"):
            analysis["model_type"] = evidence["model_resolution"]["model"]
        # Manual-source diagnostic requests are guidance, not a verified ITR
        # Solution. Retain them in review only and leave Solutions empty until
        # a confirmed resolution is available.
        analysis["diagnostic_guidance"] = analysis.get("pie_comment") or ""
        analysis["pie_guidance"] = _actionable_manual_guidance(analysis.get("pie_guidance") or analysis.get("solutions"))
        analysis["repair_actions"] = _validated_repair_actions(analysis.get("repair_actions"), raw)
        analysis["solutions"] = ""
        reply_statistics = _manual_reply_statistics(manual_messages)
        analysis["support_reply_ids"] = reply_statistics["support_reply_ids"]
        analysis["reply_statistics"] = reply_statistics
        reply, reply_suppressed = _manual_reply(analysis, source, manual_messages)
        analysis["reply_en"] = reply
        analysis["reply_suppressed"] = reply_suppressed
        if not reply and not reply_suppressed:
            analysis["reply_generation_error"] = "Manual reply could not be generated."
        tags = tag_engine.classify(_tag_text(analysis))
        draft = ManualIntakeDraft(
            draft_key=str(payload.get("draft_key") or f"temp:{uuid.uuid4()}"), source=source,
            raw_source_evidence=raw, normalized_analysis_input=normalized.current_message or raw,
            contact=contact, partner_candidate=partner_candidate, partner_confirmed=partner_confirmed,
            country=str(payload.get("country") or partner_candidate.get("country") or "").strip(), device=device, model=str(payload.get("model") or evidence["model_resolution"].get("model") or "").strip(),
            serial_number=evidence["serial_number"], session_notes=str(payload.get("session_notes") or "").strip(),
            attachment_metadata=list(payload.get("attachment_metadata") or []), source_timestamp=source_timestamp,
            case_history_append=case_history, analysis=analysis, tags=tags, device_evidence=evidence,
            image_evidence=image_evidence, reply_suppressed=reply_suppressed,
        )
        return _result(True, "prepare_manual_intake", "Manual source is ready for review.", draft=draft, analysis=analysis)
    except Exception:
        return _result(False, "prepare_manual_intake", "Manual source preparation failed.", error_type="manual_prepare_error")


def manual_draft_from_json(data):
    allowed = set(ManualIntakeDraft.__dataclass_fields__)
    return ManualIntakeDraft(**{key: value for key, value in dict(data or {}).items() if key in allowed})


def reanalyze_manual_draft(draft, human_guidance=""):
    """Run the established Inspector contract over an already-local manual draft.

    This never fetches Nextop or writes Feishu.  The original raw evidence and
    source-specific fields remain the authoritative draft payload.
    """
    if not isinstance(draft, ManualIntakeDraft):
        return _result(False, "manual_reanalyze", "Analyze the manual source before regenerating.", error_type="invalid_manual_draft")
    from dataclasses import asdict
    source = dict(draft.analysis or {})
    source.update({
        "case_history": draft.case_history_append,
        "description": source.get("description") or "",
        "fault_symptom": source.get("fault_symptom") or [],
        "pie_comment": source.get("pie_comment") or "",
        "solutions": source.get("solutions") or "",
        "model_type": draft.model or source.get("model_type") or "",
        "error_codes": source.get("error_code") or [],
        "human_guidance": str(human_guidance or "").strip(),
        "context_pack": {"knowledge_coverage": "none"},
    })
    inspector = asdict(analyzer.analyze_case_for_inspector(source))
    analysis = dict(source)
    analysis.update(inspector)
    analysis["diagnostic_guidance"] = source.get("pie_comment") or ""
    analysis["pie_guidance"] = inspector.get("ai_suggested_next_step") or ""
    # A diagnostic request remains guidance.  Only an Inspector-confirmed
    # solution may enter the future ITR Solution field.
    analysis["solutions"] = inspector.get("solution") or ""
    updated = replace(draft, analysis=analysis, reply_suppressed=False)
    return _result(True, "manual_reanalyze", "Manual analysis and reply were regenerated.", draft=updated, analysis=analysis)


def prepare_manual_append_preview(ticket_no, draft):
    """Read-only preview for a future manual append; it never calls update_record."""
    ticket_no = str(ticket_no or "").strip()
    if not ticket_no.upper().startswith("ITR-"):
        return _result(False, "manual_append_preview", "Enter an exact ITR Ticket No.", error_type="invalid_ticket_no")
    existing = open_existing_case(ticket_no)
    if not existing.get("success"):
        return existing
    record = feishu_api.get_record(existing["record_id"])
    fields = record.get("fields") or {}
    prior_history = feishu_api.normalize_field_value(fields.get("Case History")) or ""
    append = str(draft.case_history_append or "").strip()
    merged = append_manual_history(prior_history, append, draft.raw_source_evidence)
    if merged is None:
        return _result(False, "manual_append_preview", "This source evidence is already present in Case History.", error_type="duplicate")
    protected = ("Ticket No.", "Solutions", "一级标签", "二级标签", "三级标签", "PIE-Comment", "Total Replied", "Notes")
    actions = [{"field": "Case History", "action": "APPEND", "existing": prior_history, "proposed": merged}]
    actions.extend({"field": name, "action": "PRESERVE", "existing": feishu_api.normalize_field_value(fields.get(name)), "proposed": draft.analysis.get({"Solutions": "solutions", "PIE-Comment": "pie_comment"}.get(name, ""), "") if name in {"Solutions", "PIE-Comment"} else ""} for name in protected)
    return _result(True, "manual_append_preview", "Safe append preview is ready. Production append is disabled.", ticket_no=ticket_no, record_id=existing["record_id"], case=existing["case"], actions=actions, production_write_enabled=False)


def _manual_partner(draft):
    return str(draft.partner_confirmed or (draft.partner_candidate or {}).get("partner") or "").strip()


def _manual_create_fields(draft, *, include_itr_todo=False, nff_value=False, issue_owner=""):
    """Build the exact new-record payload; no reference number is invented."""
    analysis = dict(draft.analysis or {})
    evidence = dict(draft.device_evidence or {})
    if evidence.get("device_name"):
        analysis["device_name"] = evidence["device_name"]
    if evidence.get("model_resolution", {}).get("model") and not analysis.get("model_type"):
        analysis["model_type"] = evidence["model_resolution"]["model"]
    fields = build_v2_fields(draft.case_history_append, analysis, (_manual_partner(draft),), tags=draft.tags)
    reply_statistics = dict(analysis.get("reply_statistics") or {})
    if reply_statistics.get("status") == "DERIVED":
        fields.update(reply_statistics.get("fields") or {})
    if _manual_partner(draft):
        fields["Disti/Dealer/Service Point"] = _manual_partner(draft)
        fields["_partner_resolution"] = {"status": "EXPLICIT" if draft.partner_confirmed else "RESOLVED", "partner": _manual_partner(draft)}
    # No Nextop reference exists for these source types.  It must remain absent.
    fields.pop("Reference No.", None)
    if include_itr_todo:
        fields[ITR_TODO_FIELD] = True
    if nff_value:
        fields[ITR_NFF_FIELD] = True
    if issue_owner in ITR_ISSUE_OWNER_OPTIONS:
        fields[ITR_ISSUE_OWNER_FIELD] = issue_owner
    return sanitize_create_fields(fields)


def prepare_manual_create_preview(draft, *, include_itr_todo=False, nff_value=False, issue_owner=""):
    if not isinstance(draft, ManualIntakeDraft) or not str(draft.raw_source_evidence or "").strip():
        return _result(False, "manual_create_preview", "Analyze the manual source before creating ITR.", error_type="invalid_manual_draft")
    if nff_value:
        return _result(False, "manual_create_preview", "NFF remains a manual decision and requires confirmed evidence before ITR creation.", error_type="nff_evidence_required")
    fields = _manual_create_fields(draft, include_itr_todo=include_itr_todo, nff_value=False, issue_owner=issue_owner)
    return _result(True, "manual_create_preview", "Create ITR preview is ready.", fields=fields, source=draft.source,
                   attachment_count=len(draft.attachment_metadata or []), device_evidence=draft.device_evidence,
                   serial_number=draft.serial_number, production_write_enabled=False)


def _decode_manual_attachments(attachments):
    """Decode browser-local attachment data only at the explicit write boundary."""
    import base64
    decoded = []
    for item in attachments or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "attachment").strip()[:180] or "attachment"
        encoded = str(item.get("data_base64") or "")
        if not encoded:
            continue
        try:
            content = base64.b64decode(encoded, validate=True)
        except Exception:
            raise ValueError("A local attachment could not be read.")
        if not content or len(content) > 15 * 1024 * 1024:
            raise ValueError("An attachment is empty or exceeds the 15 MB local limit.")
        decoded.append((name, content))
    return decoded


def _append_uploaded_manual_attachments(record_id, attachments):
    decoded = _decode_manual_attachments(attachments)
    if not decoded:
        return {"success": True, "count": 0}
    try:
        record = feishu_api.get_record(record_id)
        current = [{"file_token": item["file_token"]} for item in (record.get("fields", {}).get("Notes") or []) if item.get("file_token")]
        tokens = list(current)
        for name, content in decoded:
            tokens.append({"file_token": feishu_api.upload_attachment(content, name)})
        response = feishu_api.update_record(record_id, {"Notes": tokens})
    except Exception:
        return {"success": False, "count": len(decoded)}
    if response.get("code") != 0:
        return {"success": False, "count": len(decoded)}
    return {"success": True, "count": len(decoded)}


def _readback_manual_ticket(record_id):
    for _attempt in range(3):
        record = feishu_api.get_record(record_id)
        ticket_no = str(feishu_api.normalize_field_value((record.get("fields") or {}).get("Ticket No.")) or "").strip()
        if ticket_no:
            return ticket_no, record
    return "", {}


def create_manual_itr(draft, attachments=None, *, include_itr_todo=False, nff_value=False, issue_owner=""):
    """Explicit new-case write: create once, then read Feishu's native Ticket No."""
    preview = prepare_manual_create_preview(draft, include_itr_todo=include_itr_todo, nff_value=nff_value, issue_owner=issue_owner)
    if not preview.get("success"):
        return preview
    response = feishu_api.create_record(preview["fields"])
    if response.get("code") != 0:
        return _feishu_failure(response, "manual_create", "Manual ITR creation failed.", source=draft.source)
    record_id = _response_record_id(response)
    if not record_id:
        return _result(False, "manual_create", "ITR create may have succeeded, but no record ID was returned. Do not create again.", error_type="uncertain_write")
    ticket_no, _record = _readback_manual_ticket(record_id)
    if not ticket_no:
        return _result(False, "manual_create", "ITR create may have succeeded, but Ticket No. readback failed. Do not create again; recover using the returned record.", error_type="readback_failed", record_id=record_id, write_state="UNCERTAIN")
    attachment_result = _append_uploaded_manual_attachments(record_id, attachments)
    if not attachment_result["success"]:
        return _result(False, "manual_create", "ITR was created, but one or more attachments could not be saved. Do not create again.", error_type="attachment_partial", record_id=record_id, ticket_no=ticket_no, write_state="PARTIAL_ATTACHMENTS")
    return _result(True, "manual_create", "ITR created with native Ticket No.", record_id=record_id, ticket_no=ticket_no, attachment_count=attachment_result["count"], write_state="COMPLETE")


def append_manual_itr(ticket_no, draft, attachments=None):
    """Explicit append writes only Case History/Notes; managed case fields are untouched."""
    preview = prepare_manual_append_preview(ticket_no, draft)
    if not preview.get("success"):
        return preview
    record_id = preview["record_id"]
    history = next(item["proposed"] for item in preview["actions"] if item["field"] == "Case History")
    with _record_write_guard(record_id) as acquired:
        if not acquired:
            return _result(False, "manual_append", "This ITR case is being updated in another workspace.", error_type="case_busy")
        # Re-read immediately before writing so an earlier preview never replaces history.
        current = feishu_api.get_record(record_id)
        prior = feishu_api.normalize_field_value((current.get("fields") or {}).get("Case History")) or ""
        merged = append_manual_history(prior, draft.case_history_append, draft.raw_source_evidence)
        if merged is None:
            return _result(False, "manual_append", "This source evidence is already present in Case History.", error_type="duplicate")
        response = feishu_api.update_record(record_id, {"Case History": merged})
        if response.get("code") != 0:
            return _feishu_failure(response, "manual_append", "Manual evidence could not be appended.", record_id=record_id)
        attachment_result = _append_uploaded_manual_attachments(record_id, attachments)
        if not attachment_result["success"]:
            return _result(False, "manual_append", "Case History was appended, but one or more attachments could not be saved. Do not append again.", error_type="attachment_partial", record_id=record_id, ticket_no=ticket_no, write_state="PARTIAL_ATTACHMENTS")
    return _result(True, "manual_append", "Evidence was appended to the existing ITR case.", record_id=record_id, ticket_no=ticket_no, attachment_count=attachment_result["count"], write_state="COMPLETE")


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

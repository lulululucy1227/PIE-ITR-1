"""Read-only partner resolution from the Feishu partner-code table."""
from __future__ import annotations

import re
from urllib.parse import urlparse

PARTNER_TABLE_NAME = "代理与服务商代号"
CCTLD_COUNTRIES = {
    "dk": "Denmark", "de": "Germany", "pl": "Poland", "cz": "Czech Republic",
    "hu": "Hungary", "si": "Slovenia", "me": "Montenegro", "ee": "Estonia",
}
_GENERIC_TLDS = {"com", "net", "org"}


def _text(value):
    if isinstance(value, list):
        return " ".join(_text(item) for item in value)
    if isinstance(value, dict):
        return str(value.get("text") or value.get("value") or value.get("name") or "")
    return str(value or "")


def normalize_alias(value):
    return re.sub(r"\s+", " ", _text(value).strip()).casefold()


def normalize_email(value):
    text = normalize_alias(value)
    return text[7:] if text.startswith("mailto:") else text


def normalize_phone(value):
    raw = _text(value).strip()
    if not raw or not re.fullmatch(r"[+()\-\s\d.]+", raw):
        return ""
    digits = re.sub(r"\D", "", raw)
    return digits if len(digits) >= 7 else ""


def normalize_domain(value):
    raw = normalize_alias(value).removeprefix("mailto:")
    if "@" in raw:
        raw = raw.rsplit("@", 1)[1]
    if "://" in raw:
        raw = urlparse(raw).hostname or ""
    raw = raw.split("/", 1)[0].removeprefix("www.").rstrip(".")
    return raw if re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+", raw) else ""


def infer_country_from_contact(value):
    domain = normalize_domain(value)
    suffix = domain.rsplit(".", 1)[-1] if domain else ""
    return CCTLD_COUNTRIES.get(suffix, "") if suffix not in _GENERIC_TLDS else ""


def _mark_values(value):
    return [item.strip() for item in re.split(r"[\n,;|]+", _text(value)) if item.strip()]


def _identifiers(value):
    raw = _text(value)
    values = {"alias": set(), "email": set(), "phone": set(), "domain": set()}
    for item in _mark_values(raw):
        email, phone, domain, alias = normalize_email(item), normalize_phone(item), normalize_domain(item), normalize_alias(item)
        if re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email): values["email"].add(email)
        elif phone: values["phone"].add(phone)
        elif domain: values["domain"].add(domain)
        elif alias: values["alias"].add(alias)
    return values


def resolve_partner(records, *, explicit_partner="", contact=""):
    """Resolve deterministic exact Marks evidence; never selects a conflict."""
    if str(explicit_partner or "").strip():
        return {"status": "RESOLVED", "partner": str(explicit_partner).strip(), "code": "", "country": "", "reason": "explicit_partner", "candidates": []}
    contact_ids = _identifiers(contact)
    matches = {kind: [] for kind in ("email", "phone", "domain", "alias")}
    for record in records or []:
        fields = record.get("fields", record) if isinstance(record, dict) else {}
        partner = _text(fields.get("Disti")).strip()
        if not partner:
            continue
        mark_ids = _identifiers(fields.get("Marks"))
        for kind, values in contact_ids.items():
            if values & mark_ids[kind]:
                matches[kind].append({"partner": partner, "code": _text(fields.get("Code")).strip(), "country": _text(fields.get("Country")).strip(), "reason": f"marks_{kind}"})
    for kind in ("email", "phone", "domain", "alias"):
        unique = {item["partner"]: item for item in matches[kind]}
        if len(unique) == 1:
            return {"status": "RESOLVED", "candidates": [], **next(iter(unique.values()))}
        if len(unique) > 1:
            return {"status": "CONFLICT", "partner": "", "code": "", "country": "", "reason": f"marks_{kind}_conflict", "candidates": sorted(unique)}
    return {"status": "UNKNOWN", "partner": "", "code": "", "country": infer_country_from_contact(contact), "reason": "no_exact_marks_match", "candidates": []}


def load_partner_records_readonly():
    """Return minimal business-source fields only; no cache or write side effect."""
    import feishu_api
    table = next((item for item in feishu_api.list_tables_readonly() if item.get("name") == PARTNER_TABLE_NAME), None)
    if not table:
        return []
    return feishu_api.get_table_records_readonly(table["table_id"], ["Disti", "Code", "Country", "Marks"])


def partner_options_readonly():
    values = []
    for record in load_partner_records_readonly():
        fields = record.get("fields", {})
        partner = _text(fields.get("Disti")).strip()
        if partner:
            values.append({"partner": partner, "code": _text(fields.get("Code")).strip(), "country": _text(fields.get("Country")).strip()})
    return sorted({item["partner"]: item for item in values}.values(), key=lambda item: item["partner"].casefold())

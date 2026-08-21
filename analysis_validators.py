"""Deterministic post-analysis safety checks; never calls an LLM."""
import re

_RISK = re.compile(r"\b(replace(?:ment)?|refund|scrap(?:ping)?|warranty|ETA|password|delete data|erase data)\b", re.I)
_CJK = re.compile(r"[\u3400-\u9fff]")

def reply_is_english(text):
    """Deterministic guard: the copy-ready reply must be English, not prompt-only."""
    text = str(text or "")
    letters = re.findall(r"[A-Za-z]", text)
    return bool(letters) and len(_CJK.findall(text)) <= max(2, len(letters) // 12)

def provenance_ids(context):
    ids = {"current_ticket"}
    for group in ("historical_itr", "error_codes", "technical_notes"):
        for item in (context.get(group, {}) or {}).get("matches", []) + (context.get(group, {}) or {}).get("exact_matches", []):
            if item.get("record_id"):
                ids.add(str(item["record_id"]))
    return ids

def validate(result, context, capability, restricted):
    """Return a normalized analysis dict and deterministic safety flags."""
    result = dict(result or {})
    allowed = provenance_ids(context)
    result["confirmed_facts"] = [str(x) for x in result.get("confirmed_facts", []) if str(x).strip()]
    result["already_tried"] = [str(x) for x in result.get("already_tried", context.get("follow_up", {}).get("already_tried", [])) if str(x).strip()]
    result["ruled_out"] = [str(x) for x in result.get("ruled_out", []) if str(x).strip()]
    result["resolution_path"] = [str(x) for x in result.get("resolution_path", []) if str(x).strip()]
    result["parts_to_verify"] = []
    hypotheses = []
    for item in result.get("hypotheses", []) or []:
        if not isinstance(item, dict):
            continue
        cited = [str(x) for x in item.get("cited", []) if str(x) in allowed]
        hypotheses.append({"cause": str(item.get("cause") or ""), "confidence": str(item.get("confidence") or "low").lower() if str(item.get("confidence") or "").lower() in {"high","medium","low"} else "low", "evidence": [str(x) for x in item.get("evidence", [])], "cited": cited, "discriminator": str(item.get("discriminator") or "")})
    result["hypotheses"] = hypotheses
    escalation = [str(x) for x in result.get("escalation", []) if str(x).strip()]
    output = " ".join(str(result.get(key) or "") for key in ("ai_suggested_next_step", "solution", "reply_en"))
    if _RISK.search(output):
        escalation.append("High-risk commitment requires human review.")
    if restricted:
        escalation.append("Unsupported capability request requires human review.")
    if result.get("reply_generation_error"):
        escalation.append("Reply generation error requires human review.")
    result["escalation"] = list(dict.fromkeys(escalation))
    result["needs_human_check"] = bool(result.get("needs_human_check")) or bool(result["escalation"])
    result["validator_restricted"] = bool(restricted)
    return result

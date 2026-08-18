"""Read-only Context Pack assembly. Feishu remains the authority."""
import re
import feishu_api

ITR_FIELDS=["Ticket No.","Reference No.","一级标签","二级标签","Model Type","Description","PIE-Comment","Solutions","SOP","Total Replied","Replied Time-First","Replied Time-NEW"]
ERROR_TABLE="tblkzas8M9EkZjQU"; NOTES_TABLE="tblZcrxn28G1IsOW"

def _text(value): return feishu_api.normalize_field_value(value) or ""
def _codes(*texts):
    return sorted({x for text in texts for x in re.findall(r"\b[A-Z]?\d{3,8}[A-Z]?\b",str(text or ""),re.I)})
def _follow_up(messages):
    text="\n".join(str(m.get("content") or m.get("text") or "") for m in messages)
    failed=[x.strip() for x in re.findall(r"([^.!?]{3,100}(?:checked|tried|replaced|reset)[^.!?]{0,100}(?:still|not work|remains|failed)[^.!?]*)",text,re.I)]
    return {"is_follow_up":len(messages)>1,"previous_context":text if len(messages)>1 else "","new_information":"","already_tried":failed,"failed_actions":failed}
def _items(table_id, fields):
    try: return feishu_api.get_table_records_readonly(table_id,fields)
    except Exception: return []
def build_context(ticket_no, fields, messages, case_history):
    reference=str(ticket_no or fields.get("Reference No.") or "").strip()
    itr=feishu_api.find_records_by_reference_exact(reference,ITR_FIELDS) if reference else []
    historical=[{"record_id":x.get("record_id"),"source":"historical_itr","match_method":"reference_exact","fields":x.get("fields",{})} for x in itr]
    codes=_codes(case_history,fields.get("Error massages"),fields.get("Description"))
    error=[x for x in _items(ERROR_TABLE,[]) if str(_text((x.get("fields")or{}).get("错误代码"))).upper() in {c.upper() for c in codes}]
    terms={w.lower() for w in re.findall(r"[A-Za-z0-9]{4,}",case_history or "")}
    notes=[x for x in _items(NOTES_TABLE,[]) if terms & {w.lower() for w in re.findall(r"[A-Za-z0-9]{4,}",str(x.get("fields")or""))}]
    coverage="strong" if historical or error else "partial" if notes else "none"
    return {"current_ticket":{"ticket_no":ticket_no,"fields":fields,"messages":messages,"source":"current_ticket"},"follow_up":_follow_up(messages),"historical_itr":{"matches":historical,"match_status":"found" if historical else "none"},"error_codes":{"exact_matches":error,"match_status":"found" if error else "none","tokens":codes},"technical_notes":{"matches":notes,"match_status":"found" if notes else "none"},"approved_kb":{"matches":[],"match_status":"none","excluded_reason":"unreviewed"},"knowledge_coverage":coverage,"low_coverage":coverage=="none","provenance":[{"source_type":"current_ticket","match_method":"direct"}]}

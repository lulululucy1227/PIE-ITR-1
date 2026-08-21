"""Run a redacted, read-only PIE real-ticket validation from the local shell.

The tool has no credentials and never prints ticket content.  It blocks the two
Feishu record-write calls in-process before loading any ticket.
"""
import argparse
import json

import analyzer
import case_service


def _state(value):
    return "PRESENT" if str(value or "").strip() else "EMPTY"


def _expected_value(current, existing, preview):
    if str(current or "").strip():
        return preview == current
    if str(existing or "").strip():
        return preview == existing
    return not str(preview or "").strip()


def _write_guard(*_args, **_kwargs):
    raise RuntimeError("WRITE_GUARD")


def validate(ticket):
    result = {
        "Ticket": ticket,
        "Fetch": "FAIL",
        "Latest Actor": "UNKNOWN",
        "Workspace Status": "ERROR",
        "Translation": "N/A",
        "Reply State": "N/A",
        "Reply Language": "N/A",
        "Description": "EMPTY",
        "Solutions": "EMPTY",
        "PIE-Comment": "EMPTY",
        "L1 Label": "EMPTY",
        "L2 Label": "EMPTY",
        "Existing ITR Found": "NO",
        "Existing Solutions": "EMPTY",
        "Preview Solutions": "EMPTY",
        "Preview Data Preservation": "FAIL",
        "Validation": "FAIL",
        "Failure Reason": "UNKNOWN",
    }
    try:
        loaded = case_service.prepare_nextop_case(ticket)
        if not loaded.get("success"):
            result["Failure Reason"] = str(loaded.get("error_type") or "NEXTOP_OR_FEISHU_READ")
            return result
        prepared = loaded["prepared"]
        result.update({
            "Fetch": "PASS",
            "Latest Actor": prepared.latest_sender_role or "UNKNOWN",
            "Existing ITR Found": "YES" if prepared.existing_record_id else "NO",
            "Existing Solutions": _state((prepared.existing_case or {}).get("solutions")),
        })
        analysis = {}
        if prepared.latest_sender_role == "PIE":
            active = prepared
            result.update({"Workspace Status": "WAITING", "Reply State": "NONE"})
            translation_source = prepared.fields.get("Description")
        else:
            analyzed = case_service.reanalyze_prepared_nextop_case(prepared)
            if not analyzed.get("success"):
                result["Failure Reason"] = str(analyzed.get("error_type") or "ANALYZE")
                return result
            active, analysis = analyzed["prepared"], analyzed.get("analysis") or {}
            reply = str(analysis.get("reply_en") or "").strip()
            reply_error = str(analysis.get("reply_generation_error") or "").strip()
            result.update({
                "Workspace Status": "INSUFFICIENT" if analysis.get("information_status") == "insufficient" else "READY",
                "Reply State": "FAIL" if reply_error else "PRESENT" if reply else "EMPTY",
                "Reply Language": "PASS" if reply and analyzer.reply_is_english(reply) else "FAIL" if reply else "N/A",
            })
            translation_source = analysis.get("customer_description")
        fields = active.fields
        classification = fields.get("_classification") or {}
        result.update({
            "Description": _state(fields.get("Description")),
            "Solutions": _state(fields.get("Solutions")),
            "PIE-Comment": _state(fields.get("PIE-Comment")),
            "L1 Label": _state(fields.get("一级标签")),
            "L2 Label": _state(fields.get("二级标签")),
            "Classification": "RESOLVED" if classification.get("status") == "RESOLVED" else "UNRESOLVED_EXPLICIT" if classification.get("reason") else "UNRESOLVED_SILENT",
        })
        if str(translation_source or "").strip():
            try:
                result["Translation"] = "PASS" if str(case_service.translate_text_to_zh(translation_source) or "").strip() else "FAIL"
            except Exception:
                result["Translation"] = "FAIL"
        preview = case_service.prepare_commit_preview(active)
        if not preview.get("success"):
            result["Failure Reason"] = str(preview.get("error_type") or "PREVIEW")
            return result
        preview_fields = preview["prepared"].fields
        result["Preview Solutions"] = _state(preview_fields.get("Solutions"))
        existing = prepared.existing_case or {}
        contracts = [
            _expected_value(fields.get(name), existing.get(existing_key), preview_fields.get(name))
            for name, existing_key in (
                ("Description", "description"), ("Solutions", "solutions"),
                ("PIE-Comment", "pie_comment"), ("Ticket Created Time", "ticket_created_time"),
            )
        ]
        if classification.get("status") == "RESOLVED":
            contracts.extend([
                preview_fields.get("一级标签") == fields.get("一级标签"),
                preview_fields.get("二级标签") == fields.get("二级标签"),
            ])
        else:
            contracts.append(bool(classification.get("reason")))
        result["Preview Data Preservation"] = "PASS" if all(contracts) else "FAIL"
        checks = [
            result["Translation"] in {"PASS", "N/A"},
            result["Preview Data Preservation"] == "PASS",
            result["Classification"] != "UNRESOLVED_SILENT",
        ]
        if prepared.latest_sender_role == "PIE":
            checks.extend([result["Workspace Status"] == "WAITING", result["Reply State"] == "NONE"])
        else:
            checks.extend([result["Reply State"] == "PRESENT", result["Reply Language"] == "PASS"])
        result["Validation"] = "PASS" if all(checks) else "FAIL"
        result["Failure Reason"] = "" if result["Validation"] == "PASS" else "CONTRACT_CHECK"
    except Exception as exc:
        result["Failure Reason"] = type(exc).__name__
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tickets", nargs="+", help="Ticket numbers to validate read-only")
    args = parser.parse_args()
    case_service.feishu_api.create_record = _write_guard
    case_service.feishu_api.update_record = _write_guard
    print(json.dumps({"validation_infrastructure": "PASS", "external_writes": "NO", "tickets": [validate(ticket) for ticket in args.tickets]}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

"""Command-line adapter for NextopSync case_service."""
import re
import sys

import case_service
import tag_engine


_MANUAL_SOURCES = {"whatsapp", "lark", "email"}


def _progress(stage, message, success=None):
    """Keep terminal presentation outside the reusable service layer."""
    if stage == "nextop_fetch":
        print("[1/3] Fetching ticket...")
    elif stage == "analysis":
        print("[2/3] Analyzing complete Case History and classifying tags...")
    elif stage == "notes":
        print("[3/3] Syncing Notes images...")
    elif stage == "candidates":
        print("Finding possible related Cases...")
    elif stage == "failed":
        print("Operation failed.")


def _display_candidate(candidate, index):
    issue = re.sub(r"\s+", " ", candidate.get("pie_comment") or candidate.get("description") or "").strip()[:120]
    print(f"[{index}] Ticket No.: {candidate.get('ticket_no') or '-'}")
    print(f"    Source: {candidate.get('reference_no') or '-'}")
    for label, key in (("Disti", "disti"), ("Device", "device_name"), ("Model", "model_type")):
        if candidate.get(key):
            print(f"    {label}: {candidate[key]}")
    if issue:
        print(f"    Issue: {issue}")
    if candidate.get("error_codes"):
        print(f"    Error Code: {', '.join(candidate['error_codes'])}")
    if candidate.get("replied_time_new"):
        print(f"    Last Reply: {case_service.format_time(candidate['replied_time_new'])}")


def _choose_candidate(candidates):
    if candidates:
        print("Possible related Cases:")
        for index, candidate in enumerate(candidates, 1):
            _display_candidate(candidate, index)
    else:
        print("No clearly related existing Case was found.")
    print("[N] Create new Case")
    while True:
        choice = input("Select a Case number or N: ").strip()
        if choice.lower() == "n":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice) - 1]
        print("Invalid selection. Please enter a displayed number or N.")


def _print_result(result):
    if result.get("duplicate_detected"):
        print(result["message"])
    elif result.get("success"):
        print("Feishu result: 0", result["message"])
    else:
        print("Error:", result.get("message", "Operation failed."))


def _paste_mode(source):
    print("Paste content, then enter END on a separate line:")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    prepared = case_service.prepare_manual_submission(source, "\n".join(lines).strip(), _progress)
    if not prepared.get("success"):
        _print_result(prepared)
        return
    selected = _choose_candidate(prepared["candidates"])
    result = (case_service.create_manual_case(prepared["draft"], _progress) if selected is None
              else case_service.update_manual_case(selected["record_id"], prepared["draft"], _progress))
    _print_result(result)


def run_loop():
    while True:
        try:
            ticket = input("Ticket number / whatsapp / lark / email (blank to exit): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not ticket:
            break
        if ticket.lower() in _MANUAL_SOURCES:
            _paste_mode(ticket.lower())
        else:
            _print_result(case_service.sync_nextop(ticket, _progress))


def reconcile_case_counts():
    """Explicit maintenance command; never runs as part of normal CLI/GUI work."""
    report = tag_engine.reconcile_case_counts()
    print("Case Count Reconciliation")
    for key in ("records_scanned", "labels_counted", "stale_rows", "updated_rows", "verify_result", "elapsed_seconds"):
        print(f"{key}: {report.get(key)}")
    return report


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argument = sys.argv[1].lower()
        if argument == "reconcile-case-counts":
            reconcile_case_counts()
        else:
            _paste_mode(argument) if argument in _MANUAL_SOURCES else _print_result(case_service.sync_nextop(sys.argv[1], _progress))
    else:
        run_loop()

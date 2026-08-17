"""Offline D1-B regressions.  These tests never call Nextop or Feishu."""
import sys
import types
import unittest
from unittest.mock import patch

# The bundled Codex interpreter intentionally has no HTTP dependency.  The
# service tests mock every network boundary, so provide only the exception
# shape imported by the project modules.
if "requests" not in sys.modules:
    _requests = types.ModuleType("requests")
    class _RequestException(Exception):
        pass
    _requests.exceptions = types.SimpleNamespace(RequestException=_RequestException)
    sys.modules["requests"] = _requests
if "bs4" not in sys.modules:
    _bs4 = types.ModuleType("bs4")
    _bs4.BeautifulSoup = object
    sys.modules["bs4"] = _bs4

import case_service as service


def _prepared(ticket="N-1", *, existing=None, kind=None):
    fields = {name: ([] if name in service.MULTI_SELECT_FIELDS else "") for name in service.V2_MANAGED_FIELDS}
    fields.update({"Case History": "[2026-01-01] Customer\nNeed help", "Reference No.": ticket, "Ticket Created Time": 1})
    return service.PreparedNextopCase(
        ticket, "[2026-01-01] Customer\nNeed help", {"pie_comment": "x"},
        fields, [], {},
        existing_record_id=existing, selected_match_kind=kind,
        can_create=existing is None, can_update=existing is not None,
    )


class PreparedNextopCommitTests(unittest.TestCase):
    def test_sync_is_prepare_then_commit_adapter(self):
        prepared = _prepared()
        with patch.object(service, "prepare_nextop_case", return_value={"success": True, "prepared": prepared}) as prepare, \
             patch.object(service, "commit_prepared_nextop_case", return_value={"success": True, "action": "created"}) as commit:
            result = service.sync_nextop("N-1", include_itr_todo=True, todo_dirty=True)
        self.assertTrue(result["success"])
        prepare.assert_called_once_with("N-1", None, duplicate_decision=None, duplicate_record_id=None)
        commit.assert_called_once_with(prepared, None, include_itr_todo=True, todo_dirty=True)

    def test_prepare_then_commit_fetches_and_analyzes_once(self):
        ticket_data = {"messages": [], "list_info": {"createTime": 1, "outerName": "", "outerAddress": "", "title": ""}}
        with patch.object(service, "open_existing_case", return_value={"match_status": "NOT_FOUND"}), \
             patch.object(service.nextop_api, "get_ticket_full", return_value=ticket_data) as fetch, \
             patch.object(service.analyzer, "analyze_case_history", return_value={"pie_comment": "x"}) as analyze, \
             patch.object(service, "build_nextop_case_history", return_value="history"), \
             patch.object(service, "build_v2_fields", return_value={"Case History": "history", "一级标签": "", "二级标签": ""}), \
             patch.object(service, "find_nextop_legacy_duplicates", return_value=[]), \
             patch.object(service.feishu_api, "find_records_by_reference_exact", return_value=[]), \
             patch.object(service, "build_notes_attachments", return_value=None), \
             patch.object(service.feishu_api, "create_record", return_value={"code": 0, "data": {"record": {"record_id": "rec1"}}}), \
             patch.object(service.feishu_api, "get_record", return_value={"record_id": "rec1", "fields": {}}), \
             patch.object(service, "_refresh_case_counts", return_value={"count": None, "warning": False, "reports": []}):
            prepared = service.prepare_nextop_case("N-1")["prepared"]
            result = service.commit_prepared_nextop_case(prepared)
        self.assertTrue(result["success"])
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(analyze.call_count, 1)

    def test_stale_exact_prepared_target_is_not_written(self):
        prepared = _prepared(existing="rec-old", kind="exact")
        with patch.object(service.feishu_api, "find_records_by_reference_exact", return_value=[{"record_id": "rec-new", "fields": {}}]), \
             patch.object(service.feishu_api, "update_record") as update:
            result = service.commit_prepared_nextop_case(prepared)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "prepared_stale")
        update.assert_not_called()

    def test_record_lock_releases_after_update_exception(self):
        prepared = _prepared(existing="rec-lock", kind="legacy")
        with patch.object(service.feishu_api, "get_record", return_value={"record_id": "rec-lock", "fields": {}}), \
             patch.object(service, "build_notes_attachments", return_value=None), \
             patch.object(service.feishu_api, "update_record", side_effect=[RuntimeError("offline"), {"code": 0}]) as update, \
             patch.object(service, "_refresh_case_counts", return_value={"count": None, "warning": False, "reports": []}):
            first = service.commit_prepared_nextop_case(prepared)
            second = service.commit_prepared_nextop_case(prepared)
        self.assertFalse(first["success"])
        self.assertTrue(second["success"])
        self.assertEqual(update.call_count, 2)


if __name__ == "__main__":
    unittest.main()

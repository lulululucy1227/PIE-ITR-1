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
    def test_verified_device_prefix_model_rules_are_deterministic(self):
        self.assertEqual(service._model_from_device_name("LUBA-VSXHJC7B"), "luba 2")
        self.assertEqual(service._model_from_device_name("luba-vpXHJC7B"), "luba 2x")
        self.assertEqual(service._model_from_device_name("Yuka-MVTZCYHY"), "yuka mini 2 800")
        self.assertEqual(service._model_from_device_name("  yuka_mvtZCYHY  "), "yuka mini 2 800")
        self.assertEqual(service._model_from_device_name("unknown-device"), "")
        self.assertEqual(service._model_from_device_name(""), "")

    def test_model_resolution_detects_conflict_without_overwriting_explicit_model(self):
        resolution = service.resolve_model("LUBA-VS123", "LUBA 3")
        self.assertEqual(resolution["status"], "MODEL_CONFLICT")
        self.assertEqual(resolution["model"], "LUBA 3")
        self.assertEqual(service.resolve_model("LUBA-VS123", "LUBA 2")["status"], "EXPLICIT")

    def test_internal_resolution_metadata_never_crosses_create_boundary(self):
        payload = service.sanitize_create_fields({"Reference No.": "SAFE-1", "_model_resolution": {"status": "UNKNOWN"}})
        self.assertEqual(payload, {"Reference No.": "SAFE-1"})

    def test_ticket_device_extraction_uses_title_when_structured_data_is_empty(self):
        ticket = {"list_info": {"title": "Luba-MBRZJ2ZJ cutting motor stopped"}, "basic": {}, "messages": []}
        resolved = service.extract_ticket_device(ticket)
        self.assertEqual(resolved["device_name"], "LUBA-MBRZJ2ZJ")
        self.assertEqual(service.resolve_model(resolved["device_name"])["model"], "luba mini 2")

    def test_ticket_device_conflict_stays_unresolved(self):
        ticket = {"list_info": {"title": "LUBA-VS12345"}, "basic": {"deviceName": "LUBA-VP12345"}, "messages": []}
        self.assertEqual(service.extract_ticket_device(ticket)["status"], "DEVICE_CONFLICT")

    def test_reanalysis_replaces_old_solution_in_prepared_payload(self):
        prepared = _prepared()
        prepared.fields.update({"Description": "Old issue", "PIE-Comment": "Old conclusion", "Solutions": "Not compatible"})
        latest = service.analyzer.InspectorAnalysis("Current issue", [], "", False, [], "Can be used as a substitute.", "CURRENT", "Can be used as a substitute.", "Hi Team,\n\nIt can be used as a substitute.\n\nBest regards,\nPIE Technical Support", "ORIGINAL", "hash")
        with patch.object(service.analyzer, "analyze_case_for_inspector", return_value=latest):
            result = service.reanalyze_prepared_nextop_case(prepared, "Use the available substitute.")
        self.assertTrue(result["success"])
        self.assertEqual(result["prepared"].fields["Solutions"], "Can be used as a substitute.")
        self.assertNotIn("Not compatible", str(result["prepared"].fields))

    def test_issue_ownership_is_human_only_and_schema_validated(self):
        self.assertIsNone(service._issue_owner_for_submit("", False))
        with patch.object(service.feishu_api, "get_select_field_options", return_value=["产品问题", "代理问题"]):
            self.assertEqual(service._issue_owner_for_submit("产品问题", True), "产品问题")
            self.assertFalse(service._issue_owner_for_submit("other", True))

    def test_preview_preserves_existing_protected_values_when_current_is_empty(self):
        prepared = _prepared(existing="rec-existing", kind="legacy")
        prepared.fields.update({"Description": "", "Solutions": "", "PIE-Comment": "", "一级标签": "", "二级标签": ""})
        existing = {"Description": "Existing description", "Solutions": "Existing solution", "PIE-Comment": "Existing guidance", "一级标签": "L1", "二级标签": "L2"}
        with patch.object(service, "refresh_latest_nextop_case", return_value={"success": True, "change_type": "NO_CHANGE", "prepared": prepared}), \
             patch.object(service.feishu_api, "get_record", return_value={"fields": existing}), \
             patch.object(service.feishu_api, "update_record") as update:
            result = service.prepare_commit_preview(prepared)
        self.assertTrue(result["success"])
        self.assertEqual(result["prepared"].fields["Solutions"], "Existing solution")
        self.assertEqual(result["prepared"].fields["Description"], "Existing description")
        update.assert_not_called()

    def test_preview_and_update_prefer_new_valid_solution_over_existing(self):
        prepared = _prepared(existing="rec-existing", kind="legacy")
        prepared.fields.update({"Description": "New description", "Solutions": "New valid solution", "PIE-Comment": "New guidance", "一级标签": "L1", "二级标签": "L2"})
        existing = {"Description": "Existing description", "Solutions": "Existing solution", "PIE-Comment": "Existing guidance", "一级标签": "Old L1", "二级标签": "Old L2", service.ITR_NFF_FIELD: True, service.ITR_ISSUE_OWNER_FIELD: "代理问题"}
        with patch.object(service, "refresh_latest_nextop_case", return_value={"success": True, "change_type": "NO_CHANGE", "prepared": prepared}), \
             patch.object(service.feishu_api, "get_record", side_effect=[{"fields": existing}, {"record_id": "rec-existing", "fields": existing}]), \
             patch.object(service, "build_notes_attachments", return_value=None), \
             patch.object(service.feishu_api, "update_record", return_value={"code": 0}) as update, \
             patch.object(service, "_refresh_case_counts", return_value={"count": None, "warning": False, "reports": []}):
            preview = service.prepare_commit_preview(prepared)
            result = service.commit_prepared_nextop_case(preview["prepared"])
        self.assertTrue(result["success"])
        update_fields = update.call_args.args[1]
        self.assertEqual(update_fields["Solutions"], "New valid solution")
        self.assertEqual(update_fields["Description"], "New description")
        self.assertNotIn(service.ITR_NFF_FIELD, update_fields)
        self.assertNotIn(service.ITR_ISSUE_OWNER_FIELD, update_fields)

    def test_explicit_nff_and_issue_ownership_are_the_only_manual_update_fields(self):
        prepared = _prepared(existing="rec-manual", kind="legacy")
        with patch.object(service, "refresh_latest_nextop_case", return_value={"success": True, "change_type": "NO_CHANGE", "prepared": prepared}), \
             patch.object(service.feishu_api, "get_record", side_effect=[{"fields": {}}, {"record_id": "rec-manual", "fields": {}}]), \
             patch.object(service, "build_notes_attachments", return_value=None), \
             patch.object(service.feishu_api, "get_select_field_options", return_value=["产品问题", "代理问题"]), \
             patch.object(service.feishu_api, "update_record", return_value={"code": 0}) as update, \
             patch.object(service, "_refresh_case_counts", return_value={"count": None, "warning": False, "reports": []}):
            result = service.commit_prepared_nextop_case(prepared, nff_value=True, nff_dirty=True, issue_owner_value="产品问题", issue_owner_dirty=True)
        self.assertTrue(result["success"])
        self.assertTrue(update.call_args.args[1][service.ITR_NFF_FIELD])
        self.assertEqual(update.call_args.args[1][service.ITR_ISSUE_OWNER_FIELD], "产品问题")

    def test_classification_state_is_visible_and_not_written_as_a_field(self):
        fields = service.build_v2_fields("history", {}, tags=("L1", "L2"))
        self.assertEqual(fields["_classification"]["status"], "RESOLVED")
        self.assertNotIn("_classification", service.sanitize_create_fields(fields))

    def test_sync_is_prepare_then_commit_adapter(self):
        prepared = _prepared()
        with patch.object(service, "prepare_nextop_case", return_value={"success": True, "prepared": prepared}) as prepare, \
             patch.object(service, "commit_prepared_nextop_case", return_value={"success": True, "action": "created"}) as commit:
            result = service.sync_nextop("N-1", include_itr_todo=True, todo_dirty=True)
        self.assertTrue(result["success"])
        prepare.assert_called_once_with("N-1", None, duplicate_decision=None, duplicate_record_id=None)
        commit.assert_called_once_with(prepared, None, include_itr_todo=True, todo_dirty=True)

    def test_prepare_then_commit_rechecks_nextop_without_reanalyzing(self):
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
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(analyze.call_count, 1)

    def test_stale_exact_prepared_target_is_not_written(self):
        prepared = _prepared(existing="rec-old", kind="exact")
        with patch.object(service, "refresh_latest_nextop_case", return_value={"success": True, "change_type": "NO_CHANGE"}), \
             patch.object(service.feishu_api, "find_records_by_reference_exact", return_value=[{"record_id": "rec-new", "fields": {}}]), \
             patch.object(service.feishu_api, "update_record") as update:
            result = service.commit_prepared_nextop_case(prepared)
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "prepared_stale")
        update.assert_not_called()

    def test_record_lock_releases_after_update_exception(self):
        prepared = _prepared(existing="rec-lock", kind="legacy")
        with patch.object(service, "refresh_latest_nextop_case", return_value={"success": True, "change_type": "NO_CHANGE"}), \
             patch.object(service.feishu_api, "get_record", return_value={"record_id": "rec-lock", "fields": {}}), \
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

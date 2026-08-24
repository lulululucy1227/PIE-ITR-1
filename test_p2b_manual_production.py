"""Offline contracts for P2B's explicit manual ITR write boundary."""
import sys
import types
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

if "requests" not in sys.modules:
    fake = types.ModuleType("requests")
    fake.exceptions = types.SimpleNamespace(RequestException=Exception)
    sys.modules["requests"] = fake
if "bs4" not in sys.modules:
    fake = types.ModuleType("bs4")
    fake.BeautifulSoup = object
    sys.modules["bs4"] = fake

import case_service
import feishu_api
import real_ticket_validation
from api_adapter import LocalApiAdapter


def draft():
    return case_service.ManualIntakeDraft(
        "temp:manual", "whatsapp", "Luba-VPHDV32K reports Error E123", "raw",
        partner_confirmed="Partner", case_history_append="[Source: whatsapp]\nraw",
        analysis={"description": "Reported error", "solutions": "review", "pie_comment": "summary",
                  "device_name": "LUBA-VPHDV32K", "model_type": "", "support_reply_ids": []},
        tags=("L1", "L2"),
        device_evidence={"device_name": "LUBA-VPHDV32K", "model_resolution": {"model": "luba 2x"}},
    )


class ManualEvidenceTests(unittest.TestCase):
    def test_nff_missing_reply_requests_only_unconfirmed_items(self):
        evidence = {"customer_issue": True, "functional_test": True, "automap_run": True}
        reply, missing = case_service.nff_reply_for_source("email", "REVIEW", evidence)
        self.assertEqual(missing, ["Communication Check PDF report", "Connect Checking screenshot", "latest log or confirmation that the uploaded log is the latest"])
        self.assertIn("Communication Check PDF report", reply)
        self.assertNotIn("Functional Test PDF report", reply)

    def test_nff_complete_and_non_candidate_do_not_request_evidence(self):
        complete = {key: True for key in case_service.NFF_EVIDENCE_LABELS}
        reply, missing = case_service.nff_reply_for_source("whatsapp", "YES", complete)
        self.assertEqual(missing, [])
        self.assertIn("Manual NFF decision", reply)
        normal, missing = case_service.nff_reply_for_source("email", "NO", {})
        self.assertEqual(normal, "")
        self.assertEqual(len(missing), 6)
    def test_device_model_and_luba2x_is_not_serial(self):
        evidence = case_service._manual_evidence("device Luba-VPHDV32K, serial: Luba2X", "", "", "Luba2X")
        self.assertEqual(evidence["device_name"], "LUBA-VPHDV32K")
        self.assertEqual(evidence["model_resolution"]["model"], "luba 2x")
        self.assertEqual(evidence["serial_number"], "")
        self.assertEqual(evidence["serial_status"], "REJECTED_MODEL_FAMILY")

    def test_image_candidate_reaches_case_state_but_model_name_is_not_serial(self):
        evidence = case_service._manual_evidence("no serial here", image_evidence=[{
            "device_candidates": ["Luba-VPHDV32K"], "serial_candidates": ["Luba2X"], "error_codes": ["E123"],
        }])
        self.assertEqual(evidence["device_name"], "LUBA-VPHDV32K")
        self.assertEqual(evidence["model_resolution"]["model"], "luba 2x")
        self.assertTrue(evidence["image_confirmation_required"])
        self.assertIn("LUBA-VPHDV32K", evidence["device_candidates"])
        self.assertEqual(evidence["serial_number"], "")

    @patch("analyzer.config.DEEPSEEK_BASE_URL", "https://company.example")
    @patch("analyzer.config.DEEPSEEK_API_KEY", "test-key")
    @patch("analyzer.requests.post", create=True)
    def test_multimodal_result_keeps_error_code_and_message_separate(self, post):
        post.return_value.raise_for_status.return_value = None
        post.return_value.json.return_value = {"choices": [{"message": {"content": '{"device_identifier":"Luba-VPHDV32K","model_candidate":"LUBA 2 X","serial_number":"Luba2X","error_codes":[],"error_messages":["4G Module Specification Mismatch"],"technical_facts":[{"label":"4G Module","value":"EC200A"},{"label":"SIM Card","value":"Ready"}],"visible_tools":["MamoSuite"],"test_failures":[],"technical_observations":[],"confidence":"medium"}'}}]}
        result = __import__("analyzer").analyze_manual_images([{"id": "img1", "type": "image/png", "data_base64": "YQ=="}])
        self.assertEqual(result[0]["attachment_id"], "img1")
        self.assertEqual(result[0]["device_candidates"], ["Luba-VPHDV32K"])
        self.assertEqual(result[0]["error_codes"], [])
        self.assertEqual(result[0]["error_messages"], ["4G Module Specification Mismatch"])
        self.assertEqual(result[0]["technical_facts"], [{"label":"4G Module","value":"EC200A"},{"label":"SIM Card","value":"Ready"}])
        self.assertNotEqual(result[0]["error_codes"], result[0]["error_messages"])

    def test_image_facts_are_reviewable_and_model_name_is_not_serial(self):
        evidence = case_service._manual_evidence("No device typed by the user", image_evidence=[{
            "device_candidates": ["Luba-VPHDV32K"], "model_candidates": ["LUBA 2 X"],
            "serial_candidates": ["Luba2X"], "error_messages": ["4G Module Specification Mismatch"],
            "technical_facts": [{"label": "4G Module", "value": "EC200A"}, {"label": "SIM", "value": "Ready"}],
        }])
        self.assertEqual(evidence["device_name"], "LUBA-VPHDV32K")
        self.assertIn("LUBA-VPHDV32K", evidence["device_candidates"])
        self.assertEqual(evidence["serial_number"], "")
        self.assertEqual(evidence["technical_facts"][0]["value"], "EC200A")

    def test_manual_reply_statistics_use_sender_and_timestamp_evidence(self):
        messages = case_service.parse_manual_messages(
            "[22/08/2026, 08:20] Partner: Need help\n"
            "[22/08/2026, 08:50] Reggie Luo: Please confirm the module.\n"
            "[24/08/2026, 11:03] PIE Technical Support: Please send the screenshot.\n"
            "[24/08/2026, 11:10] Partner: Attached."
        )
        statistics = case_service._manual_reply_statistics(messages)
        self.assertEqual(statistics["status"], "DERIVED")
        self.assertEqual(statistics["fields"]["Total Replied"], 2)
        self.assertEqual(statistics["fields"]["Replied Time-First"], messages[1]["timestamp_ms"])
        self.assertEqual(statistics["fields"]["Replied Time-NEW"], messages[2]["timestamp_ms"])

    def test_unknown_sender_never_becomes_a_support_reply(self):
        messages = case_service.parse_manual_messages("[22/08/2026, 08:20] Alex: Please restart it.")
        statistics = case_service._manual_reply_statistics(messages)
        self.assertEqual(statistics["status"], "NEEDS_CONFIRMATION")
        self.assertEqual(statistics["fields"], {})

    def test_summary_is_not_promoted_to_pie_guidance(self):
        self.assertEqual(case_service._actionable_manual_guidance("The device is active but the validity date is expired."), "")
        self.assertEqual(case_service._actionable_manual_guidance("Ask the partner to confirm whether the module was replaced."), "Ask the partner to confirm whether the module was replaced.")

    def test_repair_actions_keep_completed_work_only(self):
        source = "We replaced the motor and retested the mower. Please replace the cable. Have you ever replaced the mainboard?"
        actions = case_service._validated_repair_actions(["Motor replaced", "Please replace the cable", "Have you replaced the mainboard?"], source)
        self.assertEqual(actions, ["Motor replaced"])

    def test_negated_repair_history_is_not_converted_to_replacement(self):
        source = "The mainboard has not been changed."
        self.assertEqual(case_service._validated_repair_actions(["Mainboard replaced"], source), [])

    @patch("partner_resolver.load_partner_records_readonly", return_value=[])
    @patch("case_service.analyzer.analyze_manual_images")
    @patch("case_service.analyzer.analyze_case_history")
    @patch("case_service.tag_engine.classify", return_value=("", ""))
    def test_manual_guidance_is_not_promoted_to_verified_solution(self, _classify, analyze, images, _partners):
        analyze.return_value = {"description": "Reported mismatch", "solutions": "Ask partner to verify module.", "pie_comment": ""}
        images.return_value = [{"attachment_id": "img", "status": "ANALYZED", "device_candidates": ["Luba-VPHDV32K"], "model_candidates": [], "serial_candidates": [], "error_codes": [], "error_messages": [], "technical_facts": [], "confidence": "medium"}]
        result = case_service.prepare_manual_intake({"source": "whatsapp", "raw_source_evidence": "image attached", "attachments": [{"id": "img", "type": "image/png", "data_base64": "YQ=="}]})
        self.assertTrue(result["success"])
        self.assertEqual(result["analysis"]["solutions"], "")
        self.assertEqual(result["analysis"]["pie_guidance"], "Ask partner to verify module.")

    def test_source_specific_reply_and_waiting_suppression(self):
        analysis = {"description": "Reported error", "support_reply_ids": []}
        reply, waiting = case_service._manual_reply(analysis, "whatsapp", [{"id": 1}])
        self.assertFalse(waiting); self.assertNotIn("Best regards", reply)
        reply, waiting = case_service._manual_reply({"description": "Reported", "support_reply_ids": [1]}, "email", [{"id": 1}])
        self.assertTrue(waiting); self.assertEqual(reply, "")


class ManualWriteBoundaryTests(unittest.TestCase):

    @patch("case_service.build_v2_fields", return_value={"Description": "Reported", "Case History": "raw"})
    def test_create_preview_keeps_derived_reply_metrics_and_never_writes_unknown_zero(self, _fields):
        item = draft()
        item.analysis["reply_statistics"] = {"status": "DERIVED", "fields": {"Total Replied": 2, "Replied Time-First": 1, "Replied Time-NEW": 2}}
        fields = case_service._manual_create_fields(item)
        self.assertEqual(fields["Total Replied"], 2)
        self.assertEqual(fields["Replied Time-First"], 1)
        self.assertEqual(fields["Replied Time-NEW"], 2)
        item.analysis["reply_statistics"] = {"status": "NEEDS_CONFIRMATION", "fields": {}}
        _fields.return_value = {"Description": "Reported", "Case History": "raw"}
        self.assertNotIn("Total Replied", case_service._manual_create_fields(item))

    @patch("case_service.build_v2_fields", return_value={"Description": "Reported", "Solutions": "", "Status": "", "Ticket Created Time": "", "Total Replied": "", "Case History": "raw"})
    def test_manual_preview_omits_empty_system_fields_and_unknown_issue_owner(self, _fields):
        fields = case_service._manual_create_fields(draft(), issue_owner="")
        self.assertNotIn("Status", fields)
        self.assertNotIn("Ticket Created Time", fields)
        self.assertNotIn("Total Replied", fields)
        self.assertNotIn("问题归属", fields)
        self.assertNotIn("Solutions", fields)

    @patch("case_service.build_v2_fields", return_value={"Description": "Reported", "Solutions": "review", "一级标签": "L1", "二级标签": "L2", "Case History": "raw"})
    @patch("case_service.feishu_api.get_record")
    @patch("case_service.feishu_api.create_record")
    def test_new_create_reads_back_native_ticket_once(self, create, get_record, _fields):
        create.return_value = {"code": 0, "data": {"record": {"record_id": "rec-new"}}}
        get_record.return_value = {"fields": {"Ticket No.": "ITR-0824-0001"}}
        result = case_service.create_manual_itr(draft())
        self.assertTrue(result["success"])
        self.assertEqual(result["ticket_no"], "ITR-0824-0001")
        self.assertEqual(create.call_count, 1)

    @patch("case_service.build_v2_fields", return_value={"Description": "Reported", "Case History": "raw"})
    @patch("case_service.feishu_api.get_record", return_value={"fields": {}})
    @patch("case_service.feishu_api.create_record", return_value={"code": 0, "data": {"record": {"record_id": "rec-new"}}})
    def test_readback_failure_never_creates_a_duplicate(self, create, _record, _fields):
        result = case_service.create_manual_itr(draft())
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "readback_failed")
        self.assertEqual(create.call_count, 1)

    @patch("case_service.build_v2_fields", return_value={"Description": "Reported", "Case History": "raw"})
    @patch("case_service.feishu_api.upload_attachment", side_effect=RuntimeError("upload"))
    @patch("case_service.feishu_api.get_record", return_value={"fields": {"Ticket No.": "ITR-0824-0001", "Notes": []}})
    @patch("case_service.feishu_api.create_record", return_value={"code": 0, "data": {"record": {"record_id": "rec-new"}}})
    def test_attachment_failure_after_create_does_not_duplicate(self, create, _record, _upload, _fields):
        result = case_service.create_manual_itr(draft(), [{"name": "a.png", "data_base64": "YQ=="}])
        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "attachment_partial")
        self.assertEqual(create.call_count, 1)

    @patch("case_service.feishu_api.update_record", return_value={"code": 0})
    @patch("case_service.feishu_api.get_record")
    @patch("case_service.open_existing_case")
    def test_append_writes_only_history_and_preserves_total_replied(self, existing, get_record, update):
        existing.return_value = {"success": True, "record_id": "rec-old", "case": {"ticket_no": "ITR-0824-1000", "total_replied": 7}}
        get_record.return_value = {"fields": {"Case History": "old", "Solutions": "keep", "一级标签": "L1", "二级标签": "L2", "PIE-Comment": "keep", "Total Replied": 7, "Notes": []}}
        result = case_service.append_manual_itr("ITR-0824-1000", draft())
        self.assertTrue(result["success"])
        self.assertEqual(update.call_args.args[1], {"Case History": "old\n\n[Source: whatsapp]\nraw"})

    @patch("case_service.open_existing_case", side_effect=__import__("feishu_api").FeishuAuthRequired("x"))
    def test_adapter_maps_append_read_error_without_generic_500(self, _existing):
        result = LocalApiAdapter().manual_append_preview({"ticket_no": "ITR-1", "draft": {"draft_key": "temp:a", "source": "whatsapp", "raw_source_evidence": "raw", "normalized_analysis_input": "raw"}})
        self.assertEqual(result["error_type"], "AUTH_EXPIRED")


class AutoNumberLookupTests(unittest.TestCase):
    @patch("feishu_api._request")
    def test_ticket_number_uses_paginated_client_exact_match_not_invalid_filter(self, request):
        request.side_effect = [
            {"code": 0, "data": {"items": [{"record_id": "rec-other", "fields": {"Ticket No.": "ITR-0001"}}], "has_more": True, "page_token": "next"}},
            {"code": 0, "data": {"items": [{"record_id": "rec-target", "fields": {"Ticket No.": "ITR-0818-2001"}}], "has_more": False}},
        ]
        rows = feishu_api.find_records_by_ticket_no_exact("itr-0818-2001", ["Solutions"])
        self.assertEqual([row["record_id"] for row in rows], ["rec-target"])
        self.assertNotIn("filter", request.call_args_list[0].kwargs["json"])
        self.assertEqual(request.call_args_list[1].kwargs["params"]["page_token"], "next")

    def test_read_error_classification_is_safe(self):
        self.assertEqual(feishu_api.classify_read_error(feishu_api.FeishuAuthRequired("x")), "AUTH_EXPIRED")
        self.assertEqual(feishu_api.classify_read_error(feishu_api.FeishuReadError(None, "Permission denied")), "PERMISSION_DENIED")


class RealValidationOutputTests(unittest.TestCase):
    @patch("real_ticket_validation.validate", return_value={"Ticket": "E000001", "Validation": "PASS"})
    @patch.object(sys, "argv", ["real_ticket_validation.py", "E000001"])
    def test_validation_script_emits_one_redacted_json_line(self, _validate):
        output = StringIO()
        with redirect_stdout(output):
            real_ticket_validation.main()
        payload = __import__("json").loads(output.getvalue())
        self.assertEqual(payload["external_writes"], "NO")
        self.assertEqual(payload["tickets"][0]["Validation"], "PASS")

    def test_validation_read_wrapper_sets_one_bounded_attempt(self):
        seen = {}
        def original(_method, _path, **kwargs):
            seen.update(kwargs)
            return {"code": 0}
        real_ticket_validation._bounded_read_request(original)("GET", "/x")
        self.assertEqual(seen["max_attempts"], 1)
        self.assertEqual(seen["timeout"], (6, 12))

    def test_validation_deadline_returns_value_and_times_out_safely(self):
        self.assertEqual(real_ticket_validation._read_with_deadline(lambda: "ok", 0.1), "ok")
        with self.assertRaises(TimeoutError):
            real_ticket_validation._read_with_deadline(lambda: __import__("time").sleep(0.05), 0.001)

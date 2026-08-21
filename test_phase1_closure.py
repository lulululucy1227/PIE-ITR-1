"""Offline Phase 1 closure checks: no network and no production writes."""
import sys
import types
import unittest
from unittest.mock import patch

if "requests" not in sys.modules:
    fake = types.ModuleType("requests")
    fake.exceptions = types.SimpleNamespace(RequestException=Exception)
    sys.modules["requests"] = fake
if "bs4" not in sys.modules:
    fake = types.ModuleType("bs4"); fake.BeautifulSoup = object; sys.modules["bs4"] = fake

import analyzer
import context_service
import product_capabilities
import case_service
import feishu_api
import nextop_api


def result(**extra):
    value = {
        "customer_description": "Issue reported.", "repair_actions": [], "current_blocker": "",
        "blocker_is_inferred": False, "historical_pie_recommendations": [],
        "ai_suggested_next_step": "Review the supplied symptom.", "solution_state": "PENDING",
        "solution": "Awaiting confirmation.", "reply_en": "Hi Team,\n\nPlease confirm the symptom.\n\nBest regards,\nPIE Technical Support",
        "information_status": "sufficient", "missing_information": [], "reason_for_request": [], "next_action": "assess",
    }
    value.update(extra)
    return value


class PhaseOneContractTests(unittest.TestCase):
    def inspect(self, output, model="LUBA 3", context=None):
        with patch.object(analyzer, "_call_deepseek", return_value=output):
            return analyzer.analyze_case_for_inspector({"model_type": model, "description": "Reported issue", "context_pack": context or {}})

    def test_feishu_table_discovery_and_schema_reads_are_read_only(self):
        with patch.object(feishu_api, "_request", side_effect=[
            {"code": 0, "data": {"items": [{"table_id": "tbl-partner", "name": "Partner codes"}]}},
            {"code": 0, "data": {"items": [{"field_name": "Email Domain"}]}},
        ]) as request:
            self.assertEqual(feishu_api.list_tables_readonly()[0]["table_id"], "tbl-partner")
            self.assertEqual(feishu_api.get_table_fields_metadata_readonly("tbl-partner")[0]["field_name"], "Email Domain")
        self.assertEqual([call.args[0] for call in request.call_args_list], ["GET", "GET"])

    def test_insufficient_has_explicit_state_and_reply_only_requests_missing_items(self):
        value = self.inspect(result(information_status="insufficient", missing_information=["SN", "firmware version"], reason_for_request=["to identify the device"], reply_en="Replace mainboard"))
        self.assertEqual(value.information_status, "insufficient")
        self.assertEqual(value.next_action, "request_information")
        self.assertEqual(value.solution_state, "PENDING")
        self.assertEqual(value.solution, "")
        self.assertIn("SN", value.reply_en); self.assertIn("firmware version", value.reply_en)
        self.assertNotIn("Replace mainboard", value.reply_en)

    def test_reply_without_analysis_is_forced_to_insufficient(self):
        value = self.inspect(result(ai_suggested_next_step="", solution="", reply_en="Replace the mainboard."))
        self.assertEqual(value.information_status, "insufficient")
        self.assertNotIn("Replace the mainboard", value.reply_en)

    def test_production_analyze_route_keeps_customer_original_and_translates_internal_fields(self):
        english = result(customer_description="Original English issue", repair_actions=["Replaced the driver board."], current_blocker="Waiting for confirmation.", historical_pie_recommendations=[], ai_suggested_next_step="Request required information.", solution="Replace mainboard.")
        chinese = {"repair_actions":["已更换驱动板。"],"current_blocker":"等待确认。","historical_pie_recommendations":[],"ai_suggested_next_step":"请求必要信息。","solution":"更换主板。","missing_information":[],"reason_for_request":[]}
        with patch.object(analyzer, "_call_deepseek", side_effect=[english, chinese]):
            value=analyzer.analyze_case_for_inspector({"model_type":"LUBA 3","description":"Original English issue","context_pack":{}})
        self.assertEqual(value.customer_description,"Original English issue")
        self.assertEqual(value.repair_actions,["已更换驱动板。"])
        self.assertEqual(value.ai_suggested_next_step,"请求必要信息。")
        self.assertIn("Hi Team",value.reply_en)

    def test_human_guidance_is_context_not_a_confirmed_fact(self):
        calls=[]
        def reply(_system, content):
            calls.append(content)
            return result(confirmed_facts=[], reply_en="Hi Team,\n\nPlease reseat the vision module connector.\n\nBest regards,\nPIE Technical Support")
        with patch.object(analyzer, "_call_deepseek", side_effect=reply):
            value=analyzer.analyze_case_for_inspector({"model_type":"YUKA","description":"Vision issue", "human_guidance":"重新插拔视觉模组线束", "context_pack":{}})
        self.assertIn("重新插拔视觉模组线束", calls[0])
        self.assertEqual(value.confirmed_facts, [])
        self.assertIn("Hi Team", value.reply_en)

    def test_diagnostic_path_can_remain_actionable_without_confirmed_solution(self):
        diagnostic = result(
            current_blocker="", solution_state="PENDING", solution="",
            ai_suggested_next_step="使用已知正常的驱动板完成对比测试。",
            resolution_path=["检查 App 中的准确错误码。", "由代理使用已知正常的驱动板测试。"],
            hypotheses=[{"cause":"驱动板或切割电机之一可能异常", "confidence":"low", "evidence":["已报告的症状"], "cited":["current_ticket"], "discriminator":"已知正常驱动板的对比结果"}],
            reply_en="Hi Team,\n\nPlease check the exact App error code and perform the known-good drive-board comparison.\n\nBest regards,\nPIE Technical Support",
        )
        value = self.inspect(diagnostic, "LUBA mini 2", {"follow_up":{"already_tried":["Blade disc and bracket checked."]}})
        self.assertEqual(value.solution, "")
        self.assertEqual(value.information_status, "sufficient")
        self.assertTrue(value.resolution_path)
        self.assertIn("known-good", value.reply_en)

    def test_missing_reply_is_explicit_error_not_ready_blank(self):
        value = self.inspect(result(reply_en=""))
        self.assertIn("Reply generation error", value.reply_generation_error)

    def test_non_english_reply_gets_one_bounded_repair_without_losing_analysis(self):
        initial = result(reply_en="请确认 LUBA 3 的 Error 1207。", solution="Awaiting confirmation.")
        repaired = {"reply_en": "Hi Team,\n\nPlease confirm Error 1207 on the LUBA 3.\n\nBest regards,\nPIE Technical Support"}
        translated = {"repair_actions":[],"current_blocker":"","historical_pie_recommendations":[],"ai_suggested_next_step":"请确认信息。","solution":"等待确认。","missing_information":[],"reason_for_request":[]}
        with patch.object(analyzer, "_call_deepseek", side_effect=[initial, repaired, translated]) as call:
            value = analyzer.analyze_case_for_inspector({"model_type":"LUBA 3", "description":"Reported issue", "human_guidance":"请协助确认。", "context_pack":{}})
        self.assertEqual(call.call_count, 3)
        self.assertIn("Error 1207", value.reply_en)
        self.assertTrue(analyzer.reply_is_english(value.reply_en))
        self.assertEqual(value.solution_state, "PENDING")
        self.assertEqual(value.reply_generation_error, "")

    def test_luba1_log_requests_are_removed_from_every_output(self):
        value = self.inspect(result(information_status="sufficient", missing_information=["Upload logs"], reason_for_request=["Run LogiQ"], ai_suggested_next_step="Export device logs", solution="Use LogiQ", reply_en="Please upload device logs."), "LUBA 1")
        self.assertEqual(value.capability, {"device_log":"unsupported", "logiq":"unsupported"})
        self.assertEqual(value.information_status, "insufficient")
        joined = " ".join(value.missing_information + value.reason_for_request + [value.ai_suggested_next_step, value.solution, value.reply_en]).lower()
        self.assertNotIn("logiq", joined); self.assertNotIn("log", joined)

    def test_unknown_product_never_allows_log_request(self):
        value = self.inspect(result(ai_suggested_next_step="Upload device logs", solution="", reply_en="Please upload logs."), "Unlisted Model")
        self.assertEqual(value.capability["device_log"], "unknown")
        self.assertEqual(value.information_status, "insufficient")
        self.assertNotIn("log", value.reply_en.lower())

    def test_followup_failed_connector_check_is_not_repeated(self):
        context = {"follow_up":{"failed_actions":["Connector checked, issue remains."]}}
        value = self.inspect(result(ai_suggested_next_step="Check the connector.", solution="Check connector again.", reply_en="Please check the connector."), context=context)
        self.assertEqual(value.information_status, "insufficient")
        self.assertNotIn("connector", value.reply_en.lower())

    @patch("context_service.feishu_api.get_table_records_readonly")
    @patch("context_service.feishu_api.find_records_by_reference_exact", return_value=[])
    def test_no_match_is_valid_read_only_context(self, finder, reader):
        reader.return_value = []
        pack = context_service.build_context("E100", {"Description":"new issue"}, [], "new issue")
        self.assertEqual(pack["knowledge_coverage"], "none")
        self.assertEqual(pack["historical_itr"]["matches"], [])
        self.assertEqual(pack["approved_kb"]["match_status"], "none")
        finder.assert_called_once(); self.assertEqual(reader.call_count, 2)

    @patch("context_service.feishu_api.get_table_records_readonly")
    @patch("context_service.feishu_api.find_records_by_reference_exact", return_value=[])
    def test_exact_error_and_technical_information_keep_provenance(self, finder, reader):
        reader.side_effect = [[{"record_id":"error-1","fields":{"错误代码":"1207"}}], [{"record_id":"note-1","fields":{"Title":"1207 connector guidance"}}]]
        pack = context_service.build_context("E101", {"Description":"Error 1207"}, [], "Error 1207 connector")
        self.assertEqual(pack["error_codes"]["exact_matches"][0]["record_id"], "error-1")
        self.assertEqual(pack["technical_notes"]["matches"][0]["record_id"], "note-1")
        self.assertEqual(pack["approved_kb"]["excluded_reason"], "unreviewed")

    @patch("context_service.feishu_api.get_table_records_readonly", return_value=[])
    @patch("context_service.feishu_api.find_records_by_reference_exact", return_value=[])
    def test_followup_tracks_already_tried_and_failed_actions(self, *_):
        pack = context_service.build_context("E102", {}, [{"content":"Please check the connector."},{"content":"Connector checked, issue remains."}], "")
        self.assertTrue(pack["follow_up"]["is_follow_up"])
        self.assertTrue(pack["follow_up"]["already_tried"])
        self.assertTrue(pack["follow_up"]["failed_actions"])

    def test_capability_registry_never_defaults_to_supported(self):
        self.assertEqual(product_capabilities.capabilities("LUBA 1")["logiq"], "unsupported")
        self.assertEqual(product_capabilities.capabilities("unknown")["logiq"], "unknown")
        self.assertFalse(product_capabilities.may_request_logs("unknown"))

    def test_read_only_paths_do_not_call_write_methods(self):
        with patch.object(case_service.feishu_api, "create_record") as create, patch.object(case_service.feishu_api, "update_record") as update, patch.object(analyzer, "_call_deepseek", return_value=result()):
            analyzer.analyze_case_for_inspector({"model_type":"LUBA 3", "description":"x", "context_pack":{}})
        create.assert_not_called(); update.assert_not_called()

    def test_empty_local_credentials_fail_before_external_requests(self):
        with patch.object(feishu_api.config, "FEISHU_USER_ACCESS_TOKEN", ""), patch.object(feishu_api.requests, "request", create=True) as request:
            with self.assertRaises(feishu_api.FeishuAuthRequired):
                feishu_api._request("GET", "/open-apis/bitable/v1/apps/example")
        request.assert_not_called()
        with patch.object(nextop_api.config, "NEXTOP_AUTH", ""), patch.object(nextop_api.config, "NEXTOP_COOKIE", ""), patch.object(nextop_api.config, "NEXTOP_SATOKEN", ""):
            with self.assertRaises(nextop_api.NextopAuthRequired):
                nextop_api._headers()
        with patch.object(analyzer.config, "DEEPSEEK_API_KEY", ""), patch.object(analyzer.config, "DEEPSEEK_BASE_URL", ""), patch.object(analyzer.requests, "post", create=True) as post:
            with self.assertRaisesRegex(RuntimeError, "credentials are not configured"):
                analyzer._call_deepseek("system", "input")
        post.assert_not_called()

    def test_prepare_errors_are_stage_specific_and_never_masquerade_as_auth(self):
        ticket = {"messages": [], "list_info": {"createTime": "2026-01-01", "outerName": "", "outerAddress": "", "title": ""}}
        common = {
            "open_existing_case": {"match_status": "NOT_FOUND"},
            "build_nextop_case_history": "history",
            "analyze_case_history": {},
            "build_v2_fields": {},
            "_nextop_reply_fields": {"Status": ""},
        }
        scenarios = {
            "duplicate_lookup": ("open_existing_case", RuntimeError("lookup"), "FEISHU_LOOKUP_ERROR"),
            "nextop_fetch": ("get_ticket_full", RuntimeError("response"), "NEXTOP_REQUEST_ERROR"),
            "analyze": ("analyze_case_history", RuntimeError("analysis"), "ANALYZE_ERROR"),
            "context_build": ("build_context", RuntimeError("context"), "CONTEXT_BUILD_ERROR"),
        }
        for stage, (target, failure, code) in scenarios.items():
            with self.subTest(stage=stage):
                with patch.object(case_service, "open_existing_case", return_value=common["open_existing_case"]), \
                     patch.object(case_service, "build_nextop_case_history", return_value=common["build_nextop_case_history"]), \
                     patch.object(case_service.nextop_api, "get_ticket_full", return_value=ticket), \
                     patch.object(case_service.analyzer, "analyze_case_history", return_value=common["analyze_case_history"]), \
                     patch.object(case_service, "build_v2_fields", return_value=common["build_v2_fields"]), \
                     patch.object(case_service, "_nextop_reply_fields", return_value=common["_nextop_reply_fields"]), \
                     patch.object(case_service, "find_nextop_legacy_duplicates", return_value=[]), \
                     patch("context_service.build_context", return_value={}):
                    if target == "build_context":
                        context_patch = patch("context_service.build_context", side_effect=failure)
                    elif target == "get_ticket_full":
                        context_patch = patch.object(case_service.nextop_api, target, side_effect=failure)
                    elif target == "analyze_case_history":
                        context_patch = patch.object(case_service.analyzer, target, side_effect=failure)
                    else:
                        context_patch = patch.object(case_service, target, side_effect=failure)
                    with context_patch:
                        value = case_service.prepare_nextop_case("SAFE-STAGE")
                self.assertEqual(value["stage"], stage)
                self.assertEqual(value["error_type"], code)
                self.assertEqual(value["ticket_no"], "SAFE-STAGE")
                self.assertNotIn("AUTH", value["error_type"])

    def test_missing_feishu_read_configuration_is_explicit(self):
        with patch.object(case_service, "open_existing_case", side_effect=feishu_api.FeishuAuthRequired("missing")):
            value = case_service.prepare_nextop_case("SAFE-FEISHU")
        self.assertFalse(value["success"])
        self.assertEqual(value["error_type"], "FEISHU_CREDENTIALS_MISSING")
        self.assertEqual(value["stage"], "duplicate_lookup")

    def test_feishu_lookup_failure_keeps_only_safe_code(self):
        error = feishu_api.FeishuReadError(1234, "request value='customer@example.com'")
        with patch.object(case_service, "open_existing_case", side_effect=error):
            value = case_service.prepare_nextop_case("SAFE-FEISHU")
        self.assertEqual(value["error_type"], "FEISHU_LOOKUP_ERROR")
        self.assertEqual(value["detail"], "Feishu code: 1234")
        self.assertNotIn("customer@example.com", str(value))


if __name__ == "__main__":
    unittest.main()

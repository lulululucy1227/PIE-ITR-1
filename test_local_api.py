"""Offline safety tests for the thin local API adapter."""
import sys
import types
import unittest
from unittest.mock import patch

if "requests" not in sys.modules:
    fake = types.ModuleType("requests"); fake.exceptions = types.SimpleNamespace(RequestException=Exception); sys.modules["requests"] = fake
if "bs4" not in sys.modules:
    fake = types.ModuleType("bs4"); fake.BeautifulSoup = object; sys.modules["bs4"] = fake

import api_adapter
import case_service as service


class LocalApiTests(unittest.TestCase):
    def test_health_and_prepare_are_adapter_only(self):
        adapter = api_adapter.LocalApiAdapter()
        self.assertTrue(adapter.health()["ok"])
        with patch.object(service, "prepare_nextop_case", return_value={"success": True, "prepared": None}) as prepare:
            result = adapter.prepare({"source": "nextop", "ticket_no": "E1"})
        self.assertTrue(result["success"]); prepare.assert_called_once_with("E1")

    def test_analyze_and_translate_never_commit(self):
        adapter = api_adapter.LocalApiAdapter()
        prepared = {"ticket_no": "T", "case_history": "history", "fields": {}, "analysis": {}, "messages": [], "list_info": {}}
        analysis = {"success": True, "prepared": prepared, "analysis": {"source_hash": "h", "reply_en": "Hello"}}
        with patch.object(service, "reanalyze_prepared_nextop_case", return_value=analysis) as analyze, \
             patch.object(service, "commit_prepared_nextop_case") as commit:
            self.assertEqual(adapter.analyze({"prepared": prepared})["analysis"]["reply_en"], "Hello")
        analyze.assert_called_once(); commit.assert_not_called()

    def test_commit_is_only_write_route(self):
        adapter = api_adapter.LocalApiAdapter()
        payload = {"prepared": {"ticket_no": "E1", "case_history": "h", "fields": {}, "analysis": {}, "messages": [], "list_info": {}}}
        with patch.object(service, "commit_prepared_nextop_case", return_value={"success": True}) as commit:
            self.assertTrue(adapter.commit(payload)["success"])
        commit.assert_called_once()

    def test_commit_forwards_only_explicit_nff_and_issue_ownership(self):
        adapter = api_adapter.LocalApiAdapter()
        payload = {"prepared": {"ticket_no": "E-SYN", "case_history": "h", "fields": {}, "analysis": {}, "messages": [], "list_info": {}}, "nff_value": True, "nff_dirty": True, "issue_owner_value": "产品问题", "issue_owner_dirty": True}
        with patch.object(service, "commit_prepared_nextop_case", return_value={"success": True}) as commit:
            adapter.commit(payload)
        self.assertTrue(commit.call_args.kwargs["nff_value"])
        self.assertTrue(commit.call_args.kwargs["nff_dirty"])
        self.assertEqual(commit.call_args.kwargs["issue_owner_value"], "产品问题")
        self.assertTrue(commit.call_args.kwargs["issue_owner_dirty"])

    def test_unexpected_prepare_failure_has_safe_stage_diagnostic(self):
        adapter = api_adapter.LocalApiAdapter()
        with patch.object(service, "prepare_nextop_case", side_effect=RuntimeError("cookie=private-value")):
            result = adapter.prepare({"source": "nextop", "ticket_no": "E264714"})
        self.assertFalse(result["success"])
        self.assertEqual(result["stage"], "local_api_prepare")
        self.assertEqual(result["error_type"], "NEXTOP_RESPONSE_ERROR")
        self.assertEqual(result["detail"], "RuntimeError")
        self.assertNotIn("private-value", str(result))

    def test_translation_route_returns_safe_success_or_failure(self):
        adapter = api_adapter.LocalApiAdapter()
        with patch.object(service, "translate_text_to_zh", return_value="中文") as translate:
            self.assertEqual(adapter.translate_text({"text": "Hello"}), {"success": True, "text": "中文"})
        translate.assert_called_once_with("Hello")
        with patch.object(service, "translate_text_to_zh", side_effect=RuntimeError("secret")):
            result = adapter.translate_text({"text": "Hello"})
        self.assertEqual(result["error_type"], "TRANSLATION_ERROR")
        self.assertNotIn("secret", str(result))


if __name__ == "__main__": unittest.main()

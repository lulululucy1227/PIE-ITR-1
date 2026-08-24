import unittest
import sys
import types
from unittest.mock import patch

if "requests" not in sys.modules:
    fake = types.ModuleType("requests")
    fake.exceptions = types.SimpleNamespace(RequestException=Exception)
    sys.modules["requests"] = fake
if "bs4" not in sys.modules:
    fake = types.ModuleType("bs4"); fake.BeautifulSoup = object; sys.modules["bs4"] = fake

import case_service
import partner_resolver


RECORDS = [
    {"fields": {"Disti": "Alpha", "Code": "A", "Country": "Denmark", "Marks": "Alice; alice@example.dk; +45 12 34 56 78; alpha.dk"}},
    {"fields": {"Disti": "Beta", "Code": "B", "Country": "Germany", "Marks": "Bob; bob@example.de; +49 160 1234567"}},
]


class PartnerResolverTests(unittest.TestCase):
    def test_exact_marks_and_normalization(self):
        self.assertEqual(partner_resolver.resolve_partner(RECORDS, contact=" ALICE@example.DK ")["partner"], "Alpha")
        self.assertEqual(partner_resolver.resolve_partner(RECORDS, contact="+4512345678")["partner"], "Alpha")
        self.assertEqual(partner_resolver.resolve_partner(RECORDS, contact="https://alpha.dk/path")["partner"], "Alpha")
        self.assertEqual(partner_resolver.resolve_partner(RECORDS, contact="lice@example.dk")["status"], "UNKNOWN")
        self.assertEqual(partner_resolver.resolve_partner(RECORDS, contact="12345678")["status"], "UNKNOWN")

    def test_conflict_and_country_do_not_select_partner(self):
        records = RECORDS + [{"fields": {"Disti": "Other", "Marks": "alice@example.dk"}}]
        self.assertEqual(partner_resolver.resolve_partner(records, contact="alice@example.dk")["status"], "CONFLICT")
        self.assertEqual(partner_resolver.resolve_partner(RECORDS, contact="unknown@example.dk")["country"], "Denmark")
        self.assertEqual(partner_resolver.resolve_partner(RECORDS, contact="unknown@example.dk")["status"], "UNKNOWN")
        self.assertEqual(partner_resolver.infer_country_from_contact("person@example.com"), "")
        for suffix in ("dk", "de", "pl", "cz", "hu", "si", "me", "ee"):
            self.assertTrue(partner_resolver.infer_country_from_contact(f"x@example.{suffix}"))


class ManualIntakeTests(unittest.TestCase):
    def analysis(self, history, manual_messages=None):
        return {"device_name": "", "disti_dealer": "", "model_type": "", "pie_comment": "summary", "description": "issue", "solutions": "proposal", "fault_symptom": [], "error_code": [], "error_massages": "", "support_reply_ids": []}

    @patch("case_service.tag_engine.classify", return_value=("", ""))
    @patch("case_service.analyzer.analyze_case_history")
    @patch("partner_resolver.load_partner_records_readonly", return_value=RECORDS)
    def test_sources_preserve_raw_evidence_and_explicit_override(self, _records, analyze, _tags):
        analyze.side_effect = self.analysis
        for source in ("whatsapp", "lark", "email"):
            result = case_service.prepare_manual_intake({"draft_key": f"temp:{source}", "source": source, "raw_source_evidence": "Alice: Original evidence", "contact": "alice@example.dk", "partner_confirmed": "Manual Partner", "device": "LUBA-MB-1", "serial_number": "SN-1"})
            self.assertTrue(result["success"])
            draft = result["draft"]
            self.assertEqual(draft.draft_key, f"temp:{source}")
            self.assertEqual(draft.raw_source_evidence, "Alice: Original evidence")
            self.assertIn("[Source:", draft.case_history_append)
            self.assertEqual(draft.partner_candidate["partner"], "Manual Partner")
            self.assertEqual(draft.analysis["device_name"], "LUBA-MB-1")
            self.assertNotIn("Source timestamp:", draft.case_history_append)

    @patch("case_service.feishu_api.get_record")
    @patch("case_service.open_existing_case")
    def test_append_preview_preserves_protected_values(self, existing, get_record):
        existing.return_value = {"success": True, "record_id": "rec1", "case": {"ticket_no": "ITR-0101-01"}}
        get_record.return_value = {"fields": {"Case History": "old", "Solutions": "keep", "一级标签": "L1", "二级标签": "L2", "PIE-Comment": "keep comment"}}
        draft = case_service.ManualIntakeDraft("temp:a", "whatsapp", "raw", "raw", case_history_append="[Source: whatsapp]\nraw", analysis={"solutions": "replace", "pie_comment": "replace"})
        result = case_service.prepare_manual_append_preview("ITR-0101-01", draft)
        self.assertTrue(result["success"])
        actions = {item["field"]: item for item in result["actions"]}
        self.assertEqual(actions["Case History"]["action"], "APPEND")
        self.assertEqual(actions["Solutions"]["action"], "PRESERVE")
        self.assertEqual(actions["一级标签"]["action"], "PRESERVE")
        self.assertFalse(result["production_write_enabled"])

"""Offline normalization regression; intake has no network or write dependencies."""
import unittest
from intake import normalize_case

class MultiSourceTests(unittest.TestCase):
    def test_whatsapp_new_followup_and_already_tried(self):
        value=normalize_case("whatsapp","Customer: Unit stops.\nPIE: Check connector.\nCustomer: Connector checked, still not working.")
        self.assertEqual([x["role"] for x in value.normalized_messages],["customer","support","customer"]); self.assertIn("still not working",value.current_message)
    def test_lark_clear_and_ambiguous_roles(self):
        clear=normalize_case("lark","PIE: Please provide SN.\nDealer: SN is ABC."); ambiguous=normalize_case("lark","Issue continues without a speaker.")
        self.assertFalse(clear.needs_human_check); self.assertTrue(ambiguous.needs_human_check)
    def test_email_current_message_and_quoted_history(self):
        value=normalize_case("email","Subject: Issue\nFrom: dealer@example.test\nCurrent symptom persists.\nOn Monday wrote:\nPrevious guidance")
        self.assertIn("Current symptom",value.current_message); self.assertEqual(value.quoted_history,"Previous guidance"); self.assertFalse(value.needs_human_check)
    def test_non_nextop_has_no_fake_reference(self):
        value=normalize_case("whatsapp","Customer: Need help.")
        self.assertEqual(value.source_reference,""); self.assertEqual(value.source_type,"whatsapp")

if __name__=="__main__": unittest.main()

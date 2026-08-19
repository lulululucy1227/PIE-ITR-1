"""Synthetic, offline Golden contract checks for Phase 1.5A."""
import json, sys, types, unittest
from pathlib import Path
from unittest.mock import patch
if "requests" not in sys.modules:
    fake=types.ModuleType("requests"); fake.exceptions=types.SimpleNamespace(RequestException=Exception); sys.modules["requests"]=fake
if "bs4" not in sys.modules:
    fake=types.ModuleType("bs4"); fake.BeautifulSoup=object; sys.modules["bs4"]=fake
import analyzer
from analysis_validators import validate

def output(**extra):
    value={"customer_description":"Synthetic symptom.","repair_actions":[],"current_blocker":"","blocker_is_inferred":False,"historical_pie_recommendations":[],"ai_suggested_next_step":"Review supplied symptom.","solution_state":"PENDING","solution":"Awaiting confirmation.","reply_en":"Hi Team,\n\nPlease confirm the symptom.\n\nBest regards,\nPIE Technical Support","information_status":"sufficient","missing_information":[],"reason_for_request":[],"next_action":"assess"}; value.update(extra); return value

class GoldenContractTests(unittest.TestCase):
    def inspect(self, result, model="LUBA 3", context=None):
        with patch.object(analyzer,"_call_deepseek",return_value=result): return analyzer.analyze_case_for_inspector({"model_type":model,"description":"Synthetic symptom","context_pack":context or {}})
    def test_fixture_catalog_has_required_offline_cases(self):
        rows=json.loads(Path("tests/golden/fixtures/phase15_cases.json").read_text(encoding="utf-8")); ids={x["case_id"] for x in rows}
        self.assertEqual(len(ids),17); self.assertIn("READ_ONLY_ANALYZE_NO_WRITE",ids); self.assertIn("INVALID_CITATION_REMOVED",ids)
    def test_capability_and_insufficient_reply_invariants(self):
        value=self.inspect(output(missing_information=["upload logs"],reason_for_request=["Run LogiQ"],ai_suggested_next_step="export logs",solution="Use LogiQ",reply_en="Upload device logs."),"LUBA 1")
        joined=" ".join(value.missing_information+value.reason_for_request+[value.ai_suggested_next_step,value.solution,value.reply_en]).lower(); self.assertEqual(value.information_status,"insufficient"); self.assertNotIn("log",joined); self.assertNotIn("logiq",joined)
        unknown=self.inspect(output(ai_suggested_next_step="Upload logs",solution="",reply_en="Upload logs."),"Synthetic Unknown"); self.assertEqual(unknown.capability["logiq"],"unknown"); self.assertEqual(unknown.information_status,"insufficient")
    def test_evidence_citations_and_high_risk_are_deterministic(self):
        context={"historical_itr":{"matches":[{"record_id":"itr-1"}]},"technical_notes":{"matches":[{"record_id":"note-1"}]},"error_codes":{"exact_matches":[{"record_id":"error-1"}]}}
        value=validate({"confirmed_facts":["customer reported error"],"hypotheses":[{"cause":"x","confidence":"high","cited":["itr-1","invented"],"evidence":["history"]}],"reply_en":"We promise a replacement."},context,{"logiq":"supported"},False)
        self.assertEqual(value["hypotheses"][0]["cited"],["itr-1"]); self.assertTrue(value["needs_human_check"]); self.assertTrue(value["escalation"]); self.assertNotIn("history",value["confirmed_facts"])
    def test_failed_action_and_read_only_analysis_contract(self):
        context={"follow_up":{"already_tried":["Connector checked; still not working."],"failed_actions":["Connector checked; still not working."]}}
        value=self.inspect(output(ai_suggested_next_step="Check the connector.",solution="Check connector again.",reply_en="Check connector."),context=context)
        self.assertEqual(value.information_status,"insufficient"); self.assertIn("Connector checked",value.already_tried[0]); self.assertNotIn("connector",value.reply_en.lower())

if __name__=="__main__": unittest.main()

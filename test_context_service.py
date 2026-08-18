import unittest, sys, types
from unittest.mock import patch
if "requests" not in sys.modules:
 fake=types.ModuleType("requests"); fake.exceptions=types.SimpleNamespace(RequestException=Exception); sys.modules["requests"]=fake
import context_service

class ContextTests(unittest.TestCase):
 @patch("context_service.feishu_api.get_table_records_readonly",return_value=[])
 @patch("context_service.feishu_api.find_records_by_reference_exact",return_value=[])
 def test_no_match_never_blocks(self, *_):
  pack=context_service.build_context("E1",{"Description":"new issue"},[],"new issue")
  self.assertEqual(pack["knowledge_coverage"],"none"); self.assertEqual(pack["historical_itr"]["matches"],[])
 @patch("context_service.feishu_api.get_table_records_readonly",return_value=[])
 @patch("context_service.feishu_api.find_records_by_reference_exact",return_value=[])
 def test_follow_up_failed_action(self,*_):
  p=context_service.build_context("E1",{},[{"content":"Connector checked, issue remains."},{"content":"Please help"}],"Connector checked, issue remains.")
  self.assertTrue(p["follow_up"]["is_follow_up"]); self.assertTrue(p["follow_up"]["failed_actions"])
 @patch("context_service.feishu_api.find_records_by_reference_exact",return_value=[])
 @patch("context_service.feishu_api.get_table_records_readonly")
 def test_exact_error_and_draft_exclusion(self,read,_):
  read.side_effect=[[{"record_id":"e1","fields":{"错误代码":"1207"}}],[]]
  p=context_service.build_context("E1",{},[],"Error 1207")
  self.assertEqual(len(p["error_codes"]["exact_matches"]),1); self.assertEqual(p["approved_kb"]["matches"],[])

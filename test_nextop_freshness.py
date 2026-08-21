"""Offline contracts for read-only Nextop freshness protection."""
import sys, types, unittest
from unittest.mock import patch

if "requests" not in sys.modules:
    fake=types.ModuleType("requests"); fake.exceptions=types.SimpleNamespace(RequestException=Exception); sys.modules["requests"]=fake
if "bs4" not in sys.modules:
    fake=types.ModuleType("bs4"); fake.BeautifulSoup=object; sys.modules["bs4"]=fake

import case_service as service
import nextop_api

def message(text, sender_type=1, time=1):
    return {"content":text,"senderType":sender_type,"senderName":"PIE" if sender_type==2 else "Agent","time":time}

def prepared(messages=None):
    messages=messages or [message("Original issue")]
    info={"createTime":"1"}
    return service.PreparedNextopCase("SAFE-1", service.build_nextop_case_history(messages), {}, {"Case History":"old"}, messages, info, ticket_version=service._ticket_version(messages, info), message_fingerprint=service._message_fingerprint(messages), **service._latest_message_info(messages))

class NextopFreshnessTests(unittest.TestCase):
    def test_refresh_no_change_is_read_only(self):
        item=prepared(); ticket={"messages":item.messages,"list_info":{"createTime":"1"}}
        with patch.object(service.nextop_api,"get_ticket_full",return_value=ticket), patch.object(service.feishu_api,"create_record") as create, patch.object(service.feishu_api,"update_record") as update:
            result=service.refresh_latest_nextop_case(item)
        self.assertTrue(result["success"]); self.assertEqual(result["change_type"],"NO_CHANGE")
        create.assert_not_called(); update.assert_not_called()

    def test_repeated_refresh_is_deterministic_and_reports_latest_message(self):
        messages=[dict(message("Original issue",1,1), id="m1"), dict(message("PIE reply",2,2), id="m2")]
        item=prepared(messages); ticket={"messages":messages,"list_info":{"createTime":"1"}}
        with patch.object(service.nextop_api,"get_ticket_full",return_value=ticket):
            first=service.refresh_latest_nextop_case(item); second=service.refresh_latest_nextop_case(first["prepared"])
        self.assertEqual(first["change_type"],"NO_CHANGE"); self.assertEqual(second["change_type"],"NO_CHANGE")
        self.assertEqual((first["latest_message_id"],first["latest_sender_role"],first["message_fingerprint"]),(second["latest_message_id"],second["latest_sender_role"],second["message_fingerprint"]))

    def test_case_history_dedupes_messages_and_removes_quoted_signatures(self):
        source={"id":"m1","time":2,"senderType":1,"senderName":"Agent","content":"Fault persists.\n\nBest regards,\nAgent\n\nFrom: old@example.test\nOld chain"}
        history=service.build_nextop_case_history([source, dict(source), {"id":"m0","time":1,"senderType":2,"senderName":"PIE","content":"Please check the connector."}])
        self.assertEqual(history.count("Fault persists."),1)
        self.assertNotIn("Old chain",history)
        self.assertLess(history.index("Please check"),history.index("Fault persists"))

    def test_case_history_keeps_similar_distinct_repair_actions(self):
        history=service.build_nextop_case_history([
            {"id":"m1","time":1,"senderType":1,"senderName":"Agent","content":"Reset the mower; fault remained."},
            {"id":"m2","time":2,"senderType":1,"senderName":"Agent","content":"Reset the mower again after charging; fault remained."},
        ])
        self.assertIn("Reset the mower;",history)
        self.assertIn("again after charging",history)

    def test_reply_count_uses_stable_pie_history_only(self):
        initial=[message("Agent issue",1,1)]
        first=initial+[message("PIE first",2,2)]
        agent=first+[message("Agent follow-up",1,3)]
        second=agent+[message("PIE second",2,4)]
        self.assertEqual(service._nextop_reply_fields(initial),{})
        self.assertEqual(service._nextop_reply_fields(first)["Total Replied"],1)
        self.assertEqual(service._nextop_reply_fields(first)["Total Replied"],1)
        self.assertEqual(service._nextop_reply_fields(agent)["Total Replied"],1)
        self.assertEqual(service._nextop_reply_fields(second)["Total Replied"],2)

    def test_reply_count_includes_multiple_support_senders_and_excludes_agent_side(self):
        messages = [
            {"id":"a","senderType":1,"senderName":"Partner","time":1,"content":"Issue"},
            {"id":"w","senderType":2,"senderName":"Wayne","time":2,"content":"Reply"},
            {"id":"r","senderType":2,"senderName":"Reggie","time":3,"content":"Reply"},
            {"id":"s","senderType":2,"senderName":"Sunny","time":4,"content":"Reply"},
            {"id":"p","senderType":1,"senderName":"Partner","time":5,"content":"Follow-up"},
        ]
        self.assertEqual(service._nextop_reply_fields(messages)["Total Replied"], 3)

    def test_partial_snapshot_cannot_lower_known_reply_total(self):
        fields = service._nextop_reply_fields([message("Only visible reply", 2, 1)])
        self.assertEqual(service._preserve_reply_count(fields, 4)["Total Replied"], 4)

    def test_new_pie_reply_updates_history_and_reply_fields_without_reanalysis(self):
        item=prepared(); messages=item.messages+[message("Latest PIE guidance",2,2)]
        with patch.object(service.nextop_api,"get_ticket_full",return_value={"messages":messages,"list_info":{"createTime":"1"}}), patch.object(service,"build_v2_fields",return_value={"Case History":""}), patch.object(service,"_guard_select"), patch("context_service.build_context",return_value={}), patch.object(service.analyzer,"analyze_case_history") as analyze:
            result=service.refresh_latest_nextop_case(item)
        self.assertEqual(result["change_type"],"NEW_PIE_MESSAGE"); self.assertIn("Latest PIE guidance",result["prepared"].case_history); self.assertEqual(result["prepared"].fields["Total Replied"],1)
        analyze.assert_not_called()

    def test_new_agent_reply_requires_reanalysis_and_preserves_workspace_payload(self):
        item=prepared(); refreshed=prepared([message("Original issue"),message("Tried connector, issue remains",1,2)])
        with patch.object(service.nextop_api,"get_ticket_full",return_value={"messages":refreshed.messages,"list_info":{"createTime":"1"}}), patch.object(service,"prepare_nextop_case",return_value={"success":True,"prepared":refreshed}) as prepare:
            result=service.refresh_latest_nextop_case(item)
        self.assertEqual(result["change_type"],"NEW_AGENT_MESSAGE"); self.assertTrue(result["requires_reanalyze"]); self.assertIs(result["prepared"],refreshed); prepare.assert_called_once_with("SAFE-1", ticket_data={"messages":refreshed.messages,"list_info":{"createTime":"1"}})

    def test_auth_failure_is_safe_and_keeps_existing_prepared_case(self):
        item=prepared()
        with patch.object(service.nextop_api,"get_ticket_full",side_effect=nextop_api.NextopAuthRequired("expired")):
            result=service.refresh_latest_nextop_case(item)
        self.assertFalse(result["success"]); self.assertEqual(result["error_type"],"NEXTOP_AUTH_FAILED"); self.assertNotIn("Original issue",str(result))

    def test_commit_blocks_changed_ticket_before_any_feishu_write(self):
        item=prepared()
        stale={"success":True,"change_type":"NEW_AGENT_MESSAGE","prepared":item}
        with patch.object(service,"refresh_latest_nextop_case",return_value=stale), patch.object(service.feishu_api,"create_record") as create, patch.object(service.feishu_api,"update_record") as update:
            result=service.commit_prepared_nextop_case(item)
        self.assertFalse(result["success"]); self.assertEqual(result["error_type"],"NEXTOP_TICKET_STALE"); create.assert_not_called(); update.assert_not_called()

    def test_refresh_failure_blocks_commit_before_any_feishu_write(self):
        item=prepared()
        with patch.object(service,"refresh_latest_nextop_case",return_value={"success":False,"error_type":"NEXTOP_REFRESH_ERROR"}), patch.object(service.feishu_api,"create_record") as create:
            result=service.commit_prepared_nextop_case(item)
        self.assertFalse(result["success"]); self.assertEqual(result["error_type"],"NEXTOP_REFRESH_ERROR"); create.assert_not_called()

if __name__ == "__main__": unittest.main()

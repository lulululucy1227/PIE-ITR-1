"""Sanitized structural contracts for Nextop lookup and conversation envelopes."""
import sys, types, unittest
from unittest.mock import patch
if "requests" not in sys.modules:
    fake=types.ModuleType("requests"); fake.exceptions=types.SimpleNamespace(RequestException=Exception); sys.modules["requests"]=fake
if "bs4" not in sys.modules:
    fake=types.ModuleType("bs4"); fake.BeautifulSoup=object; sys.modules["bs4"]=fake
import nextop_api

class NextopSchemaTests(unittest.TestCase):
    def test_ticket_lookup_real_schema_shape_requires_exact_number(self):
        data={"code":"000000","data":{"records":[{"id":"opaque-id","repairOrderNo":"E260206"}]}}
        with patch.object(nextop_api,"_post",return_value=data):
            self.assertEqual(nextop_api.find_ticket_by_no("E260206")["id"],"opaque-id")

    def test_empty_lookup_is_not_claimed_as_ticket_not_found(self):
        with patch.object(nextop_api,"_post",return_value={"code":"000000","data":{"records":[]}}):
            with self.assertRaises(nextop_api.NextopLookupEmpty): nextop_api.find_ticket_by_no("E260206")

    def test_bad_lookup_shape_is_parse_error(self):
        with patch.object(nextop_api,"_post",return_value={"code":"000000","data":{}}):
            with self.assertRaises(nextop_api.NextopParseError): nextop_api.find_ticket_by_no("E260206")

    def test_messages_real_schema_is_sorted_and_sanitized(self):
        data={"code":"000000","data":[{"id":"later","sendTime":2,"senderType":2,"content":"redacted"},{"id":"early","sendTime":1,"senderType":1,"content":"redacted"}]}
        with patch.object(nextop_api,"_get",return_value=data):
            messages=nextop_api.get_messages("opaque-id")
        self.assertEqual([item["id"] for item in messages],["early","later"])

    def test_message_records_paginate_when_total_is_declared(self):
        pages=[{"code":"000000","data":{"total":2,"records":[{"id":"one","sendTime":1}]}},{"code":"000000","data":{"total":2,"records":[{"id":"two","sendTime":2}]}}]
        with patch.object(nextop_api,"_get",side_effect=pages) as get:
            messages=nextop_api.get_messages("opaque-id",size=1)
        self.assertEqual([item["id"] for item in messages],["one","two"]); self.assertEqual(get.call_count,2)

    def test_paginated_idless_messages_dedupe_with_stable_identity(self):
        duplicate={"sendTime":1,"senderType":1,"senderName":"Agent","content":"same"}
        pages=[{"code":"000000","data":{"total":3,"records":[duplicate,{"sendTime":2,"senderType":2,"senderName":"PIE","content":"reply"}]}},{"code":"000000","data":{"total":3,"records":[dict(duplicate)]}}]
        with patch.object(nextop_api,"_get",side_effect=pages): messages=nextop_api.get_messages("opaque-id",size=2)
        self.assertEqual(len(messages),2)
        self.assertEqual(messages[0], duplicate)

    def test_attachment_metadata_reports_image_video_file_and_other_without_download(self):
        attachments=nextop_api.get_message_file_attachments({"files":[{"id":"i","fileName":"photo.jpg"},{"id":"v","fileName":"clip.mp4"},{"id":"f","fileName":"device.log"},{"id":"o","fileName":"opaque"}]})
        self.assertEqual([item["kind"] for item in attachments],["image","video","file","other"])

if __name__ == "__main__": unittest.main()

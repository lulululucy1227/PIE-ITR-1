"""Synthetic-only regression tests for the manual Nextop auth workflow."""
import sys, types, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
if "requests" not in sys.modules:
    r=types.ModuleType("requests"); r.exceptions=types.SimpleNamespace(RequestException=Exception); sys.modules["requests"]=r
if "bs4" not in sys.modules:
    b=types.ModuleType("bs4"); b.BeautifulSoup=object; sys.modules["bs4"]=b
import nextop_auth, nextop_api, case_service
from api_adapter import LocalApiAdapter

CURL='curl "https://api.nextop.test" -H "x-extra: ignore" -H "Cookie: SESSION=fake-session; satoken=fake-sa; other=x" -H "Authorization: Bearer fake-auth"'

class NextopAuthTests(unittest.TestCase):
    def test_curl_parse_valid_and_order_independent(self):
        auth,cookie,sa=nextop_auth.parse_curl(CURL); self.assertEqual(auth,"Bearer fake-auth"); self.assertEqual(cookie,"SESSION=fake-session; satoken=fake-sa"); self.assertEqual(sa,"fake-sa")
    def test_curl_parse_invalid_and_empty(self):
        for value in ("", "curl -H 'Authorization: x'"):
            with self.assertRaises(nextop_auth.NextopCredentialError): nextop_auth.parse_curl(value)
    def test_missing_credentials_fail_closed_before_network(self):
        with patch.object(nextop_api.config, "NEXTOP_AUTH", ""), patch.object(nextop_api.config, "NEXTOP_COOKIE", ""), patch.object(nextop_api.config, "NEXTOP_SATOKEN", ""):
            with self.assertRaises(nextop_api.NextopAuthRequired): nextop_api._headers()
    def test_auth_failure_classified_and_ticket_preserved(self):
        with patch.object(case_service,"open_existing_case",return_value={"match_status":"NOT_FOUND"}), patch.object(case_service.nextop_api,"get_ticket_full",side_effect=nextop_api.NextopAuthRequired("Nextop authentication expired or invalid.")):
            value=case_service.prepare_nextop_case("SAFE-1")
        self.assertEqual(value["error_type"],"NEXTOP_AUTH_FAILED"); self.assertEqual(value["ticket_no"],"SAFE-1")
        self.assertEqual(value["stage"], "nextop_fetch")
    def test_persistence_is_atomic_redacted_and_preserves_other_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"config.py"; path.write_text('NEXTOP_AUTH = ""\nNEXTOP_COOKIE = ""\nNEXTOP_SATOKEN = ""\nOTHER = "keep"\n',encoding="utf-8")
            old=(nextop_auth.config.NEXTOP_AUTH,nextop_auth.config.NEXTOP_COOKIE,nextop_auth.config.NEXTOP_SATOKEN)
            try:
                nextop_auth.persist("Bearer fake-auth","SESSION=fake-session; satoken=fake-sa","fake-sa",path)
                text=path.read_text(encoding="utf-8"); self.assertIn('OTHER = "keep"',text); self.assertNotIn(CURL,text)
            finally:
                nextop_auth.config.NEXTOP_AUTH,nextop_auth.config.NEXTOP_COOKIE,nextop_auth.config.NEXTOP_SATOKEN=old
    def test_validation_read_only_and_runtime_update(self):
        calls=[]
        old=(nextop_auth.config.NEXTOP_AUTH,nextop_auth.config.NEXTOP_COOKIE,nextop_auth.config.NEXTOP_SATOKEN)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(nextop_auth,"persist") as persist:
                value=nextop_auth.update_from_curl(CURL,lambda:calls.append("read")); self.assertTrue(value["success"]); self.assertEqual(calls,["read"]); persist.assert_called_once()
        finally:
            nextop_auth.config.NEXTOP_AUTH,nextop_auth.config.NEXTOP_COOKIE,nextop_auth.config.NEXTOP_SATOKEN=old
    def test_update_api_and_status_do_not_expose_credentials(self):
        adapter=LocalApiAdapter()
        with patch("nextop_auth.update_from_curl",return_value={"success":True,"configured":True}) as update:
            self.assertTrue(adapter.update_nextop_token({"curl":CURL})["success"]); update.assert_called_once()
        state=adapter.nextop_auth_status(); self.assertEqual(set(state),{"configured"}); self.assertNotIn("fake",str(state))
    def test_update_error_is_redacted(self):
        with self.assertRaises(nextop_auth.NextopCredentialError) as error: nextop_auth.parse_curl("curl -H 'Cookie: secret-value'")
        self.assertNotIn("secret-value",str(error.exception))
    def test_update_api_returns_a_safe_invalid_curl_message(self):
        adapter=LocalApiAdapter()
        result=adapter.update_nextop_token({"curl":"-H 'Cookie: secret-value'"})
        self.assertFalse(result["success"]); self.assertEqual(result["error_type"],"NEXTOP_CREDENTIAL_INVALID")
        self.assertNotIn("secret-value",str(result))

if __name__=="__main__": unittest.main()

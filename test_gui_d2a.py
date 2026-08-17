"""Offline/static D2-A checks; no tkinter window, Feishu, or Nextop call."""
import sys
import types
import unittest
from unittest.mock import patch
from pathlib import Path

if "requests" not in sys.modules:
    _requests = types.ModuleType("requests")
    class _RequestException(Exception):
        pass
    _requests.exceptions = types.SimpleNamespace(RequestException=_RequestException)
    sys.modules["requests"] = _requests
if "bs4" not in sys.modules:
    _bs4 = types.ModuleType("bs4")
    _bs4.BeautifulSoup = object
    sys.modules["bs4"] = _bs4

import case_service
import gui


class InspectorD2aTests(unittest.TestCase):
    def _app(self, case=None):
        app = gui.PieItrAssistant.__new__(gui.PieItrAssistant)
        app._workspaces = {"ws": gui.CaseWorkspace("ws", workspace_type="EXISTING_CASE", current_case_dto=case or {"device_name": "LUBA-12345"})}
        app._active_workspace_id = "ws"
        app.preferred_analysis_language = "ORIGINAL"
        app._running = False
        app._render_inspector = lambda: None
        app._set_workspace_state = lambda _state: None
        app._set_task_progress = lambda *_args, **_kwargs: None
        app._start_task = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("unexpected AI call"))
        app.status = types.SimpleNamespace(set=lambda _value: None)
        return app

    def test_workspace_type_routes_existing_and_prepared_to_inspector_only(self):
        app = gui.PieItrAssistant.__new__(gui.PieItrAssistant)
        app._workspaces = {
            "existing": gui.CaseWorkspace("existing", workspace_type="EXISTING_CASE", current_case_dto={"record_id": "r1"}),
            "prepared": gui.CaseWorkspace("prepared", workspace_type="PREPARED_CASE", current_case_dto={"reference_no": "N1"}, prepared_case=object()),
            "new": gui.CaseWorkspace("new", workspace_type="NEW_CASE"),
        }
        app._active_workspace_id = "existing"
        self.assertTrue(app._is_inspector_workspace())
        app._active_workspace_id = "prepared"
        self.assertTrue(app._is_inspector_workspace())
        app._active_workspace_id = "new"
        self.assertFalse(app._is_inspector_workspace())

    def test_history_parser_preserves_three_events_newest_first(self):
        events = case_service.parse_case_history_for_display(
            "[2026-01-01] Customer\nQuestion\n\n[2026-01-02] PIE - Agent\nReply\n\n[2026-01-03] Dealer\nFeedback"
        )
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["role"], "DEALER")
        self.assertEqual(events[1]["role"], "PIE_REPLY")

    def test_review_workbench_contract_has_two_columns_and_no_write_call(self):
        source = Path("gui.py").read_text(encoding="utf-8")
        for text in ("CASE CONTEXT", "CASE REVIEW", "CUSTOMER ISSUE", "CURRENT BLOCKER",
                     "PREVIOUS PIE GUIDANCE", "CURRENT ASSESSMENT / NEXT STEP", "SOLUTION STATE",
                     "REPLY (ENGLISH)", "LOGIQ · OPEN LOGS", "Translation unavailable."):
            self.assertIn(text, source)
        self.assertNotIn('self.inspector_right =', source)
        self.assertIn('return str(workspace.current_case_dto.get("ticket_no")', source)
        self.assertNotIn('return "Writing" if workspace.state', source)
        inspector_slice = source[source.index("def _analyze_inspector_case"):source.index("def _refresh_tabs")]
        self.assertNotIn("create_record", inspector_slice)
        self.assertNotIn("update_record", inspector_slice)

    def test_d2d_router_progress_and_evidence_contract(self):
        gui_source = Path("gui.py").read_text(encoding="utf-8")
        service_source = Path("case_service.py").read_text(encoding="utf-8")
        self.assertIn("Single visibility router", gui_source)
        self.assertIn('show = stage not in {"ready", "today", "prepared", "review_ready"}', gui_source)
        self.assertIn('"prepared": ("READY FOR REVIEW", 0)', gui_source)
        self.assertIn('self.inspector_todo_checkbutton.grid(row=1, column=1', gui_source)
        self.assertNotIn('ttk.Checkbutton(left, text="Add to ITR Todo"', gui_source)
        self.assertIn("CaseEvidenceAttachment", service_source)
        self.assertNotIn("Tesseract", service_source)

    def test_workspace_states_remain_independent_over_repeated_switches(self):
        app = gui.PieItrAssistant.__new__(gui.PieItrAssistant)
        app._workspaces = {
            "A": gui.CaseWorkspace("A", workspace_type="EXISTING_CASE", current_case_dto={"ticket_no": "ITR-0817-1979"}, notes="A", analysis_result="analysis-A"),
            "B": gui.CaseWorkspace("B", workspace_type="NEW_CASE", source="nextop", ticket_input=""),
            "C": gui.CaseWorkspace("C", workspace_type="NEW_CASE", source="whatsapp", manual_input="C input"),
        }
        for workspace_id in ["A", "B", "C", "A", "B", "A"] * 4:
            app._active_workspace_id = workspace_id
            workspace = app._active_workspace
            if workspace_id == "A":
                self.assertTrue(app._is_inspector_workspace())
                self.assertEqual(workspace.notes, "A")
                self.assertEqual(workspace.analysis_result, "analysis-A")
            else:
                self.assertFalse(app._is_inspector_workspace())
        self.assertEqual(app._workspaces["C"].manual_input, "C input")

    def test_translation_cache_toggles_without_second_ai_call(self):
        app = self._app()
        workspace = app._active_workspace
        workspace.analysis_result = types.SimpleNamespace(source_hash="hash-1", reply_en="English")
        workspace.translation_source_hash = "hash-1"
        workspace.translation_result = {"customer_description": "中文"}
        app._select_analysis_language("ZH")
        self.assertEqual(workspace.analysis_language, "ZH")
        app._select_analysis_language("ORIGINAL")
        self.assertEqual(workspace.analysis_language, "ORIGINAL")
        app._select_analysis_language("ZH")
        self.assertEqual(workspace.analysis_language, "ZH")

    def test_translation_miss_starts_only_translation_backend(self):
        app = self._app()
        app._active_workspace.analysis_result = types.SimpleNamespace(source_hash="hash-1", reply_en="English")
        started = []
        app._start_task = lambda operation, value, completion: started.append((operation, value, completion))
        app._select_analysis_language("ZH")
        self.assertEqual(len(started), 1)
        self.assertNotIn("analyze_case_for_inspector", started[0][0].__code__.co_names)

    def test_logiq_copies_only_device_and_opens_external_url(self):
        copied, statuses = [], []
        app = self._app({"device_name": "LUBA-12345"})
        app.root = types.SimpleNamespace(clipboard_clear=lambda: copied.clear(), clipboard_append=lambda value: copied.append(value), update_idletasks=lambda: None)
        app.status = types.SimpleNamespace(set=statuses.append)
        with patch.object(gui.webbrowser, "open", return_value=True) as open_browser:
            app._open_logiq()
        self.assertEqual(copied, ["LUBA-12345"])
        open_browser.assert_called_once_with(gui.LOGIQ_URL)
        self.assertEqual(app._active_workspace.logiq_session_state, "OPENED")

    def test_logiq_without_device_does_not_copy_a_substitute(self):
        copied = []
        app = self._app({"device_name": "", "model_type": "LUBA 3"})
        app.root = types.SimpleNamespace(clipboard_clear=lambda: copied.clear(), clipboard_append=lambda value: copied.append(value), update_idletasks=lambda: None)
        app.status = types.SimpleNamespace(set=lambda _value: None)
        with patch.object(gui.webbrowser, "open", return_value=True):
            app._open_logiq()
        self.assertEqual(copied, [])

    def test_reanalyze_hash_change_invalidates_translation_cache(self):
        app = self._app()
        workspace = app._active_workspace
        workspace.analysis_result = types.SimpleNamespace(source_hash="old")
        workspace.translation_source_hash = "old"
        workspace.translation_result = {"customer_description": "旧翻译"}
        workspace.translation_cache["old"] = workspace.translation_result
        app._show_inspector_analysis(types.SimpleNamespace(source_hash="new", reply_en="English"))
        self.assertEqual(workspace.analysis_language, "ORIGINAL")
        self.assertIsNone(workspace.translation_result)
        self.assertEqual(workspace.translation_cache, {})

    def test_copy_reply_uses_original_english_in_chinese_mode(self):
        copied = []
        app = self._app()
        app.root = types.SimpleNamespace(clipboard_clear=lambda: copied.clear(), clipboard_append=lambda value: copied.append(value), update_idletasks=lambda: None)
        app._active_workspace.analysis_result = types.SimpleNamespace(reply_en="English reply")
        app._active_workspace.analysis_language = "ZH"
        app._copy_reply()
        self.assertEqual(copied, ["English reply"])

    def test_logiq_has_no_credential_or_write_contract(self):
        source = Path("gui.py").read_text(encoding="utf-8")
        self.assertIn('LOGIQ_URL = "https://logiq.cloud-cn.mammotion.com/"', source)
        logiq_slice = source[source.index("def _open_logiq"):source.index("def _analyze_inspector_case")]
        self.assertNotIn("create_record", logiq_slice)
        self.assertNotIn("update_record", logiq_slice)
        self.assertNotIn("password", logiq_slice.casefold())

    def test_inspector_prompt_grounding_and_email_contract(self):
        source = Path("analyzer.py").read_text(encoding="utf-8")
        self.assertIn("ONLY actions explicitly confirmed", source)
        self.assertIn("Exclude PIE review", source)
        self.assertIn('use "Hi Team," or "Hello,"', source)
        self.assertIn("PIE Technical Support", source)


if __name__ == "__main__":
    unittest.main()

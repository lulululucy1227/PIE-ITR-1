"""Thin JSON adapter for the existing NextopSync service boundary."""
from dataclasses import asdict, is_dataclass

def to_json(value):
    if is_dataclass(value):
        return {key: to_json(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): to_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json(item) for item in value]
    return value


def prepared_from_json(data):
    import case_service
    allowed = {name for name in case_service.PreparedNextopCase.__dataclass_fields__}
    return case_service.PreparedNextopCase(**{key: value for key, value in dict(data or {}).items() if key in allowed})


def analysis_from_json(data):
    import analyzer
    allowed = {name for name in analyzer.InspectorAnalysis.__dataclass_fields__}
    return analyzer.InspectorAnalysis(**{key: value for key, value in dict(data or {}).items() if key in allowed})


class LocalApiAdapter:
    """API-facing methods: Search/Analyze/Translate are read-only by contract."""
    def health(self):
        import nextop_auth
        import config
        nextop = nextop_auth.status()
        feishu_ready = bool(getattr(config, "FEISHU_USER_ACCESS_TOKEN", "") and getattr(config, "FEISHU_APP_TOKEN", ""))
        ai_ready = bool(getattr(config, "DEEPSEEK_API_KEY", "") and getattr(config, "DEEPSEEK_BASE_URL", ""))
        return {"ok": True, "service": "nextopsync-local-api", "nextop": nextop,
                "feishu": {"state": "READY" if feishu_ready else "AUTH_REQUIRED"},
                "ai": {"state": "READY" if ai_ready else "UNKNOWN"}}

    def nextop_auth_status(self):
        import nextop_auth
        return nextop_auth.status()

    def update_nextop_token(self, payload):
        import nextop_api, nextop_auth
        try:
            return nextop_auth.update_from_curl(payload.get("curl"), lambda: nextop_api.search_tickets("", size=1))
        except nextop_auth.NextopCredentialError as exc:
            return {"success": False, "error_type": "NEXTOP_CREDENTIAL_INVALID", "message": str(exc)}
        except Exception:
            return {"success": False, "error_type": "NEXTOP_VALIDATION_ERROR", "message": "Nextop token validation failed. Please copy the complete request as cURL again."}

    def prepare(self, payload):
        import case_service
        if str(payload.get("source") or "nextop").lower() != "nextop":
            return {"success": False, "error_type": "unsupported_source", "message": "Only Nextop preparation is available in V2 Phase 1."}
        try: return to_json(case_service.prepare_nextop_case(str(payload.get("ticket_no") or "")))
        except Exception as exc:
            import nextop_api
            if isinstance(exc,nextop_api.NextopAuthRequired): return {"success":False,"error_type":"NEXTOP_CREDENTIALS_MISSING" if "not configured" in str(exc) else "NEXTOP_AUTH_FAILED","message":"Nextop authentication is not configured." if "not configured" in str(exc) else "Nextop authentication expired or invalid."}
            return {"success":False,"error_type":"NEXTOP_RESPONSE_ERROR","stage":"local_api_prepare","message":"Preparation request failed before a safe case result was returned.","detail":type(exc).__name__}

    def prepare_manual(self, payload):
        import case_service
        return to_json(case_service.prepare_manual_intake(payload))

    def manual_partner_options(self, _payload):
        import partner_resolver
        try:
            return {"success": True, "options": partner_resolver.partner_options_readonly()}
        except Exception:
            return {"success": False, "options": [], "message": "Partner options could not be loaded. You can continue with an unresolved Partner."}

    def open_existing_itr(self, payload):
        import case_service
        return to_json(case_service.open_existing_case(payload.get("ticket_no") or ""))

    def manual_append_preview(self, payload):
        import case_service
        return self._manual_operation("append_preview", lambda: case_service.prepare_manual_append_preview(payload.get("ticket_no") or "", case_service.manual_draft_from_json(payload.get("draft"))))

    def manual_create_preview(self, payload):
        import case_service
        return self._manual_operation("create_preview", lambda: case_service.prepare_manual_create_preview(case_service.manual_draft_from_json(payload.get("draft")), include_itr_todo=bool(payload.get("include_itr_todo")), nff_value=bool(payload.get("nff_value")), issue_owner=payload.get("issue_owner") or ""))

    def manual_reanalyze(self, payload):
        import case_service
        return self._manual_operation("reanalyze", lambda: case_service.reanalyze_manual_draft(case_service.manual_draft_from_json(payload.get("draft")), payload.get("human_guidance") or ""))

    def manual_create(self, payload):
        import case_service
        return self._manual_operation("create", lambda: case_service.create_manual_itr(case_service.manual_draft_from_json(payload.get("draft")), payload.get("attachments") or [], include_itr_todo=bool(payload.get("include_itr_todo")), nff_value=bool(payload.get("nff_value")), issue_owner=payload.get("issue_owner") or ""))

    def manual_append(self, payload):
        import case_service
        return self._manual_operation("append", lambda: case_service.append_manual_itr(payload.get("ticket_no") or "", case_service.manual_draft_from_json(payload.get("draft")), payload.get("attachments") or []))

    def _manual_operation(self, stage, action):
        """Return useful redacted failures instead of the HTTP layer's generic 500."""
        import feishu_api
        try:
            return to_json(action())
        except (feishu_api.FeishuAuthRequired, feishu_api.FeishuReadError) as exc:
            category = feishu_api.classify_read_error(exc)
            messages = {
                "AUTH_EXPIRED": "Feishu authorization is missing or expired. Refresh local Feishu authorization.",
                "PERMISSION_DENIED": "Feishu authorization does not have permission to read this ITR table.",
                "TABLE_NOT_FOUND": "The configured Feishu ITR table could not be found.",
                "NETWORK_ERROR": "Feishu could not be reached. Check the network and try again.",
                "INVALID_RESPONSE": "Feishu returned an invalid response while reading ITR.",
            }
            return {"success": False, "stage": stage, "error_type": category, "message": messages.get(category, "The ITR case could not be read from Feishu.")}
        except Exception:
            return {"success": False, "stage": stage, "error_type": "MANUAL_ITR_OPERATION_ERROR", "message": "The requested ITR operation could not be completed safely."}

    def analyze(self, payload):
        import case_service
        prepared = prepared_from_json(payload.get("prepared"))
        return to_json(case_service.reanalyze_prepared_nextop_case(prepared, payload.get("human_guidance") or ""))

    def refresh(self, payload):
        import case_service
        return to_json(case_service.refresh_latest_nextop_case(prepared_from_json(payload.get("prepared"))))

    def preview(self, payload):
        import case_service
        return to_json(case_service.prepare_commit_preview(prepared_from_json(payload.get("prepared"))))

    def translate(self, payload):
        import case_service
        return to_json(case_service.translate_inspector_analysis_to_zh(analysis_from_json(payload.get("analysis"))))

    def translate_text(self, payload):
        import case_service
        try:
            text = case_service.translate_text_to_zh(payload.get("text") or "")
            return {"success": True, "text": text}
        except Exception:
            # Keep provider details, credentials, and request bodies out of the UI.
            return {"success": False, "error_type": "TRANSLATION_ERROR", "message": "Chinese translation failed."}

    def commit(self, payload):
        import case_service
        prepared = prepared_from_json(payload.get("prepared"))
        return to_json(case_service.commit_prepared_nextop_case(
            prepared,
            include_itr_todo=bool(payload.get("include_itr_todo")),
            todo_dirty=bool(payload.get("todo_dirty")),
            nff_value=bool(payload.get("nff_value")),
            nff_dirty=bool(payload.get("nff_dirty")),
            issue_owner_value=payload.get("issue_owner_value"),
            issue_owner_dirty=bool(payload.get("issue_owner_dirty")),
        ))

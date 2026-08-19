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
        return {"ok": True, "service": "nextopsync-local-api", "nextop":nextop_auth.status()}

    def nextop_auth_status(self):
        import nextop_auth
        return nextop_auth.status()

    def update_nextop_token(self, payload):
        import nextop_api, nextop_auth
        return nextop_auth.update_from_curl(payload.get("curl"), lambda: nextop_api.search_tickets("", size=1))

    def prepare(self, payload):
        import case_service
        if str(payload.get("source") or "nextop").lower() != "nextop":
            return {"success": False, "error_type": "unsupported_source", "message": "Only Nextop preparation is available in V2 Phase 1."}
        try: return to_json(case_service.prepare_nextop_case(str(payload.get("ticket_no") or "")))
        except Exception as exc:
            import nextop_api
            if isinstance(exc,nextop_api.NextopAuthRequired): return {"success":False,"error_type":"NEXTOP_CREDENTIALS_MISSING" if "not configured" in str(exc) else "NEXTOP_AUTH_FAILED","message":"Nextop authentication is not configured." if "not configured" in str(exc) else "Nextop authentication expired or invalid."}
            return {"success":False,"error_type":"NEXTOP_REQUEST_ERROR","message":"Nextop request failed."}

    def analyze(self, payload):
        import case_service
        return to_json(case_service.analyze_existing_case_for_inspector(dict(payload.get("case") or {})))

    def translate(self, payload):
        import case_service
        return to_json(case_service.translate_inspector_analysis_to_zh(analysis_from_json(payload.get("analysis"))))

    def commit(self, payload):
        import case_service
        prepared = prepared_from_json(payload.get("prepared"))
        return to_json(case_service.commit_prepared_nextop_case(
            prepared,
            include_itr_todo=bool(payload.get("include_itr_todo")),
            todo_dirty=bool(payload.get("todo_dirty")),
        ))

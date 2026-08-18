"""Explicit product constraints; unknown is never treated as supported."""
import re

REGISTRY = {"LUBA 1": {"device_log": "unsupported", "logiq": "unsupported"}}
UNKNOWN = {"device_log": "unknown", "logiq": "unknown"}
_LOG_REQUEST = re.compile(r"\b(?:device\s*logs?|export\s*logs?|upload\s*logs?|run\s*logiq|logiq)\b", re.I)


def capabilities(model):
    return dict(REGISTRY.get(str(model or "").strip().upper(), UNKNOWN))


def may_request_logs(model):
    return capabilities(model)["device_log"] == "supported"


def contains_log_request(value):
    """True for requests/actions that assume a log or LogiQ capability."""
    return bool(_LOG_REQUEST.search(str(value or "")))

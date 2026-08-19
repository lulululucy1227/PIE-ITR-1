"""Local-only HTTP adapter for V2.  Run with: python local_api.py"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from api_adapter import LocalApiAdapter


ADAPTER = LocalApiAdapter()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, _format, *_args):
        pass  # Never log case content or request bodies.

    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/health": self._send(200, ADAPTER.health())
        else: self._send(404, {"success": False, "message": "Not found."})

    def do_POST(self):
        routes = {"/api/cases/prepare": ADAPTER.prepare, "/api/auth/nextop/status": lambda _p: ADAPTER.nextop_auth_status(), "/api/auth/nextop/update": ADAPTER.update_nextop_token, "/api/cases/analyze": ADAPTER.analyze,
                  "/api/cases/translate": ADAPTER.translate, "/api/cases/commit": ADAPTER.commit}
        action = routes.get(self.path)
        if not action:
            self._send(404, {"success": False, "message": "Not found."}); return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or b"{}")
            self._send(200, action(payload))
        except (ValueError, TypeError):
            self._send(400, {"success": False, "message": "Invalid JSON request."})
        except Exception:
            self._send(500, {"success": False, "message": "Local API operation failed."})


def main():
    ThreadingHTTPServer(("127.0.0.1", 8787), Handler).serve_forever()


if __name__ == "__main__":
    main()

"""
首次飞书授权脚本 —— 运行一次即可，自动把 user_access_token 写入 config.py

用法：python feishu_auth.py
"""

import re
import json
import time
import threading
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import config

REDIRECT_URI = "http://localhost:19876/callback"
AUTH_URL = (
    f"https://open.feishu.cn/open-apis/authen/v1/index"
    f"?app_id={config.FEISHU_APP_ID}"
    f"&redirect_uri={REDIRECT_URI}"
)

_code_received = None


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _code_received
        qs = parse_qs(urlparse(self.path).query)
        code = qs.get("code", [None])[0]
        if code:
            _code_received = code
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<h2>授权成功！请关闭此窗口，回到命令行查看结果。</h2>".encode()
            )
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, *args):
        pass  # 静默


def _get_app_access_token():
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal",
        json={"app_id": config.FEISHU_APP_ID, "app_secret": config.FEISHU_APP_SECRET},
    )
    return resp.json()["app_access_token"]


def _exchange_code(code, app_token):
    resp = requests.post(
        "https://open.feishu.cn/open-apis/authen/v1/access_token",
        headers={"Authorization": f"Bearer {app_token}", "Content-Type": "application/json"},
        json={"grant_type": "authorization_code", "code": code},
    )
    return resp.json().get("data", {})


def _persist(access_token, refresh_token):
    with open("config.py", "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r'FEISHU_USER_ACCESS_TOKEN = ".*?"',
                  f'FEISHU_USER_ACCESS_TOKEN = "{access_token}"', text)
    text = re.sub(r'FEISHU_USER_REFRESH_TOKEN = ".*?"',
                  f'FEISHU_USER_REFRESH_TOKEN = "{refresh_token}"', text)
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(text)


def main():
    global _code_received

    server = HTTPServer(("localhost", 19876), _Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    print("正在打开飞书授权页面，请用你的飞书账号登录并授权...")
    print(f"如未自动打开，请手动访问：\n{AUTH_URL}\n")
    webbrowser.open(AUTH_URL)

    # 等待回调（最多 120 秒）
    for _ in range(120):
        if _code_received:
            break
        time.sleep(1)
    else:
        print("超时，未收到授权回调，请重试")
        server.shutdown()
        return

    server.shutdown()
    print("收到授权码，正在换取 token...")

    app_token = _get_app_access_token()
    data = _exchange_code(_code_received, app_token)

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    name = data.get("name", "")

    if not access_token:
        print("换取 token 失败:", json.dumps(data, ensure_ascii=False))
        return

    _persist(access_token, refresh_token)
    print(f"\n授权成功！用户：{name}")
    print("token 已写入 config.py，之后创建的飞书记录将显示你的名字。")


if __name__ == "__main__":
    main()

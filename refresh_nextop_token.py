"""
用保存的登录状态(nextop_state.json)无头打开Nextop页面，
拦截接口请求拿到最新的 Authorization / satoken / Cookie，写回 config.py
"""
import re
from playwright.sync_api import sync_playwright

STATE_FILE = "nextop_state.json"


def refresh():
    captured = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()

        def on_request(request):
            if "api.nextop.com" in request.url and "/ticketOrder/" in request.url:
                headers = request.headers
                if "authorization" in headers and "satoken" in headers:
                    captured["authorization"] = headers["authorization"]
                    captured["satoken"] = headers["satoken"]

        page.on("request", on_request)
        page.goto("https://saas.nextop.com/crm/orderManage/orderList/index", wait_until="load", timeout=60000)
        page.wait_for_timeout(8000)

        cookies = context.cookies()
        cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies if c['name'] in ("SESSION", "satoken"))

        # 保存最新登录状态，延长会话寿命
        context.storage_state(path=STATE_FILE)
        browser.close()

    if "authorization" not in captured:
        raise RuntimeError("没有捕获到新的token，登录状态可能已失效，需要重新运行 login_save_session.py")

    return captured["authorization"], cookie_str, captured["satoken"]


def persist(auth, cookie_str, satoken):
    with open("config.py", "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r'NEXTOP_AUTH = ".*?"', f'NEXTOP_AUTH = "{auth}"', text)
    text = re.sub(r'NEXTOP_COOKIE = ".*?"', f'NEXTOP_COOKIE = "{cookie_str}"', text)
    text = re.sub(r'NEXTOP_SATOKEN = ".*?"', f'NEXTOP_SATOKEN = "{satoken}"', text)
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    auth, cookie_str, satoken = refresh()
    persist(auth, cookie_str, satoken)
    print("Nextop token 已更新")
    print("authorization:", auth[:50], "...")
    print("cookie:", cookie_str)

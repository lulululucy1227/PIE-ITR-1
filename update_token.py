"""
从浏览器Network面板复制的 cURL 命令解析出 authorization / cookie / satoken，
并更新到 config.py。

用法：直接运行 `python update_token.py`，按提示粘贴 cURL，
粘贴完成后另起一行输入 END 并回车。
"""
import re


def parse_curl(curl_text):
    # Windows cmd下 "Copy as cURL" 会用 ^ 转义引号/特殊字符，统一去掉
    curl_text = curl_text.replace("^\r\n", "").replace("^\n", "").replace("^", "")

    auth = None
    cookie = None

    headers = []
    headers += re.findall(r"-H\s+'([^']*)'", curl_text)
    headers += re.findall(r'-H\s+"([^"]*)"', curl_text)

    for header in headers:
        if ":" not in header:
            continue
        name, value = header.split(":", 1)
        name = name.strip().lower()
        value = value.strip()
        if name == "authorization":
            auth = value
        elif name == "cookie":
            cookie = value

    if cookie is None:
        m = re.search(r"-b\s+'([^']*)'", curl_text) or re.search(r'-b\s+"([^"]*)"', curl_text)
        if not m:
            m = re.search(r"--cookie\s+'([^']*)'", curl_text) or re.search(r'--cookie\s+"([^"]*)"', curl_text)
        if m:
            cookie = m.group(1)

    if not auth or not cookie:
        raise ValueError("没有在cURL中找到 authorization 或 cookie 头，请确认复制的是完整的cURL命令")

    # 从cookie中只保留 SESSION 和 satoken
    jar = {}
    for part in cookie.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            jar[k.strip()] = v.strip()

    satoken = jar.get("satoken")
    if not satoken:
        raise ValueError("cookie中没有找到 satoken")

    cookie_str = "; ".join(f"{k}={jar[k]}" for k in ("SESSION", "satoken") if k in jar)

    return auth, cookie_str, satoken


def persist(auth, cookie_str, satoken):
    with open("config.py", "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r'NEXTOP_AUTH = ".*?"', f'NEXTOP_AUTH = "{auth}"', text)
    text = re.sub(r'NEXTOP_COOKIE = ".*?"', f'NEXTOP_COOKIE = "{cookie_str}"', text)
    text = re.sub(r'NEXTOP_SATOKEN = ".*?"', f'NEXTOP_SATOKEN = "{satoken}"', text)
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(text)


def read_curl_from_stdin():
    print("请粘贴cURL命令（可多行），完成后另起一行输入 END 并回车：")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    curl_text = read_curl_from_stdin()
    auth, cookie_str, satoken = parse_curl(curl_text)
    persist(auth, cookie_str, satoken)
    print("Nextop token 已更新")

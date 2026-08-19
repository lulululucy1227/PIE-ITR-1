"""Manual Copy-as-cURL authentication helper; credentials stay local and ignored."""
import json, os, re, tempfile
from pathlib import Path
import config

class NextopCredentialError(RuntimeError): pass

def parse_curl(curl_text):
    text=str(curl_text or "").replace("^\r\n", "").replace("^\n", "").replace("^", "")
    headers=re.findall(r"-H\s+'([^']*)'",text)+re.findall(r'-H\s+"([^"]*)"',text)
    values={}
    for header in headers:
        if ":" in header:
            name,value=header.split(":",1); values[name.strip().lower()]=value.strip()
    cookie=values.get("cookie")
    if not cookie:
        match=re.search(r"(?:-b|--cookie)\s+['\"]([^'\"]*)['\"]",text)
        cookie=match.group(1) if match else ""
    jar={part.strip().split("=",1)[0]:part.strip().split("=",1)[1] for part in cookie.split(";") if "=" in part}
    auth=values.get("authorization", ""); satoken=jar.get("satoken", "")
    selected="; ".join(f"{key}={jar[key]}" for key in ("SESSION","satoken") if key in jar)
    if not auth or not selected or not satoken: raise NextopCredentialError("The pasted cURL is missing required Nextop authentication fields.")
    return auth,selected,satoken

def persist(auth,cookie,satoken,config_path=None):
    path=Path(config_path or Path(__file__).with_name("config.py"))
    if not path.exists(): raise NextopCredentialError("Local credential storage is not configured.")
    text=path.read_text(encoding="utf-8")
    for key,value in (("NEXTOP_AUTH",auth),("NEXTOP_COOKIE",cookie),("NEXTOP_SATOKEN",satoken)):
        text=re.sub(rf'^{key}\s*=\s*".*?"',f'{key} = {json.dumps(value)}',text,flags=re.M)
    fd,temp=tempfile.mkstemp(prefix="pie-nextop-",suffix=".tmp",dir=path.parent); os.close(fd)
    try: Path(temp).write_text(text,encoding="utf-8"); os.replace(temp,path)
    finally:
        if os.path.exists(temp): os.unlink(temp)
    config.NEXTOP_AUTH,config.NEXTOP_COOKIE,config.NEXTOP_SATOKEN=auth,cookie,satoken

def status(): return {"configured":bool(config.NEXTOP_AUTH and config.NEXTOP_COOKIE and config.NEXTOP_SATOKEN)}

def update_from_curl(curl_text, validate):
    auth,cookie,satoken=parse_curl(curl_text)
    old=(config.NEXTOP_AUTH,config.NEXTOP_COOKIE,config.NEXTOP_SATOKEN)
    config.NEXTOP_AUTH,config.NEXTOP_COOKIE,config.NEXTOP_SATOKEN=auth,cookie,satoken
    try: validate()
    except Exception:
        config.NEXTOP_AUTH,config.NEXTOP_COOKIE,config.NEXTOP_SATOKEN=old; raise NextopCredentialError("Nextop authentication is invalid or expired.")
    persist(auth,cookie,satoken); return {"success":True,"configured":True}

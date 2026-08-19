"""Pure parser dispatch; no network, analysis, or persistence."""
import re
from .models import NormalizedCase

SOURCES = {"whatsapp", "lark", "email"}

def _role(name):
    low = str(name or "").casefold()
    if any(x in low for x in ("pie", "support", "mammotion")): return "support"
    if low: return "customer"
    return "unknown"

def normalize_case(source_type, raw_input, source_reference=""):
    source = str(source_type or "").casefold().strip()
    if source not in SOURCES: raise ValueError("Unsupported source type")
    raw = str(raw_input or "").strip()
    if not raw: raise ValueError("No content entered")
    if source == "email":
        split = re.split(r"\n(?:On .+wrote:|[-_]{5,})", raw, maxsplit=1, flags=re.I)
        current, quoted = split[0].strip(), split[1].strip() if len(split) > 1 else ""
        return NormalizedCase(source, source_reference, "", [{"id":"email-1","role":"unknown","content":current}], current, quoted, not bool(re.search(r"^(Subject|From):", raw, re.M|re.I)))
    messages=[]
    for index, line in enumerate(raw.splitlines(), 1):
        match=re.match(r"(?:\[[^\]]+\]\s*)?([^:]{1,80}):\s*(.+)", line.strip())
        if match:
            name, content=match.groups(); messages.append({"id":f"{source}-{index}","role":_role(name),"sender":name.strip(),"content":content.strip()})
        elif line.strip(): messages.append({"id":f"{source}-{index}","role":"unknown","content":line.strip()})
    return NormalizedCase(source, source_reference, "", messages, "\n".join(x["content"] for x in messages), "", any(x["role"]=="unknown" for x in messages))

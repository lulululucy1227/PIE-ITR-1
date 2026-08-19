"""AI extraction for the V2 ITR case-facts layer."""

import json
import time as _time
import hashlib
from dataclasses import dataclass

import requests

import config
import feishu_api
import field_options as fo
from product_capabilities import capabilities, contains_log_request
from analysis_validators import validate

@dataclass
class InspectorAnalysis:
    customer_description: str; repair_actions: list[str]; current_blocker: str; blocker_is_inferred: bool
    historical_pie_recommendations: list[str]; ai_suggested_next_step: str; solution_state: str; solution: str; reply_en: str; source_language: str; source_hash: str
    information_status: str = "sufficient"; missing_information: list[str] = None; reason_for_request: list[str] = None; next_action: str = "assess"; capability: dict = None
    confirmed_facts: list[str] = None; already_tried: list[str] = None; ruled_out: list[str] = None; hypotheses: list[dict] = None; resolution_path: list[str] = None; needs_human_check: bool = False; escalation: list[str] = None; parts_to_verify: list[str] = None

INSPECTOR_SYSTEM_PROMPT = """Return JSON only. Ground every fact in the supplied case data. customer_description is the concise current customer/dealer issue in its original source language, not an email copy. repair_actions contains ONLY actions explicitly confirmed as physically or operationally completed by a customer, dealer, technician, or device. Exclude PIE review, recommendations, instructions, proposed actions, future actions, and suggestions. Historical recommendations must be real PIE guidance extracted from history/Solutions only. If a blocker is inferred set blocker_is_inferred true; never state inference as fact. solution_state must be FINAL, CURRENT, WORKAROUND, PENDING, or NONE. reply_en is a complete copy-ready English email with a neutral greeting (use "Hi Team," or "Hello," unless a reliable name is present), blank lines, concise body, and a closing such as "Best regards,\nPIE Technical Support". Do not invent a recipient name and do not promise ETA, firmware dates, warranty, replacement, refund, or compensation."""


def _as_text_list(value):
    return [str(item).strip() for item in (value or []) if str(item).strip()]


def _request_reply(missing):
    items = "\n".join(f"- {item}" for item in missing)
    return f"Hi Team,\n\nTo continue the review, please provide:\n{items}\n\nBest regards,\nPIE Technical Support"


def _restricted_or_repeated(result, context, capability):
    """Hard guard for unsupported tools and plainly repeated failed actions."""
    values = []
    for key in ("missing_information", "reason_for_request", "ai_suggested_next_step", "solution", "reply_en"):
        value = result.get(key)
        values.extend(value if isinstance(value, list) else [value])
    if capability.get("device_log") != "supported" and any(contains_log_request(value) for value in values):
        return True
    failed = " ".join(context.get("follow_up", {}).get("failed_actions") or []).lower()
    proposed = " ".join(str(result.get(key) or "") for key in ("ai_suggested_next_step", "solution", "reply_en")).lower()
    return "connector" in failed and "connector" in proposed and "check" in proposed


def _insufficient(result, missing=None, reasons=None):
    missing = missing or ["the exact symptom, product model, and result of the checks already completed"]
    reasons = reasons or ["these facts are required before a safe technical next step can be selected"]
    result.update({
        "information_status": "insufficient",
        "missing_information": missing,
        "reason_for_request": reasons,
        "next_action": "request_information",
        "ai_suggested_next_step": "Request required information.",
        "solution_state": "PENDING",
        "solution": "",
        "reply_en": _request_reply(missing),
    })
    return result

def _inspector_hash(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()

def analyze_case_for_inspector(case):
    data={k:case.get(k) for k in ('description','case_history','fault_symptom','pie_comment','solutions','model_type','error_codes','status')}
    context=case.get("context_pack") or {}
    guidance="\nNo reliable historical evidence was found: use current-ticket facts only; do not invent verified precedent." if context.get("knowledge_coverage")=="none" else "\nContext evidence is supplied with provenance; distinguish evidence from inference. Do not repeat actions explicitly reported ineffective unless explaining why."
    model=str(case.get("model_type") or data.get("model_type") or "")
    capability=capabilities(model)
    contract="\nReturn additionally: information_status (sufficient|insufficient), missing_information[], reason_for_request[], next_action (assess|request_information), confirmed_facts[], already_tried[], ruled_out[], hypotheses[] (cause, confidence high|medium|low, evidence[], cited[], discriminator), resolution_path[], needs_human_check, escalation[], parts_to_verify[] (always empty). customer_description preserves original customer/dealer wording. Write repair_actions, current_blocker, historical_pie_recommendations, ai_suggested_next_step, solution, missing_information and reason_for_request in clear Simplified Chinese. Preserve product names, models, error codes, part numbers, firmware versions, LogiQ, Mammotion Kit, connector names and proprietary module names. Historical ITR and technical notes are evidence, never confirmed facts. hypothesis.cited may use only real Context Pack provenance IDs. If insufficient, reply_en must only request the listed information and must not add diagnosis/actions. If sufficient, reply_en must not introduce actions absent from assessment/solution. Never request logs or LogiQ unless Product capability explicitly says supported. Product capability: "+json.dumps(capability)
    result=_call_deepseek(INSPECTOR_SYSTEM_PROMPT+guidance+contract, json.dumps({"case":data,"context":context}, ensure_ascii=False))
    rec=list(result.get('historical_pie_recommendations') or [])
    state=str(result.get('solution_state') or 'NONE').upper()
    if state not in {'FINAL','CURRENT','WORKAROUND','PENDING','NONE'}: state='NONE'
    status=str(result.get("information_status") or "sufficient").lower()
    missing=_as_text_list(result.get("missing_information")); reasons=_as_text_list(result.get("reason_for_request"))
    if status == "insufficient":
        result = _insufficient(result, missing, reasons)
    elif _restricted_or_repeated(result, context, capability):
        result = _insufficient(result)
        status = "insufficient"; missing=result["missing_information"]; reasons=result["reason_for_request"]
    elif not str(result.get("ai_suggested_next_step") or "").strip() and not str(result.get("solution") or "").strip() and str(result.get("reply_en") or "").strip():
        result = _insufficient(result)
        status = "insufficient"; missing=result["missing_information"]; reasons=result["reason_for_request"]
    else:
        status="sufficient"; result["next_action"]="assess"
    state=str(result.get("solution_state") or state).upper()
    if state not in {'FINAL','CURRENT','WORKAROUND','PENDING','NONE'}: state='NONE'
    next_action=str(result.get("next_action") or ("request_information" if status=="insufficient" else "assess"))
    result = validate(result, context, capability, status == "insufficient" or _restricted_or_repeated(result, context, capability))
    return InspectorAnalysis(str(result.get('customer_description') or ''), [str(x) for x in result.get('repair_actions',[])], str(result.get('current_blocker') or ''), bool(result.get('blocker_is_inferred')),
        rec, '' if rec else str(result.get('ai_suggested_next_step') or ''), state, str(result.get('solution') or ''), str(result.get('reply_en') or ''), 'ORIGINAL', _inspector_hash(data),status,missing,reasons,next_action,capability,
        result["confirmed_facts"], result["already_tried"], result["ruled_out"], result["hypotheses"], result["resolution_path"], result["needs_human_check"], result["escalation"], result["parts_to_verify"])

def translate_inspector_analysis_to_zh(analysis):
    fields=['customer_description','repair_actions','current_blocker','historical_pie_recommendations','ai_suggested_next_step','solution']
    prompt='Translate only these JSON values to Chinese. Preserve structure. Do not analyze or add facts.'
    return _call_deepseek(prompt, json.dumps({k:getattr(analysis,k) for k in fields}, ensure_ascii=False))

def translate_text_to_zh(text):
    prompt = "Translate this text to Simplified Chinese only. Preserve product names, models, error codes, part numbers, firmware versions, LogiQ, Mammotion Kit, connector names and proprietary module names. Do not add analysis or facts."
    return _call_deepseek(prompt, str(text or ""))


def _live_options(field_name, fallback):
    try:
        options = feishu_api.get_select_field_options(field_name)
        if options:
            return options
    except Exception as exc:
        print(f"  Warning: unable to read options for {field_name}: {exc}")
    return fallback


def _disti_options():
    return _live_options("Disti/Dealer/Service Point", fo.DISTI_DEALER)


def _model_options():
    return _live_options("Model Type", fo.MODEL_TYPE)


V2_PROMPT = """You are an ITR technical-case extraction assistant.
The input is the complete Case History of one real support case. It preserves
source messages in order. Labels beginning with PIE identify PIE replies;
other senders are customer/dealer-side communication unless the content itself
reliably says otherwise.

Return JSON only, with exactly these keys:
{
  "device_name": "",
  "disti_dealer": "",
  "model_type": "",
  "pie_comment": "",
  "description": "",
  "solutions": "",
  "fault_symptom": [],
  "error_code": [],
  "error_massages": ""
}

Rules:
- Description contains only customer/dealer technical facts. Preserve their
  English original wording; do not translate it to Chinese and do not include
  PIE replies. Keep reported symptoms, already performed tests/replacements
  and their results, explicit error codes/messages, device name and versions.
  Never turn a PIE recommendation into a completed customer action.
- Solutions is Chinese and lists only technical advice, requested actions, or
  information requests actually made by PIE in this Case History. Preserve
  modality: recommended/requires/check/flash/upload is not completed/verified.
- PIE-Comment is a short Chinese summary of the core problem, based mainly on
  Description, symptoms, codes and error messages. Do not repeat Solutions.
- Use only explicit evidence. Do not invent message times, senders, device
  facts, dealer, errors, or actions.
- device_name is only a concrete, uniquely identifying device identifier
  explicitly present in the source (for example a real device name, serial
  number, or device-specific identifier). Product models and product series
  such as LUBA 3, LUBA 2, LUBA mini, YUKA, and YUKA mini are Model Type only,
  never device_name. If no unique device identifier is explicit, return "".
- disti_dealer and model_type must be one of the supplied options or "".
- fault_symptom and error_code must contain only supplied existing options.
  If uncertain, return [] rather than guessing.
- error_massages contains descriptive error wording only, not numeric-only
  error codes.
"""


def _call_deepseek(system_prompt, user_content, retries=5):
    if not config.DEEPSEEK_API_KEY or not config.DEEPSEEK_BASE_URL:
        raise RuntimeError("DeepSeek credentials are not configured.")
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.post(
                f"{config.DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": getattr(config, "DEEPSEEK_MODEL_FAST", None) or "deepseek-v4-flash",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1,
                },
                timeout=(20, 150),
            )
            response.raise_for_status()
            return json.loads(response.json()["choices"][0]["message"]["content"])
        except Exception as exc:
            last_error = exc
            if attempt < retries - 1:
                _time.sleep(2 ** attempt)
    raise RuntimeError(f"DeepSeek call failed after {retries} attempts: {last_error}")


def analyze_case_history(case_history: str, manual_messages=None) -> dict:
    """Extract only V2 case-facts fields from a complete Case History."""
    prompt = (V2_PROMPT
              .replace("supplied options", "supplied existing Feishu options")
              + "\nDealer options: " + ", ".join(_disti_options())
              + "\nModel options: " + ", ".join(_model_options())
              + "\nFault Symptom options: " + ", ".join(fo.FAULT_SYMPTOM)
              + "\nError Code options: " + ", ".join(fo.ERROR_CODE))
    if manual_messages is not None:
        indexed = "\n".join(
            f"[{item['id']}] {item['content']}" for item in manual_messages
        )
        prompt += """

This is a manual-source case. Do not infer a responder identity from phone
numbers, sender names, order, or tone. Classify message function from content
and context: a Support Reply gives a concrete technical answer, applicability,
diagnosis, advice, requested information, test, step, or handling decision.
A new question or feedback such as 'still not working' is not a Support Reply.
For manual sources, Description records the question/facts and concise
confirmed answers in English. Solutions records actual Support Replies in
Chinese without saying who replied. PIE-Comment is a concise Chinese summary.
Do not write phrases such as 'Another participant replied'.

Return one additional JSON key only for this call:
"support_reply_ids": [integer message IDs from the indexed messages below].
Include only IDs whose content is reliably a Support Reply. Do not invent IDs.
Indexed manual messages:
""" + indexed
    result = _call_deepseek(prompt, case_history)
    return {
        "device_name": result.get("device_name", ""),
        "disti_dealer": result.get("disti_dealer", ""),
        "model_type": result.get("model_type", ""),
        "pie_comment": result.get("pie_comment", ""),
        "description": result.get("description", ""),
        "solutions": result.get("solutions", ""),
        "fault_symptom": result.get("fault_symptom", []),
        "error_code": result.get("error_code", []),
        "error_massages": result.get("error_massages", ""),
        "support_reply_ids": [item for item in result.get("support_reply_ids", [])
                              if isinstance(item, int)] if manual_messages is not None else [],
    }


# Compatibility entry point for callers during the V2 transition.
def analyze(case_history: str) -> dict:
    return analyze_case_history(case_history)


def analyze_lark(text: str) -> dict:
    return analyze_case_history(text)

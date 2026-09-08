# Stable guidance promotion audit — task006

Task: EC-MT-20260908-STABLE-GUIDANCE-PROMOTION-006. Authority: supervisor's OPERATIONAL_MATURITY_DECISION_2026-09-08.md and subsequent READY task. This supersedes the earlier lack-of-maturity finding for the approved portions. No production Feishu/Nextop/ITR access or new case audit was performed.

## Decisions and counts

The original19 source records remain byte-equivalent in content outside review, plus the separately frozen1202 record. Nine candidates now have approved guided portions, represented by10 new Page2 cards. Seven cards are conditional repairs;3 are checks/process guidance. Original replacement/fallback wording remains private and is not approved wholesale.

| Candidate | Published portion | Scope/limit |
|---|---|---|
| REP-WHEEL-001 | Wheel motor/driver-board isolation and confirmed serviceable repair | LUBA2/2X/3; supported tool; simultaneous motor failures go to shared-power PIE review; no automatic mainboard |
| REP-CUT-001 | Actual-operation blockage/motor process | LUBA1/2/2X/3; explicit non1202, actual mowing/manual symptom; test-only software path remains separate; no driver/cable fallback |
| REP-CHARGE-001 | Two cards: no charge; station not recognized | No-charge includes LUBA1/2/2X/3; recognition includes2/2X/3. Compatible controlled source comparison; combined swap does not identify a component; no board chain |
| REP-DOCK-001 | Clean contacts/IR and evaluate supported station-side docking path | LUBA2/2X/3; check/process only, unresolved robot-side repair remains PIE |
| REP-POWER-001 | Model-supported battery supply/button/connection assessment | LUBA2/2X/3; no invented threshold; replacement requires established fault/serviceability; no mainboard default |
| REP-RTK-001 | Confirmed station-side adapter/station repair | LUBA2/2X/3; mower-side GNSS/LoRa remains PIE |
| REP-BUMP-001 | Clear mechanism and confirmed serviceable bumper/sensor repair | LUBA2/2X/3; Hall/chassis and non-serviceable cases remain PIE |
| REP-CABLE-001 | Correct model-serviceable visibly damaged cable/harness | LUBA2/2X/3; normal or unconfirmed cable is not replaced; downstream effects remain PIE |
| REP-FW-001 | Current tool/firmware/component reconciliation and applicable update method | LUBA2/2X/3; check/process only; no universal version, undocumented recovery or board default |

No new direct split is published for POS/WIFI/LIDAR. Their operational domain is mature, but this decision does not supply precise enough observable architecture-specific replacement branches. Existing positioning/map/Wi-Fi/4G distinctions and model/code-specific LiDAR escalation remain. WATER/PHY stay mature PIE-controlled assessment. WHEEL-003, CUT-002, CHARGE-002, POWER-002 and BT-001 remain weaker SOURCE_RECOMMENDATION/PIE_ONLY.

Totals within19:9 AGENT_GUIDED,10 PIE_ONLY;14 STABLE_OPERATIONAL_GUIDANCE,5 SOURCE_RECOMMENDATION. Extra REP-1202-001 is CONFLICTING_EVIDENCE/WITHHELD outside the denominator. Current canonical product:31 cards,37 paths,28 symptoms (25 normal navigation,3 reservedPIE). Earlier21 cards and27 paths remain unchanged; this adds10 scoped cards/paths and reciprocal candidate links.

## Evidence interpretation

The source's original Feishu evidence labels, priority, model wording, actions, verification and fallback are preserved separately from current review. `previous_review` retains earlier full-path reservations. Current review's `publication_scope` and promoted_refs identify the approved portions; the supervisor-accepted maintained/repeated-use signal is attributed explicitly. First operational use, numeric reuse counts, success rates and full-case outcomes are not invented. Source payload digest remains edc38d9ec9e9d0c4f9be47cbefb087f9f5975ea7378cf045aa4142dc1cb441f1.

The source-declared family selectors do not infer capacity or parts interchangeability. Model/tool support and correct serviceable component must still be established. Stable process maturity does not authorize all hardware fallbacks. Every new step retains standard canonical validation, relevant path verification, three reports and Connect Checking screenshot where applicable; missing required testing or failed/returned symptoms go to PIE without repeating replacements.

## Product and review

Page1 remains identification-only, including the two distinct cutting-condition choices and explicit non1202 qualifier. Page2 alone renders the approved process/repair. Tests check actual empty solution DOM on Page1 for every new card, exact-message/symptom convergence, wrong-model guards, Back/reentry and failed-step handling. Two UI refinements were reproduced and fixed: null-part checks no longer show a generic faulty-part placeholder; multi-path symptom choices survive a model edit before selection.

Independent source/content review and bounded UI re-review found0 unresolved Critical/Important/Minor. See FINAL_STABLE_GUIDANCE_REVIEW_2026-09-08.md and HANDOFF.md for final acceptance/artifact. Source/evidence/candidate IDs remain outside public HTTP assets and ZIP; no new knowledge engine or production integration was added.

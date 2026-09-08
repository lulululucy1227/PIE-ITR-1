# Evidence audit and candidate selection

Task: EC-MT-20260907-PILOT-001. Snapshot from canonical base 34b4cd242962b33b4cb2de0fe1daa02f5cf0448e, reviewed locally 2026-09-07. This is an engineering/evidence review, not external knowledge promotion.

## Available evidence

- MAIN existing parsed ErrorCode table, read-only: knowledge/desktop_reference_20260907_p0_additions/data/tables/error-codes.json.
- Source workbook SHA256: 5b684cf277d4ee8b768c2c62e9f436194a207fa879c27fecfe2c8e2e774753cd.
- Parsed table SHA256: 5bcaeef54e10b8a24ec73ce30ad1046b593e0268057957644eaa5ca8a7dc67f5.
- One sheet, 793 × 44. 792 parsed rows include the secondary machine header at row 2. There are 791 valid, unique code rows, including code 0.
- Types: user 418, debug 373. Severity: serious 18, warning 119, hint 654. These are reference inventory counts, NOT support frequencies or repaired-machine counts.
- The label 提示 includes 1202, 1008, 1500, 5501 and 6401. It cannot safely determine no-repair behavior.
- Raw fields: A code; B user/debug type; C module; D engineering location; E source severity; F/G/H Chinese implication/handling/button; I/J/K English equivalent, then other translations.
- Raw source remains in MAIN, unmodified, unreviewed and ineligible for direct replies. No original spreadsheet was reparsed and no raw rows were copied to the specialist knowledge store. The reproducible audit script reads only this named table and writes only aggregate metadata in artifacts/source-audit.json.
- Promoted knowledge: ERROR_CODES.md, KNOWN_FIXES.md, relevant PARTS_KNOWLEDGE.md and TOOL_KNOWLEDGE.md; diagnostic architecture and reusable regression assertions.
- Relevant Issue #1 learning was examined by the read-only auditor. Current comments did not supply the missing 1202 model scope. Unpromoted learning was not converted into official repair advice.
- No full real ITR/Nextop outcome cohort was read: this task forbids manipulating those auth/session states. No raw case mirror, raw chat, customer/device identifier or full history was imported. Historical outcomes in promoted knowledge are the available outcome evidence.

## Ranked selection

Ranks reflect available operational value and evidence, not measured frequency. Eight entries were selected for specific value; coverage count was not a target.

| Priority | Code | Reason / source | Classification and treatment |
|---|---|---|---|
| 1 | 1202 | Promoted direct service sequence; physical blockage vs free discs materially changes action. ERROR_CODES#1202, raw row747. | NOT_YET_STABLE until model scope confirmed. Mechanical check available; cable/mainboard are canonical candidates only. Agent projection strips replacement prose. |
| 2 | 1008 | Avoid needless keypad replacement/NFF on non-reproduction; distinguish external STOP trigger from recurrence. ERROR_CODES#1008, raw row735. | SELF_SERVICE_SYMPTOM_SPLIT: observed trigger, workshop cannot reproduce, recurrence. No confident keypad replacement. PIE owns NFF decision. |
| 3 | 6401 | Verified historical second vision-module replacement enabled wired upgrade. Counterexample to replacement=known-good. ERROR_CODES/KNOWN_FIXES#6401, raw row726. | PIE_ONLY; no broad replacement rule. Model and cohort unavailable. |
| 4 | 5501 | Upgrade failure can involve LiDAR/data connection; failure percentage does not prove network or faulty part. ERROR_CODES/KNOWN_FIXES#5501, raw row294. | PIE_ONLY; retain module-health evidence route. |
| 5 | 1000022 | Scoped historical resolved firmware outcome on LUBA mini 2 1000 Vision. ERROR_CODES/KNOWN_FIXES#1000022, raw row486. | HISTORICAL / PIE_ONLY. Former 2.3.30.26 target never becomes a current install instruction. |
| 6 | 1500 | Same code requires model-capability-aware communication path. ERROR_CODES#1500, raw row725. | PIE_ONLY; exact model and module state requested, no fixed part. |
| 7 | DT-041 | Prevent default mainboard replacement for communication timeout. ERROR_CODES#DT-041. | PIE_ONLY. Absent from raw table; stored message is promoted description, not claimed exact UI wording. |
| 8 | 5510 | Source explicitly says self-calibration success needs no handling; prevents unnecessary repair. Raw I323:K323. | SELF_SERVICE_SYMPTOM_SPLIT: normal function/no other fault -> no repair for message; abnormal -> PIE. No real support-frequency claim. |

Other raw-master entries are EXCLUDE_FROM_PILOT by default until reviewed for operational value and reliable action. This is withholding, not an assertion that those codes are unimportant. Success codes 2303 and 0 were audited as candidates but add little initial value beyond 5510; debug/internal/noise is not bulk-published.

## Outcome and counterexample discipline

- 1202 is a PIE-confirmed recommendation, not a measured repair success cohort. No model scope is recorded in the promoted rule. Parts reference rows showing cables in LUBA 1, LUBA 2/2X and LUBA 3 do NOT establish applicability of the service sequence.
- 6401 and 1000022 have documented historical resolved outcomes, but no denominator or full validation report set available. Neither establishes a success percentage.
- 5501 is a diagnostic handling pattern, not guaranteed replacement success.
- 1008 non-reproduction is not proof of repair and does not authorize keypad replacement or automatic NFF.
- Replaced, new, tried, resolved, returned and verified are separate facts. A repeated/returned fault does not restart the same replacement.
- UI Fixed requires an explicit check confirmation and records no state outside the current page. It states user-reported resolution, never verified NFF or ticket closure.

## Remaining business decision

Confirm exact models/series and material firmware/tool limits for the promoted 1202 free-disc -> Upper Shell Adapter Cable -> mainboard sequence. Alternatively provide a promoted repair path with adequate scope. Until then, there are ZERO real direct replacement paths in the agent build; two 1202 hardware steps remain canonical candidates. Synthetic fixture tests prove the engine capability but are not evidence of real repair efficacy.

S2 full-cohort coverage remains an explicit data limitation, not a reason to stop other work. No business data, service-frequency or outcome certainty has been invented.

## Desktop continuation (2026-09-08)
The current task's per-path promotion decisions, explicit source limitations and 1202 freeze are in KNOWLEDGE_PROMOTION_AUDIT_2026-09-08.md. Prior pilot ranking/outcome notes remain historical; they do not define the new desktop gate.

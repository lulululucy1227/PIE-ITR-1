# PIE Troubleshooter — Feishu Audit + Knowledge Build Task

Status: READY
Owner: Troubleshooter｜主管
Executor: Feishu / Lark execution agent
Mode: READ SOURCES + BUILD APPROVED TROUBLESHOOTER KNOWLEDGE ONLY

## Objective

Do not stop at auditing. Use current Feishu evidence to build the first operational knowledge set for PIE Troubleshooter.

Primary sources:
1. ITR main table — real support frequency, observed symptoms, repairs, replaced parts, outcomes, verification.
2. 工单速查 — existing reusable conclusions, repair guidance, verification, knowledge status and conflicts.
3. 信息同步库 — current technical updates, service conclusions, part/repair/verification information and other reusable synchronized knowledge relevant to Troubleshooter.
4. Existing ITR label/taxonomy data — vocabulary/source context only; do not automatically expose internal labels as agent-facing symptoms.

The build must produce a sanitized controlled knowledge layer that Builder can consume directly for the desktop web product.

## A. ITR main table audit

Read the current ITR main table and identify both:
- high-frequency Error Codes / Error Messages;
- high-frequency symptom-only cases where no Error Code is present.

Where current fields/evidence allow it, aggregate:
- Error Code / normalized Error Message if present;
- exact ITR occurrence count obtainable from the table;
- affected product/model distribution when available;
- recurring observable fault phenomenon;
- component actually replaced/repaired when recorded;
- handling/solution actually used;
- final result/outcome when recorded;
- verification evidence/method when recorded;
- unresolved / repeated / replacement-failed patterns;
- whether the case looks suitable for agent self-service.

Rules:
- count actual ITR records; do not infer frequency from Error Code reference data;
- do not invent missing outcomes;
- normalize obvious textual variants only when clearly equivalent;
- distinguish exact-code cases from symptom-only cases;
- preserve model/version differences when they materially change the repair conclusion.

## B. 工单速查 review

Read current 工单速查 and match it against both high-frequency Error Codes and high-frequency symptom-only problems.

Extract reusable fields only:
- Error Code / related symptom;
- core observable fault phenomenon;
- known conclusion;
- recommended repair/handling;
- fault component/replacement part;
- verification method;
- knowledge status/currentness;
- useful troubleshooting/reply guidance;
- conflicts/gaps/outdated conclusions compared with ITR actual outcomes.

Identify:
- high-frequency ITR problems missing useful 工单速查 coverage;
- duplicate/contradictory entries;
- outdated or weakly supported entries;
- entries too technical/internal for agent-facing publication.

## C. 信息同步库 review

Read the current 信息同步库 for content relevant to high-frequency Error Codes and symptom-only problems.

Use it to identify:
- newer technical conclusions not yet reflected in 工单速查;
- updated repair or replacement guidance;
- model/version scope corrections;
- service part relationships;
- verification changes;
- warnings that a previously common repair path is superseded or incomplete.

Do not assume information-sync content is automatically canonical. Reconcile it against actual ITR outcomes and existing reviewed knowledge. Mark unresolved conflicts for PIE review rather than choosing silently.

## D. Build the controlled symptom library

PIE Troubleshooter must support cases with no Error Code, but agents must NOT freely describe a symptom and have that free text directly drive diagnosis.

Build a controlled `SYMPTOM_LIBRARY` from actual ITR + 工单速查 + 信息同步库 evidence.

### Symptom definition

A publishable symptom is an observable machine/user-facing state BEFORE diagnosis.

Allowed examples in principle:
- machine does not power on;
- one drive wheel does not move;
- mower cannot charge;
- positioning is unavailable;
- cutting disc does not rotate;
- Wi-Fi/Bluetooth cannot connect;
- error appears but normal function remains.

Not symptoms:
- mainboard failure;
- motor damaged;
- CAN communication root cause;
- replace wheel motor;
- firmware bug;
- R&D analysis required.

Those belong to cause/component/action/internal knowledge, not the symptom selector.

### Symptom boundary rules

Each controlled symptom should:
1. describe something the agent can directly observe or confirm;
2. avoid embedding a suspected cause or repair action;
3. represent one primary phenomenon, not several unrelated problems in one option;
4. be short enough to scan quickly;
5. be distinct enough from neighboring choices to change the next repair path;
6. retain model/product applicability where the same wording has materially different meaning;
7. merge wording variants/synonyms only when they lead to the same practical path;
8. split a broad symptom when real evidence shows materially different repair paths;
9. never create a category solely because an internal label exists.

### Hierarchy

Use the smallest hierarchy that works with the real data.

Preferred default:
`Observable area/category -> controlled symptom`

Only add a third level when the second-level option is still too broad to choose a useful repair path.

Existing ITR L1/L2/L3 may help seed candidate groupings, but must be audited because internal labels can mix phenomenon, cause, component or business classification.

### Unknown symptom behavior

Provide a controlled fallback such as `None of these / Other issue`.

If free text is collected there, it is feedback for future taxonomy review only. It must not automatically produce a part replacement recommendation.

## E. Build canonical Troubleshooter records

For each sufficiently supported path, build a sanitized canonical record usable by Builder.

Two supported entry patterns:

### Error-code entry
`ERROR_CODE / ERROR_MESSAGE -> CONTROLLED_SYMPTOM -> PART -> REPAIR -> VERIFICATION -> IF_NOT_FIXED`

### Symptom-only entry
`CONTROLLED_SYMPTOM -> PART / ACTION -> REPAIR -> VERIFICATION -> IF_NOT_FIXED`

Internal metadata may retain:
- product/model scope;
- version/tool scope when material;
- evidence source(s);
- ITR occurrence count where valid;
- outcome evidence;
- knowledge status/currentness;
- agent visibility;
- alternative/failed replacement behavior;
- conflict/supersession notes.

Do not create a confident part/replacement mapping when evidence is insufficient.

## F. Prioritize and build, not merely report

Classify each candidate:
1. `P0_DESKTOP_SELF_SERVICE` — frequent/value-high + clear controlled symptom + clear part/action + clear verification.
2. `P1_DESKTOP_GUIDED` — valuable but needs a simple symptom split or one decisive check.
3. `P2_PIE_ONLY` — frequent but not stable/safe enough for direct agent repair guidance.
4. `LOW_PRIORITY / EXCLUDE` — low-value, internal-only, informational/noise, or not worth current product work.

For P0/P1, construct the actual agent-facing content fields:
- entry code/message if applicable;
- controlled symptom option;
- most likely faulty part when supported;
- direct repair/action wording;
- verification wording;
- Still-not-fixed fallback;
- applicable model/scope if agents need to choose it.

The task is not complete with a spreadsheet/report only. It must leave Builder a directly consumable sanitized knowledge dataset/specification for the desktop web.

## G. Desktop-first product requirement

Current priority is PC/desktop web.

Design knowledge presentation for fast desktop scanning:
- two obvious entry modes: `I have an Error Code` and `I do not have an Error Code`;
- symptom selection uses controlled buttons/cards/dropdowns, not a diagnostic free-text box;
- keep paths short;
- prioritize part/action/verification visibility;
- mobile needs basic compatibility only, not current optimization.

## Write boundaries

Allowed:
- READ ITR main table, 工单速查, 信息同步库 and related taxonomy/source tables;
- create/update the dedicated PIE Troubleshooter knowledge construction area specifically approved for this task if such a dedicated area already exists or can be created without modifying protected source tables;
- produce sanitized build output/report.

Not allowed:
- modify ITR main table records/schema/formulas/labels;
- rewrite 工单速查 or 信息同步库 as part of this task;
- bulk backfill or delete source records;
- write raw chats, device SN/Device Name, agent identities or other PII into Troubleshooter knowledge;
- invent repair certainty or statistics.

If no dedicated Troubleshooter destination exists in Feishu, do not repurpose the ITR main table. Produce the complete sanitized construction dataset/report and identify the required destination structure for supervisor approval.

## Acceptance

Complete only when all are true:
1. real ITR high-frequency Error Code ranking exists;
2. high-frequency symptom-only problems are separately identified;
3. 工单速查 and 信息同步库 have been reconciled against those real problems;
4. a controlled symptom library has been built under the boundary rules above;
5. P0/P1/P2/EXCLUDE classification is complete for the high-value set;
6. P0/P1 records contain actual agent-facing symptom/part/repair/verification/fallback content;
7. conflicts/evidence gaps are explicit rather than guessed;
8. Builder can consume the resulting sanitized dataset/spec directly for the desktop web without redoing the Feishu analysis.

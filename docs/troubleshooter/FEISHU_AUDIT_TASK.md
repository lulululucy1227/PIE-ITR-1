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
4. ITR 标签体系表 — existing L1/L2/L3 taxonomy used as a candidate grouping/normalization source, not as an agent-facing hierarchy by default.

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
- current L1/L2/L3 tags when present;
- whether the case looks suitable for agent self-service.

Rules:
- count actual ITR records; do not infer frequency from Error Code reference data;
- do not invent missing outcomes;
- normalize obvious textual variants only when clearly equivalent;
- distinguish exact-code cases from symptom-only cases;
- preserve model/version differences when they materially change the repair conclusion;
- use current tags as evidence of historical grouping, not as proof that the grouping is correct for Troubleshooter.

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

## D. 标签体系语义审计

Read the current ITR 标签体系表 and audit L1/L2/L3 semantically before using any of it in PIE Troubleshooter.

For every relevant current label, classify its semantic type into one of:
- `OBSERVABLE_AREA` — broad function/observable area potentially suitable for first-level symptom navigation;
- `OBSERVABLE_SYMPTOM` — direct agent-observable phenomenon potentially suitable for a controlled symptom;
- `QUALIFIER` — side/location/state distinction that may be useful only when it changes the repair path;
- `FAULT_CAUSE` — inferred/confirmed cause; internal knowledge only;
- `COMPONENT` — faulty/related part; belongs to repair result, not symptom navigation;
- `ACTION` — repair/check/handling action; not a symptom;
- `BUSINESS_INTERNAL` — warranty/routing/workflow/internal classification; not a symptom;
- `AMBIGUOUS_MIXED` — mixes phenomenon/cause/component or cannot be safely interpreted.

For each audited label, record:
- current L1/L2/L3 path;
- semantic type;
- whether it can be reused unchanged, renamed, split, merged, moved to backend-only knowledge, or excluded;
- related ITR frequency/usage if obtainable;
- conflicts or legacy/duplicate patterns;
- proposed Troubleshooter mapping if any.

Important:
- do NOT assume `L1 -> L2 -> L3` should become the Troubleshooter hierarchy;
- a label is eligible for agent-facing symptom use only if an agent can select it without already knowing the diagnosis;
- labels containing a root cause, component, repair action or internal routing must not appear as agent-facing symptoms;
- a third level is justified only when it materially changes the next part/action.

Produce an explicit mapping:

`ITR taxonomy label/path -> semantic type -> Troubleshooter Observable Area / Controlled Symptom / Qualifier / Backend-only / Exclude`

This mapping is part of the required build output.

## E. Build the controlled symptom library

PIE Troubleshooter must support cases with no Error Code, but agents must NOT freely describe a symptom and have that free text directly drive diagnosis.

Build a controlled `SYMPTOM_LIBRARY` from actual ITR + 工单速查 + 信息同步库 + audited taxonomy evidence.

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
9. never create a category solely because an internal label exists;
10. prefer wording already familiar to agents/PIE when that wording remains observable and unambiguous.

### Hierarchy

Use the smallest hierarchy that works with the real data.

Preferred default:
`Observable area/category -> controlled symptom`

Only add a third level when the second-level option is still too broad to choose a useful repair path.

Existing ITR L1/L2/L3 may seed candidate groupings only after the semantic audit in section D.

### Aliases and historical wording

For every canonical symptom, retain known wording variants/aliases from real ITR language where they clearly describe the same observable state and lead to the same practical path.

Aliases may help search/matching, but arbitrary free text must not directly generate a part or repair recommendation.

### Unknown symptom behavior

Provide a controlled fallback such as `None of these / Other issue`.

If free text is collected there, it is feedback for future taxonomy review only. It must not automatically produce a part replacement recommendation.

## F. Build canonical Troubleshooter records

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
- source ITR taxonomy mapping;
- outcome evidence;
- knowledge status/currentness;
- agent visibility;
- alternative/failed replacement behavior;
- conflict/supersession notes.

Do not create a confident part/replacement mapping when evidence is insufficient.

## G. Prioritize and build, not merely report

Classify each candidate:
1. `P0_DESKTOP_SELF_SERVICE` — frequent/value-high + clear controlled symptom + clear part/action + clear verification.
2. `P1_DESKTOP_GUIDED` — valuable but needs a simple symptom split or one decisive check.
3. `P2_PIE_ONLY` — frequent but not stable/safe enough for direct agent repair guidance.
4. `LOW_PRIORITY / EXCLUDE` — low-value, internal-only, informational/noise, or not worth current product work.

For P0/P1, construct the actual agent-facing content fields:
- entry code/message if applicable;
- Observable Area;
- controlled symptom option;
- optional qualifier only where needed;
- most likely faulty part when supported;
- direct repair/action wording;
- verification wording;
- Still-not-fixed fallback;
- applicable model/scope if agents need to choose it.

The task is not complete with a spreadsheet/report only. It must leave Builder a directly consumable sanitized knowledge dataset/specification for the desktop web.

## H. Desktop-first product requirement

Current priority is PC/desktop web.

Design knowledge presentation for fast desktop scanning:
- persistent model/product context where useful;
- two obvious entry modes: `I have an Error Code` and `I do not have an Error Code`;
- Error path: code/message -> controlled symptom only when needed -> repair card;
- Symptom path: Observable Area -> controlled symptom -> optional qualifier -> repair card;
- symptom selection uses controlled buttons/cards/dropdowns, not a diagnostic free-text box;
- keep paths short;
- prioritize part/action/verification visibility;
- mobile needs basic compatibility only, not current optimization.

## Required build outputs

The final output must include all of the following, not only a narrative report:

1. `HIGH_VALUE_PROBLEM_SET`
   - ranked high-frequency Error Code and symptom-only problems;
   - actual ITR counts where obtainable;
   - P0/P1/P2/EXCLUDE classification.

2. `TAXONOMY_SEMANTIC_AUDIT`
   - current L1/L2/L3 labels and paths;
   - semantic type;
   - reuse/rename/split/merge/backend/exclude decision;
   - mapping into Troubleshooter if applicable.

3. `CONTROLLED_SYMPTOM_LIBRARY`
   - Observable Area;
   - canonical controlled symptom;
   - aliases/known wording variants;
   - optional qualifier;
   - product/model scope;
   - linked Error Codes where applicable;
   - P0/P1/P2 status.

4. `REPAIR_KNOWLEDGE_SET`
   - Error Code/Error Message when applicable;
   - controlled symptom;
   - most likely part/action when supported;
   - repair wording;
   - verification;
   - if-not-fixed fallback;
   - evidence/currentness/conflict note;
   - agent visibility/status.

5. `SOURCE_GAP_AND_CONFLICT_REPORT`
   - ITR vs 工单速查 vs 信息同步库 vs 标签体系 conflicts;
   - missing outcomes/scope/verification;
   - items requiring PIE decision.

These outputs must be sanitized so Builder can consume them without redoing the Feishu analysis.

## Write boundaries

Allowed:
- READ ITR main table, 工单速查, 信息同步库, 标签体系表 and related source tables;
- create/update the dedicated PIE Troubleshooter knowledge construction area specifically approved for this task if such a dedicated area already exists or can be created without modifying protected source tables;
- produce sanitized build output/report.

Not allowed:
- modify ITR main table records/schema/formulas/labels;
- rewrite 工单速查, 信息同步库 or 标签体系 as part of this task;
- bulk backfill or delete source records;
- write raw chats, device SN/Device Name, agent identities or other PII into Troubleshooter knowledge;
- invent repair certainty or statistics.

If no dedicated Troubleshooter destination exists in Feishu, do not repurpose the ITR main table. Produce the complete sanitized construction dataset/report and identify the required destination structure for supervisor approval.

## Acceptance

Complete only when all are true:
1. real ITR high-frequency Error Code ranking exists;
2. high-frequency symptom-only problems are separately identified;
3. 工单速查 and 信息同步库 have been reconciled against those real problems;
4. current ITR L1/L2/L3 labels have been semantically audited rather than copied blindly;
5. explicit `ITR taxonomy -> Troubleshooter` mapping exists;
6. a controlled symptom library has been built under the boundary rules above;
7. P0/P1/P2/EXCLUDE classification is complete for the high-value set;
8. P0/P1 records contain actual agent-facing symptom/part/repair/verification/fallback content;
9. conflicts/evidence gaps are explicit rather than guessed;
10. Builder can consume the resulting sanitized dataset/spec directly for the desktop web without redoing the Feishu analysis.

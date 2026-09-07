# PIE Troubleshooter — Feishu Read-Only Audit Task

Status: READY
Owner: Troubleshooter｜主管
Executor: Feishu / Lark execution agent
Mode: READ ONLY

## Objective

Use current Feishu data to determine what PIE Troubleshooter should build first. Audit the ITR main table for high-frequency Error Codes / Error Messages and compare those results against the current 工单速查 content.

Do not modify the ITR main table, 工单速查, schema, labels, formulas, options or records during this task.

## A. ITR main table audit

Read the current ITR main table and identify the Error Codes / Error Messages that appear most often in actual support records.

Where the current fields/evidence allow it, aggregate for each candidate:
- Error Code / normalized Error Message;
- number of occurrences or exact count obtainable from the table;
- affected product/model distribution when available;
- recurring fault phenomenon / agent-described symptom;
- component actually replaced/repaired when recorded;
- handling/solution actually used;
- final result/outcome when recorded;
- verification evidence/method when recorded;
- unresolved / repeated / replacement-failed patterns;
- whether the case looks suitable for agent self-service.

Important:
- count actual ITR records; do not infer frequency from Error Code master/reference data;
- do not invent missing outcomes;
- normalize obvious textual variants only when they clearly refer to the same code/message;
- distinguish exact code frequency from symptom-only cases that do not contain a code;
- preserve model/version differences when they materially change the repair conclusion.

## B. 工单速查 audit

Read the current 工单速查 and identify content relevant to the high-frequency Error Codes found in section A.

For each matching/high-value item, extract only reusable knowledge fields such as:
- Error Code / related symptom;
- core fault phenomenon;
- known conclusion;
- recommended handling / repair method;
- fault component / replacement part if present;
- verification method;
- knowledge status / confidence / currentness if present;
- existing reply/troubleshooting guidance if useful;
- conflicts, gaps or outdated conclusions compared with ITR actual outcomes.

Also identify:
- high-frequency ITR Error Codes with no useful 工单速查 coverage;
- 工单速查 Error Code entries that appear low-frequency or unsupported in current ITR data;
- duplicate/contradictory entries;
- entries that are too technical/internal for agent-facing publication.

## C. Prioritized output

Produce a sanitized audit report for Troubleshooter｜主管 and Builder. Do not copy raw chats, PII, device names/SNs, partner identities or full ticket histories.

Required ranking:
1. `P0_DESKTOP_SELF_SERVICE` — high-frequency + clear symptom + clear part/action + clear verification.
2. `P1_DESKTOP_GUIDED` — high-frequency/value but needs a simple symptom split or one decisive check.
3. `P2_PIE_ONLY` — frequent but not stable/safe enough for direct agent repair guidance.
4. `LOW_PRIORITY / EXCLUDE` — low-value, internal-only, informational/noise, or not currently worth product work.

For each P0/P1 candidate, provide:
- code/message;
- actual ITR count;
- top recurring symptom(s);
- most common successful part/action if supported;
- outcome evidence summary;
- verification method found;
- 工单速查 coverage status;
- recommended first-page card content;
- evidence gaps / caveats.

## D. Desktop-first product direction

Current product priority is PC/desktop web. The audit should therefore prioritize which content gives the highest value on a desktop portal first. Mobile compatibility is not the optimization target in this phase.

## Boundaries

- READ ONLY in Feishu.
- No ITR main-table modifications.
- No 工单速查 modifications.
- No bulk backfill, schema/label/formula/option changes.
- No GitHub raw-case mirror.
- No invented statistics or repair certainty.

## Acceptance

The task is complete when the report gives a defensible, ranked list of real high-frequency Error Codes from the ITR main table and a side-by-side coverage/gap audit against 工单速查, sufficient for Builder to choose the next desktop-web content expansion without guessing.

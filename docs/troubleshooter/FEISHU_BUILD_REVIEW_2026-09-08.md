# PIE Troubleshooter — Feishu Build Review

Status: PARTIAL_ACCEPT / EVIDENCE-STATE RECLASSIFICATION REQUIRED
Reviewer: Troubleshooter｜主管
Date: 2026-09-08
Source: PIE Troubleshooter Feishu Knowledge Build Report 2026-09-08 + corrected VERIFIED KNOWLEDGE BUILD

## Accepted as useful evidence

The following parts are useful and may guide product priority:
- ITR population size and Error Code fill rate;
- high-frequency Error Code counts as observed in ITR;
- high-frequency symptom-only counts;
- broad KB coverage gaps, especially connectivity;
- relevant substantive technical/service content present in 信息同步库;
- evidence that Error Code cannot be the only product entry;
- corrected taxonomy separation between observable symptoms, components, causes and internal/business labels;
- corrected referential integrity of symptom and repair-path IDs;
- desktop-first product direction.

Important correction: the 信息同步库 field/value `需同步` is only an internal colleague-notification/reminder flag. It is not technical evidence and must not be used for currentness, conflict, KB coverage, or publishability decisions.

## Evidence-policy correction from Troubleshooter｜主管

The prior review was too strict in treating lack of explicit partner `solved` feedback as a blocker for mature repair guidance.

For PIE service operations:
- `VERIFIED_RESOLUTION` remains the strongest evidence;
- however, a repair method that has remained materially unchanged in maintained operational guidance for a meaningful period, is repeatedly retained/used in PIE/KB/service practice, and has not accumulated contradictory/reopen/superseding evidence may qualify as `STABLE_OPERATIONAL_GUIDANCE` even without explicit partner closure feedback.

Therefore:

`no explicit solved reply != no validation`.

Do not require every repair path to have an explicit post-repair partner confirmation before it can be used in Troubleshooter.

See `docs/troubleshooter/EVIDENCE_PROMOTION_POLICY.md`.

## Evidence states to use going forward

1. `VERIFIED_RESOLUTION`
   - explicit repair success + appropriate verification.

2. `STABLE_OPERATIONAL_GUIDANCE`
   - long-standing, actively maintained, repeatedly retained/used guidance;
   - no meaningful contradiction, repeated reopen/rework pattern or superseding rule;
   - scope sufficiently known;
   - explicit partner solved feedback is optional.

3. `ACTION_PERFORMED_OUTCOME_UNKNOWN`
   - action performed, result unclear, and insufficient operational stability yet.

4. `SOURCE_RECOMMENDATION`
   - recommendation exists but is relatively new/weakly scoped/sparsely used or not yet operationally mature.

5. `CONFLICTING_EVIDENCE`
   - credible evidence materially conflicts; do not publish as confident self-service until reconciled.

## Current assessment of corrected Feishu build

The corrected report is materially improved and may now be used as a candidate construction dataset, but its evidence labels are not yet final because it classifies all non-explicit-success paths only as `ACTION_PERFORMED_OUTCOME_UNKNOWN` or `SOURCE_RECOMMENDATION`.

This underestimates long-standing operational repair guidance.

Before final Builder publication, the affected high-value Repair Paths should be reviewed for possible upgrade to `STABLE_OPERATIONAL_GUIDANCE` using:
- age / duration in maintained service guidance;
- repeated appearance/retention in 工单速查, Solutions, 信息同步库 or PIE operating practice;
- absence of contradictory/reopen/replacement-failed evidence;
- known model/version scope;
- whether PIE has continued to use the same action without correction.

Do not invent explicit success counts that do not exist.

## Items that remain blocked or require care

### 1. 1202 remains frozen
The Feishu-derived cutting-motor path conflicts with the currently promoted 1202 cable -> mainboard path. Model scope remains unresolved. Keep `CONFLICTING_EVIDENCE / PIE_REVIEW_REQUIRED` until the user supplies the missing scope/decision.

### 2. Over-broad symptoms remain PIE-only
`行走异常/抖动`, `视觉/摄像头异常`, and `工作中异常停机` remain too broad for one stable repair path unless further split by observable distinctions.

### 3. Scope must remain evidence-backed
Do not expand a repair path from observed LUBA models to `ALL` products without evidence.

### 4. Internal tools/business areas stay out of the machine-symptom frontend
MammoSuite, Mammotion Kit, account/permission, warranty/claim and parts lookup remain internal/separate unless a future product decision explicitly includes them.

## Product architecture decision

Desktop home remains:
1. persistent Product/Model context;
2. prominent Error Code / Error Message search;
3. controlled `Choose by symptom` navigation visible on the same page;
4. both routes converge on the same canonical Repair Card.

Reason: only 38/737 ITR records contain an Error Code, so symptom navigation is operationally the dominant path while Error Code search remains a fast shortcut.

## Builder gate

Builder expansion no longer requires every P0/P1 path to become `VERIFIED_RESOLUTION`.

A path may be eligible for agent-facing P0/P1 when:
- symptom and scope are sufficiently clear;
- action is safe/executable for target agents;
- verification + fallback exist;
- evidence is either `VERIFIED_RESOLUTION` or `STABLE_OPERATIONAL_GUIDANCE`;
- no unresolved conflict/supersession exists.

The next evidence task is therefore **reclassification of mature guidance**, not collection of explicit solved feedback for every historical repair recommendation.

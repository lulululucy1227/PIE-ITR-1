# PIE Troubleshooter — Knowledge Green Supervisor Review

Status: ACCEPTED
Reviewer: Troubleshooter｜主管
Date: 2026-09-08
Accepted execution: `EC-MT-20260908-KNOWLEDGE-INGEST-004`
Accepted gate: `TROUBLESHOOTER_DESKTOP_KNOWLEDGE_GREEN`

## Acceptance

The Builder correctly completed the missing Feishu candidate-ingestion layer without regressing the desktop product.

Accepted facts from the final Issue #6 report:
- 19 non-1202 candidate Repair Paths were actually imported into the private/candidate layer;
- `REP-1202-001` remains separately frozen as conflicting evidence;
- candidate decisions: 0 promoted / 17 PIE_ONLY / 2 WITHHELD;
- evidence states for the 19: 5 `ACTION_PERFORMED_OUTCOME_UNKNOWN`, 12 `SOURCE_RECOMMENDATION`, 2 `CONFLICTING_EVIDENCE`;
- 64/64 Node tests passed;
- 33/33 browser checks passed;
- desktop product remains 21 cards / 27 canonical paths / 28 symptoms, with 25 normal navigation symptoms and 3 PIE-only symptoms;
- private candidate/provenance/review data remains absent from public HTTP assets and ZIP;
- lifecycle, extracted package, privacy and independent review gates passed;
- no MAIN workspace/runtime/8787/auth/case/analyzer mutation, production write, default/main merge or public deployment occurred.

## Important interpretation of `0 promoted`

`0 promoted` is accepted for this ingestion task, but it does NOT mean these repair methods are known to be ineffective.

The candidate payload supplied to Builder did not contain enough per-path operational-maturity evidence such as:
- earliest known use / how long the guidance has been actively used;
- repeated-use signal;
- whether the wording/action has remained materially unchanged in active PIE/KB practice;
- known contradiction / reopen / replacement-failed signal;
- source authority and maintenance status.

Under `EVIDENCE_PROMOTION_POLICY.md`, Builder must not infer `STABLE_OPERATIONAL_GUIDANCE` from age or silence alone. Therefore keeping paths private/PIE_ONLY was the correct decision with the available payload.

This also preserves the user's business correction: an explicit partner reply saying `solved` is NOT required. Stable maintained operational use can itself support publication once that stability is evidenced.

## Current product state

Engineering/local product gate: GREEN.
Knowledge ingestion/data-integrity gate: GREEN.
Agent-facing repair coverage maturity: PARTIAL.

The product is structurally ready for desktop use, but most Feishu-derived repair candidates remain intentionally private because operational-stability evidence has not yet been supplied to Builder.

## Next evidence task — source-side, not Builder-side

Do NOT ask Builder to guess or promote these paths again yet.

The next task belongs to `Troubleshooter｜Feishu` and should audit operational maturity for the 19 candidate Repair Paths using actual Feishu history / maintained knowledge sources.

For each candidate, return where obtainable:
- `repair_path_id`;
- earliest known appearance/use;
- latest material update/change;
- repeated-use signal / number or qualitative recurrence if exact count is unavailable;
- whether the same handling has remained materially unchanged;
- whether PIE/KB/service guidance continues to use it;
- known contradictions, reopen, replacement-failed or superseding guidance;
- actual model/product scope observed;
- source authority (ITR recurring practice / 工单速查 / 信息同步库 / other maintained service guidance);
- recommendation: `STABILITY_SUPPORTED / NOT_YET_SUPPORTED / CONFLICT / SCOPE_UNKNOWN`.

This maturity audit must not require an explicit `solved` reply and must not treat mere age/silence as proof.

## 1202

1202 remains outside this maturity-promotion pass until the user later supplies the missing model/version scope or other authoritative scope evidence. Do not guess it.

## Next gate

After the Feishu maturity audit is returned, Troubleshooter｜主管 will decide which candidates qualify as `STABLE_OPERATIONAL_GUIDANCE`, then Builder can run a focused publication/update regression rather than another broad rebuild.

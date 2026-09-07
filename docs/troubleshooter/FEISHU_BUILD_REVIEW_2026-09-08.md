# PIE Troubleshooter — Feishu Build Review

Status: PARTIAL_ACCEPT / REWORK_REQUIRED
Reviewer: Troubleshooter｜主管
Date: 2026-09-08
Source: PIE Troubleshooter Feishu Knowledge Build Report 2026-09-08

## Accepted as useful evidence

The following parts are useful and may guide product priority:
- ITR population size and Error Code fill rate;
- high-frequency Error Code counts as observed in ITR;
- high-frequency symptom-only counts;
- broad KB coverage gaps, especially connectivity;
- relevant substantive technical/service content present in 信息同步库;
- evidence that Error Code cannot be the only product entry.

Important correction: the 信息同步库 field/value `需同步` is only an internal colleague-notification/reminder flag. It is **not** evidence that the technical content is newer, unsynchronized to KB, superseding, stale, or pending knowledge promotion. Do not use this flag for currentness, conflict, KB coverage, or publishability decisions. See `docs/troubleshooter/FEISHU_FIELD_SEMANTICS.md`.

## Not accepted as publishable knowledge

Do NOT hand REPORT D/E/F/H directly to Builder as canonical repair knowledge.

### 1. Taxonomy semantic classification is too permissive
Many labels classified as `OBSERVABLE_AREA` actually encode components or causes, e.g. adapter failure, mainboard/driver-board charging failure, GNSS module abnormality, vision module failure, LiDAR module abnormality, wheel electrical/communication/Hall abnormality, harness/connector abnormality.
These must be reclassified into COMPONENT / FAULT_CAUSE / AMBIGUOUS, not exposed as agent-facing symptoms.

### 2. Outcome evidence is insufficient for many replacement paths
The report itself states that the ITR resolution/outcome field is nearly empty. Therefore repair paths must distinguish:
- recommended action in a source;
- action actually performed;
- verified solution with post-repair outcome.
A recommendation or `Solutions` text is not automatically a verified repair outcome.

### 3. Several repair paths are over-scoped or unsupported
Examples include `ALL` model scope or broad LUBA-family scope without evidence, and direct part/fallback chains inferred beyond the observed cohort. Model/version scope must be evidence-backed.

### 4. 1202 is in direct conflict with current specialist evidence
The Feishu report proposes cutting-motor -> driver-board -> mainboard across broad LUBA scope. The current Troubleshooter Builder checkpoint separately identified a promoted 1202 cable -> mainboard sequence with unresolved model scope. Until reconciled, 1202 must not be promoted from this Feishu report.

### 5. Controlled symptom library has broken or inconsistent references
Several symptom rows are marked publishable while their Repair Path IDs are not defined in REPORT F. Product counts are also inconsistent (`Observable Areas (9)` while 10 areas are listed; elsewhere total is 10).

### 6. Internal-tool content leaks into frontend candidates
`MammoSuite cannot connect` is included as a controlled symptom while the same report later classifies MammoSuite issues as internal/excluded. Internal-tool troubleshooting must remain separate unless the target user is explicitly authorized to use that tool.

### 7. Some controlled symptoms are too broad
Examples such as `Robot moves abnormally / jerky`, `Vision/camera abnormal`, `Map is distorted or lost`, and combined positioning states may lead to materially different repair paths. They require evidence-led splitting or PIE-only fallback.

## Product architecture decision

For desktop, do not force a preliminary binary choice between `I have an Error Code` and `I do not have an Error Code`.

Preferred desktop home:
1. persistent Product/Model context;
2. prominent Error Code / Error Message search at top;
3. controlled `Choose by symptom` area visible on the same page below/alongside it;
4. both routes converge on the same canonical Repair Card.

Reason: only 38/737 ITR records contain an Error Code, so symptom navigation is operationally the dominant path while Error Code search remains a fast shortcut.

## Required rework before Builder expansion

Feishu agent must produce a corrected `VERIFIED_KNOWLEDGE_BUILD` with these gates:

1. Reclassify every taxonomy candidate using strict semantic types:
   `OBSERVABLE_AREA / OBSERVABLE_SYMPTOM / QUALIFIER / COMPONENT / FAULT_CAUSE / ACTION / BUSINESS_INTERNAL / AMBIGUOUS_MIXED`.
2. No component/cause wording may appear as a Controlled Symptom.
3. For each Repair Path, explicitly label evidence state:
   - `SOURCE_RECOMMENDATION`
   - `ACTION_PERFORMED_OUTCOME_UNKNOWN`
   - `VERIFIED_RESOLUTION`
   - `CONFLICTING_EVIDENCE`
4. Direct part-replacement advice may be `P0/P1` only when model scope and verified outcome evidence are adequate.
5. Any unsupported `ALL` model scope must be removed or replaced by explicit evidence-backed scope / unknown.
6. Reconcile 1202 against existing promoted knowledge and leave blocked if scope/semantics conflict.
7. Every publishable symptom must reference an existing valid Repair Path or an explicit PIE-only fallback.
8. Separate internal-tool issues (MammoSuite/Kit/account/parts/warranty) from agent-facing machine symptoms.
9. Normalize all counts/area totals and validate referential integrity.
10. Canonical verification must preserve the established repair-validation requirements; agent display may be simplified but cannot silently delete required verification.
11. Do not use workflow/reminder fields such as 信息同步库 `需同步` as technical-currentness or knowledge-promotion evidence. Evaluate the substantive content only.

## Gate

Builder desktop expansion remains blocked on `VERIFIED_KNOWLEDGE_BUILD`, not on the current raw Feishu handoff.

The frequency audit is accepted for prioritization; repair mappings remain candidate data until corrected and reviewed.

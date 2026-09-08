# Independent final review — KNOWLEDGE-INGEST-004

Date: 2026-09-08. Reviewer: independently delegated implementation/data/privacy/usability reviewer. Scope: current uncommitted task004 diff and task files in the isolated Desktop clone, relative to accepted commit `a0fd13819da831cc3e1fcc77ca12ffeaf9869004`. Read-only review and in-memory validation; this report is the only reviewer-written file. No MAIN runtime, port8787, production access, external messaging, Git mutation, package/build mutation, or secondary agent was used.

## Verdict

**No unresolved reproducible Critical, Important, or Minor findings after re-review.** Local knowledge-ingestion approval is supported by the reviewed implementation and evidence. One Important promotion-reference gate defect was independently reproduced, reported, fixed by the root task, and retested successfully. This approval does not publish candidate repairs, approve deployment, or independently certify real repair outcomes.

The README, DATA_CONTRACT and current knowledge audit were checked after their task004 updates. HANDOFF was still being rewritten by root at this review checkpoint; that explicitly pending documentation is not recorded as a defect or asserted complete here. Root owns the final handoff, final full-suite rerun, commit, and task report.

## Resolved finding R1 — Important

**Published canonical paths did not validate candidate provenance in reverse.** Original `validateCandidates` checked candidate `promoted_refs` only when its review visibility was public. It did not inspect canonical path `candidate_refs`. In an in-memory canonical clone, assigning `['REP-CUT-001']` to `sym-cutting-functional-test/software.candidate_refs` returned no validation errors while that path remained a projected repair, despite REP-CUT-001 being WITHHELD. Assigning `['REP-FAKE-001']` also passed. This allowed a maintainer to attach withheld or nonexistent candidate provenance to a published action without the promised reciprocal gate.

Suggested fix: validate canonical path candidate reference type, uniqueness and existence; require reciprocal candidate public promotion and symptom applicability for projected executable paths. Root implemented this in `lib/candidates.mjs` and added a regression.

Fresh exact reproduction results after the fix:

- REP-CUT-001: `sym-cutting-functional-test/software: published action requires reciprocal promoted candidate`.
- REP-FAKE-001: `sym-cutting-functional-test/software: dangling candidate provenance`.
- Actual unchanged candidate/canonical input: `[]` validation errors.
- `node --test test/candidates.test.mjs`: **9/9 passed** after the fix.

Current shipped data never contained either invalid linkage; the finding concerned fail-closed maintenance behavior, not a demonstrated current public candidate leak.

## Data and evidence review

Read the ingestion plan, complete sanitized payload, promotion policy, independent evidence report, private JSON/parser/importer, canonical diff, build/package changes, tests, and updated contract/audit. Cross-checked maintained ERROR_CODES, KNOWN_FIXES, TOOL_KNOWLEDGE, DIAGNOSTIC_KNOWLEDGE and PARTS_KNOWLEDGE for the relevant cutting, charging/battery, firmware, positioning, LiDAR and damage constraints.

- Exact 19 full candidate IDs and their source fields match the parsed pinned payload. Source and review fields are separate. Scope wording, evidence labels, action sequence, verification, fallback and guardrails are retained; absent frozen fields remain null/empty.
- Payload normalized SHA256: `edc38d9ec9e9d0c4f9be47cbefb087f9f5975ea7378cf045aa4142dc1cb441f1`.
- Full-record review counts: 19 retained; 0 promoted; 17 PIE_ONLY; 2 WITHHELD. Evidence counts: 5 ACTION_PERFORMED_OUTCOME_UNKNOWN, 12 SOURCE_RECOMMENDATION, 2 CONFLICTING_EVIDENCE. Separate REP-1202-001 remains CONFLICTING_EVIDENCE/WITHHELD outside that denominator.
- Five reconciliation groups preserve signed/unsigned identity, including distinct `2000303` and `-2000303`. They cannot become repair approvals through the reconciliation review structure.
- Model/capability and symptom distinctions are respected: CUT/1202, Wi-Fi/4G, positioning/map loss/RTK, LiDAR architecture, current-versus-historical firmware, water/physical serviceability, and unsupported SOH thresholds. No numerical battery replacement threshold or operational success count was invented.
- The zero-promotion conclusion is supported by full-path scope/action/fallback limitations and conflicts. It does not rely on requiring a partner's explicit solved reply. Two conditional diagnostic derivatives remain documented opportunities, not counted publications.
- Source drift and invalid candidate review data reject import/build before output writes. `--write` intentionally preserves the existing reviewed batch and refuses changed source content; it does not bootstrap approval.

## Public behavior, privacy, package and usability

Independently compared projected current canonical data with the accepted base: **exact semantic equality after removing only knowledgeVersion**. No new repair content or routing was introduced by candidate ingestion. The private symptom crosswalk is removed by the existing field allowlist; the frozen 1202 repair prohibition and prior exact model/version/qualifier gates remain in the unchanged engine.

Read the preview HTTP allowlist and added private-path refusal tests. Candidate JSON, importer, source payload, reviews and build manifest are outside public runtime assets. Package script retains an eight-entry allowlist with candidate-specific content checks. An initial overly broad review scan matched the pre-existing schema field names `sourceRefs`/`label_cn` inside engine code; inspection identified these as executable schema code, not embedded private source records. Candidate-specific scanning and public JSON projection checks passed.

Independent file calculations passed for all five current dist assets against manifest byte lengths/SHA256; all eight extracted entries against staging hashes; current ZIP SHA256; and candidate-specific private markers across assets/extracted entries. Package: `error-code-pilot-20260908-074138.zip`, SHA256 `d112525a6812cf1b535303d7933253ddaa1b9dcce083ff32d67a6e90f1eac920`. No rebuild or package extraction was performed by this reviewer.

Visually inspected current `desktop-home.png`, `desktop-repair.png`, `mobile-repair.png`, and `zoom125-1366-verification.png`. Labels, action/verification/fallback hierarchy and outcome controls remain readable; mobile content stacks without clipping, and the zoomed controls remain usable. No new reproducible layout issue found. Reviewed root-generated browser evidence (33 checks, 1366/1920/390 widths, zero page errors/external requests), native125% evidence (both desktop widths, no horizontal overflow), two owned lifecycle cycles, and extracted package HTTP evidence. These broader runs were performed by root; this review independently inspected their artifacts and did not claim to rerun them.

## Limits

This is a local task-diff and retained-artifact review, not a new Feishu case audit or exhaustive firmware/parts compatibility study. No repair promotion quota applies. Real first operational use, complete repeated-use counts and comprehensive reopen history remain unknown. Any later candidate promotion still needs its own supported scope, evidence, executable action, verification/fallback and reciprocal canonical review.

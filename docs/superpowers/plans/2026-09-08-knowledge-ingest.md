# Feishu candidate ingestion implementation plan

> Execute continuously with superpowers:executing-plans, test-driven-development and verification-before-completion. Use independent evidence and final review; ordinary fixes and local approval are authorized by the task.

**Goal:** EC-MT-20260908-KNOWLEDGE-INGEST-004 → TROUBLESHOOTER_DESKTOP_KNOWLEDGE_GREEN.

**Architecture:** Preserve the accepted desktop app and canonical repair engine. Import the sanitized payload into a separate private candidate catalog with stable IDs, exact source fields and independent review decisions. Build validates this private catalog and its canonical symptom/promotion references before projecting only approved canonical knowledge. No second answer engine or runtime candidate endpoint.

**Stack:** Existing Node/static SPA, native test runner, Edge/Playwright, local PowerShell packaging. No new dependency.

**Spec:** Issue #5 comment 5579711783 and docs/troubleshooter/FEISHU_CANDIDATE_PAYLOAD_2026-09-08.md.

## Boundaries

- Only C:/Users/Reggie/Desktop/PIE-ITR-ErrorCode; MAIN remains read-only. Never port8787 or protected sessions.
- No production write, public deployment or default/main integration.
- 19 non-1202 candidates plus separately frozen REP-1202-001; absent source facts remain absent/null.
- Do not repeat the Feishu737-case audit. Provenance is the supervisor's sanitized GitHub payload, not a production Feishu read.
- Evidence/promotion independent of P0/P1; weak paths retained private/PIE_ONLY, conflict/scope-blocked paths WITHHELD.

## S0 recovery — complete

- Independent clone/branch at a0fd138, clean tracked baseline confirmed.
- origin/main fetched to1da74aa; remote delta is only the new payload. Copied that new tracked file non-destructively; no merge/reset/rebase or MAIN changes.
- Latest MASTER/REGISTRY and task/report/policy/knowledge references reviewed.
- Fresh baseline:54/54 automated tests and33/33 browser checks passed before knowledge edits.

## Exact file map

| File | Responsibility |
| --- | --- |
| error-code-pilot/lib/candidates.mjs | Private payload parser, candidate validator, provenance and promotion reference gates |
| error-code-pilot/scripts/ingest-candidates.mjs | Deterministic import/check command; retain reviewed decisions, fail on source drift |
| error-code-pilot/data/feishu-candidates.json | Actual19+1 source records, reconciliation-only codes and per-record review |
| error-code-pilot/data/canonical.json | Internal symptom→candidate links and release version; existing public rules preserved |
| error-code-pilot/scripts/build.mjs | Validate candidate integrity before emitting approved assets; private count manifest |
| error-code-pilot/test/candidates.test.mjs | Fail-first import, source parity, IDs, missing facts, review policy, scope/conflict/privacy tests |
| error-code-pilot/test/build.test.mjs | Invalid candidate build abort and private candidate route refusal |
| error-code-pilot/test/browser.mjs | Real candidate symptom remains safe; retained desktop regression/privacy |
| error-code-pilot/docs/KNOWLEDGE_INGEST_AUDIT_2026-09-08.md | Sanitized per-record decisions, reconciliation, counts and evidence limits |
| error-code-pilot/docs/DATA_CONTRACT.md, README.md, docs/HANDOFF.md | Import/update workflow, private boundary and latest gate evidence |
| MASTER_PLAN.md, AGENT_REGISTRY.md | Paired local specialist checkpoint only; canonical MAIN ownership unchanged |

## S1–S5 implementation and knowledge review

- [x] Write failing tests for exact19+1 IDs, payload field preservation, absent frozen fields, source hash and cross-references.
- [x] Implement private import/validation with independent source/review fields. Preserve sync-derived code candidates as reconciliation-only, not repair approvals.
- [x] Audit every candidate against maintained canonical knowledge/history; record state, scope, conflicts, verification/fallback and rationale. No requirement to promote a quota.
- [x] Reconcile CUT/1202, WiFi/4G, positioning/map, LiDAR/code/capability, firmware, water/physical and battery/SOH explicitly.
- [x] Keep public routes on the existing canonical contract; approved promotion references must pass existing projection/scope/verification gates.

## S6–S9 acceptance

- [x] Fresh complete automated and browser regression;1366x768,1920x1080,390mobile andnative125%zoom.
- [x] Two owned lifecycle cycles; public/private scan; five-asset build and eight-file extracted package readback/hash.
- [x] Independent final data/implementation/privacy/usability review; fix all reproducible defects and retest.
- [x] Paired local checkpoint, final local commit and exactly matching terminal Issue #6 report.

## Decisions

- Candidate import is not a public repair publication. Retention and explicit safe routing satisfy weaker-item handling; no fabricated public action is necessary.
- No routine user confirmation is required. An unresolved item is downgraded/withheld while independent work continues.
- Prior temporary-directory cleanup was policy-rejected; retain audit scratch rather than retrying deletion.

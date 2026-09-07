# Error Code Pilot implementation plan

> For agentic workers: execute using superpowers:executing-plans; use bounded read-only evidence/review subagents without overlapping writes.

**Goal:** Deliver EC-MT-20260907-PILOT-001 through the full local pilot gate, or identify only genuine remaining decisions.

**Architecture:** static ES module SPA, canonical JSON, allowlisted agent projection, read-only future adapter, localhost-only Node preview. No MAIN imports or shared state.

**Tech stack:** browser JavaScript/CSS/HTML; Node built-ins and node:test; bundled Playwright for verification only.

**Spec:** ../specs/2026-09-07-error-code-pilot-design.md and Issue #5 task comment 5575230975.

## Global constraints
- Dedicated directory C:/Users/Reggie/Desktop/PIE-ITR-ErrorCode; branch error-code/ec-mt-20260907-pilot-001-canonical.
- Issue #5 input, Issue #6 report; MAIN directory is read-only.
- English agent page. No 8787, Workbench runtime, auth/session manipulation, live LLM, production write or public deployment.
- Evidence-backed paths only; missing scope or outcome stays unknown. No invented success rate.

## Tasks and acceptance checklist

- [x] S0: Recover remote controls/task and create a fully independent clone with separate Git objects. Preserve unrelated local MAIN history; create canonical-based specialist branch without destructive operations.
- [x] S1/S2/S3: Audit existing parsed table and promoted knowledge. Files: error-code-pilot/scripts/audit-sources.mjs, docs/EVIDENCE_AUDIT.md, data/canonical.json. Output aggregates, source hashes, ranked candidates, counterexamples and unavailable real-ITR coverage. Exclude row 2 machine header; preserve signed code and code 0. No raw case copy.
- [ ] S4/S5/S7/S8: Write test/core.test.mjs before src/engine.mjs. Interfaces: validateCatalog(catalog), projectAgentCatalog(catalog), searchCards(cards,query), resolveCard(card,context), recordOutcome(card,path,choice,context), exportWorkbench(catalog,context). Test literal exact matches, sign differences, ambiguity, scope/version/lifecycle blocks, missing evidence/verification, non-looping fallback and approved-only export. Run node --test test/core.test.mjs before implementation and after fixes. Document contract in docs/DATA_CONTRACT.md.
- [x] S6: Files src/app.mjs, src/styles.css, src/index.html. Consume projected data only. Test search and branch journeys on actual DOM before claiming interaction support. Escape untrusted data with DOM textContent. No case state persistence or external asset request.
- [x] S9/S10: Files scripts/build.mjs, scripts/serve.mjs, test/build.test.mjs, test/browser.mjs. Build only explicit public files. Test malformed data fails before build publication, POST rejection, path traversal, canonical/raw file inaccessibility, fixed/failure state reset and no overflow at mobile/desktop. Run node --test and browser suite; inspect screenshots. Audit actual build for PII, credentials and source leakage.
- [x] S11: Files README.md, docs/HANDOFF.md, artifacts/*-verification.json; update local MASTER_PLAN.md and AGENT_REGISTRY.md specialist sections together. Produce dist and local zip with rollback/run instructions. Re-run applicable final checks, commit only specialist implementation and related control updates locally; do not push. Read Issue #5 newest changes and Issue #6 before final sanitized report.

## Test intent
Tests catch: unsafe normalization selecting another signed error, fuzzy auto-resolution, wrong-model replacement, historical firmware reuse, candidate leakage to approved adapter, repeating failed replacement, success interpreted as closure, unvalidated/missing fallback publish, source metadata bundled into public app, path traversal/production access, and state leakage between searches.

## Current baseline
Latest remote base: 34b4cd242962b33b4cb2de0fe1daa02f5cf0448e. Repository is the control-plane documentation baseline; no inherited application test target exists. Tests belong solely to the new Pilot. Existing MAIN local implementation is intentionally not imported.

## Execution checkpoint

- S1/S2/S3 audit/ranking complete within safely available evidence. Full live outcome-cohort coverage remains unavailable and was not used to block other work.
- S4/S7/S8 schema, edge handling and adapter complete; the grouped checklist stays open only because S5 requires the 1202 exact model/version business decision.
- S6/S9/S10/S11 independent implementation, review, test, packaging and local handoff complete.
- Fresh evidence: 30 Node tests, 20 browser checks, 2 default-port lifecycle cycles and extracted ZIP readback passed.
- The terminal Issue #6 state is BLOCKED_ALL_REMAINING for the one business scope decision, not MASTER_COMPLETE or ERROR_CODE_PILOT_GREEN.
- See error-code-pilot/docs/HANDOFF.md for the final subtask matrix and artifacts. No ordinary engineering blocker remains.

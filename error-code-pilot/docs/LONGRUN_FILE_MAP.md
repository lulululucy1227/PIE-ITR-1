# Desktop long-run file map and execution ledger

Task: EC-MT-20260908-DESKTOP-LONGRUN-003. Plan: docs/superpowers/plans/2026-09-08-troubleshooter-desktop-longrun.md.

## Gate A — recovered baseline (2026-09-08)

Independent clone: `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`; branch `error-code/ec-mt-20260907-pilot-001-canonical`. Existing implementation commit `16deca1`. Fetched canonical remote `36a1fea` and merged its eight new supervisor documents into the specialist branch without touching MAIN. MAIN is read-only; no port 8787 operations.

Fresh baseline in `error-code-pilot`: `node --test test/*.test.mjs` (30/30), `node scripts/build.mjs` (five public assets, eight guides), `node test/browser.mjs` (20/20). Gate A approved locally.

## Exact implementation map

| Path below error-code-pilot/ | Responsibility / planned change |
| --- | --- |
| data/canonical.json | Internal code cards, controlled symptoms, repair references, evidence decisions and scope |
| src/engine.mjs | Schema validation, explicit public projection, code/symptom search, canonical resolution, outcomes |
| src/app.mjs | Persistent model context, dual entry and common repair card |
| src/index.html | Desktop home structure and accessible landmarks |
| src/styles.css | Desktop layout, laptop/zoom/mobile compatibility |
| scripts/build.mjs | Validate then emit five allowlisted public assets and hashes |
| scripts/serve.mjs | Local read-only server, protected routes/port, owned lifecycle |
| scripts/package.ps1 | Allowlisted ZIP, privacy scan, extraction and standalone readback |
| scripts/lifecycle-check.mjs | Two owned start/close/relaunch cycles |
| scripts/audit-sources.mjs | Read-only aggregate provenance audit; existing evidence retained |
| run-pilot.cmd | Local launcher |
| package.json | Local build/test/start commands |
| test/core.test.mjs | Existing search/scope/projection/outcome regression |
| test/data.test.mjs | Real knowledge preservation and publication guardrails |
| test/build.test.mjs | Asset and local server security regression |
| test/desktop-contract.test.mjs | New schema, controlled symptoms and evidence policy tests |
| test/browser.mjs | Actual desktop/mobile/zoom routes and local privacy acceptance |
| test/browser-zoom.mjs | Native Chromium 125% zoom in a separate test profile; measured zoom and screenshots |
| docs/KNOWLEDGE_PROMOTION_AUDIT_2026-09-08.md | Sanitized per-path classification and promotion decisions |
| docs/DATA_CONTRACT.md | Versioned symptom/evidence/public contract |
| docs/HANDOFF.md | Local gate evidence, packaging and operational handoff |
| docs/EVIDENCE_AUDIT.md | Prior source audit retained with current audit link |
| README.md | Run, update, rollback, local limitations |

Generated `dist/`, `artifacts/` and `.local/` remain ignored. No raw input or production identifiers enter the package.

## Execution decisions

- New task supersedes the prior 1202 project blocker: freeze conflicting repairs and continue to desktop local green.
- Preserve signed `-2000303` semantics independently from any unsigned false-alarm claim; only publish no-repair behavior when an actual current source supports that exact code and condition.
- The handoff cites 19 Feishu candidate paths but does not contain their individual records. Do not invent missing records or success counts; audit accessible promoted records and document the missing candidate payload.
- Use the existing stack and a versioned extension; no framework, database or external service is needed.

## Progress

- Task 1 complete: gate A passed; file map created before implementation edits.
- Tasks 2–12 complete: schema, knowledge, navigation, common card, desktop/mobile/native zoom, privacy, lifecycle, extracted package and independent review passed. Gates A–H self-approved under the latest task. Final gate: TROUBLESHOOTER_DESKTOP_LOCAL_GREEN.
- Task 13: final execution report channel is Issue #6 only. The Issue report is the authoritative external completion record.


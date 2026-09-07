# Error Code Pilot design

Task: EC-MT-20260907-PILOT-001, Issue #5. User explicitly authorized continuous implementation and ordinary engineering decisions; this design records those decisions without a new approval stop.

## Boundary and choice
New standalone subsystem, architecture scope. Native browser ES modules plus Node built-ins are sufficient: no dependencies, backend business service, live LLM, auth, production write, public hosting, or MAIN runtime. A React/Vite build would add installation and runtime surface with no benefit for these few steps; a dynamic backend would add coupling and storage risk. Use a static English interface on localhost:8796 with a fail-closed scope-aware data engine.

## Evidence and knowledge
Read existing parsed references only. Keep raw sources where they already exist and record hash/coordinates; a local audit artifact contains aggregate counts and field classification, not whole rows. Canonical cards preserve source references, review/currentness, missing scope, observed vs recommended outcome and replacement-failed behavior. The agent build uses an explicit field allowlist and omits all internal metadata. Pilot review is not formal production promotion. Workbench export defaults to approved-only and does not infer applicability.

## Flow
Search exact signed code or message. Exact code signs are significant. Fuzzy results require explicit candidate selection and never open a repair automatically. A found code is not an applicable repair: select the documented model or confirm a source-supported component scope if no model list exists. Ask symptom only for meaningful branches. Display most likely part, action, verification and failure fallback. Fixed means user-reported outcome in this page only, never verified repair, NFF or ticket closure. Failed/recurred repair exits to a validated next step or PIE; no repeat replacement loop.

## Knowledge guardrails
Never turn master severity '提示' into 'no repair needed'; faults and successes share that label. Success-only messages may say that message needs no repair if function is normal, while other symptoms route to PIE. Historical firmware target versions remain withheld until current applicability is confirmed by PIE. Model/version unknown or mismatch cannot reveal a confident replacement path. Newly adapted cards remain local pilot-only until supervisor promotion.

## Verification and handoff
Use deterministic Node tests for schema, search, scope, lifecycle, failed replacement, export and build privacy. Use Playwright with a separate local server for real desktop/mobile interaction, layout, keyboard, escaping and network allowlist checks. Package only built allowlisted files plus local run instructions; retain raw audit and tests outside the package. Update specialist sections of control-plane files only in the local specialist branch; do not push or merge. Final sanitized report to Issue #6 states coverage, limitations and fresh evidence.

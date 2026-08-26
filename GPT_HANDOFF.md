# PIE-ITR Handoff

## Canonical repository
`lulululucy1227/PIE-ITR-1`

If any task targets another repository, stop and verify before writing.

## Current phase
Real-case accumulation + diagnostic architecture refinement. Code changes remain paused while Codex read access is unreliable.

## Read first
1. Issue #1 — daily intake inbox; read newest/relevant comments only.
2. `docs/knowledge/` — promoted reusable knowledge, only files relevant to the current case.
3. `docs/regression/REAL_CASE_REGRESSION.md` — representative regression cases.
4. `docs/architecture/DIAGNOSTIC_ARCHITECTURE.md` — stable diagnostic architecture.
5. Issue #2 only when discussing architecture changes.

Do not load all historical material by default.

## Core boundaries
- PIE is remote technical support; agent/service staff perform physical repair/testing.
- Feishu ITR is the business-fact source of truth.
- `机型映射表` is the intended model-resolution business source.
- Vision is a diagnostic input, not attachment decoration.
- `already replaced` != `ruled out`.
- Evidence routing depends on problem type, actor/device location and conversation state; logs are not universal.
- `cannot reproduce` != `fault ruled out` and does not automatically mean NFF.
- Partner reply follows **minimum sufficient response**.

## Priorities
P0: diagnostic correctness; per-case failures visible; decisive evidence reaches case state.
P1: Vision/attachments; model mapping; compact ITR review; EN/ZH preload.
P2: Evidence Router/confidence; error-code/known-fix model; Parts/SBOM strategy.

## Intake/promotion
New case -> Issue #1.
Stable reusable rule -> relevant `docs/knowledge/` file.
Representative case -> regression corpus.
Stable system-level change -> architecture doc.
Do not promote a single case without sufficient evidence.

## Security
Repository is public. Do not store passwords/tokens, raw chats, customer/agent PII, or unapproved sensitive internal material.

## Next implementation gate
When Codex read access is healthy, run a gap audit across local implementation + Issue #1 findings + promoted knowledge/regression/architecture before changing code.

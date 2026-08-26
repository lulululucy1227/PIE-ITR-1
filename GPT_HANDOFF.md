# PIE-ITR Handoff

## Canonical repository
`lulululucy1227/PIE-ITR-1`

If any task targets another repository, stop and ask the user to verify the repo.

## Current phase
Business Intelligence & Diagnostic Architecture / real-case accumulation.

Codex local/GitHub read channel is currently unreliable in the user's environment, so implementation is paused. Do not treat this as a project-code failure.

## Authoritative sources
- Issue #1 — daily real-case / defect / diagnostic-knowledge intake
- Issue #2 — Diagnostic Architecture v0.1
- `docs/knowledge/` — promoted reusable knowledge
- `docs/regression/REAL_CASE_REGRESSION.md` — representative regression cases
- `docs/architecture/DIAGNOSTIC_ARCHITECTURE.md` — compact architecture baseline

## Core business boundaries
- PIE is remote technical support; agents/service technicians perform physical repair, replacement, reseating and measurements.
- Feishu ITR remains business source of truth for ITR data.
- `机型映射表` should become the model-resolution business source.
- Vision is a required diagnostic input, not attachment decoration.
- `already replaced` does not mean `ruled out`; known-good cross-test and observed behavior changes carry more weight.
- Evidence routing is contextual; do not request logs for every case.
- Reply principle: minimum sufficient response. Internal analysis may be detailed; agent-facing reply should be as short as possible while remaining correct/actionable.

## Current priorities
P0: diagnostic correctness, per-case failure visibility, decisive evidence reaching case state.
P1: Vision/attachments, model mapping, compact ITR review, EN/ZH preload.
P2: Evidence Router, evidence confidence/provenance, known-fix/error-code model, Parts/SBOM strategy.

## Current operating mode
User sends real cases naturally. Extract useful facts/rules, keep inference separate, record meaningful items in Issue #1, and promote stable reusable knowledge into `docs/knowledge/` only when justified.

## Next implementation gate
When Codex read access is healthy, run a gap audit between current local implementation, Issue #1 real cases, and Issue #2 / architecture docs before changing code.

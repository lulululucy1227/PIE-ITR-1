# Codex Execution Policy

Status: Active

## Model selection
At the start of every new Codex execution phase, first decide whether the phase can safely use Luna. Do not default to Terra.

Prefer Luna only when implementation and modification boundaries are already clear and the phase does not involve high-risk areas such as data-structure changes, production writes, or core asynchronous/state behavior. Otherwise use Terra.

Every Codex execution instruction should state:
1. recommended model: Luna or Terra;
2. reasoning/effort: Low, Medium or High;
3. a short rationale based on complexity, ambiguity and risk.

Do not use one fixed effort level for all stages.

## Execution discipline
- Audit/read before broad implementation when the boundary is not yet proven.
- Prefer the smallest safe change that satisfies the authorized phase.
- Reuse stable existing code and interfaces rather than creating parallel implementations.
- Run relevant tests/build checks before declaring a stable milestone.
- Do not force-push, reset, clean or discard unrelated local work merely to obtain a clean state.
- Do not expose or commit secrets/credentials.

## Milestone semantics
Distinguish clearly between:
- LOCAL COMPLETE — implementation/tests are complete locally;
- GITHUB SYNCED — the intended checkpoint is committed and pushed to the correct remote/branch.

A stable milestone should update the project handoff/status sufficiently for the next GPT/Codex session to resume without relying on chat memory.

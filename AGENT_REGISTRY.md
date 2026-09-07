# PIE-ITR AGENT REGISTRY

Status: Active / Authoritative agent topology
Last updated: 2026-09-07 (Europe/Berlin)
Owner: ITR主管
Canonical repository: `lulululucy1227/PIE-ITR-1`

## 0. Registry rules

This file is the authoritative answer to “which PIE-ITR agents exist and what are they responsible for?”.

If a chat/Codex window remembers a different agent set, do not rely on memory. Read this file first, then Issue #4 (tasks) and Issue #3 (reports).

Agent role != model. A role may use different execution models over time. Every new execution task should state `EXECUTION_MODEL / EFFORT / REASON` separately.

Only one agent should own the active shared implementation line at a time. Historical specialist agents must not start concurrent writes in the same dirty workspace unless the ITR supervisor explicitly reactivates them with isolated ownership/worktree.

## 1. Current registry

| Agent / role | Status | Primary responsibility | Local directory / workspace | Current task | Input | Output | Can own Error Code专项? | Running another task now? |
|---|---|---|---|---|---|---|---|---|
| **ITR主管** | ACTIVE | Project direction, business/architecture decisions, task routing, acceptance, GitHub Issue #4 task issuance, Issue #3 report acceptance, knowledge/governance gate | Chat role; canonical repo `lulululucy1227/PIE-ITR-1`; no separate code workspace | Supervise `MT-20260907-MAIN-DAILY-USE-RELEASE-006`; maintain `MASTER_PLAN.md` / `AGENT_REGISTRY.md` | User goals; latest Issue #3 reports; governance/knowledge rules; current project risks | Master tasks/direction in Issue #4; acceptance decisions; master plan/registry; knowledge-promotion decisions | **Architect/approve: YES; implementation owner: NO** | YES — supervisor role is active continuously |
| **MAIN Agent** | ACTIVE / PRIMARY IMPLEMENTATION OWNER | Single mainline Codex executor: current Workbench implementation, integration, debugging, runtime validation, release-quality closure | `C:\Users\Reggie\Desktop\PIE-ITR-1` | `MT-20260907-MAIN-DAILY-USE-RELEASE-006` -> target `DAILY_USE_MASTER_GREEN` | Issue #4 latest task/directions; local repo/worktree; authorized local technical evidence; existing tests/knowledge | Code changes; tests; runtime acceptance; sanitized Issue #3 terminal report | **YES technically**, but **DO NOT assign while current task active** | **YES** |
| **Agent A — Diagnostic / Integration specialist** | IDLE / HISTORICAL TASKS SUPERSEDED | Diagnostics, Troubleshooting/NFF logic, prepared-case integration, cross-module diagnostic correctness | Historical work used canonical local workspace; **no dedicated isolated directory is currently authoritative**. If reactivated, assign a new isolated worktree or explicit ownership before writing. | Historical: `MT-20260905-A-TRSH-NFF-002`, `MT-20260905-INTEGRATION-001`; both superseded by newer MAIN acceptance | Diagnostic rules; Troubleshooting/NFF contracts; integration boundary; regression cases | Diagnostic/integration implementation; focused regression evidence; Issue #3 report | **YES — preferred existing specialist candidate for Error Code专项 after MAIN is free**, because the work is diagnostic/evidence-scoping rather than UI/auth | NO |
| **Agent B — Auth / Session / Runtime specialist** | DEFERRED SPECIALIST | Nextop local auth/session recovery, browser/session boundary, runtime/auth-related UX; can support infrastructure issues | Historical work used canonical workspace; no active isolated directory recorded | Historical: `MT-20260905-B-NEXTOP-LOCAL-AUTH-002`, `MT-20260905-B-AUTH-LIVE-VERIFY-003` | Auth/session state; local runtime/browser behavior; safe preflight requirements | Auth/session fixes and verification; sanitized report | **NO as technical owner. CONDITIONAL support only** for access/runtime required by Error Code tools | NO |
| **Agent C — PDF / Vision / Evidence specialist** | IDLE / HISTORICAL TASKS SUPERSEDED | PDF Evidence Reader, scanned/image PDF Vision path, evidence provenance, FAIL/page extraction | Historical work used canonical workspace; no active isolated directory recorded | Historical: `MT-20260905-C-PDF-EVIDENCE-002`, `...PDF-INTEGRATION-003`, `...PDF-VISION-VERIFY-004`, `...VISION-CONNECTIVITY-005`; objectives later covered by MAIN | PDF/image/test reports; Vision/evidence contracts; page provenance | Evidence extraction/integration; PDF/Vision regression; sanitized report | **CONDITIONAL SUPPORT, not owner** — useful if Error Code evidence is embedded in PDF/image reports, but should not own code semantics/root-cause rules | NO |
| **Agent D — paused legacy specialist** | PAUSED | No current validated mainline responsibility; previously intentionally paused because delivery/reporting was not worth blocking product work | No authoritative active directory; do not assume old session/worktree is safe to resume | NONE | Only explicit supervisor re-scope | Only a bounded specialist deliverable if reactivated | **NO by default** | NO |
| **PIE Daily Case / 案例收集 V2** | ACTIVE AUXILIARY ROLE | Daily real-case analysis in the user’s preferred format; partner reply; reusable-learning classification; discovery of patterns/contradictions | Chat role; no local code directory | Ongoing Daily Case collection, not a Codex implementation task | Partner/customer message thread, screenshots, test/log/PDF evidence, repair history, user correction, later outcome | `当前判断 / 关键依据 / 下一步`; short CN meaning + copyable EN reply when needed; learning classification (`NEW / REINFORCEMENT / CONFLICT / POSSIBLE_SUPERSEDED / DUPLICATE / INSUFFICIENT / NO_ACTION`) | **Candidate discovery: YES; implementation/official rule ownership: NO** | YES — ongoing operational intake |
| **Feishu / Lark execution agent** | AVAILABLE ON DEMAND | Execute specifically approved Feishu table/content operations and validation; does not decide technical truth | External/connected-agent role; no PIE-ITR local code directory | NONE currently | Supervisor-approved Feishu instructions, explicit fields/table scope, existing Feishu authorization | Feishu table/content changes + execution/acceptance report | **CONDITIONAL** — can implement approved Error Code table/data structure after technical rules are approved; must not own diagnostic semantics | NO |
| **Error Code Specialist** | PLANNED / UNASSIGNED | Dedicated future stream: scoped error-code -> phenomenon -> fault domain/component candidates -> checks -> handling -> validation; agent self-service output where stable | Not assigned yet | Not active; blocked by current Daily-use closure unless supervisor explicitly changes priority | Error Code source table, local technical knowledge, current technical updates, real-case outcomes, model/version scope, repair/validation evidence | Scoped Error Code knowledge, Troubleshooting candidates, regressions, agent-facing guidance; no universal fixed mapping | N/A — this is the specialist role itself | NO |

## 2. Error Code专项 ownership decision

### Preferred assignment
When the supervisor starts the Error Code专项 after current Daily-use closure, the preferred existing technical owner is **Agent A**, not because “A remembers the project better”, but because its historical scope is the closest fit:

- diagnostic routing;
- Troubleshooting/NFF evidence rules;
- cross-module prepared-case integration;
- distinction between evidence, completed repair action, attempted fix and verified solution.

### Alternative
If Agent A’s old session/context is stale or its workspace cannot be safely isolated, create a **new Error Code Specialist Codex session** instead of reviving stale state. The new specialist must bootstrap from `MASTER_PLAN.md`, `AGENT_REGISTRY.md`, current governance, Issue #4 and Issue #3 — not from old chat memory.

### Do not assign now
MAIN is currently executing `MT-20260907-MAIN-DAILY-USE-RELEASE-006`. Do not run Error Code implementation concurrently in the same workspace. Either wait for `DAILY_USE_MASTER_GREEN` or explicitly create isolated worktree/ownership with no shared runtime/state conflicts.

## 3. Historical specialist status reconciliation

### Agent A
- Previous integration/auth-dependent acceptance was superseded by newer MAIN real Workbench acceptance.
- Do not reopen historical tasks simply to make old task statuses green.
- Reactivate only for a new bounded specialist objective.

### Agent B
- Keep as deferred auth/session/runtime specialist.
- Do not keep it busy when auth is healthy.
- Reactivate only when auth/session/runtime recovery is an actual user problem or a new scoped task requires it.

### Agent C
- PDF/Vision/evidence objectives are integrated into current mainline.
- Reactivate only for a new evidence/PDF/Vision-specific gap.

### Agent D
- Remains paused.
- Do not restart merely for agent utilization.

## 4. MAIN ownership rule

MAIN is the only active implementation owner by default.

The normal flow is:

`ITR主管 -> Issue #4 -> MAIN -> Issue #3 -> ITR主管验收`

Specialists are used only when at least one of these is true:

1. the task is genuinely independent and benefits from specialist context;
2. the task can run in an isolated worktree/runtime without shared-state conflict;
3. MAIN explicitly needs bounded specialist review/evidence support;
4. the supervisor decides the specialist should become the new owner of a future stream.

Do not assign A/B/C/D tasks merely because they are idle.

## 5. Input/output contracts

### ITR主管
Input: user intent + project evidence/status.
Output: decision, task, acceptance, governance/knowledge promotion.

### MAIN
Input: one authorized Master Task + current local state.
Output: completed implementation/verification + one sanitized terminal Issue #3 report.

MAIN should autonomously close ordinary bugs/test failures/timeouts within scope. User interaction is reserved for genuine business decisions, user-only auth/OAuth/MFA, new production-write scope, destructive Git, or true external blockers.

### Daily Case V2
Input: natural real case evidence.
Output to user: concise internal analysis in the preferred format; partner reply only when needed.
Output to project: only reusable learning/correction/regression value, not raw case history.

### Feishu agent
Input: explicit approved write scope.
Output: executed Feishu change + verification. No independent technical-rule invention.

## 6. Model routing rule

No agent is permanently tied to GPT-6, Terra, Luna or Spark.

For each new execution task, the supervisor must state:

- `EXECUTION_MODEL`
- `EFFORT`
- `REASON`

Use the lowest sufficient capability consistent with correctness/risk. Do not default to GPT-6 simply because the task is important.

Current active MAIN task: **GPT-5.6 Terra / High** because it is cross-module Daily-use closure with runtime/regression/usability interactions.

`PIE_ANALYZER_MODEL` is a separate application setting and must never be changed merely because an execution task uses a different Codex model.

## 7. Shared-state safety

The following are shared-state risk areas and should not be manipulated concurrently by multiple agents without explicit isolation:

- `C:\Users\Reggie\Desktop\PIE-ITR-1` dirty worktree;
- formal Workbench runtime;
- local API port 8787;
- frontend runtime;
- Nextop local auth/session;
- Feishu auth/session;
- local learning/case state;
- current analyzer config.

Do not run multiple agents against these simply for parallelism.

## 8. Registry update rule

Update this file when any of these changes:

- a new permanent/specialist agent is created;
- an agent is retired/paused/reactivated;
- the primary implementation owner changes;
- a specialist receives a dedicated local worktree/directory;
- Error Code专项 ownership is assigned;
- current task ownership materially changes.

At each major milestone, update `MASTER_PLAN.md` and `AGENT_REGISTRY.md` together or explicitly state why only one changed.

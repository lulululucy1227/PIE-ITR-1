# PIE-ITR AGENT REGISTRY

Status: Active / Authoritative agent topology
Last updated: 2026-09-07 (Europe/Berlin)
Owner: ITR主管
Canonical repository: `lulululucy1227/PIE-ITR-1`

## 0. Registry rules

This file is the authoritative answer to “which PIE-ITR agents exist and what are they responsible for?”.

If a chat/Codex window remembers a different agent set, do not rely on memory. Read this file first, then the task/report channels belonging to the relevant agent.

Agent role != model. A role may use different execution models over time. Every new execution task should state `EXECUTION_MODEL / EFFORT / REASON` separately.

Only one agent should own a given active implementation line/worktree at a time. Parallel work is allowed only when ownership, workspace/runtime and task/report channels are explicitly isolated.

## 1. Current registry

| Agent / role | Status | Primary responsibility | Local directory / workspace | Current task | Input | Output | Error Code专项 role | Running another task now? |
|---|---|---|---|---|---|---|---|---|
| **ITR主管** | ACTIVE | Project direction, business/architecture decisions, task routing, acceptance, control-plane docs and knowledge/governance gate | Chat role; canonical repo `lulululucy1227/PIE-ITR-1`; no separate code workspace | Supervise MAIN Workbench + Error Code parallel stream; maintain `MASTER_PLAN.md` / `AGENT_REGISTRY.md` | User goals; latest task/report channels; governance/knowledge rules; project risks | Master tasks/direction; acceptance decisions; master plan/registry; knowledge-promotion decisions | **Architect/approve: YES; implementation owner: NO** | YES — supervisor role is active continuously |
| **MAIN Agent** | ACTIVE / PRIMARY WORKBENCH OWNER | Single mainline Codex executor for current Workbench implementation, integration, debugging, runtime validation and release-quality closure | `C:\Users\Reggie\Desktop\PIE-ITR-1` | `MT-20260907-MAIN-DAILY-USE-RELEASE-006` -> `DAILY_USE_MASTER_GREEN` | Issue #4 latest task/directions; MAIN local repo/worktree; authorized local technical evidence; tests/knowledge | Code changes; tests; runtime acceptance; sanitized Issue #3 report | **NO during current task**; may consume stable shared Error Code knowledge later | **YES** |
| **Agent A — Diagnostic / Integration specialist** | IDLE / HISTORICAL TASKS SUPERSEDED | Diagnostics, Troubleshooting/NFF logic, prepared-case integration, cross-module diagnostic correctness | No authoritative dedicated workspace; if reactivated, assign isolated worktree/ownership before writing | NONE | Diagnostic rules; Troubleshooting/NFF contracts; integration boundary; regression cases | Bounded diagnostic/integration review or implementation when explicitly reactivated | **REVIEW / FALLBACK SUPPORT** — no longer current owner because a clean dedicated Error Code Specialist is now activated | NO |
| **Agent B — Auth / Session / Runtime specialist** | DEFERRED SPECIALIST | Nextop local auth/session recovery, browser/session boundary, runtime/auth UX | Historical workspace only; no active isolated directory | NONE | Auth/session state; local runtime/browser behavior; safe preflight requirements | Auth/session fixes and verification | **CONDITIONAL SUPPORT only** if the Error Code product later needs access/runtime/auth infrastructure | NO |
| **Agent C — PDF / Vision / Evidence specialist** | IDLE / HISTORICAL TASKS SUPERSEDED | PDF Evidence Reader, scanned/image PDF Vision path, evidence provenance, FAIL/page extraction | Historical workspace only; no active isolated directory | NONE | PDF/image/test reports; Vision/evidence contracts; page provenance | Evidence extraction/integration; focused verification | **CONDITIONAL SUPPORT** if Error Code evidence is embedded in PDF/image reports; not semantic owner | NO |
| **Agent D — paused legacy specialist** | PAUSED | No current validated mainline responsibility | No authoritative active directory | NONE | Only explicit supervisor re-scope | Only bounded specialist deliverable if reactivated | **NO by default** | NO |
| **PIE Daily Case / 案例收集 V2** | ACTIVE AUXILIARY ROLE | Daily real-case analysis; partner reply; reusable-learning classification; discovery of repair patterns/contradictions | Chat role; no local code directory | Ongoing Daily Case collection | Partner/customer thread, screenshots, test/log/PDF evidence, repair history, user correction, later outcome | `当前判断 / 关键依据 / 下一步`; short CN meaning + copyable EN reply; learning classification | **Candidate/evidence discovery: YES; implementation/official rule ownership: NO** | YES — ongoing operational intake |
| **Feishu / Lark execution agent** | AVAILABLE ON DEMAND | Execute specifically approved Feishu table/content operations and validation; does not decide technical truth | External/connected-agent role; no PIE-ITR local code directory | NONE currently | Supervisor-approved Feishu instructions and explicit fields/table scope | Feishu content changes + execution/acceptance report | **CONDITIONAL** — can implement an approved data structure later; cannot invent repair semantics | NO |
| **Error Code Specialist** | **ACTIVE / PARALLEL SPECIALIST OWNER** | Dedicated Agent Repair Assistant stream: audit raw Error Code references and real repair outcomes; build scoped `Error/Error Message -> Symptom -> Part -> Repair -> Verification -> If not fixed` knowledge and a simple agent-facing web Pilot | **Isolated workspace to create:** `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`; must not write to MAIN workspace | `EC-MT-20260907-PILOT-001` -> target `ERROR_CODE_PILOT_GREEN` | Issue #5 latest task; `MASTER_PLAN.md`; this registry; raw Error Code sources read-only from MAIN/local references; promoted knowledge; read-only real-case/ITR outcomes when safely available; model/version/repair/validation evidence | Scoped publishable Error Code knowledge; repair cards; lightweight web Pilot; regressions/tests; sanitized Issue #6 report | **OWNER: YES** | **YES — newly activated** |

## 2. Error Code专项 ownership decision

### Current decision

The supervisor has explicitly activated **Error Code Specialist** as the independent owner instead of waiting for MAIN or reviving Agent A.

Reason:
- the stream is expected to become a long-lived independent product, not a temporary Workbench subtask;
- MAIN will remain continuously occupied with Workbench evolution;
- a clean specialist session bootstrapped from current canonical control-plane state is safer than reviving stale historical context;
- work can be isolated at workspace/runtime/task-queue level.

### Execution model for initial Pilot build

`EXECUTION_MODEL: GPT-6`
`EFFORT: High`

Reason: the first Pilot task combines heterogeneous source analysis, repair-outcome mining, knowledge-model design, product simplification, web implementation and verification. This is a one-time high-reasoning phase. Routine maintenance after the schema/product stabilizes should use the lowest sufficient model.

### Agent A position

Agent A remains a useful diagnostic/integration specialist and may later be asked to review difficult mappings or integration boundaries. It is not the current Error Code implementation owner.

## 3. Parallel isolation model

### MAIN stream

- Workspace: `C:\Users\Reggie\Desktop\PIE-ITR-1`
- Task queue: Issue #4
- Report channel: Issue #3
- Formal Workbench/runtime/8787 ownership remains MAIN-only.

### Error Code stream

- Isolated workspace target: `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`
- Task queue: Issue #5
- Report channel: Issue #6
- Must not start/manipulate formal Workbench, port 8787, MAIN analyzer config, MAIN local case state, Nextop session or Feishu session.
- May inspect MAIN-local parsed Error Code/reference data read-only and copy only the minimum needed into the isolated workspace.
- Must not modify `C:\Users\Reggie\Desktop\PIE-ITR-1`.

The two agents do not consume each other’s task queues.

## 4. Historical specialist status reconciliation

### Agent A
- Previous integration/auth-dependent acceptance was superseded by newer MAIN acceptance.
- Do not reopen historical tasks merely to make old task statuses green.
- Reactivate only for a new bounded diagnostic/integration review or if the supervisor explicitly transfers a future scope.

### Agent B
- Keep as deferred auth/session/runtime specialist.
- Reactivate only when auth/session/runtime recovery is an actual problem or an approved Error Code production phase requires it.

### Agent C
- PDF/Vision/evidence objectives are integrated into current mainline.
- Reactivate only for a new evidence/PDF/Vision-specific gap.

### Agent D
- Remains paused.
- Do not restart merely for agent utilization.

## 5. Ownership rules

The normal MAIN flow is:

`ITR主管 -> Issue #4 -> MAIN -> Issue #3 -> ITR主管验收`

The Error Code flow is:

`ITR主管 -> Issue #5 -> Error Code Specialist -> Issue #6 -> ITR主管验收`

Parallel specialists are allowed only when at least one is true:

1. the task is genuinely independent and benefits from specialist context;
2. the task runs in an isolated worktree/runtime without shared-state conflict;
3. MAIN explicitly needs bounded specialist review/evidence support;
4. the supervisor assigns a specialist as owner of a separate long-lived stream.

Do not assign agents merely because they are idle.

## 6. Input/output contracts

### ITR主管
Input: user intent + project evidence/status.
Output: decision, task, acceptance, governance/knowledge promotion.

### MAIN
Input: one authorized Workbench Master Task + current MAIN local state.
Output: completed implementation/verification + one sanitized terminal Issue #3 report.

MAIN should autonomously close ordinary bugs/test failures/timeouts within scope. User interaction is reserved for genuine business decisions, user-only auth/OAuth/MFA, new production-write scope, destructive Git, or true external blockers.

### Error Code Specialist
Input: one authorized `EC-MASTER_TASK_ID` from Issue #5 + isolated workspace + permitted read-only evidence sources.
Output: complete Pilot/knowledge implementation and verification + sanitized Issue #6 report.

It must preserve the product principle: **backend may be evidence-rich; agent-facing UX must remain simple and repair-oriented**. Do not convert the Portal into a diagnostic engineer console.

### Daily Case V2
Input: natural real case evidence.
Output to user: concise internal analysis in preferred format; partner reply only when needed.
Output to project: reusable learning/correction/regression value, not raw case history.

### Feishu agent
Input: explicit approved write scope.
Output: executed Feishu change + verification. No independent technical-rule invention.

## 7. Model routing rule

No agent is permanently tied to GPT-6, Terra, Luna or other execution models.

For each new execution task, the supervisor must state:
- `EXECUTION_MODEL`
- `EFFORT`
- `REASON`

Use the lowest sufficient capability consistent with correctness/risk.

Current MAIN task: **GPT-5.6 Terra / High** because it is cross-module Daily-use closure with runtime/regression/usability interactions.

Current Error Code initial Pilot task: **GPT-6 / High** because the initial stream must jointly reason over heterogeneous technical references, real repair outcomes, schema/product architecture and implementation. Later routine tasks should normally step down.

`PIE_ANALYZER_MODEL` is a separate application setting and must never be changed merely because an execution task uses a different Codex model.

## 8. Shared-state safety

The following MAIN areas must not be manipulated by Error Code Specialist:
- `C:\Users\Reggie\Desktop\PIE-ITR-1` dirty worktree;
- formal Workbench runtime;
- local API port 8787;
- frontend runtime belonging to Workbench;
- Nextop local auth/session;
- Feishu auth/session;
- MAIN local learning/case state;
- current analyzer config.

If the specialist needs a local web server for Pilot UX, use its own isolated workspace and a non-conflicting port or a static build/preview path.

## 9. Registry update rule

Update this file when any of these changes:
- a new permanent/specialist agent is created;
- an agent is retired/paused/reactivated;
- an implementation owner changes;
- a specialist receives a dedicated local worktree/directory;
- Error Code专项 ownership/status changes;
- current task ownership materially changes.

At each major milestone, update `MASTER_PLAN.md` and `AGENT_REGISTRY.md` together or explicitly state why only one changed.

## 10. Error Code local checkpoint — 2026-09-07

The planned specialist workspace now exists as an independent clone with separate Git objects at C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode, branch error-code/ec-mt-20260907-pilot-001-canonical.
Error Code Specialist remains the sole owner of this stream. MAIN is not reassigned.
Current local state: TECHNICAL_PILOT_READY / WAITING_BUSINESS_SCOPE for EC-MT-20260907-PILOT-001; ERROR_CODE_PILOT_GREEN is not claimed.
All independent safe audit/implementation/verification/packaging work is complete. The remaining business decision is the exact model/version scope of the promoted 1202 replacement sequence; its replacement advice stays withheld in the agent projection.
See error-code-pilot/docs/HANDOFF.md and the matching Issue #6 report. These control-file updates remain local to the specialist branch; there was no push or MAIN integration.

## 11. Error Code local knowledge checkpoint — 2026-09-08

Error Code Specialist remains sole owner in its independent clone C:/Users/Reggie/Desktop/PIE-ITR-ErrorCode on error-code/ec-mt-20260907-pilot-001-canonical. MAIN ownership and shared state are unchanged.

EC-MT-20260908-KNOWLEDGE-INGEST-004 reached TROUBLESHOOTER_DESKTOP_KNOWLEDGE_GREEN under authorized local self-approval. Actual19 candidate records imported,0 new full promotions,17 PIE_ONLY,2 WITHHELD; extra1202 retained separately frozen.64 automated tests,33 browser checks, native125% zoom, two owned starts/exits and extracted package/privacy verification passed. Independent review is closed with no unresolved finding.

This replaces the earlier local project-wide1202 waiting state; unresolved knowledge remains safely withheld and does not block the local gate under the newer task. No business decision is needed for this completed ingestion. Broader publication/integration needs a separate task. See the paired MASTER_PLAN local checkpoint and error-code-pilot/docs/HANDOFF.md. Final report only Issue #6; no push/default merge or MAIN integration.

## 12. Error Code local two-page checkpoint — 2026-09-08

Error Code Specialist remains sole owner of C:/Users/Reggie/Desktop/PIE-ITR-ErrorCode, branch error-code/ec-mt-20260907-pilot-001-canonical. EC-MT-20260908-DESKTOP-TWO-PAGE-005 reached TROUBLESHOOTER_DESKTOP_TWO_PAGE_GREEN: strict identify/solution pages, preserved canonical semantics/freeze, restored Back state and invalidated stale solution history.64Node,30browser,native125%,two owned8806 lifecycle cycles and final package/privacy checks passed. Independent60 DOM assertions; no unresolvedCritical/Important/Minor.

MAIN ownership/state and Issue #5/#6 isolation unchanged. Existing8796 listener preserved. No production access, public deployment or default/main integration. See paired MASTER_PLAN and current specialist handoff; this checkpoint is local pending supervisor acceptance.

# PIE-ITR Handoff

## Canonical repository
`lulululucy1227/PIE-ITR-1`

If any task targets another repository, stop and verify before writing.

## Authoritative project-control files
For every new GPT/Codex window, read in this order before relying on chat memory:

1. `MASTER_PLAN.md` — current phase, gates, priorities and durable project direction.
2. `AGENT_REGISTRY.md` — authoritative agent topology / responsibilities / current ownership.
3. Issue #4 — newest active supervisor task/direction.
4. Issue #3 — newest execution report/acceptance state.
5. This file + `governance/` + task-relevant `docs/`.

If an older chat remembers a different Agent set, `AGENT_REGISTRY.md` wins unless Issue #4/#3 contains a newer explicit change.

Important: active local implementation may be ahead of remote `main`. The local worktree is intentionally dirty. Do not overwrite newer local work with an older remote code baseline merely because these control-plane docs are newer.

## Current phase
Daily-use Workbench closure.

Active Master Task: `MT-20260907-MAIN-DAILY-USE-RELEASE-006`.
Primary implementation owner: MAIN Agent.
Target gate: `DAILY_USE_MASTER_GREEN`.

Packaging is paused until that gate is reached and accepted. The earlier colleague ZIP from `MT-20260907-MAIN-COLLEAGUE-PACKAGE-005` is superseded as a final release candidate because real daily-use defects were found afterward.

Current task execution model: GPT-5.6 Terra / High.
Current PIE application analyzer model: Terra. `EXECUTION_MODEL` and `PIE_ANALYZER_MODEL` are separate settings; never infer an analyzer-model change from a Codex task model choice.

## Read first for Daily Case / knowledge work
1. `MASTER_PLAN.md`
2. `AGENT_REGISTRY.md`
3. Issue #1 — Learning Candidate intake; read newest/relevant comments only.
4. `docs/workbench/CONTINUOUS_LEARNING_LOOP.md` — current daily-case learning/write behavior.
5. `docs/knowledge/CANDIDATE_CLASSIFICATION.md` — classify learning value before any GitHub write.
6. `governance/DATA_PROTECTION.md` — storage/security boundary.
7. `docs/knowledge/` — promoted reusable knowledge relevant to the current case.
8. `docs/regression/REAL_CASE_REGRESSION.md` — reusable regression assertions.
9. `docs/architecture/DIAGNOSTIC_ARCHITECTURE.md` — stable diagnostic architecture.
10. Issue #2 only when discussing architecture changes.

Do not load all historical material by default.

## New Daily Case Window bootstrap — mandatory
When a new chat/window is designated as the Daily Case collection window, before its first GitHub write read the current versions of:
- `MASTER_PLAN.md`
- `AGENT_REGISTRY.md`
- `README.md`
- `GPT_HANDOFF.md`
- `docs/workbench/CONTINUOUS_LEARNING_LOOP.md`
- `docs/knowledge/CANDIDATE_CLASSIFICATION.md`
- `governance/DATA_PROTECTION.md`

Then apply this default:
`current case -> read full context from Nextop / ITR when needed -> solve current issue -> evaluate reusable learning -> write only the reusable learning/correction/regression value to GitHub`.

GitHub is not used to determine whether the same device has returned. Device-level history, partner conversation and ticket history should be re-read from Nextop / ITR using the current work order/context when needed.

Do not persist device name, work-order/CaseID, agent name/company, full raw email/chat or full accepted reply merely for traceability. Keep them out unless a specific knowledge/regression rule genuinely depends on that exact field or wording.

## Daily Case / Workbench presentation contract
Customer description remains the existing design:
- original English;
- Chinese translation.

The internal analysis shown after it should prioritize:
1. 当前判断
2. 关键依据
3. 下一步
4. 我的建议 / 我的补充
5. 回复代理 / 回复邮件

For normal case handling:
- current judgment should state the most likely direction but explicitly say when root cause cannot yet be determined;
- key basis should contain only 2–5 facts that actually change diagnosis;
- next action should address the largest current uncertainty; default to one action -> one diagnostic question;
- when a partner-facing English reply is needed, provide a brief Chinese meaning/reference before the final English reply;
- final English reply should be easy to copy as plain text, use short natural technical-colleague wording, avoid AI checklist/report style, and not include a person's name in the closing;
- if a sign-off is needed, use `Best regards,` without appending a personal name unless explicitly requested;
- if the case is outside PIE outbound scope, do not generate a partner-facing reply: provide the internal technical note/routing action instead.

## Core boundaries
- PIE is remote technical support; agent/service staff perform physical repair/testing.
- Nextop / Feishu ITR / Case History are the full case-fact sources of truth.
- `机型映射表` is the intended model-resolution business source.
- Vision is a diagnostic input, not attachment decoration.
- `already replaced` != `ruled out`.
- `cannot reproduce` != `fault ruled out` and does not automatically mean NFF.
- `clean log` != `repair completed`.
- `error code` != `root cause`.
- `new replacement` != `known-good`.
- Evidence routing depends on problem type, actor/device location and conversation state; logs are not universal.
- Partner reply follows **minimum sufficient response**.

## Privacy / analyzer boundary
P0 is accepted MASTER GREEN.

Raw ticket history and unnecessary identity/commercial content stay local. Cloud analysis receives only the minimized Technical Evidence Envelope. Local technical reference retrieval is scoped evidence and must not send full source documents/rows/bodies to the analyzer.

`retrieved != applicable != decisive`.

## Validation / NFF
Default final validation loop:
- Functional Test
- Communication Check
- Auto Map Run
- retain the three reports
- Connect Checking screenshot

Relevant non-ultrasonic FAIL remains meaningful unresolved evidence. Ultrasonic test failure is not a repair-acceptance blocker by itself.

Burn-in Test means Mammotion Kit aging/stability testing and does not replace the standard validation loop.

NFF remains AI candidate -> PIE final confirmation.

## Logs
Logs are not the default answer. Use them only when they can discriminate between current hypotheses.

If a log's Device Name / SN does not match the current case device, stop using that log to diagnose the current machine until the correct device/log is confirmed.

## Intake / promotion
Every Daily Case should be checked for learning value.

Classify: `NEW / REINFORCEMENT / CONFLICT / POSSIBLE_SUPERSEDED / DUPLICATE / INSUFFICIENT / NO_ACTION`.

GitHub candidate should preserve the reusable content, not the entire case:
- model/product scope when relevant;
- symptom/error/component/path;
- decisive evidence and validated action/result;
- reusable diagnostic or service strategy;
- scope/version/guardrail;
- Workbench/reply/business-boundary correction.

Stable reusable rule -> relevant `docs/knowledge/` file.
Representative regression assertion -> regression corpus.
Stable system/workflow/governance change -> architecture/workbench/governance file.

Do not promote a single case into a broad universal rule without sufficient evidence.
Do not call an Issue #1 comment a formal rule unless promoted to the appropriate tracked file.

## Security
Never store API keys, tokens, passwords or other credentials.
If the user explicitly says certain information must not be recorded, exclude it.

## Agent execution/reporting
- ITR主管 -> Issue #4 tasks/direction.
- MAIN -> implementation/verification -> Issue #3 terminal report.
- Historical A/B/C/D specialists are not active shared-workspace owners unless explicitly reactivated per `AGENT_REGISTRY.md`.
- `BLOCKED SUBTASK != BLOCKED PROJECT`.
- Ordinary bugs/test failures/timeouts inside authorized scope should be repaired autonomously.
- Every terminal MAIN state should be reported to Issue #3; do not make the user manually carry reports when GitHub delivery is available.

## Next implementation gate
Do not reopen colleague packaging or start Error Code implementation in the shared workspace until MAIN reports `DAILY_USE_MASTER_GREEN` and the supervisor accepts it, unless the supervisor explicitly changes priority/ownership and isolates the work.

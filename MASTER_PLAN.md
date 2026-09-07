# PIE-ITR MASTER PLAN

Status: Active
Last updated: 2026-09-07 (Europe/Berlin)
Owner: ITR主管
Canonical repository: `lulululucy1227/PIE-ITR-1`
Canonical local workspace: `C:\Users\Reggie\Desktop\PIE-ITR-1`

## 0. Authority and recovery order

For a new GPT/Codex window, recover project state in this order:

1. `MASTER_PLAN.md` — current project direction, phase, gates and next priorities.
2. `AGENT_REGISTRY.md` — authoritative agent topology and responsibilities.
3. Issue #4 — newest active supervisor task / direction update.
4. Issue #3 — newest execution report / acceptance state.
5. `GPT_HANDOFF.md` and `governance/` — durable business, security and execution rules.
6. Relevant `docs/` only as needed for the task.

If chat memory conflicts with these files, do not invent a merged state. Prefer the newer GitHub control-plane state and verify against the latest Issue #3/#4 comments.

Important: the active local implementation can be ahead of remote `main`. The local worktree is intentionally dirty. Do not overwrite newer local code merely because remote GitHub docs are newer.

## 1. Mission

PIE-ITR is not a generic CRM or AI chatbot. Its purpose is to make PIE technical support work easier:

`Solve today’s ticket -> learn from the actual outcome -> turn stable patterns into agent self-service knowledge -> reduce repeated known tickets.`

The system should help PIE answer three questions quickly:

- What is the problem now?
- Why is that the current judgment?
- What is the single most valuable next action?

The long-term business outcome is not simply “more tickets processed”. Known/repeated/self-service-eligible tickets should decline while PIE focuses on genuinely complex/new cases.

## 2. Stable business boundaries

- PIE is remote technical support. Agent/service staff perform physical repair, replugging, wiring, replacement and on-site testing.
- Nextop / Feishu ITR / Case History are case-fact sources of truth; GitHub is not a second ticket database.
- `already replaced != ruled out`.
- `cannot reproduce != ruled out / NFF`.
- `clean log != repair completed`.
- `error code != root cause`.
- `new replacement != known-good`.
- Vision is evidence, not diagnosis.
- Error Code is scoped evidence, not a universal fixed answer mapping.
- NFF remains AI candidate -> PIE final confirmation.
- ITR Todo remains preview -> human confirmation.
- No automatic production send to Nextop / WhatsApp / Lark / Email.

## 3. Current formal Workbench behavior

### Daily startup
Formal daily entry remains the project launcher (`start_v2.bat` in the active local implementation).

The intended lifecycle is:

`launch -> Chinese Workbench -> work -> close visible Workbench -> owned runtime exits -> 8787 released -> later relaunch succeeds`.

### Case presentation contract
The customer-description section is intentionally unchanged:

1. Customer/partner original English
2. Chinese translation

After that, the internal analysis presentation must follow:

1. 当前判断
2. 关键依据
3. 下一步
4. 我的建议 / 我的补充
5. 回复代理 / 回复邮件

The existing human-edit/supplement behavior must remain. Presentation changes must not create a second analyzer or second Daily Case page.

### Daily Case diagnostic presentation
- `当前判断`: direct current direction; if evidence is insufficient, explicitly state that the root cause cannot yet be determined.
- `关键依据`: only 2–5 facts that materially change the diagnostic direction.
- `下一步`: prioritize the action that resolves the largest current uncertainty; default to one action -> one diagnostic question.
- External reply: short, human technical-colleague style; no AI checklist/heading/report style; typically 3–6 short sentences; `Best regards,` with no automatic personal name.

### Multi-domain cases
Multiple detected domains must not normally terminate with “PIE manually split before analysis”. Internally, the system may form candidate episodes and judge whether they are one fault chain, independent, or relationship-uncertain. Continue safe analysis where possible; ask the human only when an ambiguous relationship materially changes the next action.

## 4. Current technical gates already reached

### P0 — Cloud data minimization: MASTER GREEN
The formal analyzer path uses a local Technical Evidence Envelope. Raw ticket history, contact data, commercial information, unrelated correspondence, unique device identifiers and credentials are kept out of the cloud analyzer by default.

Current authorized PIE analyzer model: Terra.

Important: `EXECUTION_MODEL` for Codex and `PIE_ANALYZER_MODEL` are separate concepts. A task model selection never authorizes an application analyzer model switch.

### P1 — Daily Reply + local technical knowledge: MASTER GREEN
- Daily Reply style contract is enforced.
- Parsed local technical references participate through scoped local retrieval before analysis.
- Retrieval is evidence only: `retrieved != applicable != decisive`.
- Administrative reference material does not participate in diagnosis.
- Raw reference documents / full rows / full bodies remain local; only selected minimal technical facts may enter the sanitized envelope.

Local parsed-reference state reported by MAIN on 2026-09-07: 6 Excel sources (1,904 data rows) and 1 Word source (76 paragraphs) were converted/registered; technical index and administrative index are separated. Image-only information from the Word file is not treated as parsed fact unless separately interpreted and validated.

### P2 — ITR Review missing-field handling: MASTER GREEN
Missing values are not silently guessed. Review should distinguish source absent, normalization/mapping failure, ambiguous/withheld, or not applicable. Blank/unknown local values must not clear existing Feishu values.

### P3 — Runtime lifecycle
A prior clean-room acceptance passed two close -> owned-runtime-exit -> port-8787-free -> relaunch cycles. This must still be included in the current Daily-use closure regression because later implementation changes can regress it.

### P4 — Feishu production write gate
The intended gate is:

`Preview -> Feishu preflight -> visible non-empty diff -> explicit human Confirm/Commit -> write approved changed fields -> read-back verification`.

Synthetic/gate coverage exists; a real production Commit is not a prerequisite for Daily-use usability and must still require explicit final human confirmation. Unknown/blank Workbench values cannot clear existing Feishu values.

## 5. Current active phase

### ACTIVE MASTER TASK
`MT-20260907-MAIN-DAILY-USE-RELEASE-006`

Owner: MAIN Agent
Current target: `DAILY_USE_MASTER_GREEN`

Current supervisor direction includes:
- real daily-use usability closure, not packaging;
- multi-domain cases must not default-block safe analysis;
- user-facing normal Workbench language should be Chinese;
- preserve customer original English + Chinese translation;
- internal presentation follows `当前判断 -> 关键依据 -> 下一步`;
- preserve `我的建议/我的补充` and existing evidence/NFF/ITR-review behavior;
- verify single-domain, multi-domain, insufficient evidence, replaced-but-still-failing, cannot reproduce, scoped Error Code, degraded attachments, local-knowledge hit/miss/applicability, Reply, manual supplement/reanalysis, ITR review, NFF candidate, normal close, 8787 release and relaunch;
- ordinary defects must be reproduced, generically fixed, regression-tested and revalidated without using the user as a retry button.

Current execution model for this task: GPT-5.6 Terra / High.
Current application analyzer model: Terra.

### Packaging gate
Packaging is explicitly paused.

The package produced by `MT-20260907-MAIN-COLLEAGUE-PACKAGE-005` proved portability/startup but is superseded as a release candidate because real daily-use defects were found afterward. Do not distribute it as the final colleague package.

Only after `DAILY_USE_MASTER_GREEN` is accepted by the supervisor should colleague packaging/release testing reopen.

## 6. Standard repair / NFF validation rules

Default final validation loop:

- Functional Test
- Communication Check
- Auto Map Run
- retain the three reports
- Connect Checking screenshot

PDF handling is failure-oriented: relevant non-ultrasonic FAIL remains meaningful evidence of an unresolved area. Ultrasonic test failure is not a repair-acceptance blocker by itself.

Burn-in Test means Mammotion Kit aging/stability testing. It is additional stability validation and does not replace the standard validation loop.

## 7. Logs

Logs are used only when they can discriminate between current hypotheses. If repair history, test configuration, fault timing, actual behavior, Device Name or SN is unclear, resolve those first.

If Device Name / SN in a log does not match the current case device, stop using that log to diagnose the current machine until the correct device/log is confirmed.

## 8. Solve -> Learn -> Prevent roadmap

### Solve
Workbench helps PIE understand evidence, choose the minimum useful next action and draft the partner reply.

### Learn
For real at-time tickets, preserve original Prediction; later evidence produces Actual Candidate; compare Prediction / final PIE handling / Actual as MATCH / PARTIAL / MISS / NOT_EVALUABLE; Learning Candidate stays human-gated.

### Pattern
Comparable cohorts must consider model/version, fault domain, error code, actor/location, decisive evidence, previous repair action and result. Correlation is not root cause.

### Prevent
Stable, reviewed patterns may become agent-facing Troubleshooting / FAQ / SOP so agents solve repeated low-risk issues themselves. The desired outcome is fewer repeated known tickets without increasing reopen/rework.

## 9. Error Code专项 — planned, not active

Error Code work is a dedicated future stream, not a shortcut from code to fixed repair answer.

Planned output orientation:

`Error Code -> observed fault phenomenon -> scoped fault domain/component candidates -> decisive checks -> repair/handling method -> post-repair validation`

Requirements:
- exact model/version/tool scope where applicable;
- distinguish warning/informational codes from repair-driving evidence;
- evidence strength and currentness;
- alternative causes and replacement-failed cases;
- no universal `code -> replace part` behavior;
- final agent-facing guidance should be self-service oriented only where safe and stable.

Do not start this stream in the active shared workspace while MAIN is still executing `MT-20260907-MAIN-DAILY-USE-RELEASE-006` unless the supervisor explicitly isolates ownership/worktree.

Preferred existing specialist candidate is documented in `AGENT_REGISTRY.md`.

## 10. Feishu / production-write posture

- Feishu ITR writes may only occur behind the explicit review/confirmation gate.
- No bulk write/backfill/delete/schema/taxonomy rewrite is implied by a single-case write authorization.
- NFF and Todo keep human final gates.
- The ITR main table remains protected from broad changes unless specifically justified/approved.

## 11. Execution discipline

- One MAIN owner for the active shared implementation line.
- Old specialist agents do not concurrently modify the same dirty workspace unless the supervisor explicitly reactivates them with isolated ownership.
- `BLOCKED SUBTASK != BLOCKED PROJECT`.
- Ordinary bugs/test failures/timeouts are handled autonomously inside the authorized scope.
- Every terminal MAIN state should be reported to Issue #3; supervisor tasks/direction go to Issue #4.
- Agent identity is not a model identity. Select the lowest sufficient model/effort per task and state `EXECUTION_MODEL / EFFORT / REASON`.

## 12. Next gate

Do not reopen packaging or start Error Code implementation until one of the following happens:

1. MAIN posts `DAILY_USE_MASTER_GREEN` to Issue #3 and supervisor accepts it; or
2. supervisor explicitly changes priority/ownership.

At `DAILY_USE_MASTER_GREEN`, next decisions are:
- colleague package/pilot release;
- Error Code专项 ownership and isolation;
- continue real-case operating evidence accumulation for Solve -> Learn -> Prevent.

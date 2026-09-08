# PIE-ITR MASTER PLAN

Status: Active
Last updated: 2026-09-07 (Europe/Berlin)
Owner: ITR主管
Canonical repository: `lulululucy1227/PIE-ITR-1`
Canonical MAIN local workspace: `C:\Users\Reggie\Desktop\PIE-ITR-1`
Planned Error Code isolated workspace: `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`

## 0. Authority and recovery order

For a new GPT/Codex window, recover project state in this order:

1. `MASTER_PLAN.md` — current project direction, phase, gates and next priorities.
2. `AGENT_REGISTRY.md` — authoritative agent topology and responsibilities.
3. For MAIN: Issue #4 newest active task/direction, then Issue #3 newest execution report.
4. For Error Code Specialist: Issue #5 newest active task/direction, then Issue #6 newest execution report.
5. `GPT_HANDOFF.md` and `governance/` — durable business, security and execution rules.
6. Relevant `docs/` only as needed for the task.

If chat memory conflicts with these files, do not invent a merged state. Prefer the newer GitHub control-plane state and verify against the task/report channel belonging to the active agent.

Important: the active MAIN local implementation can be ahead of remote `main`. The MAIN worktree is intentionally dirty. Do not overwrite or normalize newer local code merely because remote GitHub docs are newer.

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
- Stable real-case patterns may nevertheless justify a simple agent-facing `symptom -> most likely part -> repair -> verification` path when evidence is strong and scope is clear.
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

## 5. Current active phase — two isolated parallel tracks

### Track A — MAIN / Workbench

ACTIVE MASTER TASK: `MT-20260907-MAIN-DAILY-USE-RELEASE-006`

Owner: MAIN Agent
Workspace: `C:\Users\Reggie\Desktop\PIE-ITR-1`
Task channel: Issue #4
Report channel: Issue #3
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

### Track B — Error Code / Agent Repair Assistant

ACTIVE PARALLEL STREAM.

Owner: Error Code Specialist
Planned isolated workspace: `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`
Task channel: Issue #5
Report channel: Issue #6
Initial master task: `EC-MT-20260907-PILOT-001`
Initial target: `ERROR_CODE_PILOT_GREEN`
Execution model for the initial one-time architecture/data/product build: GPT-6 / High, because this phase combines heterogeneous source analysis, repair-outcome mining, schema design, product simplification, implementation and verification. Later routine maintenance should use the lowest sufficient model.

The two tracks are intentionally independent. Track B must not write to the MAIN dirty workspace or manipulate the formal Workbench runtime, port 8787, MAIN analyzer config, local case state, Nextop session or Feishu session.

### Packaging gate
Packaging of the colleague Workbench is explicitly paused.

The package produced by `MT-20260907-MAIN-COLLEAGUE-PACKAGE-005` proved portability/startup but is superseded as a release candidate because real daily-use defects were found afterward. Do not distribute it as the final colleague package.

Only after `DAILY_USE_MASTER_GREEN` is accepted by the supervisor should colleague packaging/release testing reopen. Error Code Pilot work does not depend on that packaging gate because it runs in an isolated stream.

## 6. Standard repair / NFF validation rules

Default final validation loop:

- Functional Test
- Communication Check
- Auto Map Run
- retain the three reports
- Connect Checking screenshot

PDF handling is failure-oriented: relevant non-ultrasonic FAIL remains meaningful evidence of an unresolved area. Ultrasonic test failure is not a repair-acceptance blocker by itself.

Burn-in Test means Mammotion Kit aging/stability testing. It is additional stability validation and does not replace the standard validation loop.

For agent self-service, the displayed verification should be the minimum clear set needed for that repair path, while the canonical knowledge retains the full validated requirement and escalation evidence where applicable.

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
Stable, reviewed patterns may become agent-facing Troubleshooting / FAQ / repair guidance so agents solve repeated low-risk issues themselves. The desired outcome is fewer repeated known tickets without increasing reopen/rework.

## 9. Error Code专项 — ACTIVE PARALLEL STREAM

### Product objective

The external product is an **Agent Repair Assistant**, with Error Code Repair Guide as the first module. It is intentionally simpler than the PIE Workbench.

Primary agent-facing flow:

`Error Code / Error Message -> observed fault phenomenon -> most likely faulty part -> recommended repair -> verification -> fixed / still not fixed`

Rules:
- the agent-facing page must be simple, direct, readable and repair-oriented;
- the normal path should reach a repair answer in at most a small number of clicks;
- do not expose internal evidence hierarchy, root-cause tree, diagnostic confidence, R&D routing or engineering notes unless an agent genuinely needs a specific instruction;
- if one code has multiple common real-world manifestations, use a simple symptom choice to separate them;
- add an extra decisive check only when real evidence shows symptom selection alone cannot safely distinguish the repair path;
- if a strong, scoped real-case pattern shows that a specific symptom is usually repaired by replacing a specific serviceable part, the page should state that part and action directly;
- unstable or unsupported relationships must not be converted into confident replacement advice;
- warning/informational codes that do not require repair should say so plainly;
- replacement-failed cases must not mechanically repeat the same replacement forever; route to a validated alternative or PIE.

### Knowledge architecture

Raw Error Code sources remain internal reference data and are not the portal database.

Canonical pilot knowledge orientation:

`ERROR -> SYMPTOM -> PART -> REPAIR -> VERIFICATION -> IF_NOT_FIXED`

Internal metadata may retain:
- model/product scope;
- firmware/tool scope when material;
- source/evidence/currentness;
- case cohort counts where actually available;
- knowledge status and agent visibility;
- alternative causes;
- replacement-failed behavior;
- last review / supersession information.

Do not invent success rates or universal `code -> part` mappings when source evidence is incomplete.

### Evidence priority

The Error Code master/reference explains what the software detected. Real ITR / Daily Case outcomes explain what actually repaired machines in practice. Agent-facing repair recommendations should prefer stable, scoped, reviewed real repair outcomes over theoretical completeness.

### Initial implementation posture

Pilot implementation should remain lightweight:
- static/read-only knowledge where practical;
- lightweight web SPA;
- exact code search + exact message search + safe fuzzy candidate results;
- no LLM runtime required for the first portal;
- no graph database, large expert system, duplicated Workbench, CMS or production integration unless later evidence requires it;
- no public deployment during the initial Pilot task.

### Isolation

The specialist may inspect MAIN-local parsed Error Code sources read-only and copy only the minimum needed into its isolated workspace. It may not modify the MAIN worktree.

ITR / case sources are read-only evidence inputs for this stream. Do not copy full ticket histories, PII, device identifiers or raw chats into GitHub or published knowledge.

## 10. Feishu / production-write posture

- Feishu ITR writes may only occur behind the explicit review/confirmation gate.
- No bulk write/backfill/delete/schema/taxonomy rewrite is implied by a single-case write authorization.
- NFF and Todo keep human final gates.
- The ITR main table remains protected from broad changes unless specifically justified/approved.
- Error Code Pilot has no production-write authorization to Feishu / ITR / Nextop.

## 11. Execution discipline

- MAIN remains the sole owner of the active shared Workbench implementation line.
- Error Code Specialist owns only the isolated Error Code stream/worktree.
- MAIN reads Issue #4 and reports to Issue #3.
- Error Code Specialist reads Issue #5 and reports to Issue #6.
- Neither agent should consume the other stream’s newest READY task merely because it is newer globally.
- Historical specialists do not concurrently modify the same dirty workspace unless explicitly assigned an isolated scope.
- `BLOCKED SUBTASK != BLOCKED PROJECT`.
- Ordinary bugs/test failures/timeouts are handled autonomously inside authorized scope.
- Agent identity is not a model identity. Select the lowest sufficient model/effort per task and state `EXECUTION_MODEL / EFFORT / REASON`.

## 12. Current gates

### MAIN gate

`DAILY_USE_MASTER_GREEN`

After supervisor acceptance, decide:
- colleague package / pilot release;
- subsequent Workbench improvements;
- integration opportunities with stable Error Code knowledge.

### Error Code gate

`ERROR_CODE_PILOT_GREEN`

Requires at minimum:
- isolated worktree and no MAIN workspace mutation;
- audited Raw Error Code sources separated from publishable knowledge;
- high-value initial Error Code set selected from actual support value/evidence rather than raw-master coverage;
- real symptom -> part -> repair -> verification cards where evidence is adequate;
- unsupported/ambiguous cases withheld or routed to PIE rather than guessed;
- warning/informational and replacement-failed behaviors handled;
- exact/message/fuzzy search behavior verified;
- simple mobile + desktop web Pilot verified;
- no raw case/PII leakage;
- no production write or public deployment;
- clear future adapter so Workbench can later consume the same canonical Error Code knowledge without requiring runtime coupling during Pilot.

Only after `ERROR_CODE_PILOT_GREEN` should the supervisor decide production hosting/auth, external rollout, broader code coverage, and Workbench integration.

### Error Code local specialist checkpoint — 2026-09-07

Local branch checkpoint only; remote MAIN acceptance is unchanged.
Workspace created: C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode.
Branch: error-code/ec-mt-20260907-pilot-001-canonical.
State: TECHNICAL_PILOT_READY / WAITING_BUSINESS_SCOPE; ERROR_CODE_PILOT_GREEN not yet claimed.
Eight selected code entries and a standalone local web Pilot are implemented. Fresh Node/browser/build/privacy/start/relaunch and extracted-package checks passed; see error-code-pilot/docs/HANDOFF.md.
Remaining decision: confirm exact model/series and material version limits for the promoted 1202 cable -> mainboard sequence. Replacement prose remains outside agent data until confirmed.
MAIN implementation/runtime/sessions are untouched by this specialist. Task/report remain Issue #5 / Issue #6.

### Error Code local knowledge checkpoint — 2026-09-08

EC-MT-20260908-KNOWLEDGE-INGEST-004: TROUBLESHOOTER_DESKTOP_KNOWLEDGE_GREEN, local specialist self-approval under the latest Issue #5 task. This supersedes the old local waiting-for-1202-scope project status above; the1202 hardware knowledge item itself remains frozen.

Actual sanitized candidate import19 plus separate frozen1202;0 new full-path promotions,17 PIE_ONLY,2 WITHHELD, frozen extraWITHHELD. Existing desktop behavior preserved. Final64 Node tests,33 browser checks, native125% zoom, two owned lifecycle cycles and extracted eight-entry package/hash/privacy checks passed. Independent review's reciprocal candidate-provenance defect was reproduced, fixed and approved on re-review; no unresolved finding.

Workspace/owner unchanged: C:/Users/Reggie/Desktop/PIE-ITR-ErrorCode, Error Code Specialist. Only the new canonical payload was synced from origin/main1da74aa; no MAIN merge/reset/runtime mutation or production/public/default-branch write. See error-code-pilot/docs/HANDOFF.md. Paired registry update is local only; canonical MAIN acceptance is not asserted. Task/report channels remain Issue #5 / Issue #6.

### Error Code local two-page checkpoint — 2026-09-08

EC-MT-20260908-DESKTOP-TWO-PAGE-005 reached TROUBLESHOOTER_DESKTOP_TWO_PAGE_GREEN. Page1 identifies only; Continue opens Page2 for approved action/verification or safePIE. Back restores selections; edits/refresh/deep links invalidate stale results. Knowledge/promotion decisions and1202 freeze unchanged.64Node,30browser,native125%,two owned8806 lifecycle cycles and extracted8-entry package/privacy checks passed. Independent review60 assertions; unresolvedCritical/Important/Minor0.

Specialist owner/workspace/branch and Issue #5/#6 channels unchanged. Existing8796 listener preserved; no MAIN or production/default-branch/public deployment mutation. See error-code-pilot/docs/HANDOFF.md. This paired local checkpoint does not assert remote supervisor acceptance.

### Error Code local stable-guidance checkpoint — 2026-09-08

EC-MT-20260908-STABLE-GUIDANCE-PROMOTION-006 reached TROUBLESHOOTER_STABLE_GUIDANCE_GREEN.9 supervisor-approved candidate portions publish10 scoped Page2 cards (CHARGE scope split);10 candidates remainPIE_ONLY, extra1202frozen. Canonical31cards/37paths; original21cards unchanged. StrictPage1 identification remains intact.69Node,30existing+21newbrowser, native125% for all10newcards at both desktop sizes, owned8806 lifecycle and extracted8-entry package/privacy checks passed. Independent review unresolvedCritical/Important/Minor0.

Owner/workspace/branch and Issue #5/#6 boundaries unchanged. No MAIN, production/default-branch/public deployment mutation. See current specialist handoff and paired registry checkpoint. Local approval does not assert remote supervisor acceptance.

### Error Code local controlled-selection checkpoint — 2026-09-08

EC-MT-20260908-CONTROLLED-SELECTION-UI-007 reached TROUBLESHOOTER_CONTROLLED_SELECTION_GREEN under authorized local self-approval. A centered progressive identification window asks for supported model/problem area, then controlled specific symptom and optional error code; only necessary confirmation precedes Page 2 actions and verification. Catalog membership, exact symptom/path authorization, stale-input guards and Other-to-PIE handling prevent free-text repair routing. This supersedes the all-text homepage proposal.

Knowledge remains unchanged: nine approved portions / ten scoped guidance cards, remaining PIE_ONLY and frozen 1202 preserved. Fresh 75 Node, 17 controlled-selection, 32 two-page and 21 stable-guidance checks passed, plus native 125% zoom at both desktop sizes, basic mobile, public projection/privacy, owned lifecycle and extracted standalone package checks. Independent review and final addendum have no unresolved findings.

Owner/workspace and Issue #5/#6 isolation remain unchanged. No MAIN/production/public-deployment/default-branch mutation. See error-code-pilot/docs/HANDOFF.md and paired registry checkpoint. Supervisor acceptance is not asserted by this local record.

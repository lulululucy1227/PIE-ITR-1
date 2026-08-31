# PIE-ITR Handoff

## Canonical repository
`lulululucy1227/PIE-ITR-1`

If any task targets another repository, stop and verify before writing.

## Current phase
Real-case accumulation + diagnostic architecture refinement. Code changes remain paused while Codex read access is unreliable.

## Read first
1. Issue #1 — Learning Candidate intake; read newest/relevant comments only.
2. `docs/workbench/CONTINUOUS_LEARNING_LOOP.md` — current daily-case learning/write behavior.
3. `docs/knowledge/CANDIDATE_CLASSIFICATION.md` — classify learning value before any GitHub write.
4. `governance/DATA_PROTECTION.md` — storage/security boundary.
5. `docs/knowledge/` — promoted reusable knowledge relevant to the current case.
6. `docs/regression/REAL_CASE_REGRESSION.md` — reusable regression assertions.
7. `docs/architecture/DIAGNOSTIC_ARCHITECTURE.md` — stable diagnostic architecture.
8. Issue #2 only when discussing architecture changes.

Do not load all historical material by default.

## New Daily Case Window bootstrap — mandatory
When a new chat/window is designated as the Daily Case collection window, before its first GitHub write read the current versions of:
- `README.md`
- `GPT_HANDOFF.md`
- `docs/workbench/CONTINUOUS_LEARNING_LOOP.md`
- `docs/knowledge/CANDIDATE_CLASSIFICATION.md`
- `governance/DATA_PROTECTION.md`

Then apply this default:
`current case -> read full context from Nextop / ITR when needed -> solve current issue -> evaluate reusable learning -> write only the reusable learning/correction/regression value to GitHub`.

GitHub is not used to determine whether the same device has returned. Device-level history, partner conversation and ticket history should be re-read from Nextop / ITR using the current work order/context when needed.

Do not persist device name, work-order/CaseID, agent name/company, full raw email/chat or full accepted reply merely for traceability. Keep them out unless a specific knowledge/regression rule genuinely depends on that exact field or wording.

## Daily Case user-output convention
For normal case handling in the Daily Case window:
- show the diagnostic reasoning/decision logic first;
- when a partner-facing English reply is needed, provide a Chinese translation before the final English reply;
- the final English reply should be easy to copy as plain text and should not include a person's name in the closing;
- if a sign-off is needed, use a neutral closing such as `Best regards,` without appending a personal name unless the user explicitly asks for one;
- if the case is outside PIE outbound scope, do not generate a partner-facing reply: provide the internal technical note/routing action instead.

## Core boundaries
- PIE is remote technical support; agent/service staff perform physical repair/testing.
- Nextop / Feishu ITR / Case History are the full case-fact sources of truth.
- `机型映射表` is the intended model-resolution business source.
- Vision is a diagnostic input, not attachment decoration.
- `already replaced` != `ruled out`.
- Evidence routing depends on problem type, actor/device location and conversation state; logs are not universal.
- `cannot reproduce` != `fault ruled out` and does not automatically mean NFF.
- Partner reply follows **minimum sufficient response**.

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

## Next implementation gate
When Codex read access is healthy, run a gap audit across local implementation + Issue #1 findings + promoted knowledge/regression/architecture before changing code.

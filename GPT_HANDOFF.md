# PIE-ITR Handoff

## Canonical repository
`lulululucy1227/PIE-ITR-1`

If any task targets another repository, stop and verify before writing.

## Current phase
Real-case accumulation + diagnostic architecture refinement. Code changes remain paused while Codex read access is unreliable.

## Read first
1. Issue #1 — learning intake inbox; read newest/relevant comments only.
2. `docs/workbench/CONTINUOUS_LEARNING_LOOP.md` — current daily-case learning/write behavior.
3. `docs/knowledge/CANDIDATE_CLASSIFICATION.md` — classify learning value before any GitHub write.
4. `governance/DATA_PROTECTION.md` — public-repo data boundary.
5. `docs/knowledge/` — promoted reusable knowledge, only files relevant to the current case.
6. `docs/regression/REAL_CASE_REGRESSION.md` — representative regression cases.
7. `docs/architecture/DIAGNOSTIC_ARCHITECTURE.md` — stable diagnostic architecture.
8. Issue #2 only when discussing architecture changes.

Do not load all historical material by default.

## New Daily Case Window bootstrap — mandatory
When a new chat/window is designated as the Daily Case collection window, do **not** infer GitHub behavior from old Issue #1 comments or prior chat memory alone.
Before the first GitHub write in that window, read the current versions of:
- `README.md`
- `GPT_HANDOFF.md`
- `docs/workbench/CONTINUOUS_LEARNING_LOOP.md`
- `docs/knowledge/CANDIDATE_CLASSIFICATION.md`
- `governance/DATA_PROTECTION.md`

Then apply this default:
`daily case != GitHub write`.
Classify learning value first. `NO_ACTION` / `DUPLICATE` stay out of GitHub. `REINFORCEMENT` normally stays out unless evidence/scope is materially strengthened. Only retain minimal sanitized candidates when there is durable new learning value.

Never copy raw emails/chats into this public repository. Do not store partner/customer PII, email addresses, company/contact names, device names, internal/external ticket references, or other identifying case metadata unless explicitly approved and indispensable to a sanitized regression artifact.

## Daily Case user-output convention
For normal case handling in the Daily Case window:
- show the diagnostic reasoning/decision logic first;
- when a partner-facing English reply is needed, provide a Chinese translation before the final English reply;
- the final English reply should be easy to copy as plain text and should not include a person's name in the closing;
- if a sign-off is needed, use a neutral closing such as `Best regards,` without appending a personal name unless the user explicitly asks for one;
- if the case is outside PIE outbound scope, do not generate a partner-facing reply: provide the internal technical note/routing action instead.

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
Daily case facts -> Feishu ITR / Case History.
Potential durable learning -> classify first (`NEW / REINFORCEMENT / CONFLICT / POSSIBLE_SUPERSEDED / DUPLICATE / INSUFFICIENT / NO_ACTION`).
Candidate worth retaining -> Issue #1, minimal and sanitized.
Stable reusable rule -> relevant `docs/knowledge/` file.
Representative case -> regression corpus.
Stable system/workflow/governance change -> architecture/workbench/governance file.
Do not promote a single case without sufficient evidence.
Do not call an Issue #1 comment a formal rule.

## Security
Repository is public. Do not store passwords/tokens, raw chats, customer/agent PII, device/case identifiers, or unapproved sensitive internal material.

## Next implementation gate
When Codex read access is healthy, run a gap audit across local implementation + Issue #1 findings + promoted knowledge/regression/architecture before changing code.

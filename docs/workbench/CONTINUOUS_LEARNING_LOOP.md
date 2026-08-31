# Workbench Continuous Learning Loop

Status: Planned — implement when Codex/local read access is healthy.

## Goal
Make PIE ITR Workbench learn from real daily support work without turning every case into permanent knowledge or forcing PIE to manually maintain a knowledge base.

Core principle:

`Detect -> Candidate -> Evidence -> Human Gate -> Promote`

Workbench may automatically detect potential learning, but it must not silently convert a single case into a stable rule.

## Information layers

### 1. Case Fact
Belongs to the current case / ITR factual record.
Examples:
- actual customer/agent issue
- completed repair actions
- error codes / tool results / image or log evidence
- actual outcome / resolved state
- final verified finding

Case facts do not automatically become reusable knowledge.

### 2. Learning Candidate
Workbench detects that a case may contain reusable value.
Candidate should capture only the minimum useful structure:
- candidate type
- observed fact/pattern
- possible reusable rule
- supporting evidence
- scope / model / version boundary when known
- confidence
- source case reference **inside the internal business system only when needed**

For GitHub/public-repository retention, the candidate must be sanitized and should omit direct case identifiers unless explicitly approved and indispensable.

### 3. Stable Knowledge / Rule
Only after PIE confirmation or sufficient repeated evidence.
Promotion targets:
- diagnostic/tool/error/parts/known-fix knowledge -> `docs/knowledge/` and/or formal KB
- representative case -> `docs/regression/`
- stable system-level behavior -> `docs/architecture/` / `docs/workbench/` / `governance/`

## Daily-case write gate
A daily case does **not** automatically create an Issue #1 comment.

Before any GitHub write derived from a case:
1. Classify it using `CANDIDATE_CLASSIFICATION.md`.
2. Check whether the learning is already represented in current knowledge/rules.
3. Check the public-repository data boundary.
4. Write only when there is durable learning value worth retaining.

Default actions:
- `NO_ACTION` -> no GitHub write.
- `DUPLICATE` -> no GitHub write.
- `REINFORCEMENT` -> normally no new case comment; retain only when the new evidence materially expands confidence/scope and that expansion matters.
- `INSUFFICIENT` -> no durable rule; keep in the case workflow/review queue if needed.
- `NEW` / `CONFLICT` / `POSSIBLE_SUPERSEDED` -> minimal sanitized Learning Candidate may enter Issue #1 for review.

Issue #1 is a **learning intake inbox**, not a raw daily-case ledger.
Do not use Issue #1 to mirror complete emails, chats, Case History, or every accepted reply.

## High-value learning signals
Workbench should preferentially detect:

1. Prediction vs Actual Result
   - what Workbench assessed/recommended
   - what the final verified result was

2. Decisive Evidence
   - which log, image, tool test, cross-test, error code or observed behavior actually changed the diagnosis

3. Failed Assumption
   - which earlier hypothesis or rule was disproved

4. Reusable Validation Method
   - which test/cross-validation reliably narrowed the fault

5. Known Fix / Version Dependency
   - verified fix plus applicable model/version/scope and currentness boundary

6. Workflow / Reply Correction
   - e.g. wrong actor/tool assignment, impossible Next Action, overly long reply, wrong conversation-state handling

## PIE feedback UX
Do not require long manual write-ups.

Recommended lightweight feedback:

### Assessment outcome
`Was this assessment correct?`
- Correct
- Needs correction

If corrected, allow one short field:
`Actual finding:`

### Action/result outcome
`Did this resolve the issue?`
- Resolved
- Partially effective
- Not resolved

### Explicit learning action
Optional `Add Learning` action with three choices:
- Case result only
- Reusable diagnostic knowledge
- Workbench rule / behavior correction

Workbench should draft the candidate automatically; PIE reviews rather than manually structures it.

## Candidate trigger policy
Do not interrupt after every case.

Only surface a learning candidate when there is likely new value, such as:
- new error code or new meaning for an existing code
- new verified root cause
- conflict with existing knowledge
- known fix verified, invalidated or version-limited
- strong known-good cross-validation result
- Workbench assessment proved wrong
- Next Action was technically correct but impossible for current actor/device location
- explicit PIE correction
- repeated same pattern across multiple cases
- newly confirmed tool/model capability
- useful Vision/log/tool evidence pattern
- reply-generation failure with clear reusable lesson

Repeated cases with no new learning should stay quiet.

## Evidence and promotion rules

- Preserve distinction between confirmed fact, direct evidence, repair history and inference.
- `already replaced` is not proof of exclusion.
- A single case may justify a case result or reusable validation method, but not automatically a general troubleshooting path.
- System-level rules require explicit PIE confirmation or repeated/strong evidence.
- Model/version/tool scope must be retained when relevant.
- Later outcomes must not be back-projected into the original at-the-time analysis.
- An Issue #1 comment is not itself a formal durable rule. After PIE confirmation, promote stable system/workflow/governance changes into the relevant tracked file.

## Public-repository sanitization gate
GitHub is public and is not the business-fact database.
Before retaining a Learning Candidate or regression artifact in GitHub:
- remove partner/customer names, email addresses, phone numbers and contact signatures;
- remove partner/company identity unless the identity itself is explicitly approved and necessary to the rule;
- remove device names, serial-like identifiers, internal/external ticket numbers and source references unless explicitly approved and indispensable to regression;
- do not paste raw emails, full chats, raw Case History or private attachment content;
- retain only the technical facts required to understand the learning, Evidence strength and scope.

## Storage flow

```text
Daily case
  -> ITR / Case History factual record
  -> Workbench learning detection
      -> no new value: end
      -> potential value: classify candidate
          -> not worth durable retention: end / internal review only
          -> worth retention: minimal sanitized Learning Candidate
              -> PIE review
                  -> case-specific only
                  -> reusable Knowledge
                  -> Regression Case
                  -> Workbench/System Rule
```

GitHub is for durable rules, candidates worth retaining, regression cases and architecture; it is not the raw full-case database.

## New-window bootstrap requirement
When a new Chat/GPT window is designated as the Daily Case collection window, before its first GitHub write it must re-read the current repository versions of:
- `README.md`
- `GPT_HANDOFF.md`
- this file
- `docs/knowledge/CANDIDATE_CLASSIFICATION.md`
- `governance/DATA_PROTECTION.md`

Do not rely only on prior-chat memory or early Issue #1 comments to infer the current write policy.

## Implementation boundary

Do not implement this feature until Codex/local read access is healthy.

First implementation step must be a gap audit across:
`Local Workbench implementation <-> Issue #1 <-> knowledge/regression/architecture docs`

Then design the minimum UI/data model needed for:
- assessment/result feedback
- Learning Candidate generation
- human review state
- promotion target
- provenance/scope/confidence

Avoid building a heavy standalone knowledge-management UI inside the main support workflow.

## Acceptance criteria

The feature is successful when:
- normal ticket handling remains faster than manual knowledge maintenance;
- PIE can correct the system with one short interaction;
- useful learning is captured without prompting on every case;
- single cases do not silently become universal rules;
- final outcomes can be compared with original predictions;
- stable learning can be promoted to the correct knowledge/regression/architecture layer;
- partner-facing replies remain minimum-sufficient and are not made longer by the learning system;
- opening a new Daily Case window cannot silently revert GitHub writes to a raw-case mirror pattern.

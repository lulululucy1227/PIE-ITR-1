# Workbench Continuous Learning Loop

Status: Planned — implement when Codex/local read access is healthy.

## Goal
Make PIE ITR Workbench learn from real daily support work without forcing PIE to manually maintain a knowledge base or mechanically duplicating every ticket.

Core principle:

`Detect -> Candidate -> Evidence -> Human Gate -> Promote`

Workbench may automatically detect potential learning, but it must not silently convert a single case into a broad stable rule.

## Information layers

### 1. Case Fact
Belongs to the current case / ITR factual record.
Examples:
- actual customer/agent issue
- completed repair actions
- error codes / tool results / image or log evidence
- actual outcome / resolved state
- final verified finding
- device/ticket/agent metadata needed to trace the case

Case facts do not automatically become reusable knowledge, but some case facts are valuable provenance for later learning and regression.

### 2. Learning Candidate
Workbench detects that a case may contain reusable value.
Candidate should capture the useful structure:
- candidate type
- observed fact/pattern
- possible reusable rule
- supporting evidence
- scope / model / version boundary when known
- confidence
- source case reference / device / work-order metadata when useful for traceability
- exact accepted/sent reply when reply wording itself is part of the learning

Do not automatically strip direct case identifiers or conversation material merely because the repository is public. Retain them when they materially help traceability, comparison, regression or reply learning, unless the user explicitly says not to record them.

### 3. Stable Knowledge / Rule
Only after PIE confirmation or sufficient repeated evidence.
Promotion targets:
- diagnostic/tool/error/parts/known-fix knowledge -> `docs/knowledge/` and/or formal KB
- representative case -> `docs/regression/`
- stable system-level behavior -> `docs/architecture/` / `docs/workbench/` / `governance/`

## Daily-case write gate
Every Daily Case should be evaluated for learning value.

Before any GitHub write derived from a case:
1. Classify it using `CANDIDATE_CLASSIFICATION.md`.
2. Check whether the learning is already represented in current knowledge/rules.
3. Decide what original case information is useful for provenance/regression.
4. Check whether the user explicitly excluded any information from recording.
5. Write the amount of case evidence + derived learning needed to remain useful later.

Default actions:
- `NO_ACTION` -> normally no new knowledge artifact.
- `DUPLICATE` -> normally no new knowledge artifact unless the case adds useful traceability or repeated-evidence value.
- `REINFORCEMENT` -> retain when the case materially strengthens confidence, model scope, evidence pattern or regression coverage.
- `INSUFFICIENT` -> do not promote a stable rule; keep the case/evidence only if it remains useful for later resolution.
- `NEW` / `CONFLICT` / `POSSIBLE_SUPERSEDED` -> create a reviewable Learning Candidate with enough provenance to reconstruct why it matters.

Issue #1 is a **learning intake inbox**, not a requirement to copy every Daily Case verbatim. However, case identifiers, agent context, relevant conversation excerpts and accepted replies may be retained when they add value.

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
   - wrong actor/tool assignment, impossible Next Action, overly long reply, wrong conversation-state handling, authority-boundary error

7. Traceability / recurrence
   - same device returning multiple times
   - same work-order family or issue recurring after a repair
   - repeated evidence from the same partner or model that changes confidence/scope

## Value of original case metadata
Original case metadata can be useful and should not be discarded automatically.

- **Device name / identifier**: high value for linking repeated repairs, recurrence, before/after logs and repair history on the same unit.
- **Ticket / CaseID / work-order reference**: high traceability value for finding the original business case and validating what actually happened later.
- **Agent / partner name/company**: lower direct technical value, but useful for conversation continuity, partner tool capability, prior instructions and repeated communication patterns.
- **Exact partner wording**: useful when the wording changes the correct interpretation or exposes a conversation-state failure.
- **Exact PIE reply actually sent**: high value for Reply Regression, especially when studying brevity, authority boundaries, or whether a diagnostic action was clearly communicated.

Retention should therefore be **value-based**, not automatically anonymization-based.

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
- same device/issue returning after repair in a way that changes the repair strategy

Repeated cases with no new learning can stay quiet, but repeated evidence that strengthens or weakens an existing rule is not automatically noise.

## Evidence and promotion rules

- Preserve distinction between confirmed fact, direct evidence, repair history and inference.
- `already replaced` is not proof of exclusion.
- A single case may justify a case result or reusable validation method, but not automatically a general troubleshooting path.
- System-level rules require explicit PIE confirmation or repeated/strong evidence.
- Model/version/tool scope must be retained when relevant.
- Later outcomes must not be back-projected into the original at-the-time analysis.
- An Issue #1 comment is not itself a formal durable rule. After PIE confirmation, promote stable system/workflow/governance changes into the relevant tracked file.

## Retention / exclusion gate
The user controls what supplied case information may be retained.

Default:
- information supplied in a Daily Case may be used for case traceability, regression and knowledge derivation;
- do not automatically remove device names, work-order IDs, agent names/company or full accepted replies;
- keep only information that has practical diagnostic, provenance, regression or reply-learning value;
- never store credentials/secrets.

Explicit user exclusion overrides the default. If the user says an item does not need to be recorded/uploaded, omit that item.

## Storage flow

```text
Daily case
  -> ITR / Case History factual Source of Truth
  -> Workbench learning detection
      -> no useful learning/trace value: end
      -> useful value: classify candidate
          -> retain useful case provenance/evidence
          -> derive reusable learning
              -> PIE review / explicit correction
                  -> case-specific evidence only
                  -> reusable Knowledge
                  -> Regression Case
                  -> Workbench/System Rule
```

GitHub is for durable project learning, including selected case provenance when it improves that learning; it does not need to be a verbatim backup of every business ticket.

## New-window bootstrap requirement
When a new Chat/GPT window is designated as the Daily Case collection window, before its first GitHub write it must re-read the current repository versions of:
- `README.md`
- `GPT_HANDOFF.md`
- this file
- `docs/knowledge/CANDIDATE_CLASSIFICATION.md`
- `governance/DATA_PROTECTION.md`

Do not rely only on prior-chat memory or early Issue #1 comments to infer the current write policy.
The required default is: **evaluate every case for learning; do not automatically discard supplied case information; only omit information the user explicitly excludes, irrelevant noise, or credentials/secrets.**

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
- useful provenance (device/ticket/reply/partner context) can be retained when needed;
- partner-facing replies remain minimum-sufficient and are not made longer by the learning system;
- opening a new Daily Case window cannot silently revert to an outdated intake/retention policy.

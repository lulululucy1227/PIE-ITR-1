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
- source case reference

### 3. Stable Knowledge / Rule
Only after PIE confirmation or sufficient repeated evidence.
Promotion targets:
- diagnostic/tool/error/parts/known-fix knowledge -> `docs/knowledge/` and/or formal KB
- representative case -> `docs/regression/`
- stable system-level behavior -> `docs/architecture/` / Workbench contract

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

## Storage flow

```text
Daily case
  -> ITR / Case History factual record
  -> Workbench learning detection
      -> no new value: end
      -> potential value: Learning Candidate
          -> PIE review
              -> case-specific only
              -> reusable Knowledge
              -> Regression Case
              -> Workbench/System Rule
```

GitHub is for durable rules, candidates worth retaining, regression cases and architecture; it is not the raw full-case database.

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
- partner-facing replies remain minimum-sufficient and are not made longer by the learning system.

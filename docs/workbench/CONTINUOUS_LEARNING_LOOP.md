# Workbench Continuous Learning Loop

Status: Planned — implement when Codex/local read access is healthy.

## Goal
Make PIE ITR Workbench learn from real daily support work without turning GitHub into a second ticket database.

Core principle:

`Detect -> Candidate -> Evidence -> Human Gate -> Promote`

Workbench may automatically detect potential learning, but it must not silently convert a single case into a broad stable rule.

## Information layers

### 1. Case Fact
Belongs to the current Nextop / ITR / Case History factual record.
Examples:
- actual customer/agent issue
- completed repair actions
- error codes / tool results / image or log evidence
- actual outcome / resolved state
- final verified finding
- device, work-order and conversation history

These facts are used to solve the current ticket. They do not need to be duplicated into GitHub just to preserve case history.

### 2. Learning Candidate
Workbench detects that a case contains reusable value.

Candidate should capture the smallest useful reusable structure:
- candidate type
- product/model scope when relevant
- symptom / error / component / path
- decisive evidence
- validated action/result
- possible reusable rule
- scope / version boundary
- guardrail / counterexample
- confidence
- Workbench/reply/business-boundary correction when relevant

Normally do not include device name, work-order/CaseID, agent name/company, full raw conversation or full accepted reply. Those belong to the source case in Nextop / ITR and can be re-read there when a current work order requires full history.

Exact wording may be retained only when the wording itself is the object of regression, for example a reply-generation failure that cannot be represented adequately as a shorter assertion.

### 3. Stable Knowledge / Rule
Only after PIE confirmation or sufficient repeated evidence.
Promotion targets:
- diagnostic/tool/error/parts/known-fix knowledge -> `docs/knowledge/` and/or formal KB
- regression assertions -> `docs/regression/`
- stable system-level behavior -> `docs/architecture/` / `docs/workbench/` / `governance/`

## Daily-case write gate
Every Daily Case should be evaluated for learning value, but not every Daily Case should create a GitHub artifact.

Before any GitHub write derived from a case:
1. Classify it using `CANDIDATE_CLASSIFICATION.md`.
2. Check whether equivalent knowledge already exists.
3. Extract only the reusable learning and evidence needed to support it.
4. Preserve model/version/tool scope when it affects applicability.
5. Check whether the user explicitly excluded any information from recording.

Default actions:
- `NO_ACTION` -> no GitHub write.
- `DUPLICATE` -> no new knowledge item.
- `REINFORCEMENT` -> update/strengthen existing knowledge only if the new evidence materially changes confidence, scope or regression coverage.
- `INSUFFICIENT` -> do not promote a stable rule; continue evidence collection in the current ticket.
- `NEW` / `CONFLICT` / `POSSIBLE_SUPERSEDED` -> create a concise reviewable Learning Candidate.

## High-value learning signals
Prefer to capture:

1. **Prediction vs Actual Result**
   - what was assessed/recommended
   - what was later verified

2. **Decisive Evidence**
   - log, image, tool test, cross-test, error code or behavior that actually changed the diagnosis

3. **Failed Assumption**
   - which earlier hypothesis or rule was disproved

4. **Reusable Validation Method**
   - which test or cross-validation reliably narrowed the fault

5. **Known Fix / Version Dependency**
   - verified fix plus applicable model/version/scope/currentness boundary

6. **Workflow / Reply Correction**
   - wrong actor/tool assignment, impossible Next Action, overly long reply, wrong conversation-state handling, authority-boundary error

7. **Repair / service strategy**
   - when to continue repair, stop repair, replace an assembly, escalate, or route to another owner

## What is usually not learning
Normally do not persist merely because it appeared in the case:
- device identifier;
- work-order / CaseID;
- agent personal name;
- company name when it does not alter capability or responsibility;
- full email/chat history;
- exact reply text when the reusable lesson can be expressed as a shorter reply rule.

These can be read again from the current ticket's source system when needed.

## Evidence and promotion rules
- Preserve distinction between confirmed fact, direct evidence, repair history and inference.
- `already replaced` is not proof of exclusion.
- A single case may justify a case result or reusable validation method, but not automatically a general troubleshooting path.
- System-level rules require explicit PIE confirmation or repeated/strong evidence.
- Model/version/tool scope must be retained when relevant.
- Later outcomes must not be back-projected into the original at-the-time analysis.
- An Issue #1 comment is not itself a formal durable rule. After PIE confirmation, promote stable system/workflow/governance changes into the relevant tracked file.

## Storage flow

```text
Daily case
  -> read full ticket/context from Nextop / ITR
  -> solve current issue
  -> learning detection
      -> no reusable value: end
      -> reusable value: classify candidate
          -> extract decisive evidence + reusable rule
              -> PIE review / explicit correction
                  -> Knowledge
                  -> Regression assertion
                  -> Workbench/System Rule
```

GitHub stores reusable project learning, not complete case histories.

## New-window bootstrap requirement
When a new Chat/GPT window is designated as the Daily Case collection window, before its first GitHub write it must re-read the current repository versions of:
- `README.md`
- `GPT_HANDOFF.md`
- this file
- `docs/knowledge/CANDIDATE_CLASSIFICATION.md`
- `governance/DATA_PROTECTION.md`

Required default:
**Use the full case to reason; store only what future similar cases need to know.**

Do not rely only on prior-chat memory or early Issue #1 comments to infer the current write policy.

## Implementation boundary
Do not implement this feature until Codex/local read access is healthy.

First implementation step must be a gap audit across:
`Local Workbench implementation <-> Issue #1 <-> knowledge/regression/architecture docs`

Avoid building a heavy standalone knowledge-management UI inside the main support workflow.

## Acceptance criteria
The feature is successful when:
- normal ticket handling remains faster than manual knowledge maintenance;
- PIE can correct the system with one short interaction;
- useful learning is captured without prompting on every case;
- single cases do not silently become universal rules;
- stable learning is promoted to the correct knowledge/regression/architecture layer;
- GitHub search returns reusable diagnostic/service logic rather than device-level ticket history;
- opening a new Daily Case window cannot silently revert to raw-case mirroring.

# Data Protection and Write Boundaries

Status: Active

## ITR protection
ITR is the business-fact Source of Truth. Knowledge work, analysis, Workbench development and Feishu-agent tasks default to read-only access to the ITR main table.

Any proposed ITR main-table schema/field/formula/workflow or business-logic change requires a separate rationale and explicit user approval before implementation. The proposal should state: reason, affected scope, risks, and alternatives.

The ITR taxonomy/tag system follows the same default protection boundary unless a task explicitly authorizes a change.

## Evidence preservation
Original source evidence must not be silently rewritten to fit a derived conclusion. Raw source text/attachments and derived analysis are conceptually separate.

Source timestamps may only be represented as source timestamps when they were actually parsed from source evidence. Do not manufacture or infer precise source timestamps.

## Repository security
This repository may contain case-derived working knowledge and traceability metadata when they are useful to PIE learning, regression, or future diagnosis.

Never commit:
- API keys, tokens, passwords, secrets or credentials;
- material the user explicitly says must not be recorded or uploaded;
- fabricated identifiers, timestamps, findings or outcomes.

Do not automatically delete or omit information only because the repository is public. The user's standing instruction is that case information may be retained by default unless the user explicitly says a specific item should not be recorded.

## Case-information retention rule
For Daily Case learning, the following information may be retained when it contributes to traceability, diagnosis, regression, conversation continuity, or reply-quality learning:
- device name / device identifier;
- internal or external ticket / work-order / CaseID reference;
- agent or partner name/company;
- model and repair history;
- exact error codes, logs/tool findings and performed actions;
- the actual partner question or relevant conversation excerpt;
- the actual PIE reply that was accepted/sent, especially when reply wording itself is part of the learning;
- later result/correction that validates or disproves the assessment.

These fields are not automatically knowledge by themselves. Their value is to preserve provenance and allow later comparison across cases.

## Knowledge abstraction rule
Each real case should still be processed into the highest-value reusable form rather than merely copied as raw text.

Use two layers when useful:
1. **Case trace / evidence** — enough original context to reconstruct what happened and why the conclusion was made.
2. **Derived learning** — the reusable diagnostic rule, repair strategy, reply rule, workflow boundary, regression assertion, or candidate knowledge.

A case can therefore keep identifiers or an exact accepted reply while also producing an abstract reusable rule.

Do not remove identifiers, names, ticket references or full replies solely for sanitization. Remove them when:
- the user explicitly says not to record them;
- they add no useful traceability/learning value and only create noise;
- they are secrets/credentials or otherwise unsafe to publish.

## User override
The user has final authority over retention of supplied case information.
- If the user says `不要记录`, `不用上传`, `这个信息不需要沉淀`, or equivalent, exclude that information from GitHub learning artifacts.
- If the user does not give such an exclusion, default to evaluating the information for knowledge/traceability value rather than discarding it.

Feishu ITR / Case History remains the business-fact Source of Truth, while GitHub may retain selected case evidence plus derived rules needed for durable project learning.

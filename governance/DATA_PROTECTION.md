# Data Protection and Write Boundaries

Status: Active

## ITR protection
ITR is the business-fact Source of Truth. Knowledge work, analysis, Workbench development and Feishu-agent tasks default to read-only access to the ITR main table.

Any proposed ITR main-table schema/field/formula/workflow or business-logic change requires a separate rationale and explicit user approval before implementation. The proposal should state: reason, affected scope, risks, and alternatives.

The ITR taxonomy/tag system follows the same default protection boundary unless a task explicitly authorizes a change.

## Evidence preservation
Original source evidence must not be silently rewritten to fit a derived conclusion. Raw source text/attachments and derived analysis are conceptually separate.

Source timestamps may only be represented as source timestamps when they were actually parsed from source evidence. Do not manufacture or infer precise source timestamps.

## Repository storage boundary
GitHub is the durable store for reusable project learning, not for reconstructing complete individual tickets.

Full current-case context should be read from Nextop / Feishu ITR / Case History when needed. Therefore GitHub normally does not need to retain device-level or ticket-level identifiers simply for traceability.

Normally do not persist:
- device name / device identifier;
- internal/external work-order, ticket or CaseID reference;
- agent personal name;
- partner/company identity unless its capability/authority is itself relevant to the rule;
- full raw email/chat or Case History;
- full accepted/sent reply unless exact wording is the regression object.

This is an architecture/noise-control boundary, not a claim that those fields have zero information value. They remain available in the source case and can be re-read there.

## What GitHub should preserve
Retain the technical facts needed to make future similar cases easier to solve:
- model/product scope when relevant;
- component / functional path;
- symptom and exact error code where relevant;
- decisive evidence;
- validated action/result;
- reusable cross-validation or diagnostic method;
- repair/service strategy;
- scope/version/currentness boundary;
- counterexample/guardrail;
- PIE authority/routing boundary;
- reusable reply-generation rule or concise regression assertion;
- explicit user correction that changes system behavior.

## User override
If the user explicitly says specific information should not be recorded/uploaded, exclude it.
If the user explicitly asks to retain a particular case/example or exact wording for regression, that instruction may override the normal minimization rule.

## Security
Never commit API keys, tokens, passwords, secrets or credentials.
Do not fabricate identifiers, timestamps, findings or outcomes.

## Source-of-truth principle
Nextop / Feishu ITR / Case History answer: **what happened in this individual ticket?**
GitHub Knowledge/Regression/Governance answer: **what should we learn from it for the next similar ticket?**

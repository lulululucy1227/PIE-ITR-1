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
This repository is not a production-data backup. Do not commit:
- customer/agent PII;
- raw ITR or Case History exports;
- private Feishu attachments;
- API keys, tokens, secrets or credentials;
- non-public internal data unless explicitly approved for publication.

Use abstractions and sanitized examples for governance/tests committed to a public repository.

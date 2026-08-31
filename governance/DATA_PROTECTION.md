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
- partner/customer names, email addresses, phone numbers or contact signatures;
- raw ITR or Case History exports;
- raw emails/chats or private Feishu attachments;
- device names, serial-like identifiers, internal/external ticket numbers or source references unless explicitly approved and indispensable to a sanitized regression artifact;
- API keys, tokens, secrets or credentials;
- non-public internal data unless explicitly approved for publication.

Use abstractions and sanitized examples for governance/tests committed to a public repository.

## Daily-case sanitization rule
A real case may be used to derive a Learning Candidate, regression case or rule, but the GitHub artifact must contain only the minimum technical facts required to preserve the learning.

Before writing a case-derived artifact to GitHub:
1. Remove direct identity/contact metadata.
2. Remove raw conversation text and signatures.
3. Remove case/device identifiers by default.
4. Keep only evidence meaning, technical pattern, scope and confidence needed for review/reuse.
5. If the learning can be represented without a real-case trace in GitHub, prefer the abstracted rule/candidate.

Feishu ITR / Case History remains the place for complete business facts and source traceability.

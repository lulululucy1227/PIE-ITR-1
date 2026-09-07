# PIE Troubleshooter

Status: Active parallel product stream
Owner: Troubleshooter｜主管
Builder: Troubleshooter｜Builder

## Current product priority

Desktop web is the current primary delivery surface. Mobile remains basic-compatible but is not the optimization priority for the next phase.

## Evidence priority

Before expanding Error Code coverage, audit two Feishu sources read-only:

1. ITR main table — identify high-frequency Error Codes / Error Messages and the actual fault phenomena, replaced parts, handling and outcomes associated with them.
2. 工单速查 — identify existing reusable conclusions, troubleshooting/repair methods, verification methods, reply/knowledge status, and conflicts/gaps against ITR outcomes.

The purpose is not to copy Feishu into GitHub. The output should be a sanitized aggregate/candidate list that Builder can use to prioritize the desktop web product.

## Product flow

`Error Code / Error Message -> observed symptom -> most likely faulty part -> repair -> verification -> fixed / still not fixed`

Keep agent-facing content simple and direct. Complexity belongs in evidence review, not the page.

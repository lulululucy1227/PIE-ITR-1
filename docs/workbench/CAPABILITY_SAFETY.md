# Product Capability Safety

Status: Active baseline

## Fail-safe capability rule
Diagnostic and support capabilities are product/model-specific unless explicitly defined otherwise.

Do not infer that an unknown product supports a diagnostic capability merely because another product does.

Examples include device logs, LogiQ, tool functions, firmware operations and model-specific diagnostic paths.

## Unknown capability
When capability support is unknown:
- do not present it as supported;
- prefer a safe “unknown/not established” result;
- request/consult the relevant capability registry or authoritative product evidence.

## Workbench consequence
Analysis and next-action generation must consult product capability rules before recommending actions such as collecting device logs. Unsupported/unknown capabilities must not be emitted as routine troubleshooting steps.

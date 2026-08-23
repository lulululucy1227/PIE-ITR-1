# Case Identity and Intake Rules

Status: Active baseline

## Canonical ITR identity
For a persisted ITR case, the existing ITR `Ticket No.` (for example `ITR-0818-2001`) is the canonical case identity.

`Reference No.` is an external/source reference and must not be substituted for the canonical ITR identity.

Before a Feishu ITR record exists, a workflow may use a temporary local key (for example a UUID-based temporary identity). After successful create/readback, migrate the workflow to the permanent ITR identity without creating a second permanent Workbench identity.

## Intake sources
The system supports multiple intake sources, including Nextop, WhatsApp, Lark and Email. Source-specific parsing must preserve raw evidence and must not invent fields that were not present in the source.

## Cross-case isolation
Temporary/local identity and matching logic must not allow evidence from one case to leak into another case merely because source references, partner names or similar text overlap.

## Partner resolution
Partner identity resolution should use evidence-driven matching such as exact aliases, email, normalized phone and carefully bounded domain/country signals when applicable.

Rules:
- conflicting signals fail safe rather than silently choosing a partner;
- unknown identity remains unknown unless resolved;
- explicit manual override may take precedence when intentionally supplied;
- avoid hardcoded partner mappings as a substitute for resolver logic.

# Open-source Reuse Policy

Status: Active

## Principle
Before building substantial new PIE ITR capabilities from scratch, check reputable maintained open-source projects for reusable components, schemas, ingestion/audit patterns and tooling.

The goal is lower implementation cost and lower maintenance burden, not maximum dependency count.

## Classification
For each candidate, explicitly classify:
- DIRECT REUSE — suitable component/library can be safely integrated;
- PATTERN REUSE — architecture/schema/algorithm is useful, but importing the full project is not justified;
- REJECT — unsuitable because of license, maintenance, security, deployment complexity or project mismatch.

## Evaluation factors
At minimum review:
- license;
- maintenance/activity;
- security and dependency footprint;
- deployment/runtime cost;
- fit with existing Feishu/Workbench architecture;
- migration/lock-in risk;
- whether it duplicates stable existing functionality.

## Constraint
Do not adopt a large platform merely because it contains useful features. Prefer composition, adaptation and small reusable pieces. Existing stable write paths and data ownership boundaries must not be replaced without explicit architectural justification.

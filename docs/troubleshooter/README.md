# PIE Troubleshooter

Status: Active parallel product stream
Owner: Troubleshooter｜主管
Builder: Troubleshooter｜Builder

## Current product priority

Desktop web is the current primary delivery surface. Mobile remains basic-compatible but is not the optimization priority for the next phase.

## Product scope

PIE Troubleshooter is not only an Error Code portal. It must support two controlled entry modes:

1. `I have an Error Code / Error Message`
2. `I do not have an Error Code`

The second path must use a controlled symptom library. Agent free text must not directly determine a repair recommendation.

## Evidence priority

Before expanding coverage, reconcile three Feishu sources:

1. ITR main table — real frequency, observable symptoms, actual repairs/replaced parts, outcomes and verification.
2. 工单速查 — reusable conclusions, repair guidance, verification, knowledge status, conflicts/gaps.
3. 信息同步库 — newer synchronized technical/service knowledge, model/version/part/verification updates and possible supersession signals.

Existing ITR labels/taxonomy are vocabulary inputs only. They are not automatically agent-facing symptoms because internal labels may mix phenomenon, cause, component and business classification.

## Controlled symptom model

A symptom is an observable machine/user-facing state before diagnosis.

Preferred hierarchy:

`Observable area/category -> controlled symptom`

Add a third level only when real evidence shows the second level is still too broad to choose a useful repair path.

Each published symptom must be:
- directly observable/confirmable by an agent;
- cause-neutral;
- action-neutral;
- one primary phenomenon;
- short and easy to scan;
- sufficiently distinct to change the next path;
- derived from real support evidence rather than invented taxonomy completeness.

`Other / None of these` may collect free-text feedback for taxonomy maintenance, but that text must not directly generate a replacement recommendation.

## Core flows

### Error-code flow

`Error Code / Error Message -> controlled symptom when needed -> most likely faulty part -> repair -> verification -> fixed / still not fixed`

### Symptom-only flow

`controlled symptom -> most likely faulty part/action -> repair -> verification -> fixed / still not fixed`

If evidence is not strong enough for a direct part/action, route to PIE instead of fabricating certainty.

## Product principle

Backend review can be complex. The desktop agent page must remain simple and direct. The primary visible answer is the likely faulty part/action and how to verify the repair, not an engineering explanation.

# PIE Troubleshooter — Simple Knowledge Reuse Design

Status: APPROVED DIRECTION
Date: 2026-09-15
Owner: Troubleshooter｜主管

## 1. Product principle

Troubleshooter exists to help agents and repair technicians finish repairs correctly with as little interaction as possible.

The front end must optimize for:

`minimum input -> clear problem -> direct repair -> clear verification`

Internal knowledge may be complex. The agent-facing experience must not be.

Do not add features merely because the knowledge exists. Every visible field, click, panel and sentence must earn its place by materially helping the repair.

## 2. Required-input budget

Normal path should require only:

1. **Model** — required controlled selection.
2. **Problem / Controlled Symptom** — required controlled selection, filtered by model.
3. **Error Code / Error Message** — optional; may narrow/highlight symptom candidates but must not create a repair answer without symptom confirmation.

`Observable Area` remains useful metadata/grouping, but should no longer be a mandatory extra click when the symptom list can be grouped cleanly.

`Firmware version` is not a normal required input. Ask for it only just-in-time when the selected repair path is genuinely version-dependent.

`Other / None of these` remains available. Free text there is only for PIE escalation and future taxonomy review; it must never directly generate a replacement recommendation.

Target normal interaction:

`Model -> choose problem -> Continue -> repair`

If an exact Error Code is entered, the system may pre-filter or pre-highlight the most relevant controlled symptom, but the user still confirms the symptom.

## 3. Page 1 — Find the problem

Keep the page visually light.

Show only what is currently needed:
- Model
- Problem / Controlled Symptom
- optional Error Code / Message
- just-in-time qualifier only if it changes the repair path
- just-in-time firmware only if the path requires it
- Continue

Do not expose:
- faulty part
- root cause
- repair steps
- SKU
- tools
- verification
- evidence/confidence
- internal taxonomy

Do not build a dense dashboard, category wall or expert console.

## 4. Page 2 — Repair

The first visible content should answer one question:

**What should I do now?**

Default visible structure:

1. Problem summary
2. Primary repair/check action
3. Part / tool only when needed for that action
4. Expected result when the step has a meaningful pass/fail observation
5. Verification
6. Still not fixed -> next safe step / PIE

Rules:
- Prefer one primary action over a long diagnostic checklist.
- Do not show five possible replacement parts at once.
- Parts appear after the branch supports them.
- Do not expose speculative second/third replacement chains.
- Extra rationale, cases, technical background and detailed learning content should be collapsed under a secondary `Why / Learn more` affordance, not shown by default.
- New technicians should be able to expand details; experienced technicians should be able to read the answer quickly without wading through training material.

## 5. Reuse the Reply Assistant knowledge base

Treat the current Work Order Reply Assistant knowledge base as a READ-ONLY source.

Expected high-value source families include:
- `docs/knowledge/ERROR_CODES.md`
- `docs/knowledge/KNOWN_FIXES.md`
- `docs/knowledge/DIAGNOSTIC_KNOWLEDGE.md`
- `docs/knowledge/PARTS_KNOWLEDGE.md`
- `docs/knowledge/TOOL_KNOWLEDGE.md`

The Builder must first locate the newest current Reply Assistant workspace and knowledge directory. The historical canonical workspace `C:\Users\Reggie\Desktop\PIE-ITR-1` may be used only as a read-only fallback if no newer workspace is identified.

The Troubleshooter workspace remains isolated at `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`.

## 6. One-way reviewed reuse, not live coupling

Do not make Troubleshooter depend on the Reply Assistant at runtime.

Use a reviewed one-way import model:

`Reply Assistant knowledge -> source snapshot/manifest -> classify/reconcile -> Troubleshooter canonical/private knowledge -> public projection`

For every reused fact, retain source path/section/hash or equivalent provenance privately.

Classify source facts as one of:
- `PUBLIC_REPAIR_FACT`
- `PUBLIC_TOOL_STEP`
- `PUBLIC_PART_FACT`
- `PRIVATE_INTERNAL`
- `NEEDS_SCOPE_REVIEW`
- `CONFLICT`
- `DUPLICATE`

Only evidence-backed, correctly scoped facts may affect the public repair experience.

## 7. What should be reused first

Priority 1: enrich existing mature Troubleshooter repair cards with information that reduces repair effort:
- decisive check
- confirmed tool step
- confirmed part/SKU when exact model/path compatibility is supported
- replacement/serviceability boundary
- model capability guardrail
- expected result
- verification detail

Priority 2: add a new repair path only when the Reply Assistant knowledge contains a clearly scoped, stable, agent-executable pattern that can be presented without increasing normal input complexity.

There is no target count. Do not expand coverage merely to increase the number of cards.

## 8. Useful source examples already present

Examples of source content that may be valuable after scope/reconciliation:
- GNSS Antenna Check before defaulting to positioning hardware replacement.
- Connect Checking Wi-Fi `--` does not by itself prove Wi-Fi hardware failure.
- Burn-in Test as a discriminating stability check in the correct contradictory cutting-motor scenario.
- Wired Mammotion Kit for relevant firmware/module synchronization workflows.
- Historical verified firmware fixes where the version scope remains valid.
- SBOM as source of truth for service part identification.
- LUBA 3 LiDAR families must not be mixed; exact mapping matters.
- chassis structural breach -> complete chassis service strategy when scope is confirmed.
- confirmed serviceability boundaries and known-good cross-validation patterns.

These examples are source candidates, not automatic publication approvals.

## 9. Do not copy these into the agent-facing product by default

Do not publish merely because the information exists:
- credentials/passwords
- customer/partner PII
- SN / Device Name / raw ticket history
- internal warranty or Service Manager routing
- internal NFF workflow
- reply-writing style rules
- R&D/internal escalation language
- speculative hypotheses
- raw evidence hierarchy
- broad multi-step engineering diagnosis that the agent does not need

## 10. Conflict and currentness rules

Do not silently overwrite existing Troubleshooter knowledge.

If Reply Assistant knowledge and Troubleshooter knowledge disagree:
- preserve both privately;
- determine whether one is newer and explicitly superseding;
- check model/version scope;
- use `EVIDENCE_PROMOTION_POLICY.md`;
- if still materially ambiguous, keep the item private/PIE_ONLY and report it.

1202 remains frozen. The presence of a 1202 path in another knowledge source does not authorize publication until its scope conflict is resolved.

## 11. Simplicity guardrails

This task must not create:
- inventory/ERP management
- a second document repository
- a large sidebar of new modules
- an expert-system tree visible to agents
- a mandatory Area -> Symptom -> Qualifier -> Version questionnaire for normal cases
- a giant SKU table before the faulty part is identified
- a requirement to read related cases before repairing

If a new feature increases required user input or front-page density, Builder must justify that it materially changes the repair path; otherwise do not add it.

## 12. Success criteria

The result is successful when:
- normal problem lookup is faster than the current controlled-selection flow, not slower;
- current stable repair cards gain useful real service knowledge where supported;
- no existing scope/safety guardrail regresses;
- agents see less information at one time, not more;
- new technicians can expand details when needed;
- experienced technicians can reach the action quickly;
- reused Reply Assistant knowledge remains traceable, reviewable and private until explicitly projected;
- no runtime dependency is created between the two products;
- the standalone Troubleshooter package and privacy boundary remain intact.

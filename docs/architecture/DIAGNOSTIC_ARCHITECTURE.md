# PIE-ITR Diagnostic Architecture

## Core flow
`Problem -> Confirmed Facts -> Evidence -> Completed Repair Actions -> Evidence Strength -> Remaining Fault Domains -> Missing Decisive Evidence -> Next Action -> Fallback/Escalation`

## Evidence Router
Route evidence by problem type; do not use one universal sequence.
- Charging/current/voltage/contact: logs/LogiQ when supported + known-good charging cross-test.
- GNSS/positioning/satellite=0: MammoSuite, Connect Checking, screenshots/reports first.
- Module communication/serial/CAN: error code + tool/module status + shared data/power path.
- Upgrade failure: failure stage + error code + module health + firmware; network is only one possibility.
- Physical damage/part request: Vision + model + Parts/SBOM + repair policy.
- Screenshot error: Vision + error-code knowledge + model/tool/version context.

## Evidence strength
Contextual, but generally:
1. direct tool/test result or observed behavior
2. known-good cross-validation
3. controlled behavior change after action/replacement
4. high-confidence log/image/report evidence
5. agent factual statement
6. repair-history statement
7. historical known fix
8. unconfirmed AI/Vision extraction
9. AI inference

## Semantic separation
- Repair Action: confirmed already performed.
- Attempted Fix: performed, outcome not verified or failed.
- Verified Solution: issue resolved and verified.
- Next Action: recommended next step.

## Safety rules
- One error code may have multiple root causes.
- Historical firmware fixes are version-scoped, not permanent universal answers.
- Vision findings retain provenance/confidence and may require confirmation.
- Contact identity alone is insufficient for cross-channel case merge.
- Agent emotion may change tone only, not diagnosis/NFF/ownership/repair strategy.
- Video Call is a workflow state, not a root cause.

## Reply generation
Use minimum sufficient response:
- answer the current question first;
- include only necessary action(s) or blocking question(s);
- do not expose full internal reasoning unless needed.

## Sources
- Issue #1: real-case intake and defects.
- Issue #2: architecture baseline and priorities.

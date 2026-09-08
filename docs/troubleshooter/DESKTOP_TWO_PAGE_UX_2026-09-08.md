# PIE Troubleshooter — Desktop Two-Page UX

Status: ACTIVE PRODUCT DECISION
Owner: Troubleshooter｜主管
Date: 2026-09-08

## Decision

PIE Troubleshooter PC/Desktop must use a strict two-page interaction model.

This is not a cosmetic preference. The purpose is to separate **problem identification** from **repair guidance**, so repair conclusions do not bias the agent while choosing the fault phenomenon.

## Page 1 — Identify the problem

Page 1 contains only the inputs needed to identify the issue.

Allowed content:
- persistent Product / Model context;
- Error Code / Error Message input/search;
- safe fuzzy candidate results when exact match is unavailable;
- controlled `Choose by symptom` navigation;
- Observable Area -> Controlled Symptom -> optional qualifier only when it materially changes the repair path;
- safe `Other / None of these` fallback that routes to PIE / taxonomy feedback;
- Continue / View solution action once a supported path is selected.

Do NOT show on Page 1:
- Most likely faulty part;
- suspected root cause;
- replacement recommendation;
- repair steps;
- verification steps;
- fallback repair chain;
- evidence/confidence metadata;
- internal PIE/R&D notes.

Reason: showing a likely part or repair action while the agent is still choosing the symptom can bias the selection and contaminate the diagnostic path.

## Page 2 — Repair and verification

Page 2 appears only after Page 1 has resolved a supported Error Code/Symptom path or a safe PIE-only outcome.

Normal supported repair page should prioritize:
1. concise selected issue summary;
2. Most likely faulty part / target area, when publishable;
3. What to do;
4. After repair / Verification;
5. `Still not fixed` fallback / escalation.

Where useful, Page 2 may also include:
- applicable model/scope;
- one decisive prerequisite/check if the repair path requires it;
- Fixed / Still not fixed local state.

Do not expose internal evidence hierarchy, source/provenance, taxonomy semantics, confidence math, candidate status or engineering notes on the normal agent page.

## Error Code path

`Page 1: model + Error Code/Message -> exact/candidate match -> controlled symptom only if needed -> Continue`

`Page 2: selected issue -> part/target -> repair -> verification -> still not fixed`

## Symptom-only path

`Page 1: model -> area -> controlled symptom -> optional qualifier -> Continue`

`Page 2: selected issue -> part/target -> repair -> verification -> still not fixed`

Both entry methods must converge on the same canonical Repair Path. Do not maintain separate Error-Code and symptom solution content.

## PIE_ONLY / unsupported behavior

If Page 1 resolves to PIE_ONLY, unsupported, conflicting or insufficiently scoped knowledge:
- Page 2 may still be used as the result page;
- it should explain the minimum next action / evidence to collect / contact PIE;
- it must not fabricate a repair recommendation simply to fill the second page.

## Desktop-first layout

Current priority is PC/Desktop.

Page 1 should optimize scan speed and selection clarity rather than showing large amounts of explanatory content.
Page 2 should optimize repair execution and verification readability.

Mobile remains basic-compatible only in the current phase.

## Acceptance

The UX change is accepted only when:
- Page 1 contains no part/repair/verification leakage;
- Page 2 contains the actionable repair/verification result;
- browser Back returns to the previous Page 1 selection without corrupting model/symptom state;
- changing Page 1 input invalidates stale Page 2 result state;
- exact Error Code, fuzzy candidate, symptom-only and PIE_ONLY paths are all tested;
- existing knowledge projection/privacy boundaries remain intact;
- 1202 remains frozen according to current knowledge rules.

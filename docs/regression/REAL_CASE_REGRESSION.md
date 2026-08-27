# PIE-ITR Real-case Regression Corpus

Use representative cases to validate future changes. Do not hard-code ticket IDs into production behavior.

## Case template
- Case ID
- Product / Device
- Problem
- Evidence Available
- Completed Repair Actions
- Correct Technical Assessment
- Correct Evidence Route
- Correct Next Action
- Incorrect Actions To Avoid
- Known Result
- Required Capabilities
- Regression Assertions

## Initial regression references
### E257011
Focus: translation preload, reply EN/ZH behavior, workflow clarity, ITR review performance/diff, attachment thumbnails.

### E276600
Focus: log-derived charging diagnosis must produce actionable Next Action; decisive logs must reach assessment/reply.

### E284459
Focus: empty case state must not appear successful; separate service health from per-case pipeline success.

### E283687
Focus: GNSS/satellite=0 evidence should route to MammoSuite/Connect Checking/screenshots rather than logs-first.

### E279986
Focus: distinguish MammoSuite vs Mammotion Kit; known-good charging cross-test outweighs replacement history.

### E283413
Focus: Parts/SBOM repair strategy; serviceable chassis module should precede whole-unit replacement request.

### E280886
Focus: attachment Vision must extract technical evidence/error codes and feed case reasoning.

### E277490
Focus: Error 1500 combined with model capability and firmware state.

### E279928
Focus: failed remote upgrade = attempted action, not solution; cross-channel continuation + Video Call.

### THPO127-25012
Focus: full-thread continuity + device-location/actor-aware evidence routing.
Regression expectations:
- identify whether the mower is currently at end-customer site or agent workshop;
- do not instruct end customers to use MammoSuite/Mammotion Kit;
- preserve historical motor-error evidence even when the workshop cannot reproduce the problem;
- do not infer a driver-board fault without decisive evidence;
- answer the agent's latest correction/context first;
- keep the outbound reply minimal and operational;
- do not hard-code case-specific RTK assumptions as product-wide rules without separate verification.

### Luba-VAEBA54E — boundary exit / GNSS
Focus: temporal causality, contextual evidence routing, MammoSuite GNSS Antenna Check, and reply compression after partner frustration.
Regression expectations:
- treat Error 1004 as a consequence when the partner confirms it occurred after the mower had already left the work area;
- do not infer LiDAR failure from a post-event tilt error;
- prioritize the actual current issue: why the mower leaves the work area;
- when logs indicate low vehicle GNSS signal, route the agent to MammoSuite `GNSS Antenna Check` before defaulting to part replacement;
- if GNSS Antenna Check is abnormal, inspect the rear GNSS antenna disk/connector and use known-good cross-validation where appropriate;
- if GNSS Antenna Check is normal and the boundary issue remains, continue to the next relevant fault domain; a known-good LiDAR cross-test may be used as a later discriminating step rather than the first conclusion;
- do not keep requesting Auto Map Run in this case when the partner has already stated it cannot complete on this LUBA 3 workflow; treat that tool limitation as case-specific/pending validation unless independently confirmed;
- outbound reply must omit repeated acknowledgments/background and contain only the minimum actionable next step. The accepted reply started directly with `Please run the GNSS Antenna Check in MammoSuite first.`

### Error 1000022 / 5501 / 6401 / DT-041
Focus: version-aware known fixes, module communication, upgrade-failure routing, and non-exclusion from replacement history.

## Reply-quality regression
Add simple-question cases where one sentence is sufficient. Failure condition: reply adds unnecessary explanation, repeated context, excessive bullets, or AI-like verbosity without improving correctness/actionability.

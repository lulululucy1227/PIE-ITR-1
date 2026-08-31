# Diagnostic Knowledge

Status: Active baseline

## Core evidence rules

- `already replaced` != `ruled out`.
- Prefer decisive observed behavior change over repair history alone.
- Known-good cross-validation is stronger than assuming a newly installed/replaced part is good.
- `cannot reproduce` != `fault ruled out`.
- A clean log does not by itself equal complete repair verification when standard functional/service validation is applicable.

## Evidence routing

Choose evidence based on the actual problem, current actor, device location and conversation state.

- End-customer site: use customer-capable evidence/actions only (reproduce, remap where applicable, screenshots, latest log if upload is possible, visible symptom/error details).
- Agent/service workshop: MammoSuite/Mammotion Kit, service reports, known-good cross-tests, module-level tests and repair validation may be appropriate.
- Do not request logs mechanically for every case.
- Do not instruct end customers to use service-only tools.

## Repair / replacement strategy for confirmed internal water damage

When substantial internal water ingress/corrosion is confirmed, repair strategy must consider residual reliability risk across **unreplaced** electrical modules, not only the modules already diagnosed or replaced.

Technical handling:
- Do not assume replacing one or two affected boards eliminates water-related risk in the rest of the machine.
- If multiple major modules have already been repaired/replaced and the same or related fault continues to recur, continued part-by-part repair may become technically unpredictable.
- In that situation PIE may recommend complete-unit replacement from a **technical repair-strategy** perspective when further repair cannot reasonably ensure long-term reliability.
- This technical recommendation is not warranty/replacement approval; routing/authorization follows `governance/BUSINESS_BOUNDARIES.md`.
- If a service center nevertheless chooses to continue repair, diagnosis should still follow the actual affected functional circuit/assembly and known-good evidence rather than blind part replacement.

Scope boundary:
- Water ingress alone does not identify ingress cause or responsibility.
- No visible external breach does not prove manufacturing defect.
- Prior repair/opening changes the causal possibilities but does not prove that the repair caused ingress.

## Known-good cross-validation

Use confirmed-good compatible components when appropriate to isolate a fault domain.
Examples of applicable categories include battery, driverboard, mainboard, upper shell, vision module, LiDAR, charging station/adapter, motors and other serviceable modules where model compatibility is known.

Rules:
- The reference part must be known-good/behaviorally validated, not merely “another replacement part”.
- Do not dismantle arbitrary customer/delivery units; use legitimately available reference parts/machines.
- A changed behavior after a known-good swap is stronger evidence than a historical error alone.

## MammoSuite pre/post repair validation

Where applicable at an agent/service workshop, the standard whole-machine validation set is:
- Functional Test
- Communication Check
- Auto Map Run
- Connect Checking screenshot

Use the set before repair when baseline validation is needed and repeat after repair for repair validation.
PASS is strong evidence, not universal proof that every intermittent/site-specific/thermal issue is eliminated.

## Mainboard / module replacement and discovery/synchronization

After mainboard/vision-module replacement, if Bluetooth/App discovery fails, a high-value service path is:
1. Confirm the relevant connector/module path.
2. Connect by cable with Mammotion Kit when supported.
3. Run `Flash Name` when that procedure is applicable.
4. Ensure: **The module firmware versions must be the same.**
5. Retest discovery/connectivity.

If a previously valid Mammotion Kit procedure becomes inconsistent after software/tool updates, collect direct workflow/version/error evidence before inventing a new procedure.

## Charging-path reasoning

When a charging case has already identified one external fault (for example a faulty adapter) but charging/low-supply symptoms recur afterward, do not treat the earlier finding as proof that the whole charging system is healthy.

Reusable validation method:
- isolate the external charging path with a confirmed-good charging station + confirmed-good adapter where applicable;
- if the fault persists with the external path controlled, continue mower-side charging/power diagnosis;
- do not promote a single case's exact error-code combination directly into a universal component mapping without separate evidence.

## Symptom-cluster / assembly reasoning

When several failed functions belong to the same service assembly, do not default to a generic bottom-up battery/CAN/mainboard path. Use model structure/SBOM/exploded-view capability first to identify the common assembly and cross-test that assembly when practical.

## Reply-generation diagnostic rule

Internal reasoning may be detailed. Partner-facing output should be the minimum sufficient action/answer for the latest partner point.

- Answer the latest partner point first.
- Do not expose internal evidence hierarchy unless needed for execution.
- Do not restate the whole case.
- Do not force structured checklists when one or two natural sentences are sufficient.

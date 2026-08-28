# PIE-ITR Diagnostic Knowledge

## Evidence principles
- `already replaced` is repair history, not proof of exclusion.
- Known-good cross-validation and observed behavior change usually outweigh repair-history statements.
- Do not request logs universally; route to the evidence source most likely to discriminate the fault.
- Failed/attempted actions are not verified solutions.
- Evidence routing must consider who currently has the device and what that actor can actually do.
- Error timing matters: an error that appears after the main abnormal event may be a consequence rather than the root cause. Do not reverse causality without supporting evidence.

## Reusable patterns
### Charging path
When logs show abnormal docking/charging voltage/current/contact behavior, use those facts to narrow the remaining charging path and produce a concrete next action. Do not fabricate a hardware conclusion if decisive log evidence is absent.

### Battery Test / controlled battery cross-validation
When a MammoSuite Battery Test shows an abnormally steep discharge curve or abnormal battery-voltage behavior, preserve before/after evidence and change only one major variable at a time.
- Before battery replacement, upload a fresh log through MammoSuite.
- Replace the battery with a new or confirmed-good compatible battery.
- Re-run the **Battery Test** using the customer's original charging station and original power adapter when the charging path itself is still under investigation. Keeping the same charging hardware avoids changing multiple variables at once.
- After the repeat Battery Test, upload another fresh log and retain/send the new Battery Test result for comparison.
- A currently normal charge at the workshop does not by itself exclude the customer's charging station/adapter if the original customer-side symptom involved unstable charging or voltage switching.
- The comparison target is: `same mower + same customer charging station/adapter + different confirmed-good battery`, with logs captured before and after the change.

### No power / no boot
When a mower is completely unresponsive, do not stop at external power checks and do not anchor on an older unrelated error. Use a staged known-good isolation path where applicable:
1. confirmed-good compatible battery;
2. observe mainboard / driverboard LED state during power-on attempt;
3. reseat keypad, keypad cable, main power and CAN connectors with power disconnected;
4. known-good driverboard cross-test;
5. known-good mainboard cross-test;
6. if the mower still does not start, known-good **upper shell** cross-test.
External power being normal does not prove the complete power-on chain is normal. A replaced module is not excluded unless the replacement is known-good or the behavior change validates it.

### Model existence / naming validation
Before querying SBOM, Parts, compatibility, or repair guidance, first validate the partner-reported product name against the current model-mapping table / supported product list.
- If the reported model name does not exist in the current product mapping, do not continue analysis as if it were valid.
- Ask for the exact official model name or map the request to a supported model only when the evidence is clear.
- Obvious naming mistakes should be caught before SBOM lookup; otherwise downstream compatibility conclusions may be built on a nonexistent product.
- Example: `YUKA 3` is not a current official model family in the mapped product list. Do not infer compatibility with LUBA 3 from similar generation naming.
- Recommended order for product/part questions: `Partner text -> model-mapping validation -> exact official model -> SBOM/Parts -> compatibility / repair conclusion`.

### GNSS / positioning
Satellite count, Connect Checking, MammoSuite and report evidence may be more diagnostic than logs. `satellite = 0` or failed test items should influence assessment directly.

### Upgrade failure
Treat upgrade failure as a symptom, not a root cause. Consider failure stage, error codes, module communication, firmware state, module health and network/wired path.
- Do not classify the root cause from the failure percentage alone. Failing around ~70%, ~93%, or another late stage does not by itself prove network instability.
- `network instability` should remain a hypothesis unless supported by direct network evidence or a controlled network-path comparison.
- If upgrade failure coexists with repeated errors from a specific module/fault domain, keep that module health in the active diagnosis even when one attempt fails late.
- A known-good compatible module cross-test that changes the outcome carries more weight than an inference based on upgrade percentage. If the mower upgrades successfully and the associated errors disappear with a known-good module, that strongly supports the original module being faulty.

### Shared communication faults
When several modules show communication loss, inspect shared communication/power/data paths before replacing multiple modules independently.

### Recurrence after replacement
If replacing a module makes the mower work normally for a period and the same symptom later returns, treat the temporary recovery as meaningful behavior-change evidence, but not as proof that the replacement module itself is now faulty.
- `worked after replacement for a few days` supports that the replaced module/fault domain is relevant, but adjacent connector, communication, firmware-sync, power or controller-side faults can still cause recurrence.
- Do not jump straight to replacing the same module again.
- Recollect the current symptom evidence first: exact error/screenshot, connector state, Communication Check / Connect Checking where applicable, and fresh log evidence.
- Then decide whether to cross-test the replacement module again or continue into the adjacent communication/mainboard path.

### Multi-motor undervoltage / common power-path fault
When several motor channels report undervoltage at the same timestamp, especially together with battery short-circuit protection, do not diagnose several motors as independently failed.
- Treat the event as a likely common power-path fault until disproven.
- High-priority checks: battery health; charging-station and adapter output; main power cables/connectors between battery, driverboard and mainboard; CAN cable/connectors between driverboard and mainboard.
- For the customer's charging station and adapter, measure both **no-load voltage** and **voltage under load** with a multimeter. A unit that appears normal unloaded may still collapse under load.
- If the mower was repaired successfully in the workshop and the same power/motor errors reappear after return to the customer, keep the customer's charging station/adapter as an active fault source. Do not assume the mower alone caused the recurrence.
- Use a test driverboard to test all four wheel motors and both cutting motors separately. This isolates a motor that may be overcurrent, shorted or mechanically overloaded and potentially damaging the replacement driverboard.
- Do not replace the driverboard again before checking the shared power path and individual motor loads.
- A simultaneous unrelated-looking communication/timestamp error may be a secondary effect of the voltage event; do not promote it to root cause without separate evidence.

### Abnormal cutting-disc noise
When an abnormal mechanical noise sounds like the cutting disc is obstructed, inspect the cutting-disc underside first before escalating to motor or controller diagnosis.
- Check for grass, debris or other material physically blocking the disc and confirm the disc can move freely after cleaning.
- If the same noise remains after cleaning and no obstruction is present, continue to the relevant mechanical mounting/support component rather than assuming an electrical fault.
- Confirmed YUKA case: if the noise persists after the cutting disc is cleaned and free, replace the adapter bracket `C.P.SH.000077000`.
- Audio/video evidence may support a likely mechanical source, but the diagnosis should still be validated by the physical inspection result.

### Side-bumper fault isolation
When a side-bumper error remains after the side bumper strip/assembly has been replaced, do not immediately assume the new bumper is also faulty or jump straight to mainboard replacement.
- Cross-test the suspect/replacement side bumper on a confirmed-good compatible mower first.
- If the same bumper works normally on the known-good mower, this strongly shifts suspicion to the mower-side sensing path rather than the bumper itself.
- A likely mower-side fault domain is the side-bumper Hall sensor / chassis-side sensing structure.
- If the Hall sensor is confirmed faulty and is not independently serviceable, replace the chassis according to the model's supported repair strategy.
- Preserve the distinction between `likely Hall-sensor/chassis fault` and `confirmed Hall-sensor fault`; the chassis-replacement conclusion should follow cross-validation and applicable serviceability evidence.

### Cross-validation
If the mower works normally on a known-good charging station/adapter, the original charging station/adapter/power path becomes a high-priority fault domain even if one of those parts had already been replaced.
More generally, for any replaceable compatible module, use a confirmed known-good module when practical to separate `suspect module fault` from `machine-side shared-path fault`. Observe whether boot, communication, upgrade, positioning, charging or other target behavior changes after the cross-test.
- `No spare part on hand` does not automatically mean `wait for ordered parts`. If the workshop already has a compatible confirmed-good part that is legitimately available to remove, it can be temporarily installed for cross-validation.
- Do not imply that the agent should dismantle a normal customer machine, a machine awaiting delivery, or any unit that is not appropriate to use as a donor/reference.
- Service centers should consider keeping one confirmed-good compatible mower as a **reference machine** for diagnostics. Its compatible modules can then be used as known-good references for other faulty units when appropriate.
- A reference machine is a long-term workshop diagnostic asset, not an instruction to cannibalize an arbitrary working mower.

### Device location / actor capability
Before assigning the next test, identify whether the mower is currently with the end customer or at the agent/service workshop.
- End customer: only request actions realistically available to the customer, such as reproduce/remap, upload latest log, or provide screenshots/error details.
- Agent/service workshop: service diagnostic tools and structured service reports may be requested where applicable.
Do not instruct an end customer to run service-only tools.

### Staged customer-to-workshop evidence collection
When the mower is currently at the customer's site but may later return to the agent workshop, split evidence collection by device location instead of asking for service-tool tests immediately.
- While the mower is with the customer: if the fault recurs, ask the customer to upload a fresh log immediately, note the approximate occurrence time, and capture a short video or screenshot of the abnormal behavior.
- Do not repeatedly ask the customer to remap/reset when those actions have already failed to resolve the issue and the next useful evidence is incident-time data.
- After the mower returns to the workshop: run the applicable MammoSuite checks, including **GNSS Antenna Check**, **Functional Test**, **Communication Check**, **Auto Map Run**, and provide the **Connect Checking** screenshot.
- Upload a fresh log again after the workshop tests so PIE can compare customer-side incident evidence with workshop test results.
- If no device log is visible in the data center, state that explicitly and request a new incident-time upload rather than inferring the positioning state from absent data.
- This state is not automatically NFF. A customer-side active fault with the mower still at the customer remains an evidence-collection case; NFF becomes relevant only after the mower enters the workshop and the original issue still cannot be reproduced/found.

### Non-reproduction
`Cannot reproduce at workshop` does not equal `fault ruled out` and does not automatically qualify a case as NFF. Preserve historical error evidence and consider environment/site-dependent causes when the test environment changed.

### Conversation continuity
Use the full thread to understand current state, but answer the latest partner point first. Do not generate a detached evidence checklist that ignores corrections, device location, completed actions, or the current question.

### Post-repair verification
A symptom disappearing and a clean/latest log are positive evidence, but they do not by themselves prove the mower is ready to return to the customer.
- After repair, use the standard MammoSuite verification set where applicable: **Functional Test**, **Communication Check**, **Auto Map Run**, plus a **Connect Checking** screenshot.
- These outputs serve as repair-completion evidence and should be requested even when the latest logs show no error.
- `latest log has no error` should be treated as supporting evidence, not a substitute for the post-repair test reports.
- If all post-repair checks are normal and the original fault does not recur, the mower can be considered ready for return.

### Water-ingress / warranty evidence collection
Do not jump directly from `water marks`, `water-damaged packaging`, `machine will not power on`, or general signs of use to a warranty decision.
- First collect enough technical evidence to separate: **water-ingress fact**, **possible ingress point**, **repair/disassembly history**, **customer cleaning method**, and only then the later **warranty/service-policy decision**.
- Ask whether this is the first repair/opening, whether the mower has been disassembled before, and what was previously repaired. Previous repair history may be relevant to sealing, but does not prove that a prior repair caused ingress.
- Ask the customer/agent for the exact cleaning method, not a yes/no statement such as `cleaned according to instructions`. Clarify hose use, pressure-washer use, and which areas were directly washed.
- General intake photos, body-condition photos, bumper photos, packaging photos, or distant underside photos are **not sufficient evidence** to identify a water-entry point.
- Request close-up evidence targeted at possible ingress/sealing areas, including where applicable: bellows cover below the grass comb, cutting motor area, key membrane, SN label, visible cracks, damaged seals, or other plausible entry points.
- Absence of a visible entry point in current photos does not prove a product defect or customer misuse. If the evidence is insufficient, say the cause/entry point cannot yet be confirmed and request better evidence.
- PIE should complete this technical evidence collection before routing the final warranty determination to the Service Manager when policy approval is needed.

### Workflow routing boundary
Not every partner request belongs to PIE technical diagnosis. If the issue is caused by an after-sales system workflow, warranty/service-policy decision, or master-data option rather than mower behavior, route it to the owning service/process role instead of inventing a technical workaround.
- Example: in MSCS, if a **Repair Order** does not provide the correct normal-status model option for the mower, treat it as an MSCS/service-process issue.
- Example: if the original issue was reported during warranty but remained unresolved, while the unit is now out of warranty and the original service work order is already closed, treat this as a warranty/service-process decision for the Service Manager rather than a PIE technical reply.
- Do not tell the partner to select a similar or substitute model unless the service-process owner has explicitly confirmed the mapping.
- Do not promise warranty coverage, reopen a work order, or authorize service handling from PIE unless explicitly authorized.
- Route the case to the Service Manager / owning service-process role.
- Once a case is clearly outside PIE scope, do **not** generate a partner-facing email by default. Instead provide only: (1) a short routing prompt to the Service Manager, and (2) an ultra-brief internal note in both Chinese and English.
- Internal-note style: one sentence per language, immediately identifying the key problem and why Service Manager review is required. Avoid background detail that is not needed for routing.

### Reply compression
Internal reasoning may be detailed; outbound reply should contain only the answer, necessary action and truly blocking question. If a sentence can be removed without harming correctness or the next step, remove it.
- Do not repeat the partner's history, corrections, or already-understood background unless a brief acknowledgment is necessary to avoid confusion.
- Prefer one direct instruction plus one fallback over a multi-step diagnostic checklist.
- Avoid generic transitions such as `Based on the current information`, `At this stage`, `Thank you for the detailed information`, or similar filler when they add no action value.
- Do not restate internal evidence hierarchy or diagnostic rationale unless the partner needs it to perform the next action.
- When the partner has already complained about long/AI-like replies, bias even harder toward concise, natural, context-continuous language.
- Final pre-send check: `What is the shortest response that fully helps the agent move forward?` Delete anything that does not improve correctness, execution, or clarity.

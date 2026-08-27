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

### No power / no boot
When a mower is completely unresponsive, do not stop at external power checks and do not anchor on an older unrelated error. Use a staged known-good isolation path where applicable:
1. confirmed-good compatible battery;
2. observe mainboard / driverboard LED state during power-on attempt;
3. reseat keypad, keypad cable, main power and CAN connectors with power disconnected;
4. known-good driverboard cross-test;
5. known-good mainboard cross-test;
6. if the mower still does not start, known-good **upper shell** cross-test.
External power being normal does not prove the complete power-on chain is normal. A replaced module is not excluded unless the replacement is known-good or the behavior change validates it.

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

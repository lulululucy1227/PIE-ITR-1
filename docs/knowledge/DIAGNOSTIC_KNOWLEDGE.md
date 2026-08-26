# PIE-ITR Diagnostic Knowledge

## Evidence principles
- `already replaced` is repair history, not proof of exclusion.
- Known-good cross-validation and observed behavior change usually outweigh repair-history statements.
- Do not request logs universally; route to the evidence source most likely to discriminate the fault.
- Failed/attempted actions are not verified solutions.
- Evidence routing must consider who currently has the device and what that actor can actually do.

## Reusable patterns
### Charging path
When logs show abnormal docking/charging voltage/current/contact behavior, use those facts to narrow the remaining charging path and produce a concrete next action. Do not fabricate a hardware conclusion if decisive log evidence is absent.

### GNSS / positioning
Satellite count, Connect Checking, MammoSuite and report evidence may be more diagnostic than logs. `satellite = 0` or failed test items should influence assessment directly.

### Upgrade failure
Treat as a symptom, not a root cause. Consider failure stage, error codes, module communication, firmware state, module health and network/wired path.

### Shared communication faults
When several modules show communication loss, inspect shared communication/power/data paths before replacing multiple modules independently.

### Cross-validation
If the mower works normally on a known-good charging station/adapter, the original charging station/adapter/power path becomes a high-priority fault domain even if one of those parts had already been replaced.

### Device location / actor capability
Before assigning the next test, identify whether the mower is currently with the end customer or at the agent/service workshop.
- End customer: only request actions realistically available to the customer, such as reproduce/remap, upload latest log, or provide screenshots/error details.
- Agent/service workshop: service diagnostic tools and structured service reports may be requested where applicable.
Do not instruct an end customer to run service-only tools.

### Non-reproduction
`Cannot reproduce at workshop` does not equal `fault ruled out` and does not automatically qualify a case as NFF. Preserve historical error evidence and consider environment/site-dependent causes when the test environment changed.

### Conversation continuity
Use the full thread to understand current state, but answer the latest partner point first. Do not generate a detached evidence checklist that ignores corrections, device location, completed actions, or the current question.

### Reply compression
Internal reasoning may be detailed; outbound reply should contain only the answer, necessary action and truly blocking question. If a sentence can be removed without harming correctness or the next step, remove it.

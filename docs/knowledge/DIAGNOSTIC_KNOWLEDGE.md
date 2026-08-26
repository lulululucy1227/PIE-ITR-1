# PIE-ITR Diagnostic Knowledge

## Evidence principles
- `already replaced` is repair history, not proof of exclusion.
- Known-good cross-validation and observed behavior change usually outweigh repair-history statements.
- Do not request logs universally; route to the evidence source most likely to discriminate the fault.
- Failed/attempted actions are not verified solutions.

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

### Reply compression
Internal reasoning may be detailed; outbound reply should contain only the answer, necessary action and truly blocking question. If a sentence can be removed without harming correctness or the next step, remove it.

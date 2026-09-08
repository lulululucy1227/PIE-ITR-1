# Stable guidance promotion independent review

Task: EC-MT-20260908-STABLE-GUIDANCE-PROMOTION-006
Date: 2026-09-08
Baseline: 32c83b4; reviewed uncommitted canonical/candidate data and stable-guidance tests.

## Assessment

No reproducible Critical, Important, or Minor defect found in the reviewed promotion content and engine-level behavior. The supported portions of all nine approved candidates are represented by ten cards (seven repair paths and three check paths). Charging and station recognition correctly preserve their different model scopes.

## Evidence reviewed

- Supervisor operational maturity decision, original sanitized candidate payload, promotion/evidence policy.
- Diagnostic, tool, and parts knowledge, including simultaneous motor/shared-power handling, cutting test limitations, bumper Hall/chassis serviceability, model-specific repairability, and firmware workflow boundaries.
- Actual canonical/candidate changes against 32c83b4 and unchanged engine qualifier/outcome behavior.

## Verified boundaries

- Existing canonical cards are byte-equivalent at parsed-object level; candidate source content outside review is unchanged; frozen records are unchanged.
- Nine approved candidates are AGENT_GUIDED; ten remaining candidates are PIE_ONLY. Operational history is attributed to supervisor acceptance without inventing an earliest-use date or numeric outcome count.
- Non-1202 cutting action requires explicit actual-mowing/manual-operation qualification. Functional-Test-only behavior remains separate, and exact 1202 search/frozen hardware handling is preserved.
- Multiple wheel/motor failures stop individual-part replacement and route to PIE for shared power; passing a motor test does not automatically establish a driver-board fault.
- Bumper replacement requires a confirmed serviceable fault; mower-side Hall/chassis sensing and unclear serviceability route to PIE.
- No-charge includes LUBA 1; station-recognition excludes it. Combined source swaps do not falsely identify a particular failed component.
- All new paths retain the full standard validation requirements and direct failed/returned handling to PIE rather than speculative downstream hardware.
- Positioning/connectivity/LiDAR remain unsplit and PIE-facing; water/physical damage remain internal assessment; five weak candidates remain unpromoted.

## Executed verification

`node --test error-code-pilot/test/stable-guidance.test.mjs`: 5 passed, 0 failed. These tests also run both catalog/candidate validators, verify public projection privacy, qualifier gating, scope gating, frozen routing, and failed/returned outcome behavior.

## Limits

This review did not run builds/package tasks, inspect production, use port 8787, or perform browser screenshot QA. Parent agent owns browser, packaging, and full-suite validation. No real-world hardware outcome or compatibility beyond the local approved sources was inferred. Only this report was written.

## Bounded UI re-review

Reviewed the two changes in `src/app.mjs` and the reproductions/assertions in `test/stable-browser.mjs`; no build or browser process was started by this reviewer.

Finding counts: **Critical 0; Important 0; Minor 0.**

- Null-part check paths no longer render the misleading faulty-part placeholder. The action, verification, fallback, and outcome controls remain present; information paths retain their existing message and non-null repair targets remain rendered.
- When a multi-reference symptom has been selected but no branch has been selected, a model/firmware edit now recreates its condition choices through `openSymptom`. The model value is already updated before this call. Rebuilding the selection does not reset visit repair history, bypass a qualifier, or render solution content on identification. `validCatalog` ensures all referenced cards/paths exist; `resolveSymptom` returns the chooser for this valid multi-reference state, so this path does not recurse indefinitely.
- The added browser reproduction checks changing the model before branch selection and then rejecting the non-1202 qualifier, requiring PIE without an answer grid. The broader cases assert the absence of a part box for check paths.
- Generic family selector entries are acceptable for this scoped promotion: the new cards use precisely the families declared by the sanitized source, and their instructions still require model-supported tests and confirmed serviceable parts. This does not establish capacity-level or cross-family part compatibility. The selector is derived from literal card scope strings; scope resolution uses literal normalized equality, not inferred family expansion. The existing exact `LUBA 2 5000X` legacy guidance was unchanged and remains separately gated.

Browser result counts are intentionally not claimed here: the parent agent is rerunning the 21-case stable and legacy browser suites and owns that execution evidence.

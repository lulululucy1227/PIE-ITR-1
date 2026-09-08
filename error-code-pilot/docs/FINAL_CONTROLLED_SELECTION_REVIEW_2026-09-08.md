# Independent controlled-selection review — 2026-09-08

Task: `EC-MT-20260908-CONTROLLED-SELECTION-UI-007`  
Target: `TROUBLESHOOTER_CONTROLLED_SELECTION_GREEN`  
Baseline: `9612d92d9f322395e0085d2c329984533374e94d`  
Scope: `src/app.mjs`, `src/engine.mjs`, `src/index.html`, `src/styles.css`, the controlled-selection tests, and the adapted browser tests.

## Verdict

**Approved for the bounded local controlled-selection change.** Unresolved findings: **Critical 0 / Important 0 / Minor 0**.

The implementation now presents one centered identification stage at a time: controlled catalog model plus one of the ten observable areas, then a controlled normal symptom plus optional code/message, then only the applicable condition, qualifier, or scope confirmation. Repair/action/verification content remains on Page 2. The UI does not expose literal first-level or second-level taxonomy labels.

## Safety and routing findings

- Model identities come only from public catalog scopes. Area values come from the existing ten-value constant. Symptom options come only from the 25 public navigation symptoms filtered by exact model and area. Exact membership is retained; no model-family or capacity inference was introduced.
- Unknown-scope paths cannot become wildcard repairs. A repair requires the exact selected symptom reference `{card_id, repair_path_id}`. A non-direct follow-up is allowed only after the referenced predecessor is recorded as completed and its existing fallback points to that follow-up.
- Forged model/symptom values, cross-area IDs, stale candidate buttons, stale solution/outcome controls, edited firmware, and stale browser history fail closed. Other/free text routes to PIE and cannot identify a part.
- Legacy code cards remain auxiliary to the required controlled fault symptom. Existing non-repair code conditions remain usable, while an unlinked code cannot authorize a repair.
- Error `1202` is restricted to the Cutting area and retains only the public obstruction check and free-disc PIE route. The frozen cable/mainboard paths remain nonselectable and no repair mapping was invented.
- Error `5510` remains searchable, but a selected fault symptom cannot be converted into the normal-function information branch. The user receives a PIE explanation that the success message does not explain the remaining fault. No 26th normal-function symptom was invented; the original canonical information card is unchanged.
- No canonical knowledge, candidate data, promotion totals, `PIE_ONLY` decisions, master plan, registry, MAIN workspace, production system, or remote state changed in the reviewed diff.

## Review-driven fixes

The initial review found that repair authorization was checked only at card level. That could have allowed an unreferenced repair path on a future multi-path card. The final implementation binds the exact path and separately permits only completed non-direct fallback traversal. Both initial resolution and outcome advancement now use the same guard.

The review also required input-bound candidate callbacks and pre-mutation outcome guards. Those are present, with browser regressions for stale candidates, stale outcomes, an unlinked code repair, an unreferenced direct path, and a legitimate one-step non-direct follow-up.

## Verification evidence

- Fresh independent `node --test test/controlled-selection.test.mjs`: **6 passed, 0 failed**.
- Fresh independent `git diff --check 9612d92`: no whitespace errors.
- Independent diff inspection confirms no changes to `data/canonical.json`, `data/feishu-candidates.json`, `MASTER_PLAN.md`, or `AGENT_REGISTRY.md`.
- Independent visual inspection of the generated 1366px and 390px home/detail screenshots found centered compact panels with no visible horizontal overflow or mixed identification stages.
- Builder reported a red/green reproduction for the final fallback guard: the unreferenced direct fallback exposed one answer grid before the fix and exposed none after it. Builder then reported **17 controlled browser checks passed**. The root owner is responsible for the final complete suite, native 125% zoom, lifecycle, and package gates after this review.

## Static addendum — direct transition after Details Continue

The final `prepareIdentification` / `beginIdentification` wrapper change is acceptable and adds no review finding. After the user explicitly submits the detail panel, it advances directly to Page 2 only when `resolved()` already returns a terminal `repair`, `check`, `information`, or `escalate` result. Scope requirements, ambiguous paths, code/message candidate confirmation, and observable qualifiers remain on the confirmation stage. `viewSolution()` resolves the state again, so the existing catalog identity, exact repair-path authorization, firmware, and stale-input guards remain in force. Setting the identification stage back to `symptom` before pushing the solution history entry makes Back restore the selected detail controls. This addendum is based on static inspection only; no additional build or browser command was run while the owner's final suites were active.

This approval covers the local diff only. It authorizes no merge to a default branch, MAIN write, deployment, or remote write.

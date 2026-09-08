# PIE Troubleshooter — Operational Maturity Decision

Status: SUPERVISOR_ACCEPTED_WITH_SCOPED_PROMOTION
Date: 2026-09-08
Owner: Troubleshooter｜主管
Source: Feishu `PIE Troubleshooter Repair Knowledge Operational Maturity Audit 2026-09-08`

## Core decision

The maturity audit is accepted as operational evidence. However, `STABILITY_SUPPORTED` does not automatically mean the entire current Repair Path wording may be published as a direct replacement rule.

We distinguish:
- stable operational process / diagnostic sequence;
- stable direct part replacement;
- broad/mixed path that still needs splitting;
- stable internal assessment process that should remain PIE-facing.

A long-used, maintained, non-superseded method may qualify as `STABLE_OPERATIONAL_GUIDANCE` without an explicit partner `solved` reply. This decision still preserves model/scope/architecture boundaries and does not convert a broad path into a universal one-part answer.

## A. Promote as STABLE_OPERATIONAL_GUIDANCE — guided agent-facing process

These are approved to move from candidate/PIE_ONLY into agent-facing guided handling, with the safe wording/fallback constraints below:

1. `REP-WHEEL-001`
   - Stable: wheel-movement diagnostic/repair process.
   - Publish: Motor Test / isolate wheel motor vs driver-board path where model/tool supports it; replace the confirmed failing wheel motor or scoped driver-board path.
   - Do NOT publish an automatic `then replace mainboard` fallback. If still not fixed after the validated path, route to PIE.

2. `REP-CUT-001`
   - Stable: non-1202 cutting-disc mechanical-blockage + motor evaluation process.
   - Publish: clear actual blockage/debris first; evaluate motor where supported; replace confirmed failed cutting-motor assembly.
   - Do NOT merge this symptom-only path with frozen Error 1202.
   - Driver-board/cable fallback remains PIE unless separately supported.

3. `REP-CHARGE-001`
   - Stable: no-charge / charging-source isolation process.
   - Publish: confirm adapter/station via model-appropriate known-good/cross-test; replace the confirmed faulty adapter or charging station.
   - Do NOT auto-escalate to driver board/mainboard without further scoped evidence.

4. `REP-DOCK-001`
   - Stable: docking/IR/charging-station first-line process.
   - Publish: clean contacts/IR window, repeat docking verification, evaluate station/IR path according to model.
   - If unresolved after supported station-side checks, route to PIE rather than universal robot-side replacement.

5. `REP-POWER-001`
   - Stable: no-power/unexpected shutdown power-path process.
   - Publish: battery voltage / model-applicable battery checks + power-button/connection checks.
   - Component replacement only when the failing element is established. Mainboard is not an automatic fallback.

6. `REP-RTK-001`
   - Stable: RTK connection first-line process.
   - Publish: station power/indicator/adapter first; replace confirmed faulty station/adapter where scoped.
   - Mower-side GNSS/LoRa becomes PIE-guided if station path is normal.

7. `REP-BUMP-001`
   - Stable: bumper false-trigger process.
   - Publish: confirm no obstruction/stuck mechanism; replace bumper/sensor only when the mechanism is clear and fault remains.
   - Harness/mainboard fallback remains PIE-guided.

8. `REP-CABLE-001`
   - Stable and comparatively direct because the symptom is visible damage.
   - Publish: replace the confirmed visibly damaged cable/harness with the correct model-scoped part, then complete verification.
   - If the cable is visually/electrically normal or replacement does not fix the issue, route to PIE.

9. `REP-FW-001`
   - Stable: firmware/tool remediation process.
   - Publish: reconcile current tool/firmware/component versions and use the current model-applicable update method.
   - Never expose one universal target version.
   - Repeated update failure routes to module/data-path diagnosis / PIE, not automatic mainboard replacement.

## B. Stability accepted, but do NOT publish the current broad Repair Path unchanged

These have operational maturity evidence, but the current path mixes materially different phenomena, architectures or hardware actions. They require splitting before direct agent publication:

1. `REP-POS-001`
   - Stable domain/process, but `positioning failed/inaccurate` + map issues + GNSS/RTK are too broad.
   - Keep as guided area/PIE routing until split into observable symptom-specific paths.

2. `REP-WIFI-001`
   - Stable connectivity support practice, but WiFi and 4G must not share one hardware repair path.
   - Split WiFi and 4G before any direct part recommendation.
   - Until split, agent-facing output may provide non-destructive connectivity/version checks only, then PIE.

3. `REP-LIDAR-001`
   - Stable LiDAR support domain, but architecture and Error Code behavior vary materially by model/code (including 2401/2407/5501/6401/2000303 context).
   - Do not publish universal `replace LiDAR` across current scope.
   - Keep model/code-specific existing promoted knowledge and PIE escalation until split.

## C. Operationally stable process, but remain PIE/internal assessment rather than self-service repair

1. `REP-WATER-001`
   - Water ingress assessment is stable, but this is damage/warranty/root-entry assessment, not a generic agent self-service replacement card.
   - Agent-facing may request visible evidence and verification only when appropriate; final damage/repair scope remains PIE-controlled.

2. `REP-PHY-001`
   - Physical-damage assessment is stable, but `replace damaged component` is too generic to be a useful standalone self-service Repair Path.
   - Keep PIE/internal assessment unless a specific observable damage -> specific serviceable part path is built.

## D. Remain NOT_YET_SUPPORTED / PIE_ONLY

Keep these as candidate/PIE_ONLY for now:
- `REP-WHEEL-003`
- `REP-CUT-002`
- `REP-CHARGE-002`
- `REP-POWER-002`
- `REP-BT-001`

Reason: the audit itself reports insufficient/narrow evidence or multi-cause ambiguity.

## E. 1202

No change.
- `REP-1202-001` remains frozen / conflicting.
- Do not infer model scope.
- Search + physical-blockage guardrail may remain.

## Publication principle for Builder

When implementing these promotions:
- `STABLE_OPERATIONAL_GUIDANCE` may be agent-visible even without explicit solved replies;
- promote the supported stable portion, not every fallback phrase from the original candidate;
- a stable diagnostic/process path can be published as Guided even when a universal direct replacement is not justified;
- `Still not fixed` should normally route to PIE when the next hardware step is not independently supported;
- preserve standard canonical validation requirements and show only the minimum necessary verification on Page 2.

## Sequencing

The active latest Builder task remains `EC-MT-20260908-DESKTOP-TWO-PAGE-005` and should finish first.

After the two-page UX gate is green, issue a separate bounded knowledge-promotion task using this decision. Do not mix new knowledge promotion into an in-progress UI task and risk obscuring regression ownership.

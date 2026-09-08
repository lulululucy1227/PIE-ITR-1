# PIE Troubleshooter — Feishu Candidate Payload

Status: SANITIZED_CANDIDATE_INPUT
Date: 2026-09-08
Owner: Troubleshooter｜主管
Source: user-provided `VERIFIED KNOWLEDGE BUILD PIE Troubleshooter 2026-09-08`

## Purpose

This file exists because the desktop long-run Builder reported that the Feishu candidate Repair Path payload was not present in its accessible repository/handoff, so **0 Feishu candidate records were imported**.

This is a sanitized candidate payload only. It is NOT an automatic publication decision.

Builder must reconcile every candidate against:
- `docs/troubleshooter/EVIDENCE_PROMOTION_POLICY.md`;
- current promoted `docs/knowledge/ERROR_CODES.md`;
- current promoted `docs/knowledge/KNOWN_FIXES.md`;
- existing specialist canonical knowledge;
- scope/conflict/supersession rules.

Important business rule:
- explicit partner `solved` feedback is not mandatory;
- long-standing, actively maintained, repeatedly used and non-conflicting guidance may qualify as `STABLE_OPERATIONAL_GUIDANCE`;
- age/silence alone is insufficient;
- ambiguous/conflicting/weakly scoped paths remain candidate or PIE_ONLY.

## Controlled symptom references

Use the already approved SYM-001..SYM-028 definitions in `docs/troubleshooter/BUILDER_HANDOFF_2026-09-08.md`.

## Candidate Repair Paths

### REP-WHEEL-001
- symptoms: `SYM-001`, `SYM-002`
- candidate priority: P0
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Wheel Hub Motor or Driver Board
- candidate action:
  1. Run Motor Test in MammoSuite.
  2. If the motor fails, replace the wheel hub motor.
  3. If the motor is OK, replace the driver board.
- canonical verification candidate: Functional Test + Communication Check + Auto Map Run; retain reports + Connect Checking screenshot.
- fallback candidate: mainboard.
- Feishu evidence label: `ACTION_PERFORMED_OUTCOME_UNKNOWN`
- publication: REVIEW_REQUIRED

### REP-WHEEL-003
- symptom: `SYM-003`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Wheel Assembly
- candidate action: inspect wheel hub for physical damage; replace damaged wheel hub assembly.
- verification candidate: visual inspection + spin test + Functional Test.
- fallback candidate: wheel hub motor.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

### REP-CUT-001
- symptoms: `SYM-004`, `SYM-006`
- candidate priority: P0/P1 by symptom
- candidate scope: LUBA 1 / LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Cutting Motor Assembly
- candidate action:
  1. Clear debris / confirm no mechanical blockage.
  2. Run Motor Test where applicable.
  3. If motor fails, replace cutting motor assembly.
- verification candidate: Motor Test + Auto Map Run; confirm cutting disc operates normally.
- fallback candidate: driver board / cable harness.
- Feishu evidence label: `ACTION_PERFORMED_OUTCOME_UNKNOWN`
- publication: REVIEW_REQUIRED
- guardrail: do not overwrite the separate frozen Error 1202 promoted path.

### REP-CUT-002
- symptom: `SYM-005`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Lifting Motor or Sensor
- candidate action: check lifting mechanism for blockage; run Motor Test; replace lifting motor if failed.
- verification candidate: cutting height adjusts correctly + relevant Motor Test/Auto Map Run.
- fallback candidate: lifting sensor, then mainboard.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

### REP-CHARGE-001
- symptoms: `SYM-007`, `SYM-009`
- candidate priority: P0/P1 by symptom
- candidate scope: LUBA 1 / LUBA 2 / LUBA 2X / LUBA 3 for `SYM-007`; LUBA 2 / 2X / 3 for `SYM-009`
- target part/domain: Power Adapter or Charging Station
- candidate action: cross-test with known-good adapter/station; replace the confirmed faulty adapter or station.
- verification candidate: charging indicator/current + relevant standard validation.
- fallback candidate: driver board, then mainboard.
- Feishu evidence label: `ACTION_PERFORMED_OUTCOME_UNKNOWN`
- publication: REVIEW_REQUIRED

### REP-CHARGE-002
- symptom: `SYM-008`
- candidate priority: P1
- candidate scope: LUBA 1 / LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Battery or Charging Circuit
- candidate action: check battery health/SOH where tool/model supports it; replace battery when applicable threshold/rule is met; otherwise inspect charging connections.
- verification candidate: full charge cycle / capacity / model-applicable battery validation.
- fallback candidate: driver board, then mainboard.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED
- scope guardrail: MammoSuite SOH support is model-dependent; do not show unsupported tool steps universally.

### REP-DOCK-001
- symptom: `SYM-010`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: IR / Charging Station path
- candidate action: clean charging contacts and IR window; repeat docking test; if still failing, evaluate/replace charging station as supported.
- verification candidate: repeated docking success.
- fallback candidate: robot-side IR path.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

### REP-POWER-001
- symptoms: `SYM-011`, `SYM-013`
- candidate priority: P0/P1 by symptom
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Battery / Power Button / power path
- candidate action: check battery voltage; apply model-appropriate battery rule; check power-button connection.
- verification candidate: powers on and remains stable + relevant standard validation.
- fallback candidate: mainboard only after upstream power path is ruled out.
- Feishu evidence label: `ACTION_PERFORMED_OUTCOME_UNKNOWN`
- publication: REVIEW_REQUIRED

### REP-POWER-002
- symptom: `SYM-012`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Battery
- candidate action: check battery SOH/cycle/runtime where supported; replace only when applicable service rule is met.
- verification candidate: runtime/Functional Test according to model capability.
- fallback candidate: investigate abnormal drain/power path before mainboard replacement.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

### REP-POS-001
- symptoms: `SYM-014`, `SYM-016`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Positioning / GNSS / RTK path
- candidate action: isolate RTK/base-station state from mower positioning state before replacing mower hardware; use known-good comparison only where supported.
- verification candidate: positioning/map behavior + Auto Map Run where applicable.
- fallback candidate: PIE escalation / model-capability-specific LiDAR or mainboard investigation.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED
- guardrail: do not collapse map-loss and GNSS hardware into one universal replacement rule.

### REP-RTK-001
- symptom: `SYM-015`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: RTK Station / adapter / mower-side GNSS-LoRa path
- candidate action: check RTK station power/indicator and adapter before station replacement.
- verification candidate: stable RTK connection/status using model-applicable method.
- fallback candidate: mower-side GNSS/LoRa path / PIE.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

### REP-WIFI-001
- symptoms: `SYM-017`, `SYM-018`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Connectivity / antenna / firmware / mainboard depending symptom/model
- candidate action: check physical antenna/connection only when applicable; reconcile version mismatch before hardware replacement.
- verification candidate: stable target network connection.
- fallback candidate: firmware/version reconciliation or PIE.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED
- guardrail: WiFi and 4G must not be treated as the same hardware path by default.

### REP-BT-001
- symptom: `SYM-019`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Bluetooth / model-specific module path
- candidate action: verify connection failure and model architecture before mainboard/module replacement.
- verification candidate: stable Bluetooth connection.
- fallback candidate: version/model compatibility or PIE.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

### REP-BUMP-001
- symptom: `SYM-020`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: Bumper Sensor / mechanical bumper path
- candidate action: first confirm no physical obstruction/stuck mechanism; replace bumper sensor only when supported after mechanism is clear.
- verification candidate: bumper response with no false trigger + relevant validation.
- fallback candidate: harness/mainboard path / PIE.
- Feishu evidence label: `ACTION_PERFORMED_OUTCOME_UNKNOWN`
- publication: REVIEW_REQUIRED

### REP-LIDAR-001
- symptom: `SYM-021`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3 in Feishu candidate; actual product architecture must be reconciled before publication.
- target part/domain: LiDAR / data path
- candidate action: module replacement is candidate only; first reconcile existing promoted 5501/6401/2000303/2401/2407 knowledge and product capability.
- verification candidate: LiDAR data + Auto Map Run where applicable.
- fallback candidate: cable/data path / PIE.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

### REP-WATER-001
- symptom: `SYM-022`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: affected water-damaged components
- candidate action: evidence collection / inspect entry point and corrosion; component replacement depends actual damage.
- verification candidate: full standard final validation after repair where applicable.
- fallback candidate: PIE water-damage assessment.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: PIE_ONLY_BY_DEFAULT
- guardrail: water ingress remains a damage/assessment case; do not present a generic `replace mainboard` path.

### REP-CABLE-001
- symptom: `SYM-023`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: visibly damaged cable/harness
- candidate action: replace the confirmed visibly damaged cable/harness with correct scoped part.
- verification candidate: Functional Test + Communication Check + path-specific verification; standard final validation where appropriate.
- fallback candidate: affected component/path investigation.
- Feishu evidence label: `ACTION_PERFORMED_OUTCOME_UNKNOWN`
- publication: REVIEW_REQUIRED

### REP-PHY-001
- symptom: `SYM-024`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3
- target part/domain: visibly damaged component
- candidate action: identify actual damaged serviceable component; repair/replace according to part scope.
- verification candidate: path-specific + standard final validation where applicable.
- fallback candidate: PIE assessment.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: PIE_ONLY_BY_DEFAULT

### REP-FW-001
- symptom: `SYM-025`
- candidate priority: P1
- candidate scope: LUBA 2 / LUBA 2X / LUBA 3 in Feishu candidate; actual version/tool/model rules must remain scoped.
- target part/domain: Software/Firmware
- candidate action: reconcile current firmware/tool version and component version consistency; do not expose a universal target version.
- verification candidate: version state + Functional Test / applicable path validation.
- fallback candidate: diagnose the module/data path; do not default to mainboard merely because update fails.
- Feishu evidence label: `SOURCE_RECOMMENDATION`
- publication: REVIEW_REQUIRED

## Frozen conflicting Error path

### REP-1202-001
- Error Code: `1202`
- symptom: `SYM-004`
- status: `CONFLICTING_EVIDENCE / PIE_REVIEW_REQUIRED`
- agent-facing hardware repair publication: FROZEN
- allowed: search, physical-blockage guardrail, safe escalation.
- prohibited: use Feishu cutting-motor/driver-board path to overwrite promoted cable/mainboard knowledge; or publish promoted cable/mainboard path universally before scope is confirmed.

## Reconciliation-only sync-derived Error candidates

These are not automatic Repair Card approvals:
- `2401` / `2407`: LUBA 3 LiDAR/radar internal faults; reconcile transient/nonpersistent 2407 behavior and current firmware rules before direct replacement guidance.
- `2000303` unsigned: information-sync source describes LUBA 3 timestamp abnormal as false alarm; existing canonical knowledge distinguishes signed `-2000303` and context-sensitive handling. Do not collapse signed/unsigned forms.
- `1000022`: historical scoped firmware resolution exists; preserve historical verified status and current-version guardrail.
- `1420`: commonly false-alarm-like but may indicate vision-module communication abnormality; keep symptom/scope split and verification loop, not a universal part replacement.
- `1500`: chassis data serial-port disconnect; keep model-capability communication-path diagnosis, not universal one-part mapping.

## Acceptance for Builder ingestion

Builder must:
1. import these candidate records into the private/candidate layer;
2. preserve exact IDs and symptom references where compatible;
3. perform per-record evidence promotion review under `EVIDENCE_PROMOTION_POLICY.md`;
4. promote only `VERIFIED_RESOLUTION` or justified `STABLE_OPERATIONAL_GUIDANCE` with adequate scope/verification/fallback;
5. keep weaker candidates as private/PIE_ONLY rather than dropping them;
6. run referential integrity + public projection + browser + privacy/package regression;
7. report imported/promoted/withheld counts explicitly;
8. never claim Feishu production read/write occurred during Builder execution.

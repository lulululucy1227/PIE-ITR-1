# PIE-ITR Error Code Knowledge

Only promote evidence-backed knowledge. Error codes are not one-code-one-solution mappings.

## 1000022
- Product evidence: LUBA mini 2 1000 Vision.
- Message: `Insufficient light at night. This feature is unavailable`.
- Real case: Auto Map Run blocked on 2.3.27.23; upgrade to 2.3.30.26 + reboot resolved.
- Use as historical verified fix, not a permanent target version.

## 1500
- Message: `Chassis data serial port disconnected`.
- Check relevant vision/LiDAR communication path based on model capability.
- Also check applicable firmware/version state.
- Do not use one fixed response for every model.

## 5501
- LiDAR/IMU-related fault domain.
- Real cases show LiDAR body or data/connection path can cause upgrade failure, including stalls around 60% or 70%.
- On upgrade failure, check current/history error codes and module communication before assuming network/software.

## 6401
- Observed message: `Both the chassis log port and data port are disconnected`.
- Real case: wired upgrade failed; replacing vision module again enabled upgrade.
- Key rule: a newly replaced part can still be defective.

## DT-041
- Internal module communication abnormality / timeout.
- Identify actual offline module/link first, then trace communication/data/power chain.
- Do not default to mainboard replacement.

## 1202 — cutting disc blocked
- Message: `Cutting disc blocked` / German UI `Schneidscheibe blockiert`.
- First confirm there is no actual mechanical obstruction, tangled material, or debris under the cutting discs.
- MammoSuite cannot test the left and right cutting-disc motors separately. Do not instruct an agent to isolate left/right cutting motors independently in MammoSuite.
- If both cutting discs are clean/free and error `1202` remains, current PIE-confirmed service path is to replace the **Upper Shell Adapter Cable**, the connection cable between the upper shell and the mainboard.
- If error `1202` still remains after replacing the Upper Shell Adapter Cable, replace the **mainboard**.
- A recently replaced driverboard is repair history and does not by itself change this diagnostic path.
- Guardrail: if a real physical blockage is present, clear the mechanical obstruction before using the cable/mainboard path.

## 458 — right cutting-disc motor overcurrent
- Meaning confirmed by PIE: right cutting-disc motor overcurrent.
- If it appears together with several wheel-drive hardware-overcurrent codes and battery MOS overtemperature, do not diagnose the cutting motor in isolation first.

## 586 — right-front wheel-hub drive hardware overcurrent
- Meaning confirmed by PIE: right-front wheel-hub drive hardware overcurrent.

## 362 — left wheel-hub drive overcurrent
- Meaning confirmed by PIE: left wheel-hub drive overcurrent.

## 2714 — battery MOS temperature high
- Meaning confirmed by PIE: battery MOS temperature high.
- When it occurs in the same event as multiple independent motor/drive overcurrent codes, treat it as evidence of a shared high-current / drive-stage event rather than an isolated battery-health reading.

## 554 — left-front wheel-hub drive hardware overcurrent
- Meaning confirmed by PIE: left-front wheel-hub drive hardware overcurrent.

## 394 — right wheel-hub drive overcurrent
- Meaning confirmed by PIE: right wheel-hub drive overcurrent.

## Multi-channel overcurrent + Battery MOS high-temperature pattern
When several motor/drive channels report overcurrent at the same time — for example cutting-disc overcurrent plus multiple wheel-hub drive overcurrent/hardware-overcurrent codes — and battery MOS high-temperature is present in the same event:
- do not interpret it as several independent motors failing simultaneously;
- the driverboard / shared drive-power stage becomes a high-priority fault domain;
- if the driverboard has already failed/replaced repeatedly, do not stop at replacing it again: investigate why it is being damaged or overloaded;
- high-value upstream checks include confirmed-good battery cross-test, evidence of water ingress/corrosion, main power harness/connectors, and individual motor short/overload isolation;
- a visually intact wiring harness does not exclude an electrical fault under load;
- if previous water ingress is confirmed, repeated driverboard failure may be secondary to broader moisture/corrosion damage and the repair strategy should be reassessed rather than continuing blind board replacement.

## -552 / -392 / -584 — wheel-motor undervoltage
- `-552`: left front wheel hub motor voltage too low.
- `-392`: right wheel hub motor voltage too low.
- `-584`: right front wheel hub motor voltage too low.
- If multiple wheel-motor undervoltage codes occur at the same timestamp, do not assume multiple independent motor failures.
- When they coincide with battery protection or other shared-power symptoms, prioritize the common power path: battery, charging station/adapter, main power cables/connectors, driverboard and related communication/control path.

## -2720 — Battery short circuit protection triggered
- Message observed: `Battery short circuit protection triggered`.
- In a real case, `-2720` occurred at the same timestamp as several wheel-motor undervoltage codes.
- That combination is strong evidence for a shared power-supply event and should outrank a hypothesis of several motors failing independently.
- Check battery health, charging-station/adapter no-load and loaded voltage, battery-driverboard-mainboard power path, and driverboard-mainboard CAN connection before replacing the driverboard again.
- Use a test driverboard to isolate all four wheel motors and both cutting motors individually if motor overcurrent/short or mechanical overload is still suspected.

## -2000303 — LiDAR internal timestamp abnormal
- Message observed: `The internal timestamp of the lidar is abnormal`.
- If this appears simultaneously with a clear shared-power event, treat it as potentially secondary until separate LiDAR evidence shows otherwise.
- Do not promote it to root cause solely because it is present in the same error batch.

## Maintenance rule
Each future entry should include model scope, symptom, decisive evidence, likely fault domains, first actions, version dependency, known fix, source, confidence, validation date, and current/superseded/deprecated status.

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

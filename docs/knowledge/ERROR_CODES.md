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

## Maintenance rule
Each future entry should include model scope, symptom, decisive evidence, likely fault domains, first actions, version dependency, known fix, source, confidence, validation date, and current/superseded/deprecated status.

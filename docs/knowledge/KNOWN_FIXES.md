# PIE-ITR Known Fixes

Historical fixes are evidence, not timeless instructions. Every entry should remain scoped by model/version/symptom and be revisited when software or repair policy changes.

## 1000022 — LUBA mini 2 1000 Vision
- Symptom: `Insufficient light at night. This feature is unavailable`; Auto Map Run blocked.
- Observed version: 2.3.27.23.
- Verified historical resolution: upgrade to 2.3.30.26, restart, error disappeared.
- Status: historical verified fix.
- Rule: compare against current applicable firmware before reusing this recommendation.

## 5501 / LiDAR-related upgrade failure
- Real cases: LiDAR body/data-path faults can prevent firmware upgrade and may stall around 60–70%.
- Verified handling pattern: inspect error history/module communication and LiDAR body/data connection before treating upgrade failure as network-only.
- Status: reusable diagnostic pattern, not a guaranteed one-step fix.

## 6401 / chassis log+data port disconnected
- Real case: wired upgrade failed; replacing vision module again allowed the upgrade to complete.
- Status: evidence supporting the rule that replacement history does not prove component health.

## LUBA 2 5000X — Function Test cutting-motor anomaly / version dependency
- Symptom: cutting/blade motor does not start in **Functional Test**, while the same cutting function works normally in **Auto Run** and/or manual mowing.
- This pattern should not be treated as proof of cutting-motor hardware failure when real mowing operation is normal.
- Historical observation: version `1.30.31.10` previously allowed the Function Test cutting item to pass in one instance, but the same symptom later reappeared on `1.30.31.10`. Therefore `1.30.31.10` is not a stable universal fix for this symptom.
- Current PIE-confirmed handling: when this symptom occurs on `1.30.31.10`, select software version `1.30.29.19` and update the mower, then repeat the Function Test. Similar cases have passed the test after switching to `1.30.29.19`.
- Status: reusable version-dependent known fix, with prior `1.30.31.10` interpretation corrected/superseded for this scenario.
- Guardrail: keep the scope narrow to this Function Test mismatch. If the cutting motor also fails in Auto Run/manual mowing, or other motor/driver faults are present, do not treat it as the same software-only case.

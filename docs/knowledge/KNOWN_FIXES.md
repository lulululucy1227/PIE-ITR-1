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

# Knowledge promotion audit — 2026-09-08

Task: EC-MT-20260908-DESKTOP-LONGRUN-003. Local Builder self-approval under EVIDENCE_PROMOTION_POLICY.md; independent read-only evidence review completed. This is a publication decision, not a repair-success measurement.

## Source and decision basis

Reviewed current canonical remote 36a1fea, ERROR_CODES, KNOWN_FIXES, TOOL_KNOWLEDGE, the corrected supervisor handoff/review, prior sanitized local provenance and relevant Git history. No live production access or original workbook reparse. The source table hash remains 5bcaeef54e10b8a24ec73ce30ad1046b593e0268057957644eaa5ca8a7dc67f5.

The supervisor reports 38/737 records containing a code and 19 Feishu candidate repair paths. These are attributed audit figures, not independently recounted here. Individual records for the 19-path payload were not present in the handoff/repository searched: actual imported Feishu repair records = 0. No fabricated placeholder actions or implied 19-record audit. Their later import can proceed as candidates.

## Promotion judgment

The LUBA 2 5000X Function Test-only mismatch is the single promoted repair action: STABLE_OPERATIONAL_GUIDANCE, exact source firmware 1.30.31.10, select 1.30.29.19 and update, real mowing normal and no other motor/driver fault. Sources explicitly describe similar cases passing. Git 6370b88 introduced the older interpretation; 4d748c3/5b7c49c recorded recurrence; dcc45fb/2bd5772 corrected the recovery target; 7f4b29f/3b13d9c clarified the update wording. Later tool maintenance retained it. Earliest observed repository use: 2026-08-31; last substantive correction: 2026-09-01; current review: 2026-09-08. The classification uses explicit reuse and active correction/maintenance, not a seven-day age threshold or silence. Complete closure/verification cohorts were not audited.

All approved nonrepair checks/information/escalation are reviewed safety or diagnostic guards, not lower-evidence hardware promotions. Historical verified entries preserve their narrow observed outcomes; neither is an unconditional present-day repair. Every canonical path has verification/fallback; software repair retains all three standard tests, reports, Connect Checking screenshot and the Burn-in boundary.

## Per-path decisions

| Card / repair_path_id | Evidence state | Scope | Visibility / publication | Conflict, currentness and rationale | Verification / fallback |
| --- | --- | --- | --- | --- | --- |
| ec-1202 / blocked | SOURCE_RECOMMENDATION | unknown | P1_DESKTOP_GUIDED / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-1202 / cable | CONFLICTING_EVIDENCE | unknown | PIE_ONLY / withheld | FROZEN; conflicting cable/mainboard vs Feishu motor/driverboard paths; scope unresolved | Present / path |
| ec-1202 / mainboard | CONFLICTING_EVIDENCE | unknown | PIE_ONLY / withheld | FROZEN; conflicting cable/mainboard vs Feishu motor/driverboard paths; scope unresolved | Present / escalate |
| ec-1008 / stop | SOURCE_RECOMMENDATION | unknown | P1_DESKTOP_GUIDED / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-1008 / not-reproduced | SOURCE_RECOMMENDATION | unknown | P1_DESKTOP_GUIDED / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-1008 / recurring | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-5510 / normal | SOURCE_RECOMMENDATION | not_required | P1_DESKTOP_GUIDED / approved | Explicit calibration success only; normal operation/no other active fault required | Present / escalate |
| ec-5510 / abnormal | SOURCE_RECOMMENDATION | not_required | PIE_ONLY / approved | Explicit calibration success only; normal operation/no other active fault required | Present / escalate |
| ec-1000022 / pie | VERIFIED_RESOLUTION | LUBA mini 2 1000 Vision | PIE_ONLY / approved | Historical resolution only; old target remains internal; current PIE review | Present / escalate |
| ec-1500 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-5501 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-6401 / pie | VERIFIED_RESOLUTION | unknown | PIE_ONLY / approved | Historical wired-upgrade observation; replacement history is not known-good; no universal replacement | Present / escalate |
| ec-dt041 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-458 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-586 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-362 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-2714 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-554 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-394 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec--552 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec--392 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec--584 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec--2720 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Retained promoted safe guardrail; no unscoped part recommendation | Present / escalate |
| ec-minus2000303 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Signed promoted shared-power secondary guardrail; no root-cause/no-repair inference | Present / escalate |
| sym-cutting-functional-test / software | STABLE_OPERATIONAL_GUIDANCE | LUBA 2 5000X / 1.30.31.10 | P1_DESKTOP_GUIDED / approved | Current maintained narrow test-only/version fix; affirmative qualifier required | Present / escalate |
| ec-2000303 / pie | SOURCE_RECOMMENDATION | unknown | PIE_ONLY / approved | Unsigned row 202 says upload logs; no false-alarm/no-repair evidence | Present / escalate |

## Counts (canonical records, not field success)

```json
{
  "cards": 21,
  "paths": 26,
  "evidenceStates": {
    "SOURCE_RECOMMENDATION": 21,
    "CONFLICTING_EVIDENCE": 2,
    "VERIFIED_RESOLUTION": 2,
    "STABLE_OPERATIONAL_GUIDANCE": 1
  },
  "visibility": {
    "P1_DESKTOP_GUIDED": 5,
    "PIE_ONLY": 21
  },
  "publication": {
    "approved": 24,
    "withheld": 2
  }
}
```

## Withheld and safe exclusions

- ec-1202:cable and ec-1202:mainboard: conflicting evidence and unknown applicability; internal sequence retained, never published by model/scope edits alone.
- 1000022 historical firmware target: preserved internally, no current prescription.
- 6401 historical module-replacement observation and 5501/1500/DT-041 diagnostic domains: no generalized replacement publication.
- Positive 2000303 false-alarm/no-repair claim: unsupported by available exact source; safe log/PIE route instead. Negative -2000303 remains a distinct identity.
- SYM-026/027/028: broad symptoms remain PIE-only, absent from normal navigation.
- SYM-001–025 without an approved matching action: concise PIE route. Only SYM-004 has a narrow approved repair; SYM-021 reuses the canonical LiDAR diagnostic escalation.
- The missing 19 Feishu candidate records are not constructed, promoted or counted as ingested.

These exclusions do not block desktop local green under the latest task. No business answer is required to keep them safely withheld. Wider release, new source import or unfreezing 1202 belongs to separately authorized work.

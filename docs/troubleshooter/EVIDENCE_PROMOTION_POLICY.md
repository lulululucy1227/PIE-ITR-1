# PIE Troubleshooter — Repair Knowledge Evidence & Promotion Policy

Status: Active
Owner: Troubleshooter｜主管
Date: 2026-09-08

## Purpose

PIE Troubleshooter must not require an explicit partner reply such as `solved` before a repair method can be treated as usable knowledge.

In real PIE service operations, a repair instruction may remain in active use for a long period, be repeatedly referenced by PIE/KB/service guidance, and receive no contradictory/reopen evidence. That stability is itself meaningful operational evidence.

At the same time, a newly written recommendation or one-off suggestion must not automatically become a confident repair card merely because no one has contradicted it yet.

## Core rule

`Explicit verified resolution` is the strongest evidence, but it is NOT the only path to publishable repair guidance.

A repair path may also become publishable when it qualifies as **STABLE_OPERATIONAL_GUIDANCE**.

## Evidence states

### 1. VERIFIED_RESOLUTION
Use when there is explicit evidence that:
- the repair/action was performed;
- the target problem was resolved or expected function restored;
- appropriate post-repair verification passed where applicable.

This is the strongest state.

### 2. STABLE_OPERATIONAL_GUIDANCE
Use when explicit `solved` feedback is absent or incomplete, but the repair guidance has meaningful operational stability.

Typical supporting signals:
- the guidance has remained materially unchanged in an actively maintained authoritative source for a meaningful period;
- the same part/action has been repeatedly used or retained across PIE/KB/service practice;
- no meaningful contradictory repair pattern, repeated reopen/rework signal, superseding rule, or scope conflict has emerged;
- the applicable model/product/version scope is known well enough;
- PIE has not withdrawn or corrected the guidance despite continued operational exposure.

An explicit partner confirmation is NOT required for this state.

`Long-standing and unchanged` must be interpreted in the context of an actively used service workflow, not as proof from age alone.

### 3. ACTION_PERFORMED_OUTCOME_UNKNOWN
Use when the action was performed in one or more cases but the result is not sufficiently known, and the guidance has not yet accumulated enough operational stability to qualify as STABLE_OPERATIONAL_GUIDANCE.

### 4. SOURCE_RECOMMENDATION
Use for a recommendation that exists in a source but is relatively new, weakly scoped, sparsely used, or not yet supported by enough stable operational history.

### 5. CONFLICTING_EVIDENCE
Use when credible sources/cases materially disagree, or a known replacement-failed/reopen pattern undermines the current path.

Do not publish the conflicting path as a confident self-service recommendation until reconciled.

## Promotion rule for Agent-facing Repair Cards

A repair path may be considered for `P0_DESKTOP_SELF_SERVICE` or `P1_DESKTOP_GUIDED` when:
- symptom/entry scope is sufficiently clear;
- product/model/version scope is sufficiently clear;
- repair action is executable by the target agent;
- verification/fallback exists;
- evidence state is either:
  - `VERIFIED_RESOLUTION`, or
  - `STABLE_OPERATIONAL_GUIDANCE`.

`SOURCE_RECOMMENDATION` and `ACTION_PERFORMED_OUTCOME_UNKNOWN` do not automatically block all use, but they normally require either guided wording, stronger review, or PIE-only handling until operational stability is established.

## Important distinction

Do not confuse:

`no explicit solved reply`

with:

`no evidence that the repair method works`.

Likewise, do not confuse:

`no complaint yet`

with:

`proven stable guidance`.

Operational validation comes from maintained, repeated, non-conflicting use — not from silence alone.

## Currentness / supersession

A previously stable repair path can be downgraded if:
- firmware/hardware architecture changes;
- a new service policy supersedes it;
- repeated replacement-failed cases appear;
- model scope proves narrower than assumed;
- new real-case evidence contradicts the old path.

## Evidence review fields recommended for future Feishu/Builder handoff

For each Repair Path, retain where available:
- `evidence_state`;
- `first_seen / earliest_known_use`;
- `last_reviewed / last_material_change`;
- `repeated_use_signal`;
- `known_conflicts_or_reopens`;
- `scope`;
- `source_authority`;
- `superseded_by` if applicable.

A fixed age threshold is intentionally not defined; the significance of time depends on use frequency, source authority and product change rate.

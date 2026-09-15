# Troubleshooter Hardware Top 10 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a current, evidence-backed hardware-first Top 10 repair set for PIE Troubleshooter, with each issue expressed as `observable symptom -> repair/solution -> verification`, while also enriching the repair instructions with exact part/SKU/tool/disassembly/expected-result details wherever current sources support them.

**Architecture:** Keep the existing standalone Troubleshooter and its simple `Model -> Controlled Symptom -> Repair` flow. Use the current Work Order Reply Assistant knowledge vault and safely available recent case-derived evidence as READ ONLY sources. Rank problems internally for content priority; do not add a Top 10 dashboard or extra mandatory user input. Existing mature cards are reusable seeds, not the scope limit.

**Tech Stack:** Existing `error-code-pilot` static/read-only knowledge projection, current service-guidance resource contract, Node/browser regression harness, Windows standalone packaging.

**Spec / policy basis:** `docs/troubleshooter/SIMPLE_KNOWLEDGE_REUSE_DESIGN_2026-09-15.md`, `docs/troubleshooter/EVIDENCE_PROMOTION_POLICY.md`, latest accepted Issue #6 report.

## Global Constraints

- Hardware-first: the Top 10 should prioritize mechanical/electrical/component/serviceable-hardware faults. Pure software/app/firmware problems are not eligible merely because they are common.
- Firmware/software may appear only as a guardrail, exclusion check, prerequisite, or version condition for a primarily hardware repair path.
- If fewer than 10 hardware issues have adequate current evidence, do not fill the remaining slots with weak software items; document the evidence gap and continue with the strongest hardware set available.
- Existing 10 mature cards are not automatically the Top 10 and are not the content ceiling.
- New Repair Paths may be added when current evidence supports clear scope, repair action, verification and safe agent execution.
- Keep normal front-end input simple: `Model -> Controlled Symptom -> Repair`; no new mandatory input, no category wall, no Top10 dashboard, no parts wall.
- Error Code / Message remains optional; it may narrow or support a path but does not replace symptom confirmation.
- 1202 remains frozen unless a separate supervisor decision explicitly changes its publication status.
- No invented frequency, success rate, SKU, quantity, torque, voltage threshold, tool setting, or repair certainty.
- Reply Assistant workspace/vault and any current case source are READ ONLY.
- No Feishu/Nextop/ITR production writes, no public deployment, no MAIN runtime mutation, no default/main merge.

---

### Task 1: Recover latest specialist state and supersede the old narrow scope

**Files:**
- Read Issue #5 newest task/amendment and Issue #6 latest accepted report
- Read current `error-code-pilot` local specialist state
- Create `error-code-pilot/data/hardware-top10-audit.json` or equivalent private audit artifact

**Interfaces:**
- Consumes: newest valid local descendant of task 008/009 work
- Produces: explicit current baseline and a hardware candidate inventory

- [ ] Preserve any safe work already completed under task 009; do not discard valid enrichment.
- [ ] Treat the previous `existing 10 cards only / no new Repair Paths` limitation as superseded.
- [ ] Enumerate current public Controlled Symptoms, mature cards, PIE_ONLY paths, existing parts/tool/service resources and all current hardware-related private candidates.
- [ ] Confirm normal user flow and public safety boundaries before content expansion.

### Task 2: Locate current source-of-truth material in the Work Order Reply Assistant

**Files / sources READ ONLY:**
- Re-detect current Work Order Reply Assistant workspace
- Re-detect current active `维修与售后知识库`
- Current standard knowledge, case-derived knowledge, error code, parts/SBOM, tool SOP, repair strategy, technical notice/PCN, guided repair, version applicability and serviceability material

**Interfaces:**
- Produces: provenance-manifested candidate facts and hardware issue evidence

- [ ] Do not assume September 15 paths are still current; resolve the live workspace/vault first.
- [ ] Search the entire relevant current knowledge vault, not only the five archived `docs/knowledge` files.
- [ ] Prefer current active knowledge over copied/archive material when authority/currentness is clear.
- [ ] If safely available local recent case/ITR-derived data exists in the Reply Assistant workspace, use it read-only to support current frequency/recurrence ranking without copying PII/raw chats.
- [ ] Use the newest 90-day window when available. If the source does not cover 90 days, use the newest continuous period available and state the exact window in the final report.
- [ ] Record source path, section/table, source role, hash and currentness for every fact used.
- [ ] Do not treat file modification time alone as evidence of technical currentness.

### Task 3: Build a hardware-first candidate pool and determine the current Top 10

**Output:**
- Private `hardware-top10-audit` with ranking evidence and selection rationale
- Public-facing content only after promotion review

- [ ] Normalize real support problems into observable hardware-oriented issue candidates; do not rank by raw Error Code count alone.
- [ ] Candidate domains may include, where supported by actual evidence: charging/power path, drive/wheel, cutting system, docking hardware, bumper/sensor, GNSS/positioning hardware, LiDAR hardware, cable/harness, water ingress/structural damage, physical/mechanical assemblies, battery/board/shared-power faults.
- [ ] Exclude pure app/UI/backend/firmware-update-only problems from Top 10.
- [ ] For each candidate collect, when available: recent occurrence/reuse signal, affected model families, observable symptom, confirmed/stable repair action, verification, agent executability, known conflicts/reopens and serviceability.
- [ ] Rank primarily by current support value: recurrence/frequency when supported, agent repair relevance, clarity of observable symptom, stable hardware solution, verification quality and cross-model usefulness.
- [ ] If exact counts are not available, do not fabricate numeric ranking evidence. Use a documented priority rationale and label count/frequency as unavailable.
- [ ] Produce exactly one current Top 10 list if the evidence supports 10 hardware issues. If fewer than 10 meet the minimum evidence bar, produce the strongest set and an explicit `TOP10_GAP` instead of inserting weak software issues.

### Task 4: For each Top 10 issue, freeze the minimum repair contract

Each selected issue must contain at least:

1. **Problem / observable symptom** — what the repair technician can actually see or confirm before diagnosis.
2. **Solution / repair method** — the shortest evidence-backed repair or isolation route that actually moves the repair forward.
3. **Verification** — how to confirm the repair is complete.
4. **Still not fixed** — next approved action or PIE escalation, without speculative replacement chains.

Optional fields to enrich when supported:
- exact part name;
- SKU / part number;
- quantity;
- tool;
- tool usage/setting;
- concise disassembly/installation procedure;
- expected observable result;
- model/version qualifier;
- brief safety/compatibility stop condition.

- [ ] A Top 10 issue cannot be a vague component category such as `mainboard issue`; it must start from an observable problem.
- [ ] A Top 10 issue can share a symptom across models only when the repair route is genuinely compatible; otherwise split by materially different model scope.
- [ ] Prefer one decisive check or one direct repair over a long engineering checklist.
- [ ] Do not expose internal root-cause trees or evidence discussion by default.

### Task 5: Promote evidence-backed new hardware Repair Paths where justified

- [ ] Existing mature cards that overlap Top 10 should be enriched, not duplicated.
- [ ] If a Top 10 hardware issue is not currently represented by a mature card, create a new Repair Path only when symptom scope, model scope, action, verification and fallback satisfy `VERIFIED_RESOLUTION` or `STABLE_OPERATIONAL_GUIDANCE` publication rules.
- [ ] A frequent hardware issue with insufficiently stable self-service repair may still be documented privately as `TOP10_PIE_GUIDED`, but must not be published as a confident replacement card.
- [ ] Do not lower the publication bar merely to reach ten public cards.
- [ ] Preserve counterexamples and replacement-failed cases.

### Task 6: Deep-enrich the Top 10 repair content from current knowledge

For every Top 10 issue, search current sources for:
- exact service part and SKU;
- quantity;
- model compatibility / DO NOT MIX rules;
- tools and exact supported functions;
- tool usage;
- disassembly/installation sequence;
- cable routing / connector / assembly notes;
- expected observation/result;
- post-repair validation;
- relevant PCN / technical change / supersession.

Publication rules:
- SKU requires `exact model + exact repair target + exact compatible SKU`.
- Quantity must be explicit.
- Tool/function must be supported for the target model/path.
- Disassembly/installation must be sufficiently scoped and safe; vague fragments remain withheld.
- Expected result must be observable and source-supported.
- Do not infer torque/voltage/current/time thresholds.

### Task 7: Keep the UI simple while making the result page more useful

**Page 1 remains:**
`Model -> Controlled Symptom -> Repair`

- [ ] No Top10 selection step.
- [ ] No mandatory Area click.
- [ ] Error Code remains optional.
- [ ] Firmware/qualifier appears only when path-critical.

**Page 2 default visible order:**
1. Problem summary
2. **What should I do now?**
3. Part / SKU / Tool only when exact and required
4. Expected result when useful
5. Verification
6. Still not fixed

- [ ] Put novice-only learning detail under a compact `How to do it / Details` expansion.
- [ ] Do not show multiple speculative replacement parts.
- [ ] Hide empty modules.
- [ ] Do not add a Top10 dashboard or extra navigation module; Top10 is a content-priority artifact, not an interaction burden.

### Task 8: Produce the Top 10 management deliverable

Create a durable supervisor artifact, e.g. `docs/troubleshooter/HARDWARE_TOP10_2026-09-16.md`, with one concise table containing:

- Rank / priority
- Problem / observable symptom
- Main model scope
- Hardware domain / confirmed target where appropriate
- Solution / repair method
- Verification
- Published status (`SELF_SERVICE`, `GUIDED`, `PIE_ONLY`)
- Part/SKU if confirmed
- Main evidence source/currentness
- Remaining gap

Rules:
- The table is for PIE/supervisor knowledge management; do not expose internal evidence columns to agents.
- State the evidence time window and whether rank is count-based or priority-based.
- Do not report made-up percentages/success rates.

### Task 9: Full safety, regression and package closure

- [ ] Add tests for every new/changed Top10 mapping and each newly published SKU/tool/disassembly resource.
- [ ] Verify model/path scope, stale-state invalidation, replacement-failed handling and no speculative chain.
- [ ] Run Controlled Selection, two-page, Stable Guidance, exact/message/fuzzy/unsupported Error Code, Other/PIE_ONLY, 1202, privacy and projection regressions.
- [ ] Verify Page 1 mandatory input count did not increase.
- [ ] Verify Page 2 remains scan-friendly for all Top10 public/guided paths at 1366x768 and 1920x1080 plus actual Windows Edge 125%.
- [ ] Basic mobile compatibility only.
- [ ] Run two owned lifecycle start/stop/relaunch cycles.
- [ ] Regenerate standalone Windows package and verify extracted run, public-resource readback, whitelist and hash parity.
- [ ] Perform independent final review focused on ranking validity, software contamination of hardware Top10, unsupported part/SKU, unsafe procedure, scope broadening, source leakage and accidental UI complexity.
- [ ] Fix ordinary defects autonomously and rerun affected tests plus final full gates.

## Final Report Requirements

Report to Issue #6 with:

1. exact current Reply Assistant workspace/vault used;
2. exact evidence time window used for `current Top10`;
3. whether ranking is count-based, partially count-based, or priority-based;
4. candidate count and exclusion reasons;
5. final hardware-first Top 10 table: `symptom + solution + verification`;
6. which Top10 issues reused existing mature cards;
7. which new Repair Paths were created and why;
8. per-Top10 resource coverage: part, SKU, qty, tool, tool usage, disassembly, expected result, verification, fallback;
9. items withheld / PIE_ONLY and why;
10. confirmation that pure software problems were excluded from Top10 unless explicitly documented as unavoidable evidence gap;
11. confirmation that normal user input did not increase;
12. fresh automated/browser/privacy/lifecycle/package evidence;
13. standalone artifact path + SHA256;
14. only true remaining business/source decisions.

## Final Gate

Claim `TROUBLESHOOTER_HARDWARE_TOP10_GREEN` only when:

- the current hardware-first Top 10 has been derived from actual current sources rather than guessed;
- each selected issue has at minimum `observable symptom + solution/repair route + verification`;
- software-only issues have not displaced stronger hardware repair problems;
- every publishable issue follows evidence/scope/serviceability rules;
- the normal agent interaction remains simple;
- the result page is richer but not visually dense;
- source/privacy/safety boundaries remain intact;
- all fresh regression/browser/lifecycle/package gates pass after final fixes.

If fewer than 10 hardware issues satisfy the evidence bar, do not fabricate the remainder. Report the strongest supported set plus `TOP10_GAP`, while still completing all safe enrichment work.
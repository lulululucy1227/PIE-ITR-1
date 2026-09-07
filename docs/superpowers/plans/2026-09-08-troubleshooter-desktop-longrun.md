# PIE Troubleshooter Desktop Long-Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` where helpful and `superpowers:verification-before-completion` before any final green claim. Use `superpowers:systematic-debugging` for unexpected failures. Execute continuously; do not stop for routine confirmation.

**Goal:** Turn the existing isolated Error Code Pilot into a desktop-first PIE Troubleshooter that supports both Error Code search and controlled symptom navigation, safely promotes stable repair knowledge, and finishes with autonomous engineering/knowledge self-review and a locally runnable artifact.

**Architecture:** Keep the existing standalone `error-code-pilot` lightweight read-only application in `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`. Extend the current canonical knowledge/projection/search stack rather than rebuilding it. The UI becomes desktop-first: persistent product/model context, prominent Error Code/Error Message search, and controlled symptom navigation on the same page. Both routes converge on one Repair Card contract. Candidate knowledge remains separate from agent-visible promoted knowledge.

**Tech Stack:** Existing specialist stack in `error-code-pilot` (Node/static SPA/local read-only server and current test/browser tooling). Do not introduce a framework/backend/LLM/DB unless the existing implementation cannot satisfy a concrete requirement.

**Spec:** `docs/troubleshooter/BUILDER_HANDOFF_2026-09-08.md`

## Global Constraints

- Canonical repo: `lulululucy1227/PIE-ITR-1`.
- Specialist workspace: `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode` only.
- MAIN workspace `C:\Users\Reggie\Desktop\PIE-ITR-1` is read-only for this stream.
- Do not use port 8787.
- No Feishu/Nextop/ITR production writes.
- No public/external deployment.
- No merge/push into default/main unless separately authorized.
- No PII, raw chats, SN/Device Name, credentials or full ticket histories in published artifacts.
- Desktop is the optimization target; mobile only requires non-broken basic compatibility.
- Error Code is a fast shortcut, not the dominant product architecture.
- Controlled symptoms are observable/cause-neutral/repair-neutral. Free text cannot directly generate a repair recommendation.
- Preserve existing promoted knowledge from `docs/knowledge/ERROR_CODES.md` and `docs/knowledge/KNOWN_FIXES.md`.
- `1202` repair path remains frozen/PIE-only until scope conflict is resolved.
- Evidence policy is authoritative: `VERIFIED_RESOLUTION` and `STABLE_OPERATIONAL_GUIDANCE` may support agent-facing P0/P1. Explicit partner `solved` feedback is not mandatory. Age/silence alone is not enough.
- If evidence is ambiguous, default the path to hidden/PIE_ONLY and continue the project. Do not stop the whole run for one knowledge blocker.

---

## Task 1 — Recover current specialist state and map exact implementation files

**Files:** inspect the current specialist checkout before editing. Expected implementation root: `error-code-pilot/`; exact current files must be recorded in `error-code-pilot/docs/LONGRUN_FILE_MAP.md` before changes.

**Produces:** a current file map covering canonical knowledge data, agent projection/export, search/index logic, SPA entry/UI modules, styles, server/launcher, tests, browser tests, build/package scripts and docs.

- [ ] Read `MASTER_PLAN.md`, `AGENT_REGISTRY.md`, newest READY Issue #5 task, newest relevant Issue #6 report, `docs/troubleshooter/BUILDER_HANDOFF_2026-09-08.md`, `docs/troubleshooter/EVIDENCE_PROMOTION_POLICY.md`, `docs/troubleshooter/SYMPTOM_MODEL.md`, `docs/knowledge/ERROR_CODES.md`, and `docs/knowledge/KNOWN_FIXES.md`.
- [ ] Verify the specialist checkout/branch is the existing isolated implementation; do not recreate or normalize MAIN.
- [ ] Run the existing unit/data/browser/build test baseline fresh and record exact commands/results.
- [ ] Create `error-code-pilot/docs/LONGRUN_FILE_MAP.md` containing exact current paths and responsibility of every file to be touched.
- [ ] If baseline has failures, reproduce and fix them first using systematic debugging; rerun baseline before proceeding.
- [ ] Commit only inside the specialist branch when a coherent checkpoint is reached.

**Self-approval gate A:** proceed only after isolation is confirmed, baseline is known, and exact file map exists. If a non-critical historical test is obsolete because of the new approved product direction, update the test with rationale rather than stopping.

---

## Task 2 — Extend canonical schema for symptom-first navigation and evidence promotion

**Files:** use exact canonical/schema/validation paths from Task 1; update schema tests in the corresponding existing test directory.

**Interfaces to preserve:** existing exact code/message/fuzzy search; approved-only public projection; scope/currentness guards; replacement-failed behavior.

**Required data capabilities:**
- `symptom_id`
- `observable_area`
- canonical EN/CN controlled symptom labels
- aliases where already supported
- optional qualifier only when it changes repair path
- `repair_path_id`
- model/product scope
- evidence state including `VERIFIED_RESOLUTION`, `STABLE_OPERATIONAL_GUIDANCE`, `ACTION_PERFORMED_OUTCOME_UNKNOWN`, `SOURCE_RECOMMENDATION`, `CONFLICTING_EVIDENCE`
- agent visibility / publishability
- conflict/supersession state
- verification and fallback
- Error Code/Error Message links where applicable

- [ ] Write failing validation tests for symptom uniqueness, valid area values, valid repair references, evidence-state enum, no orphan publishable symptom, and 1202 frozen behavior.
- [ ] Implement the minimal schema/data changes.
- [ ] Add tests proving candidate data cannot leak into approved public export simply because priority is P0/P1.
- [ ] Add tests proving `STABLE_OPERATIONAL_GUIDANCE` is eligible for promotion when other gates pass, while `SOURCE_RECOMMENDATION` is not auto-promoted.
- [ ] Run all schema/data/projection tests.

**Self-approval gate B:** schema may be approved locally when validation is deterministic, existing Error Code behavior remains green, and candidate/approved boundaries are explicit.

---

## Task 3 — Load the supervisor-approved controlled symptom skeleton

Use exactly the product skeleton in `docs/troubleshooter/BUILDER_HANDOFF_2026-09-08.md` unless a hard referential defect is found.

**Required areas:** Movement, Cutting, Charging, Docking, Power, Positioning, Connectivity, Sensors, Physical, Software.

**Required symptom set:** SYM-001 through SYM-025 as navigation candidates; SYM-026 through SYM-028 remain PIE-only and must not resolve to direct repair cards.

- [ ] Add/normalize the 10 approved areas and 28 symptom IDs in canonical candidate data.
- [ ] Preserve EN as formal agent-facing language; retain CN labels internally or in development metadata where useful.
- [ ] Validate that component/cause/internal-tool labels are not used as controlled symptoms.
- [ ] Ensure no MammoSuite/Kit/account/parts/warranty category becomes a normal agent symptom area.
- [ ] Add deterministic tests for area counts, symptom IDs, PIE-only routing and alias matching if present.

**Self-approval gate C:** navigation data is locally approved when all 28 IDs are unique, all 25 navigation symptoms render, all 3 PIE-only symptoms route safely, and no cause/component/internal taxonomy leaks into the symptom picker.

---

## Task 4 — Perform autonomous repair-knowledge promotion audit

This task replaces the incorrect rule that only explicit `solved` outcomes count.

**Authoritative policy:** `docs/troubleshooter/EVIDENCE_PROMOTION_POLICY.md`.

**Candidate sources:** current existing specialist canonical data, promoted GitHub knowledge, the structured candidate paths already captured in `docs/troubleshooter/BUILDER_HANDOFF_2026-09-08.md`, local source provenance already present in the specialist workspace, and relevant historical Git/repo evidence available without touching protected Feishu/Nextop sessions.

For every candidate repair path:
- [ ] Check whether the instruction is actively maintained/used and materially unchanged over meaningful operational exposure.
- [ ] Check for contradictions, repeated replacement-failed/reopen evidence, superseding rules, model/version conflicts or narrower scope.
- [ ] Check that the repair action is executable by the intended agent and has a valid verification/fallback.
- [ ] Classify into exactly one evidence state.
- [ ] Promote to agent-visible only if evidence state is `VERIFIED_RESOLUTION` or `STABLE_OPERATIONAL_GUIDANCE` and scope/verification/agent capability gates pass.
- [ ] If the evidence is insufficient or ambiguous, keep as candidate/PIE_ONLY and continue; do not ask the user.
- [ ] Never infer `STABLE_OPERATIONAL_GUIDANCE` from age/silence alone.

Specific mandatory cases:
- 1202: retain exact lookup/physical-blockage guardrail; repair path stays frozen/PIE-only.
- 1000022: preserve narrow historical verified firmware fix and currentness guardrail; do not prescribe the historical target as universally current.
- 2000303: preserve false-alarm/no-repair behavior where supported by promoted/current knowledge; do not turn it into a hardware replacement card.
- 1008, 5501, 6401, 1500, DT-041: preserve existing promoted semantics and do not weaken them through generic symptom mappings.

Create `error-code-pilot/docs/KNOWLEDGE_PROMOTION_AUDIT_2026-09-08.md` containing only sanitized per-path decisions: path ID, evidence state, scope, visibility, conflict/reopen notes, verification/fallback status and rationale.

**Self-approval gate D:** Builder is authorized to self-approve engineering publication into the local agent projection only for paths that pass the policy. Any unresolved path is automatically withheld/PIE_ONLY rather than blocking the run.

---

## Task 5 — Rebuild desktop-first home without a binary entry toggle

**Target behavior:** one home screen with persistent model/product context, prominent Error Code/Error Message search, and visible `Choose by symptom` navigation.

- [ ] Write browser/component tests for homepage layout and interaction before modifying UI.
- [ ] Implement persistent model/product selector/context.
- [ ] Keep Error Code/Error Message search prominent at the top.
- [ ] Render the 10 symptom areas on the same page; selecting an area reveals only its controlled symptoms.
- [ ] Do not show a required `I have / I do not have Error Code` choice.
- [ ] Keep fuzzy search candidate-only; never silently choose a repair path.
- [ ] Ensure model changes recompute available scope/results without stale state.
- [ ] Desktop scan speed takes priority over mobile-specific layout work.

Desktop acceptance viewports must include at least 1366x768 and 1920x1080. Basic non-broken mobile check may remain 390px wide but mobile redesign is not required.

**Self-approval gate E:** home may pass when both entry routes are visible without unnecessary clicks, model context is persistent, no stale result survives a conflicting model switch, and no horizontal overflow/page errors occur.

---

## Task 6 — Converge Error Code and symptom routes on one Repair Card

- [ ] Write tests proving the same canonical repair path produces the same card regardless of entry route.
- [ ] Repair Card order: `Most likely faulty part / target area` → `What to do` → `After repair / verification` → `Still not fixed`.
- [ ] Do not expose evidence-state labels, source names, taxonomy, confidence math, R&D notes or internal reasoning in the normal agent card.
- [ ] Show one decisive check only when it materially changes the repair path.
- [ ] If a selected symptom has no approved repair path, show a concise PIE-only result rather than an empty/broken card.
- [ ] If a replacement failed/issue returned, avoid looping the same action forever; follow canonical alternative/fallback or route PIE.
- [ ] `Fixed` remains a local/self-reported UI state only and must not write/close ITR/NFF.

**Self-approval gate F:** the card contract is approved when data parity, no-candidate-leakage, verification/fallback presence and failed-repair non-looping behavior all pass deterministic tests.

---

## Task 7 — Verification policy cleanup

The canonical repair requirement must not be weakened by UI simplification.

- [ ] For every locally promoted repair path, validate that a verification requirement and failure fallback exist.
- [ ] Where the established standard loop applies, retain: Functional Test + Communication Check + Auto Map Run + three reports + Connect Checking screenshot.
- [ ] Agent UI may display the minimum relevant verification steps, but the canonical record must retain the full applicable requirement.
- [ ] Do not treat Burn-in as a substitute for the three standard verification tests.
- [ ] Add validation/test failure for any publishable path missing verification or fallback.

---

## Task 8 — Critical knowledge and UX edge-case matrix

Add automated tests and browser checks for at least:
- exact Error Code lookup;
- exact Error Message lookup;
- signed Error Code where supported;
- fuzzy search with multiple candidates;
- unsupported code;
- known informational/false-alarm code;
- Error Code requiring symptom disambiguation;
- symptom-only approved path;
- symptom-only PIE_ONLY path;
- model-incompatible path;
- version/currentness-sensitive knowledge;
- 1202 frozen behavior;
- replacement failed/returned;
- model switch after a result is open;
- candidate data present internally but absent from public projection;
- no free-text diagnosis path.

If any test fails, debug/fix/rerun autonomously. Do not stop at the first defect.

---

## Task 9 — Desktop usability self-review and refinement

Perform an explicit self-review from the perspective of an agent trying to repair quickly.

Questions Builder must answer with evidence from the actual UI:
1. Can an agent with an Error Code reach the useful result quickly?
2. Can an agent without an Error Code find an observable symptom without understanding internal taxonomy?
3. Are area/symptom labels mutually understandable enough to avoid obvious wrong selection?
4. Does the result emphasize the part/action/verification rather than internal explanation?
5. Is there unnecessary diagnostic branching that can be removed without reducing safety?
6. Are low-confidence/PIE-only paths clearly withheld rather than appearing broken?
7. Does the desktop page remain readable at 125% browser zoom and common laptop widths?

- [ ] Capture/inspect actual browser screenshots during review.
- [ ] Fix ordinary UX issues directly.
- [ ] Rerun relevant browser tests after each material fix.

**Self-approval gate G:** Builder may approve the desktop UX only after a fresh browser pass. Do not approve by reading source code alone.

---

## Task 10 — Privacy, projection and local-security review

- [ ] Confirm public projection contains no PII, SN/Device Name, raw case histories, auth material, Git metadata or unnecessary internal evidence.
- [ ] Confirm candidate/internal knowledge endpoints/assets cannot be reached through normal static/server routes.
- [ ] Confirm write methods/routes are absent or refused.
- [ ] Confirm no external network requests are made by the standalone UI unless already explicitly approved.
- [ ] Confirm MAIN workspace/runtime/port 8787 remained untouched.
- [ ] Run source-leakage scans over the final dist/package.

**Self-approval gate H:** any privacy/source-leak failure blocks packaging until fixed.

---

## Task 11 — Fresh full regression, lifecycle and package

Do not reuse prior PASS claims.

- [ ] Run complete unit/data/projection/search/browser suite fresh.
- [ ] Run desktop browser acceptance fresh at required viewports.
- [ ] Run basic mobile non-regression.
- [ ] Run two owned local server start → close → port-free → relaunch cycles on a non-8787 port.
- [ ] Build final local dist/package.
- [ ] Verify package allowlist and extracted standalone run/readback.
- [ ] Compute artifact hash.
- [ ] Update local run/update/rollback instructions.

---

## Task 12 — Independent self-review before final claim

Treat the implementation as if reviewing another engineer's work.

Review independently for:
- product/spec compliance;
- symptom taxonomy leakage;
- evidence-promotion mistakes;
- candidate-to-public leakage;
- scope overreach;
- stale promoted knowledge regression;
- 1202 accidental publication;
- broken references/orphans;
- UX regressions;
- privacy/source leakage;
- test gaps.

If defects are found, fix them and rerun the affected verification. Do not merely list defects in the final report if they can be safely repaired within scope.

Builder is authorized to self-approve all **local** engineering/knowledge gates in this plan after evidence and tests pass.

Builder is NOT authorized to self-approve:
- public/external deployment;
- production hosting/auth rollout;
- Feishu/Nextop/ITR production writes;
- merge/push into default/main;
- changing the frozen 1202 business scope by guess;
- introducing raw/private source data into the public projection.

If any of these would be required, leave that item pending and continue all other work.

---

## Task 13 — Final status and Issue #6 report

Post one concise final report to Issue #6 with the matching master task ID.

Required fields:
- `EC-REPORT_ID`
- `EC-MASTER_TASK_ID`
- `STATUS`
- `EXECUTION_MODEL / EFFORT`
- local commit/branch/workspace
- implementation summary
- knowledge promotion summary: counts by evidence state and visibility
- exact list of withheld/conflicting knowledge, including 1202
- test/browser/lifecycle/package results
- privacy/projection result
- artifact path/hash
- any genuine remaining business/authorization decisions
- recommended next phase

## Final local gate

Claim `TROUBLESHOOTER_DESKTOP_LOCAL_GREEN` only when all of the following are true:
1. desktop-first homepage is implemented;
2. model context + Error Code search + symptom navigation work together;
3. 10 areas and approved symptom skeleton are integrated with safe PIE-only behavior;
4. existing promoted Error Code knowledge remains intact;
5. repair promotion follows the new evidence policy, including `STABLE_OPERATIONAL_GUIDANCE`;
6. no unresolved/candidate repair path leaks to agents;
7. 1202 remains safely frozen unless separately resolved;
8. all agent-visible paths have verification + fallback;
9. fresh automated/browser/lifecycle/privacy/package checks pass;
10. independent self-review has no unresolved fixable defect;
11. no production write/public deployment/default-branch integration occurred.

If one knowledge item is unresolved but safely withheld, this does NOT block `TROUBLESHOOTER_DESKTOP_LOCAL_GREEN`.

Only a platform-wide defect, privacy leak, broken safe-routing behavior, or failure of the local product itself should block the local green gate.

# Troubleshooter Simple Knowledge Reuse Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reuse the most valuable current Work Order Reply Assistant knowledge inside the isolated PIE Troubleshooter while reducing normal agent input and keeping the repair page direct, sparse and safe.

**Architecture:** Keep the products runtime-independent. Read the Reply Assistant knowledge base read-only, create a traceable internal import manifest/snapshot inside the isolated Troubleshooter workspace, reconcile useful facts against current Troubleshooter canonical knowledge, then project only approved scoped facts into the existing repair-card/service-guidance layer. Simplify Page 1 by removing unnecessary mandatory interaction; keep Page 2 focused on one actionable repair path with progressive disclosure.

**Tech Stack:** Existing isolated Troubleshooter stack and current tests/build/package tooling. No new framework, database, CMS, LLM runtime or production integration.

**Spec:** `docs/troubleshooter/SIMPLE_KNOWLEDGE_REUSE_DESIGN_2026-09-15.md`

## Global Constraints

- Reply Assistant workspace/knowledge is READ ONLY.
- Troubleshooter writes only inside `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`.
- No MAIN runtime/8787/session/analyzer/production mutation.
- No public deployment or default/main merge.
- 1202 remains frozen.
- Normal user path must not gain additional required fields.
- No runtime dependency from Troubleshooter to Reply Assistant.
- Internal source material never enters public projection unless explicitly classified and approved.
- Preserve existing mature Guidance, PIE_ONLY behavior, model/version scope, two-page separation and privacy boundaries.

---

### Task 1: Recover current specialist state and map actual files

**Files:**
- Read: latest Issue #5 task and Issue #6 reports.
- Read: `docs/troubleshooter/SIMPLE_KNOWLEDGE_REUSE_DESIGN_2026-09-15.md`.
- Read: current local `error-code-pilot` implementation/data/test/docs tree.
- Do not create a parallel implementation if an existing canonical data/service-guidance module already exists.

**Interfaces:**
- Consumes: current `TROUBLESHOOTER_CONTROLLED_SELECTION_GREEN` local state.
- Produces: exact local file map used by Tasks 2–7.

- [ ] Confirm isolated workspace and clean/known local state.
- [ ] Identify exact current canonical/private/public data files, UI entry files, service-guidance adapter files, tests and packaging scripts.
- [ ] Identify the newest current Reply Assistant local workspace from current MAIN control-plane/report state. Use `C:\Users\Reggie\Desktop\PIE-ITR-1` only as read-only fallback if no newer workspace is present.
- [ ] Confirm the Reply Assistant knowledge directory and record source paths/hashes before reading content.
- [ ] Verify no write occurs outside the specialist workspace.

### Task 2: Build a reviewed Reply Assistant knowledge-source manifest

**Source families to inspect first:**
- `docs/knowledge/ERROR_CODES.md`
- `docs/knowledge/KNOWN_FIXES.md`
- `docs/knowledge/DIAGNOSTIC_KNOWLEDGE.md`
- `docs/knowledge/PARTS_KNOWLEDGE.md`
- `docs/knowledge/TOOL_KNOWLEDGE.md`

**Interfaces:**
- Consumes: read-only source sections + current Troubleshooter canonical/private knowledge.
- Produces: internal-only manifest with source path, section identity/hash, classification, target card/path if any, scope and decision.

- [ ] Add failing tests that prove source provenance/private manifest cannot leak to public assets.
- [ ] Implement the minimal manifest/snapshot representation using the existing specialist data conventions.
- [ ] Classify each potentially reusable fact as `PUBLIC_REPAIR_FACT`, `PUBLIC_TOOL_STEP`, `PUBLIC_PART_FACT`, `PRIVATE_INTERNAL`, `NEEDS_SCOPE_REVIEW`, `CONFLICT`, or `DUPLICATE`.
- [ ] Explicitly exclude passwords/credentials, PII, NFF/internal workflow, warranty routing, reply-writing rules and raw case material from public candidates.
- [ ] Record 1202 as non-promotable/frozen regardless of source presence.
- [ ] Run manifest/privacy tests.

### Task 3: Reconcile and enrich existing mature repair cards first

**Interfaces:**
- Consumes: existing mature Guidance/Repair Cards + manifest candidates + `EVIDENCE_PROMOTION_POLICY.md`.
- Produces: updated private canonical/service-guidance data for existing cards only where source scope is supported.

- [ ] Add failing tests for each newly reused fact before modifying canonical/public data.
- [ ] Prioritize facts that reduce repair effort: decisive check, confirmed tool step, exact compatible part/SKU, serviceability boundary, capability guardrail, expected result, verification detail.
- [ ] Reconcile model/version scope before attaching any fact to a card.
- [ ] If source and current Troubleshooter disagree, keep both private and classify `CONFLICT` unless one is explicitly newer/superseding and scope-safe.
- [ ] Do not publish a speculative backup part chain after the stable step fails; route to PIE.
- [ ] Do not add a target number of cards or facts.
- [ ] Run targeted canonical/public-projection tests.

### Task 4: Add only high-value new repair paths that remain simple

**Interfaces:**
- Consumes: remaining manifest candidates not used by Task 3.
- Produces: zero or more new scoped Repair Paths only when they meet the existing promotion policy and require no new normal input complexity.

- [ ] Identify candidates with clear observable symptom, model scope, executable action, verification and safe fallback.
- [ ] Prefer `VERIFIED_RESOLUTION` or `STABLE_OPERATIONAL_GUIDANCE`.
- [ ] Reject/keep private anything that needs a broad engineering tree, ambiguous part mapping, weak scope or internal-only workflow.
- [ ] Do not create new symptoms merely to make source knowledge fit.
- [ ] Run full referential-integrity and no-invented-knowledge tests.

### Task 5: Simplify Page 1 interaction without weakening controlled diagnosis

**Target normal flow:**
`Model -> Problem / Controlled Symptom -> Continue -> Repair`

**Interfaces:**
- Consumes: existing controlled model/symptom data and optional Error Code search.
- Produces: simplified identification state compatible with the existing Page 2 contract.

- [ ] Write failing browser/state tests proving `Observable Area` is no longer a mandatory extra step when the symptom list can be grouped cleanly.
- [ ] Keep Area internally as grouping/filter metadata.
- [ ] Present model-filtered symptoms in one clean control/grouped list rather than a dense category dashboard.
- [ ] Keep Error Code / Message optional. Exact code may pre-filter or highlight symptom candidates, but user confirms the controlled symptom.
- [ ] Keep firmware hidden unless the selected path is version-dependent, then request it just-in-time.
- [ ] Keep `Other / None of these`; its free text only routes to PIE/taxonomy feedback and cannot generate repair advice.
- [ ] Preserve Back/change-input invalidation, deep-link safety and stale-result protections.
- [ ] Verify desktop-first layouts at 1366x768 and 1920x1080 plus real Edge 125% zoom; mobile only needs basic compatibility.

### Task 6: Make Page 2 easier to scan for both new and experienced technicians

**Interfaces:**
- Consumes: existing Repair Card and service-guidance adapter.
- Produces: sparse default repair view with optional detail expansion.

- [ ] Add failing UI tests for the visible hierarchy: problem summary -> primary action -> needed part/tool -> expected result -> verification -> still-not-fixed.
- [ ] Make the first visible instruction answer `What should I do now?`.
- [ ] Do not show multiple possible replacement parts simultaneously unless the repair path genuinely requires preparation of multiple items.
- [ ] Show exact SKU only after the branch has identified the compatible service part; never infer SKU from part name alone.
- [ ] Keep rationale, related cases, technical background and training details collapsed under `Why / Learn more` or equivalent.
- [ ] Do not add separate inventory, document-repository, ERP or expert-console modules.
- [ ] Keep empty future resource modules hidden.
- [ ] Verify every currently public mature card still renders correctly.

### Task 7: Full regression, privacy, package and self-repair loop

**Interfaces:**
- Consumes: all changes from Tasks 2–6.
- Produces: local final package + Issue #6 report.

- [ ] Run all existing Node/unit/schema/referential tests plus new import/simplification tests.
- [ ] Run Controlled Selection regression.
- [ ] Run two-page flow regression.
- [ ] Run Stable Guidance regression for all public mature cards.
- [ ] Run Error Code exact/message/fuzzy and unsupported-code checks.
- [ ] Run Other/PIE_ONLY/failed-or-returned/1202 regression.
- [ ] Run public-projection/privacy/source-leakage scan.
- [ ] Run two owned lifecycle start/stop/relaunch cycles.
- [ ] Regenerate the standalone Windows package and test extracted startup/readback/hash parity.
- [ ] Perform an independent review focused on: accidental UX complexity, hidden extra required inputs, source leakage, scope broadening, speculative SKU/part publication and regression of existing repair knowledge.
- [ ] Reproduce and fix every ordinary defect found; rerun the affected gate and then the complete final regression. Do not stop for routine failures.
- [ ] Post one concise final Issue #6 report with source counts, reused/public/private/conflict counts, exact UX simplification, test evidence, artifact hash and remaining true business decisions.

## Final Gate

Claim `TROUBLESHOOTER_SIMPLE_KNOWLEDGE_GREEN` only when all are true:

1. Reply Assistant knowledge reuse is one-way, traceable and runtime-independent.
2. Useful knowledge enriches Troubleshooter without bulk-copying internal/noisy material.
3. Normal Page 1 interaction is no more than Model + Controlled Problem, with Error Code optional and version just-in-time.
4. Page 2 is easier to scan and does not expose a wall of parts/diagnostic text.
5. Existing stable Guidance, PIE_ONLY, 1202 freeze, scope and privacy protections remain intact.
6. Full automated/browser/lifecycle/package/privacy regression passes after all fixes.
7. No routine implementation issue remains unresolved.

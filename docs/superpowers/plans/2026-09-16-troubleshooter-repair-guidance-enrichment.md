# Troubleshooter Repair Guidance Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enrich the existing 10 mature Troubleshooter repair cards with only evidence-backed part/SKU, tool, tool-usage, disassembly/installation, expected-result and verification details available from the current Work Order Reply Assistant knowledge base, while keeping the agent-facing repair experience simple.

**Architecture:** Keep the existing standalone Troubleshooter runtime, controlled selection flow, canonical/public projection, and service-plan resource contract. Treat the Reply Assistant knowledge vault as READ ONLY; create/extend a traceable private source snapshot and bind only reviewed facts to existing repair cards. Do not create a new inventory system, document center, expert tree, or new runtime dependency.

**Tech Stack:** Existing `error-code-pilot` stack and test harness in the isolated Troubleshooter workspace; static/read-only knowledge projection; existing Windows standalone packaging.

**Spec:** `docs/troubleshooter/SIMPLE_KNOWLEDGE_REUSE_DESIGN_2026-09-15.md`

## Global Constraints

- Target only the existing 10 mature scoped repair cards first; do not add new Repair Paths in this task.
- Normal front-end path remains `Model -> Controlled Symptom -> Repair`; no new mandatory user input.
- Reply Assistant workspace and knowledge vault are READ ONLY.
- Do not infer a SKU from part name, family name, appearance, or similar model.
- Publish a part/SKU only when exact model + repair target + compatibility are supported.
- Publish tool guidance only when the exact tool/function is supported for the target model/path.
- Publish disassembly/installation steps only when scope and safety conditions are supported; otherwise withhold them.
- Keep advanced detail collapsed/secondary so experienced technicians can scan the primary action immediately.
- 1202 remains frozen.
- PIE_ONLY, POS/WIFI/LIDAR narrow-scope rules, water/physical-damage boundaries, and privacy rules must not regress.
- No public deployment, Feishu/Nextop/ITR production write, MAIN runtime mutation, or default/main merge.

---

### Task 1: Recover the newest specialist baseline and freeze the 10-card target matrix

**Files:**
- Read current specialist knowledge/public projection/service-plan resources in `error-code-pilot/`
- Create or update a private audit matrix under `error-code-pilot/data/`
- Test with existing schema/projection tests

**Interfaces:**
- Consumes: current `TROUBLESHOOTER_SIMPLE_KNOWLEDGE_GREEN` local specialist state
- Produces: one target matrix listing each mature card, Repair Path, exact model scope, current action, current verification, and missing optional resources

- [ ] Re-read Issue #5 latest READY task and Issue #6 latest accepted report.
- [ ] Use the newest local specialist state; do not reset to remote `main` if local is newer.
- [ ] Enumerate the exact 10 mature scoped cards currently published.
- [ ] For each card, record whether these fields are already supported: `part_name`, `sku`, `quantity`, `tool`, `tool_usage`, `disassembly_installation`, `expected_result`, `verification`, `still_not_fixed`.
- [ ] Mark each missing field as `SEARCH_REQUIRED`, not as empty UI content.
- [ ] Add deterministic validation that every published resource is bound to an existing card/path/model.

### Task 2: Targeted read-only search of the current Reply Assistant knowledge vault

**Files:**
- Read-only: current Work Order Reply Assistant workspace and `维修与售后知识库`
- Update private provenance manifest/snapshot in `error-code-pilot/data/`

**Interfaces:**
- Consumes: 10-card target matrix
- Produces: evidence candidates tied to a specific card/path/model/field

- [ ] Re-detect the current Reply Assistant workspace and active knowledge vault instead of assuming the previous path is still current.
- [ ] Search by the exact model, symptom, component, existing action and known aliases for each of the 10 cards.
- [ ] Search relevant current folders first, especially existing parts/SBOM/料号依据, repair SOP, tool SOP, repair strategy, guided repair, PCN/technical notice, known fix, version applicability and Error Code content.
- [ ] Do not bulk-copy entire directories. Copy only minimal technical facts needed for a specific field.
- [ ] Record source path, section, file hash and read time for every candidate fact.
- [ ] Re-read any file actually used before final packaging and verify its hash did not silently change during the task.

### Task 3: Classify every candidate field and reject unsupported detail

**Files:**
- Update reviewed private snapshot/manifest
- Test classification and projection rules

**Interfaces:**
- Consumes: targeted source candidates
- Produces: per-field decisions for each of the 10 cards

- [ ] Classify each candidate as one of: `PUBLISH_EXACT`, `PUBLISH_SCOPED_NOTE`, `PRIVATE_ONLY`, `NEEDS_SCOPE_REVIEW`, `CONFLICT`, `DUPLICATE`, `NOT_RELEVANT`.
- [ ] For SKU candidates, require exact model + exact repair target + exact SKU mapping. If any link is missing, do not publish the SKU.
- [ ] For quantity, publish only when the source explicitly supports the service quantity; never infer `1` merely because one part is shown.
- [ ] For tools, require the exact tool/function to be appropriate for the target model/path. Do not confuse MammoSuite and Mammotion Kit.
- [ ] For disassembly/installation, require model/path scope and necessary safety/sequence detail. A vague “remove cover” note is not enough for publication.
- [ ] For expected result, use only observable results supported by the source; do not invent voltage/measurement thresholds.
- [ ] Preserve conflicts privately and continue other cards.

### Task 4: Enrich existing Repair Cards without increasing normal interaction complexity

**Files:**
- Modify current service-plan/resource projection only as needed
- Modify public card projection only for approved scoped details
- Tests for each enriched card

**Interfaces:**
- Consumes: reviewed field decisions
- Produces: enriched but still concise Page 2 content

- [ ] Keep the default visible order: `Problem summary -> What should I do now? -> required Part/SKU/Tool -> Expected result when useful -> Verification -> Still not fixed`.
- [ ] Do not add new mandatory Page 1 input.
- [ ] Do not show a SKU/part/tool block when there is no approved resource for that specific card.
- [ ] Do not show several possible replacement parts at once.
- [ ] If a repair branch confirms a specific serviceable part, show the exact part/SKU/quantity only there.
- [ ] Put optional learning detail such as rationale, tool explanation or longer assembly notes behind a compact expandable `Details` / `How to do it` affordance.
- [ ] Experienced technicians must be able to read the primary action without expanding anything.
- [ ] New technicians must be able to expand only the extra detail needed to perform the same approved action.

### Task 5: Preserve safety and failure behavior

**Files:**
- Existing engine/public projection tests
- New regression cases as needed

**Interfaces:**
- Consumes: enriched cards
- Produces: safe failure/fallback behavior

- [ ] Keep 1202 frozen and unchanged.
- [ ] Keep PIE_ONLY items from receiving speculative part/SKU/tool/disassembly content.
- [ ] If a published step fails, route only to an already approved next step or PIE; do not introduce a speculative second/third replacement chain.
- [ ] Keep replacement-failed/returned safeguards.
- [ ] Changing model/symptom/error input must invalidate stale Page 2 resources, including previously shown SKU/tool/disassembly content.

### Task 6: Audit usability and remove accidental complexity

**Files:**
- Browser/UI regression tests and evidence screenshots

**Interfaces:**
- Consumes: final enriched UI
- Produces: verified simple repair experience

- [ ] Verify normal required input remains exactly Model + Controlled Symptom, with Error Code optional.
- [ ] Verify no new category wall, parts wall, document library, inventory view, dashboard or expert tree appears.
- [ ] For each enriched card, check that the first visible action is understandable in a quick scan.
- [ ] Check that optional details do not visually compete with the main action.
- [ ] Test at 1366x768, 1920x1080 and Windows Edge 125% zoom; mobile only needs basic compatibility.
- [ ] Fix any layout/wording that creates visual overload and rerun checks.

### Task 7: Full regression, package and independent final review

**Files:**
- Existing full test suite
- Regenerated standalone Windows package
- Final evidence/report files

**Interfaces:**
- Consumes: completed enrichment
- Produces: `TROUBLESHOOTER_REPAIR_GUIDANCE_GREEN` or a precise blocked/gap report

- [ ] Run fresh full Node/schema/projection tests.
- [ ] Run source-manifest/hash/readback tests.
- [ ] Run Controlled Selection, two-page flow, Stable Guidance, Error Code search, Other/PIE_ONLY, failed/returned and 1202 regressions.
- [ ] Add exact tests for every newly published SKU/tool/disassembly/expected-result resource.
- [ ] Run privacy/public-projection scan to ensure source documents, internal notes, credentials, raw ticket data and private provenance never enter the agent package.
- [ ] Run two owned lifecycle start/stop/relaunch cycles.
- [ ] Regenerate the standalone Windows package and verify extracted-run behavior and full file/hash parity.
- [ ] Perform an independent final review focused on unsupported SKU publication, incorrect tool selection, unsafe/vague disassembly guidance, accidental complexity, stale-state leakage and source-scope broadening.
- [ ] Fix ordinary findings autonomously and rerun affected plus final full gates.
- [ ] Post final report to Issue #6 with a 10-card matrix showing exactly what was found, published, withheld and still missing.

## Final Gate

Claim `TROUBLESHOOTER_REPAIR_GUIDANCE_GREEN` only when:

- all 10 mature cards have been audited against the current Reply Assistant knowledge base;
- every usable exact resource found has either been safely integrated or explicitly withheld with reason;
- no unsupported SKU/tool/disassembly/threshold is invented;
- normal agent input remains simple and unchanged;
- Page 2 is more useful without becoming visually dense;
- all fresh automated/browser/privacy/lifecycle/package gates pass after all fixes;
- ordinary engineering defects are resolved;
- final Issue #6 report contains an exact per-card gap matrix and only true business/source gaps.

A card is allowed to remain partially populated. Missing source material is a documented knowledge gap, not a reason to invent content or block the rest of the project.

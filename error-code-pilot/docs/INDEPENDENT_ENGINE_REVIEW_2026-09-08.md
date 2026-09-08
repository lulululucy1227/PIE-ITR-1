# Independent engine, schema and knowledge review

Task: EC-MT-20260908-DESKTOP-LONGRUN-003. Reviewed 2026-09-08.

Scope: supplied `engine-review.diff` (d5aeafe..c2f8752), current engine/schema/data, engine report, independent knowledge review, plan Tasks 2/3/4/6/7/8, evidence promotion policy, source knowledge and data-contract documentation. UI, lifecycle/server, package and remote integration are excluded. Only this report was written; no production/source edits, commits, MAIN access, servers, port 8787 or remote writes.

## Verdict

**Changes required for engine/schema quality approval: 3 Important findings; no Critical or Minor findings.** The present reviewed knowledge is substantially spec-compliant, but the publication, qualifier and supersession contracts have reproducible gaps with schema-valid records. These are future-import / resolver-contract defects; I did not find evidence that the current production data exposes a forbidden hardware action or actual private customer information.

The reported integration suite result is 51/51, attributed to the root integration run. I did not rerun the complete suite. Fresh independent, read-only Node probes reproduced all findings below and checked the current-data behaviors summarized afterward. Existing tests do not cover these cases.

## Important findings

### I1 — Candidate symptom prose bypasses the publication boundary

Location: `error-code-pilot/src/engine.mjs:31–35` (`safePath`), plus `:223–225` for direct canonical multi-reference choices.

`safePath` removes candidate action/part text but copies `path.symptom` verbatim even when the path is candidate, conflicting, superseded or withheld. Consequently an internal candidate description containing a proposed replacement, internal reasoning or private source text reaches the public JSON and path picker. `resolveSymptom` additionally reads canonical path symptoms directly for multi-reference choices, without routing those labels through the public projection.

Fresh reproduction: clone the real `sym-cutting-functional-test` card into a schema-v2 single-card catalog, set its path publication to `candidate`, set its symptom to `PRIVATE-CANDIDATE repair suggestion`. `validateCatalog` returns `[]`; `JSON.stringify(projectAgentCatalog(catalog)).includes('PRIVATE-CANDIDATE')` returns **true**. The candidate is safely converted to escalation, but its unreviewed prose still leaks.

Required fix: preserve stable path identity while using a neutral public label for ineligible paths, or introduce an independently reviewed public label rather than reusing candidate prose. Apply the same policy to canonical `resolveSymptom` choice labels. Add canary regressions covering candidate symptom text in projection, direct resolution and multi-reference selection. This must preserve usable generic PIE navigation and the reviewed 1202 blockage guard.

### I2 — Direct completed-step traversal reuses another path's qualifier confirmation

Location: `error-code-pilot/src/engine.mjs:193–204`.

The `while(completed.includes(path.id))` loop changes from the selected completed path to its next path without clearing `context.qualifierConfirmed`. A true value confirming condition A therefore also authorizes a different condition B. The fix in `recordOutcome` at line 242 protects that interface but leaves the exported shared resolver (and routes delegating to it) vulnerable to stale confirmation when completed history is restored or reused.

Fresh reproduction: in the same valid single-card fixture, make path `software` require `Condition A`; append a reviewed eligible `next` path requiring `Condition B` with `directSelectable:false`; make software's fallback reference next. Call `resolveCard(card, {model:'LUBA 2 5000X', firmware:'1.30.31.10', pathId:'software', completedRepairs:['software'], qualifierConfirmed:true})`. Validation returns `[]`; both canonical and projected calls return **repair** for next instead of `qualifier_required` for Condition B.

Required fix: invalidate qualifier confirmation whenever resolver traversal changes the effective path. Prefer associating a confirmation with its card/path and scope if more general state reuse is supported. Add direct resolver regressions for canonical and projected input, and a symptom-route regression that reenters a completed referenced path. Retain the existing recordOutcome regression.

### I3 — Card-level supersession does not suppress executable checks/information

Location: `error-code-pilot/src/engine.mjs:20–26`, `:61`, and `:178–182`.

Card-level `supersededBy` is checked only when `path.kind === 'repair'`. An approved `check` or `information` path on a CURRENT card whose card-level supersededBy points to newer guidance passes validation, projection and direct resolution. Projection drops card-level supersededBy, so the public resolver cannot recover that signal. Such checks can include executable procedures or a no-repair conclusion and must not silently survive a superseding rule.

Fresh reproduction: clone the real narrow card; set `card.supersededBy='newer-card'`; change its approved path to `kind:'check', part:null`; use matching model/version and qualifier confirmation. `validateCatalog` returns `[]` and `resolveCard` returns **check**. The same obsolete check remains in public projection.

Required fix: consistently gate card-level supersession for executable guidance, or reject inconsistent CURRENT-plus-supersededBy records during validation and ensure direct canonical resolution also fails closed. Add check/information regressions for projection and direct resolution. If retained historical escalation is intended, make that exception explicit and safe rather than applying the repair-only check to everything implicitly.

## Current-data and knowledge assessment

Fresh probes confirmed:

- Canonical validation returns no errors; 21 cards, 26 paths, 28 symptoms, 25 public navigation symptoms.
- Exactly one public repair exists: `sym-cutting-functional-test:software`. Exact model/version and affirmative qualifier are enforced: missing qualifier returns `qualifier_required`; wrong model or firmware returns `scope_required`; matching context returns `repair`.
- 1202 retains its reviewed physical-blockage check; both cable and mainboard paths project as escalation. No hardware unfreeze was found.
- Exact positive 2000303 selects `ec-2000303`; negative -2000303 selects `ec-minus2000303`. Positive fresh-log/PIE handling does not assert a false alarm or no repair; signed shared-power caution remains conditional.
- Approved escalation action arrays for 1008, 5501, 6401, 1500, DT-041 and -2000303 are preserved exactly through direct resolution.

Source review supports the narrow STABLE_OPERATIONAL_GUIDANCE classification: maintained KNOWN_FIXES and TOOL_KNOWLEDGE retain the corrected 1.30.29.19 recommendation, describe similar-case success, and constrain it to 1.30.31.10, normal real mowing and absence of additional motor/driver faults. The classification is based on those retained/repeated signals and correction history, not age or silence alone. No independently verified release applicability, success denominator or complete outcome cohort is claimed.

The full canonical verification loop remains recorded for the promoted repair, including the three tests, reports, Connect Checking screenshot and Burn-in limitation. Historical 1000022 target stays internal/currentness-gated; 6401 remains replacement-history caution rather than generalized replacement advice. Promoted source documents were retained. The absence of the 19 structured Feishu records is documented as missing payload with zero imported records, not filled with invented candidates.

Symptom references and transition references validate against existing identities; the reserved SYM-026/027/028 are excluded from normal projection. Empty reference sets provide intentional PIE coverage and are consistent with the later detailed navigation requirements, even though Task 2's shorthand “no orphan publishable symptom” could be read more narrowly.

The build scan's change from the bare word `evidence` to quoted metadata keys is appropriate for preserving legitimate reviewed action prose. It does not itself validate every public text field; I1 explains the outstanding boundary issue.

## Verification and limits

Independent checks used in-memory clones and stdout only. The three issue reproductions each passed schema validation before exercising the behavior. A separate fresh probe validated real canonical counts, single-repair exposure, 1202 projection, scope/qualifier outcomes, signed-code identity and approved escalation preservation. No complete-suite rerun or UI conclusion is claimed.

After fixes, rerun targeted regressions for I1–I3 and the affected engine/data/projection checks. Full final integration remains the root worker's responsibility.

## Bounded fix re-review — 2026-09-08

Reviewed only `engine-fix-review.diff`, its changes to I1–I3, the new regressions, and the separate approved 1202 `free` escalation. **All three original findings are resolved. No new Critical, Important or Minor finding was identified in this bounded diff. Engine/schema fix review: approved.** This verdict supersedes the initial changes-required verdict for I1–I3; it does not provide UI, packaging or complete-product approval.

- I1: `safePath` now uses neutral text for every ineligible path, and canonical multi-reference symptom choices call `publicPath` before exposing a label. Candidate action and symptom canaries remain absent from projection and resolver output. The approved 1202 `free` path independently retains the useful observable wording; both frozen hardware paths remain nonselectable generic escalation identities.
- I2: every completed-path traversal clears the local qualifier flag. A qualifier can then be confirmed explicitly by selecting the effective next path; it is not inherited from the earlier completed path. Canonical/projected direct traversal and symptom reentry require the next qualifier.
- I3: card-level supersession is now part of `approvedCard`, covering projection, direct canonical resolution, symptom references and Workbench export. Approved checks, information, repairs and escalations on a superseded card cannot execute or be exported.

Fresh independent verification: `node --test --test-name-pattern='direct completed-repair traversal|candidate symptom prose|CURRENT card carrying supersededBy' error-code-pilot/test/desktop-contract.test.mjs` exited 0: **3 tests passed, 0 failed**. A separate in-memory assertion probe verified real-catalog validity; exactly `blocked` and `free` as selectable 1202 branches; retained free-disc observable wording; blocked→check and free→escalate; direct cable/mainboard requests remain escalation with no Upper Shell Adapter Cable prose; and canonical/projected symptom reentry requires Condition B after completing Condition A, while explicit next-path confirmation remains usable. All assertions passed.

The new approved escalation changes the current canonical path count from 26 to **27**; earlier counts in this report describe the pre-fix snapshot. Keep final audit/report counts synchronized. The implementer/root's fresh 54/54 complete-suite result is attributed, not independently rerun here. No UI review, source mutation or commit occurred during this re-review.

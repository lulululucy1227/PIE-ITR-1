# Canonical symptom and repair contract

Schema version 2; legacy schema 1 synthetic tests retain signed-code regression. The standalone app has no MAIN imports or services.

## Publication boundary

Internal `data/canonical.json` includes source references and decisions. `projectAgentCatalog` validates it and emits only explicitly approved visible cards; candidate, pilot, retired, superseded and hidden cards are excluded. Nonpublishable paths become generic PIE routes without candidate action or part prose. Public nested fields are allowlisted. Code 1202 repair actions are hard-frozen regardless of supplied model, approval or scope.

Every v2 path has one of `VERIFIED_RESOLUTION`, `STABLE_OPERATIONAL_GUIDANCE`, `ACTION_PERFORMED_OUTCOME_UNKNOWN`, `SOURCE_RECOMMENDATION`, `CONFLICTING_EVIDENCE`, independently from publication and priority/visibility. A repair additionally requires current confirmed model scope, no conflict/supersession, adequate verification/fallback and reviewed evidence. Stable guidance requires recorded repeated use, active maintenance, adequate scope and no contradiction; age or silence alone is insufficient. Explicitly approved nonrepair safety checks, conditional information and PIE diagnostic guidance can retain weaker source evidence without claiming a verified repair.

`review` contains structured decision flags and rationale. Optional internal history records earliest documented use, last material change, review date, repeated-use/maintenance signals and source authority. These are never exported to the agent page.

## Data

Catalog: `schemaVersion`, `knowledgeVersion`, `cards[]`, `symptoms[]`.

Card: `id`, signed-string `code` (null for symptom-only), `message`, `aliases[]`, classification, lifecycle, publication, agentVisible, scope, evidence, lastReviewed, supersededBy, paths. A missing scope is unknown, never ALL. Exact normalized model and applicable firmware matching are required for scoped executable actions.

Path: `id` (repair_path_id within its card), symptom, kind, part/target area, action, verification.steps plus full verification.canonical, ifNotFixed, directSelectable, evidence_state, publication, agent_visibility, conflict, supersededBy, review and optional qualifier. The qualifier must be affirmatively confirmed and is cleared when model/version or repair step changes. Failure transitions must be acyclic and reference existing paths; a failed prerequisite does not confirm another condition.

Symptom: `symptom_id`, `observable_area`, `label_en`, `label_cn`, aliases, NAVIGATION/PIE_ONLY visibility, `repair_refs[{card_id,repair_path_id}]`. Exactly 28 approved skeleton IDs are loaded in the real data; 25 navigation records are projected across 10 areas. SYM-026/027/028 stay PIE-only and are never direct-repair shortcuts. Empty refs are intentional safe PIE coverage, not invented repair records. Multiple refs require an explicit choice; no symptom implies a particular error code without evidence.

## Interfaces

- `validateCatalog` returns deterministic errors; build aborts before mutating valid output on error.
- `projectAgentCatalog` emits the safe public catalog.
- `searchCards` preserves exact signed codes/messages and returns explicit fuzzy candidates; numeric typos are not silently corrected.
- `searchSymptoms` matches controlled English labels/aliases only; free text cannot synthesize a repair.
- `resolveCard` and `resolveSymptom` share the same canonical path result. Prerequisite states include choose_symptom, choose_path, scope_required and qualifier_required.
- `recordOutcome` requires checks before reported_fixed (`caseClosed:false`); failed or returned actions route to the next validated alternative or PIE.
- `exportWorkbench` is only a pure future read-only contract. Approval, applicability and decisive=false remain distinct. It performs no integration or writes.

The screen retains failure/returned state per card during the current visit across route and model changes. Model context is persistent within the visit; this is not a service-case database. Reload starts a new local visit.

## Two-page interaction boundary — task005

Page1 renders issue/message, controlled symptom, optional qualifier and model/version identification only. It does not read resolved part/action/verification/fallback fields into the identification DOM. Continue resolves the same canonical path again before Page2 displays its approved repair/check/information or safe escalation. Scope-required results never display a speculative repair.

Browser history stores only a per-load session token, page marker and input revision. It contains no model, search, symptom, case or repair data. Selection and per-card failed/returned outcomes stay in memory. Back restores the current identification selection and removes solution content from the DOM; input edits increment the revision so stale forward entries fail safe. Reload/direct solution access starts with empty selection. A new page load cannot reuse a prior qualifier. No router framework, backend, storage or external service was added, and no canonical knowledge decision changed.

## Verification and source updates

Applicable canonical repair validation retains Functional Test, Communication Check, Auto Map Run, all three reports and Connect Checking screenshot. Burn-in is supplemental, never a replacement. Missing verification or fallback fails validation. Operational applicability is reviewed when updating knowledge; prior firmware targets are not timeless recommendations.

As of EC-MT-20260908-KNOWLEDGE-INGEST-004, the supervisor's sanitized payload is available and all19 non-1202 records are imported. REP-1202-001 is a separate frozen record. Prior zero-import statements describe task003 only.

## Private candidate contract

`data/feishu-candidates.json` has schemaVersion1, sanitized source path/hash with productionRead/Write=false, candidates[19], frozen[1], and five reconciliation-only Error Code groups. Every source field is preserved exactly from the supplied Markdown; missing facts remain null/empty. Candidate scope is source wording, never parsed into invented universal compatibility. All19 IDs and the extra frozen ID resolve through private symptom `candidate_refs`, separately from approved `repair_refs`. Signed and unsigned codes remain distinct.

Each candidate's independent `review` records evidence_state, visibility, rationale, source_refs, last_reviewed, promoted_refs, known_conflicts_or_reopens, scope/verification/fallback confirmation, active_maintenance and nullable operational history. Flags describe the full imported path, not supported fragments. No observed operational first-use, repeated-use count or full-path maintenance history was supplied, so those facts are not inferred from repository age. Empty conflicts means no listed conflict in this bounded review, not a complete real-case reopen audit.

Promotion requires VERIFIED_RESOLUTION or STABLE_OPERATIONAL_GUIDANCE plus reviewed scope, verification and fallback, no conflict/supersession, and independently approved canonical action references with matching symptom applicability and private parent linkage. Stable guidance additionally needs affirmative maintenance and repeated-use evidence; an explicit partner solved reply is not required. Weak/private records cannot carry promoted references. CONFLICTING_EVIDENCE must be WITHHELD; frozen1202 can never publish a hardware action. Priority is retained only as source metadata.

`parseCandidatePayload` rejects duplicate IDs/fields and unknown source fields. `validateCandidates` enforces exact19+1 IDs, source/hash parity, required reviews and bidirectional references. Build validates canonical and private data before changing dist, then uses the existing allowlist projection. `candidateCounts` reports record decisions, never repair success rates. The importer, private JSON, metadata, source text and build audit manifest are never runtime assets.

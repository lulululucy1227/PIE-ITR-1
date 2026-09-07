# Canonical knowledge and future Workbench contract

Version: pie.error-code.readonly.v1. Runtime has no MAIN imports or services.

## Three boundaries

1. Raw Source: existing parsed master in MAIN, read-only; never a portal database.
2. Canonical Knowledge: data/canonical.json, internal provenance, currentness, outcome meaning, scope and proposed repair sequence. Every adapted record remains publication=pilot.
3. Agent View: dist/knowledge.json, generated via projectAgentCatalog. Only explicit nested field allowlists are exported. Scope-unknown or non-current replacement text is replaced by concise PIE escalation.

## Minimal schema

Catalog: schemaVersion=1, knowledgeVersion, cards[].

Card: id, signed string code, message, aliases[], classification, lifecycle, publication, agentVisible, scope, evidence, lastReviewed, supersededBy, paths[].

Scope: status (confirmed/unknown/not_required), models[] (exact normalized match), firmware[] (exact allowlist when material). Empty firmware list means no restriction is encoded; it is not proof that every version is safe. Missing model scope is unknown, never all models.

Evidence: kind (promoted_service_rule/promoted_case_outcome/promoted_diagnostic_pattern/raw_reference), refs[], outcome (recommended/resolved/not_resolved/mixed/not_evaluable/informational), cohortCount (known positive integer or null), optional internal notes. Synthetic tests have separate explicit labels and do not enter the catalog.

Path: id, symptom, kind (repair/check/information/escalate), part (required only for repair), action[], verification.steps[], verification.canonical[], ifNotFixed (escalate + message, or path + pathId + message). directSelectable=false protects follow-up-only steps. Failure transitions must exist and form an acyclic graph. Physical blockage is not assumed cleared by clicking Still not fixed.

Publication: pilot / approved / withheld. Lifecycle: CURRENT / HISTORICAL / REVIEW_REQUIRED / SUPERSEDED / RETIRED. Promotion is a separate human knowledge decision; local engineering review never assigns approved. Superseded requires a successor; retired/superseded and hidden cards do not appear in agent search.

## Engine interfaces

- validateCatalog(catalog) -> string[] errors. Build rejects invalid knowledge before changing valid output.
- projectAgentCatalog(catalog) -> agent catalog; explicit allowlist down to scope/fallback fields.
- searchCards(cards, query) -> {kind, matches, autoOpen:false}. Exact signed codes preserve identity including 0. Exact code/message may be opened by the submitting UI. Fuzzy and multi-code input remain candidate lists requiring choice. Unsupported numeric codes are never corrected to a nearby code.
- resolveCard(card, {pathId, model, firmware, completedRepairs, returned}) -> choose_symptom / scope_required / repair / check / information / escalate.
- recordOutcome(card, pathId, choice, context) -> next safe result. choice fixed requires verificationComplete=true and yields reported_fixed with caseClosed=false. not_fixed follows a validated next path or PIE; returned always escalates. UI retains failed IDs and returned state across model/symptom changes until a new search.
- exportWorkbench(catalog, context) -> {contract, knowledgeVersion, readOnly:true, entries}. Only approved, visible, current canonical records are eligible. Each entry retains sourceRefs and applicability; decisive=false even when applicable. Unknown scope cannot yield confident replacement.

Future Workbench code may import the engine and the same canonical file under a separate integration task. Current approved-only export returns zero entries because portal adaptations have not passed the supervisor's publication gate. No Feishu/Nextop write, auth/session access, analyzer model switch or second diagnosis source is implied.

## Verification rules

Canonical repair verification retains Functional Test, Communication Check, Auto Map Run, three reports and Connect Checking screenshot, plus non-ultrasonic FAIL and Burn-in boundaries. The screen shows the concise steps needed for the selected path; a test that cannot run or a remaining relevant fault escalates. NFF stays with PIE. The browser's checkbox is self-reporting, not validation of uploaded reports.

## Update discipline

Edit canonical data, retain source references, distinguish recommended vs resolved, verify scope, run all tests, rebuild, and review the public projection. Do not hand-edit dist. Keep unsupported relationships withheld. Never add raw ticket identifiers or full source rows. Retain a previous local package for rollback; do not reset MAIN or overwrite source history.

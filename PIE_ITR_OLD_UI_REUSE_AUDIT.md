# PIE ITR Old UI / Framework Reuse Audit

**Scope:** read-only comparison of the frozen legacy `ITR工单助手` and the current PIE ITR Workbench V2.  No production source, configuration, credentials, Git state, or legacy files were changed by this audit.

## 1. Executive Summary

**Decision: KEEP CURRENT V2 UI.**

The legacy assistant has useful interaction and visual-design ideas, but is not a reusable UI framework in isolation.  It is a 60 KB single-file page directly shaped around a legacy FastAPI application and a broad orchestration pipeline.  Replacing the current V2 UI would import legacy assumptions about SSE analysis, knowledge-base retrieval, attachments, free-form reply generation, and Feishu preview/commit.

Current V2 is smaller and already preserves the product boundaries that matter: workspace isolation, generation-based stale-response protection, capability guards, structured Analyze contract, local Todo state, and explicit Commit-only writes.  Targeted V2 UX improvements cost materially less and carry much less regression risk than a page replacement.

## 2. Old UI Architecture

The legacy application is a local FastAPI server (`app.py`, 406 lines / about 20 KB) serving one self-contained page (`static/index.html`, 1,138 lines / about 60 KB).  The page contains its own CSS, HTML, and imperative browser JavaScript.  It has no component boundary, state store, typed API contract, or separately testable view modules.

`app.py` imports and coordinates `pipeline`, `nextop`, `itr_fill`, `feishu_sync`, `settings`, optional image processing, and the legacy LLM module.  Its `/api/analyze` endpoint launches the whole legacy pipeline and streams progress/results over Server-Sent Events.  The UI consequently expects the legacy pipeline's combined result schema.

**Coupling classification: TIGHTLY COUPLED.**  The visual page can be opened independently only in a technical sense; its useful panels depend on route-specific legacy result fields and side effects supplied by the legacy backend.

## 3. Old UI Map

| Area | Legacy implementation | Backend dependency |
|---|---|---|
| Sticky header and ticket tabs | Inline page state (`TABS`) and tab renderer | Ticket number, analysis progress, Feishu existence |
| Nextop credential modal | cURL textarea and Save/Validate action | `POST /api/nextop/token` |
| Ticket run/progress | `EventSource` stream with stage messages | `GET /api/analyze` and legacy `pipeline.run()` |
| Review cards | Hero, diagnosis, materials, checklist, fields | Broad legacy analysis schema |
| Attachments/lightbox | Thumbnails, image choice and errors | Local attachment cache and `/api/attachment` |
| Knowledge hits | Expandable note details | Legacy retrieval index and `/api/note` |
| Reply editor/translation | Editable reply and translation view | Legacy reply field and `/api/translate` |
| Paste intake | Modal for pasted Lark/WhatsApp/Email text | `POST /api/paste/preview` |
| Feishu preview/commit | Modal, selected attachments, commit button | `POST /api/feishu/preview`, `/api/feishu/commit` |

The old UI does have thoughtful presentation patterns: tabs with status dots, a modal system, toast feedback, progress messages, attachment review, expandable evidence, and an explicit pre-commit preview.

## 4. API Coupling

Legacy endpoints found in `app.py` are:

| Endpoint | Legacy responsibility | Reusable against V2 as-is? |
|---|---|---|
| `GET /api/analyze` | Runs `pipeline.run`, SSE progress, stores result in `_RUNS` | No |
| `GET /api/attachment`, `GET /api/note` | Reads legacy attachment/cache/vault data | No |
| `POST /api/feishu/preview`, `POST /api/feishu/commit` | Legacy `itr_fill` plan and write workflow | No |
| `GET /api/feishu/exists` | Legacy Feishu lookup | No |
| `POST /api/paste/preview` | Legacy text-plan pipeline | No |
| `POST /api/kb/archive` | Archives into legacy KB | No |
| `POST /api/translate` | Legacy LLM translation route | No |
| `POST /api/nextop/token` | Legacy token parse/persist/validation | No |
| `GET /api/health`, `/api/health/nextop` | Legacy KB/gateway/token status | No |

Current V2 deliberately exposes a narrower boundary: `/api/cases/prepare`, `/api/cases/analyze`, `/api/cases/translate`, `/api/cases/commit`, plus `/api/auth/nextop/status` and `/api/auth/nextop/update`.  V2 returns prepared-case and structured Inspector-contract objects, not legacy pipeline/SSE payloads.

## 5. Current V2 Comparison

| Concern | Current V2 | Legacy UI |
|---|---|---|
| Frontend structure | React/TypeScript workbench with local case state | One large static HTML file with inline imperative code |
| Backend ownership | Thin local adapter → `case_service.py` | `app.py` orchestrates many legacy services |
| Analyze | Structured contract, capability validation, explicit insufficient-information state | Full legacy pipeline result and free reply generation |
| Writes | Only explicit Commit via current service boundary | Preview/commit and KB archive are native page flows |
| Workspace safety | Per-case generation tokens reject stale responses | Legacy tabs have state, but no current V2 generation contract |
| Multi-source foundation | Current normalized intake and golden contracts | Legacy paste preview tied to `itr_fill` |
| Credentials | Current local ignored storage and fail-closed handling | Legacy parser/persistence path |
| Future fit | Can evolve within Phase 1.5 guardrails | Would require schema and boundary reconstruction |

## 6. Direct Reuse Candidates

These are **reference-only candidates**, not direct code-copy candidates:

| Legacy element | Recommended treatment | Why |
|---|---|---|
| Token modal information hierarchy | Recreate visually in current V2 | Matches current manual cURL flow, without old persistence code |
| Toast/progress wording | Adapt interaction language | Useful user feedback, no legacy data dependency |
| Tab status-dot concept | Consider later as a V2-only enhancement | Current workspaces need V2 operation/generation semantics |
| Card spacing, headings, expandable evidence | Use as a visual reference | Can address current density without importing schemas |
| Attachment preview pattern | Defer until a dedicated attachment task | Current V2 has no approved legacy attachment/cache API reuse |
| Pre-commit review emphasis | Preserve current explicit Commit boundary; design may inspire later UI | Legacy write payload must not cross into V2 |

No legacy JS, HTML block, endpoint, pipeline function, configuration, token handler, or Feishu commit implementation should be copied directly.

## 7. Backend Boundary Compatibility

The boundaries are incompatible without a substantial adapter/rewrite.

- Legacy Analyze assumes SSE plus one aggregate payload from `pipeline.run()`.
- V2 splits read-only preparation, structured analysis, translation, and explicit commit into guarded operations.
- Legacy Feishu preview/commit depends on `itr_fill`, legacy attachment selection, and optional KB archive.
- V2 Commit must continue to use `case_service.commit_prepared_nextop_case()` with its stale checks, duplicate protection, locks, Todo semantics, and Feishu-owned fields.
- Legacy reply generation is not constrained by V2's insufficient-information and capability contracts.
- Legacy token handling is not a substitute for current fail-closed authentication handling.

An adapter broad enough to make the old page run would either duplicate business logic or turn V2 endpoints into a compatibility layer for obsolete contracts.  Both violate the existing thin-UI/API rule.

## 8. Workspace / Multi-case

Both products display multiple tickets, but the safety model differs.

Legacy uses a browser-side `TABS` map and status rendering.  Current V2 adds per-workspace operation generations and checks whether a response is still live before applying it.  That is the protection needed when a delayed A result arrives after the operator moved to B.

Porting the old page would require re-implementing V2's prepare/analyze/translate/commit generations, case-local Todo/notes/language state, and close behavior across a large imperative page.  It would not be a simple UI swap.

## 9. Multi-source Future Fit

The old page includes a paste modal for Lark, WhatsApp, and Email.  However, that modal calls legacy `itr_fill.plan_text()` and returns legacy plan data.  It is not compatible with the current pure intake normalization and golden-contract foundation.

Keeping V2 lets future multi-source UI call the current normalized intake boundary.  Reusing the old paste screen would require a dedicated redesign and new contract anyway; it does not reduce the core implementation cost.

## 10. Code Size / Complexity

| Item | Approximate size | Complexity consequence |
|---|---:|---|
| Legacy `app.py` | 406 lines / 20 KB | Routes coordinate pipeline, cache, files, token, Feishu and LLM concerns |
| Legacy `static/index.html` | 1,138 lines / 60 KB | Style, markup, state, event handling and API calls are interleaved |
| Current V2 workbench | Small focused React/TypeScript surface | Existing business logic remains in current Python services |
| Current V2 local API | Narrow route map | Operations correspond to the current contracts |

The raw size of the old page is not a code-saving asset: much of it represents interfaces and state for features that must not be brought into the present V2 boundary.

## 11. Migration Cost

Estimated implementation, testing, and regression cost for a safe replacement is **medium-to-high**:

1. Map every legacy panel to the V2 prepared-case/Inspector schema.
2. Replace SSE pipeline assumptions with separate V2 asynchronous operations.
3. Rebuild workspace generation/stale-response logic.
4. Remove or re-authorize legacy KB, attachment cache, vision, archive and free-reply behaviors.
5. Rewire all write controls to the current explicit Commit boundary.
6. Add contract, workspace, capability, and responsive-layout regression coverage.

The expected saving is low because the transferable parts are primarily visual patterns, while the costly parts are the coupled behavior that cannot move.

## 12. Hybrid Option

The only safe hybrid is **design reference, not component migration**:

- Keep the current V2 workspace shell, local API, and generation guard.
- Selectively recreate a legacy-inspired modal, card hierarchy, tab affordance, or progress display in React.
- Continue to use current V2 payloads and `case_service.py` exclusively.

This is not recommended as a separate migration project now.  It is simply the normal approach for future, scoped V2 UX fixes.

## 13. Risks

- Reintroducing unapproved legacy KB, OCR/vision, attachment, or archive behavior.
- Breaking the strict explicit-Commit-only write boundary.
- Losing V2 Analyze safeguards: LUBA 1 no-log guard, unknown-capability default, insufficient-information reply constraint, and failed-action repetition prevention.
- Breaking multi-case stale-response isolation.
- Bringing legacy credential/config handling into the current project.
- Expanding scope from UX reuse into migration of outdated Nextop/Feishu/business layers.
- Creating a second implementation of core flows, making future audits and tests less reliable.

## 14. Code Savings

| Potential reuse | Realistic saving | Reason |
|---|---:|---|
| Visual tokens and spacing ideas | Small | Must be re-expressed in V2 CSS |
| Modal layout/feedback language | Small | Current V2 has different actions and error contract |
| Ticket-tab appearance | Small-to-medium | State safety must be implemented in V2, not copied |
| Analyze/reply/knowledge/commit panels | None | Payloads and business boundaries are incompatible |
| Legacy backend routes | None | Would regress or duplicate current service ownership |

Overall expected net code saving is **under 20%** of a targeted V2 UX improvement, while replacement creates a materially larger regression surface.

## 15. FINAL UI DECISION

# KEEP CURRENT V2 UI

Do not migrate the legacy assistant page or backend into PIE ITR Workbench.  Retain it as a frozen reference only.  If a future approved UX task needs it, use screenshots/behavioral reference to improve one specific V2 panel while preserving all existing V2 contracts and guards.

## 16. Migration Plan

No migration is approved or necessary.

If a future UI task is explicitly authorized, use this bounded plan instead:

1. Pick one V2 pain point (for example, review-card readability or a token-modal message).
2. Copy only the user-facing design intent, not legacy source.
3. Implement it in current React/CSS against existing V2 payloads.
4. Add/adjust a focused frontend test and retain current workspace/capability tests.
5. Confirm that no new backend endpoint, write path, credential exposure, or legacy dependency was added.

## ChatGPT Handoff

- **Old UI tech:** FastAPI plus one 1,138-line static HTML page with inline CSS and imperative JavaScript; analysis uses SSE.
- **Thin or coupled:** TIGHTLY COUPLED.  UI behavior relies on legacy `pipeline`, `itr_fill`, `nextop`, `feishu_sync`, attachment/cache and KB routes.
- **Top usable references:** token-modal hierarchy, progress/toast feedback, card spacing, tab status affordances, pre-commit review emphasis.
- **What must not move:** `pipeline.py` orchestration, old Nextop/Feishu layers, old token persistence, KB retrieval/archive, attachment/cache/vision plumbing, old free reply generation, and old commit code.
- **Current V2 migration need:** none.  V2 already has safer service ownership, structured Analyze and capability contracts, explicit commit boundary, and generation-based multi-case isolation.
- **Multi-case effect:** legacy tabs do not replace the V2 response-generation safety model; a swap would require reimplementation.
- **Backend compatibility:** incompatible without a broad and undesirable compatibility adapter.
- **Expected savings:** under 20% for targeted UX work; no net saving for a page replacement.
- **Final recommendation:** KEEP CURRENT V2 UI; use legacy only as a visual/interaction reference for future narrowly approved V2 UX work.

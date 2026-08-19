# NextopSync — Current Handoff

## Goal and architecture

- Formal development directory: `C:\\Users\\Reggie\\Desktop\\PIE-ITR-1` on `agent/pie-itr-v2-workbench` (no remote configured).
- Zero-credential baseline is restored and fail-closed: absent Nextop, Feishu, or DeepSeek credentials fail before an external request. Current cleanup baseline is this commit.

- Turn technical communications into structured ITR Cases without bypassing Feishu-owned formulas, lookups, downstream tags, IDs, or Closed automation.
- Current mainline: V2 React Workbench. V1: `gui.py` Tkinter operational fallback; `main.py` CLI fallback.
- Shared backend: `case_service.py` orchestrates existing Nextop, Feishu, analyzer, tag, image, duplicate, lock, Todo, and commit rules.
- V2 preview: React/TypeScript `frontend/` -> local `local_api.py`/`api_adapter.py` -> existing `case_service.py`. V2 does not duplicate business rules and is not the default entry point.

## Key files

- `case_service.py`: service boundary; Nextop `prepare -> commit`, record locks, DTOs, Todo/commit safeguards.
- `analyzer.py`: V2 extraction and Inspector/translation AI contracts.
- `gui.py`: V1 workspaces and Inspector presentation only.
- `api_adapter.py`, `local_api.py`: thin JSON/local HTTP adapter (`health`, `prepare`, `analyze`, `translate`, `commit`).
- `frontend/`: V2 React/Vite workbench; `start_v2.bat` starts local preview pair.
- `test_case_service_d1b.py`, `test_gui_d2a.py`, `test_local_api.py`: current offline regression suite.

## Must not regress

- Search/Load, Analyze, Translate, and LogiQ are non-writing; only explicit Commit may write through existing `case_service.commit_prepared_nextop_case()`.
- Prepared commit must not refetch Nextop or re-run AI; preserve stale checks, duplicate protection, record lock, validation, Todo gate, count refresh, and readback.
- Todo is a user-controlled main-table Checkbox only. Never create separate Todo records or infer a Todo write.
- Workspaces own their state. V1 and V2 tabs must not leak context, analysis, translation, Todo, notes, loading, or errors.
- Keep V1 launchers and backend intact. No credentials in code/logs/handoff; LogiQ remains external-browser-only.

## Current implementation

- V1 D2-D has two-column Case Review, workspace router, compact context, local scroll handling, Chinese-first Inspector, English email reply/copy, and teal LogiQ entry. `CaseEvidenceAttachment` is a future-only DTO; no OCR/vision exists.
- V2 local preview has multi-case tabs, empty New Case, API-backed Search/Analyze/Translate/explicit Commit UI, Todo/notes local state, reply copy, and LogiQ button.
- Phase 1 Closure baseline: successful V2 Search/Load automatically queues context-aware Analyze; failed preparation does not; Re-analyze remains manual. Workspace operation generations discard stale/closed responses. Context Pack is read-only: current Nextop conversation, same-reference Historical ITR, exact Error Code and Technical Information records with record/source provenance. No match is valid (`knowledge_coverage=none`); unreviewed `工单速查_V2` remains excluded as authoritative knowledge.
- Inspector contract now includes `information_status`, `missing_information`, `reason_for_request`, and `next_action`. An insufficient result is normalized to a request-only English reply. A deterministic output guard prevents unsupported LogiQ/device-log requests and plainly repeated failed connector checks. Capability baseline: LUBA 1 has `device_log=unsupported` and `logiq=unsupported`; all unlisted products are `unknown`, never implicitly supported. Only explicit Commit may write.
- V2 UI retains case-local Todo/notes/close state, Review fields, Copy Reply, translation cache behavior, and responsive desktop layout (270px Context column, no body horizontal overflow, internally scrollable Reply). LogiQ UI is enabled only for an explicitly supported capability and otherwise remains unavailable.
- Safe dead-code cleanup removed only `generate_sop.py`, an unreferenced legacy batch-write SOP prototype with no launcher, test, or documentation reference. V1 fallback and all current launch/token utilities remain preserved.
- Phase 1.5A Golden Foundation adds offline synthetic contract coverage, deterministic validator fields, and pure pasted-source normalization. V2 supports a manual Copy-as-cURL Nextop credential update flow with ignored local storage, runtime update, read-only validation, and explicit missing/expired auth errors; fail-closed remains intact. Real Nextop read acceptance passed for `E264714`: token update, Search/Load, ticket fetch, read-only Context, automatic Analyze, and correct-workspace display. No Nextop write, Feishu write, or ITR Commit occurred.
- Old UI reuse audit decision: **KEEP CURRENT V2 UI**. The legacy assistant is reference-only. Reusable concepts are card hierarchy, progress/status feedback, modal hierarchy, ticket status affordance, attachment review pattern, and pre-commit review emphasis. Do not migrate legacy `app.py`, `static/index.html`, pipeline, Nextop/Feishu adapters, KB/archive, or free reply generation.

## Known risks / unverified work

- Git reconciliation is in progress; local source is preserved and the remote baseline is the commit parent. Sensitive local configuration and runtime caches remain ignored.

## Rules

- Current code is factual; do not invent fields, data sources, timestamps, senders, Dealers, device identifiers, or credentials.
- Python owns Case History, V2 facts, and first/second tags. Feishu owns schema/formulas/lookups/third tags/Knowledge ID/Closed.
- Do not add Data Browser, OCR/Vision, LogiQ API/login, Tauri, installer, or another business layer without a separate task.
- Read only task-relevant files; use symbol search and local ranges. Keep this file concise and update it after completed milestones only.

## Tests and next task

```powershell
python -B -m unittest -q test_case_service_d1b.py test_gui_d2a.py test_local_api.py
cd frontend; pnpm run build
```

- Current offline regression: 52 Python tests pass (including 4 Golden, 4 multi-source, and 8 auth tests); 9 frontend state/layout tests pass; V2 production build passes. Real acceptance confirms only the read-only Nextop flow above; no real Nextop/Feishu writes were made.
- Known limitation: automated browser control was unavailable locally, so 1600x900 and 1920x1080 Chrome 100% visual acceptance remains a manual check; CSS/static tests cover its no-overflow, bounded-context, and scrollable-reply contract.
- Next and only task after explicit user direction: Phase 1.5 Golden Regression / governed old-code comparison. Do not start Parts, RAG, Vision, assistant-ui, Data Browser, or any external write work automatically.

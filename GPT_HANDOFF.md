# NextopSync — Current Handoff

## Goal and architecture

- Current development branch: `agent/pie-itr-v2-workbench` (local work reconciled against `origin/agent/initial-pie-itr-workbench`).

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
- V2 acceptance fixes add workspace ID/generation async guards, closed-case response discard, Todo isolation, and LogiQ device-name clipboard behavior. Five lightweight Node tests plus 20 Python offline tests and V2 production build pass. No real ticket/business endpoint or production write was invoked.

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

- Current status: 20 offline tests and V2 production build pass; V2 local browser acceptance is complete with safe mock data.
- Next and only task: V2 Real Read-only Acceptance — waiting for a user-confirmed safe ticket. V1 stays a stable fallback; do not schedule visual-only V1 work.

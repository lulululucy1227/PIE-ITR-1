# NextopSync Development Rules

- Treat current code as the source of truth. Preserve V1 Tkinter as an independent fallback and reuse `case_service.py` for all business operations.
- Keep UI/API layers thin: no duplicated Feishu, Nextop, analyzer, tag, duplicate, lock, or commit logic.
- Only explicit Commit may write ITR. Search/Load, Analyze, Translate, Todo toggles, and LogiQ must not write.
- Preserve prepare-to-commit deduplication, stale/duplicate guards, record locks, Todo semantics, and Feishu-owned fields.
- Keep credentials out of source, logs, tests, and handoff. Do not execute real external writes without explicit user authorization.
- Use workspace-local state and generation/request identity for async UI work; never let one Case overwrite another.
- Do not add deferred systems (Data Browser, OCR/Vision, LogiQ API/login, Tauri) without a dedicated approved task.
- Token discipline: read `GPT_HANDOFF.md` first, then only symbols/files needed for the active task. Prefer `rg` plus local reads. Keep handoff concise; do not add historical logs or copied source.
- Use `apply_patch` for edits. Do not reset, overwrite, or delete user work. Check Git status when available; if no repository exists, report that limitation.

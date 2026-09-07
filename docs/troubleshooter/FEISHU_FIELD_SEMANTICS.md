# PIE Troubleshooter — Feishu Field Semantics

Status: Active clarification
Owner: Troubleshooter｜主管
Date: 2026-09-08

## 信息同步库：`需同步`

`需同步` is an internal collaboration/reminder flag used by PIE to notify colleagues to read or acknowledge a message.

It does **not** mean:
- the technical content is newer than 工单速查;
- the item has not yet been synchronized into KB;
- the item should be promoted into Troubleshooter;
- the existing KB is stale;
- the item represents a superseding technical conclusion.

Therefore `需同步` must be ignored when judging technical currentness, conflict, supersession, KB coverage, or Troubleshooter publishability.

The actual content of 信息同步库 may still be used as technical/service evidence when relevant, but it must be evaluated on its substantive content and corroborating evidence, not on the `需同步` flag.

## General rule

Workflow/status/reminder fields in Feishu are not technical evidence unless their business semantics explicitly say so. Before using any such field for knowledge currentness or diagnostic reasoning, verify what the field means operationally.

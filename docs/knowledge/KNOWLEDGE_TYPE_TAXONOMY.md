# Knowledge Type Taxonomy

Status: Active baseline

## Goal
Knowledge type exists to help PIE/customer support understand a Knowledge Entry at a glance. It is not an ontology and must not become a deep classification system.

Default target: keep the active taxonomy small (about six customer-facing types). Add a new type only when it changes how the knowledge is used, reviewed, searched or maintained.

## Active types

### 1. 维修解决方案
Use only when evidence supports a concrete problem, an action that was actually performed, and an explicit result/resolution.

Do not use when the content is only a recommendation, suspected root cause, next troubleshooting step or diagnostic sequence.

### 2. 诊断与排查
Use for verified diagnostic facts, troubleshooting paths, cross-tests, log-based localization, inspection sequences and PIE-recommended next checks when a final repair result is not established.

This type intentionally combines “diagnostic fact” and “troubleshooting path” to avoid unnecessary fragmentation.

### 3. 料号与兼容性
Use when the core reusable value is a part number, replacement/supply rule, interchangeability/compatibility, discontinuation or component-ordering rule.

### 4. 软件与工具
Use for Mammotion Kit, ToolSuite/MammoSuite, flashing, upgrade, tool behavior, software operation and tool-version handling.

### 5. 产品与版本
Use for product capability/limitation, firmware/version-specific behavior, historical version facts, service/account behavior and similar facts whose main meaning is product/version status rather than a repair action.

Historical/current status is lifecycle metadata, not a separate Knowledge Type.

### 6. 部件与结构
Use when the core fact is hardware/component identity, structure, location, integrated assembly relationship or visual identification, and the value is not primarily a part-number/compatibility rule.

## Classification principles

- Classify by the entry's primary reusable value, not by every fact it contains.
- One entry should normally have one type.
- Topic ID / fault category / fault module remain separate classification dimensions and should not be duplicated inside Knowledge Type.
- Image requirement is not a Knowledge Type.
- “Single case”, “historical version”, “pending evidence” and “superseded” are not Knowledge Types; they belong to evidence/lifecycle/status.
- Avoid a broad “Other” type when an entry clearly fits one of the six types. If repeated valid knowledge does not fit, report the gap before adding a seventh type.

## Migration guidance

Existing records should be reclassified without changing their factual content:
- old 维修解决方案 -> keep only if repair gate is met; otherwise 诊断与排查;
- 诊断事实 / 排查路径 -> 诊断与排查;
- 料号/兼容性 -> 料号与兼容性;
- 软件/工具操作 -> 软件与工具;
- 产品能力 / version facts / service behavior -> 产品与版本;
- structure/component-identification facts -> 部件与结构.

The taxonomy is deliberately shallow so a support agent can understand it immediately and so filters remain usable as the KB grows.
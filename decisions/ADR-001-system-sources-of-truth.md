# ADR-001: Separate business facts, knowledge, and system rules

Status: Accepted
Date: 2026-08-23

## Decision

PIE ITR 系统使用不同的 Source of Truth，而不是让一个工具承担全部职责。

- Feishu ITR = Business Fact Source of Truth
- 工单速查 / KB = Derived Curated Knowledge Store
- GitHub `PIE-ITR-1` = System Rules & Architecture Source of Truth
- Workbench = Application Layer / user work surface

## Rationale

ITR 持续变化并包含原始业务 Evidence；Knowledge 需要筛选、治理和生命周期；架构规则需要版本控制和审计。将三者混在同一数据层会造成覆盖历史、规则漂移和难以追溯。

## Consequences

- Knowledge 流程默认不修改 ITR。
- GitHub 不存储真实 ITR 全量数据。
- 正式规则发生变化时应更新本仓库，而不是只留在聊天或临时 Prompt 中。
- Workbench 可以消费多个知识/事实源，但不因此成为它们的 Source of Truth。
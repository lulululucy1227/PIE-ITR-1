# Knowledge Lifecycle

Status: Draft baseline — lifecycle automation is not yet authorized

## Problem

ITR 持续新增和变化，而部分 Knowledge 与固件、工具版本、备件状态或产品策略相关。Knowledge 在创建时正确，不代表以后仍然 Current。

因此需要生命周期管理，但不应把“自动同步”误解成“自动覆盖正式知识”。

## Recommended lifecycle model

当前先使用语义层面的状态：

- CURRENT — 当前 Evidence 支持，允许日常使用。
- HISTORICAL — 曾经有效，但因版本/产品状态变化不再作为当前默认答案；仍保留历史追溯价值。
- SUPERSEDED — 已被新的 Knowledge/结论明确替代，应关联替代项。
- RETIRED — 不再适合日常检索/使用，且没有必要作为当前知识展示。
- REVIEW_REQUIRED — 新 Evidence 可能影响该 Knowledge，需要 PIE 判断。

这些名称是治理基线，不代表必须立即修改飞书现有选项；正式 Schema 变更需单独评估。

## Version change

例如旧 Mammotion KIT 版本存在问题，PIE 当时告知后续版本计划修复：

1. 原 Knowledge 可以在当时保持 CURRENT，但结论必须准确表达“计划修复”，不能声称已经修复。
2. 后续 ITR/正式 Evidence 明确显示问题已修复时，系统应生成 POSSIBLE_SUPERSEDED / REVIEW_REQUIRED 信号。
3. PIE 确认后，旧 Knowledge 转为 HISTORICAL 或 SUPERSEDED，并创建/关联当前结论。
4. 不建议简单删除旧 Knowledge，因为旧版本设备/工具仍可能需要历史信息。

## Correction vs supersession

- 原知识当时就是错误的：Correction，需要保留审计痕迹并修正错误。
- 原知识当时正确、后来环境变化：Supersession/Historical transition，不应把旧知识描述成“原来错误”。

## Automation boundary

ITR 可以持续扫描，但正式 Knowledge 不需要每次 ITR 变化就自动重写。

推荐机制：

```text
ITR new/change
    -> detect relationship
    -> NEW / REINFORCEMENT / CONFLICT / POSSIBLE_SUPERSEDED / NO_ACTION
    -> candidate/review queue
    -> PIE human decision
    -> Knowledge lifecycle change
```

AI 可以提出“可能已过期”，但在 Evidence 和规则尚未达到高置信度前，不应自动把 CURRENT 改成 HISTORICAL/SUPERSEDED。
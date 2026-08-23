# Knowledge Governance

Status: Active baseline

## Purpose

工单速查是面向 PIE 技术客服使用的 Curated Knowledge Base，不是 ITR 全量镜像，也不是自动摘要表。

每条 Knowledge 应尽可能帮助 PIE 快速回答四类问题：

1. 这个问题目前已知什么？
2. 分析这个问题还需要客户提供什么信息？
3. 当前 Evidence 支持的处理/诊断方法是什么？
4. 可以如何追问或回复客户？

## Core rules

### Evidence first
任何事实性结论必须能追溯到允许的 Evidence。Legacy Solutions、历史回复模板等字段不能因为“看起来合理”就自动升级为已确认事实。

### Human gate
AI/智能体可以生成候选、分类、摘要和变更建议，但正式发布和关键生命周期变更必须保留 PIE 人工 Gate。

### Reusable, not merely true
一条 ITR 中真实发生过的内容，不等于值得成为独立 Knowledge。Knowledge 应具有合理的重复使用价值。

### Preserve scope
单案例诊断不能自动推广成所有同机型/同故障的标准方案。必要时明确标注“单案例”“适用范围待确认”等边界。

### Currentness is explicit
Knowledge 必须能够表达当前有效性。版本相关知识不能因为创建时正确就永久保持“当前有效”。具体生命周期见 `KNOWLEDGE_LIFECYCLE.md`。

### Do not silently rewrite history
当新 Evidence 改变现状时，优先保留可追溯历史关系，而不是无审计地覆盖旧事实。

## Knowledge content expectations

根据知识类型按需包含：

- 知识标题
- Topic / 故障类别与模块
- 适用机型
- 已知结论
- 处理/诊断方法
- 分析所需信息
- 客户追问/回复模板
- 来源 ITR / Evidence
- 图片或图片事实描述（如必要）
- Knowledge 状态与审核状态
- 版本/适用范围边界

并非所有字段都必须机械填满。没有 Evidence 的内容应留空或明确待确认，而不是补全推测。

## Current operating mode

当前 Knowledge 批量沉淀仍处于规则验证阶段：GPT 负责规则与审查，飞书智能体执行数据操作，PIE 人工审核。

在 Evidence Gate、candidate classification、lifecycle 等规则稳定前，不将整套流程过早固化为复杂自动化。
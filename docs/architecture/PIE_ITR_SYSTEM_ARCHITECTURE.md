# PIE ITR System Architecture

Status: Active baseline

## 1. System layers

### ITR Layer — factual case record
ITR 记录实际发生的代理问题、PIE 处理、Case History、附件及相关业务字段。ITR 是业务事实 Source of Truth。

知识治理流程默认只读 ITR；除非存在独立、明确授权，不得为了知识沉淀反向修改 ITR。

### Knowledge Layer — curated reusable knowledge
工单速查不是 ITR 副本。它只承载经过 Evidence Gate、结构化整理和 PIE 人工审核后具有复用价值的知识。

它应回答：当前面对某类问题，已有 Evidence 支持的已知结论是什么、需要哪些信息、如何诊断/处理、如何向客户回复，以及知识当前是否仍适用。

### Application Layer — PIE ITR Workbench
Workbench 是 PIE 日常处理 Case 的工作入口，而不是 Knowledge Store。

它可以组合 ITR 当前 Case context 与多个知识源，例如工单速查、Error Code、标签体系、SBOM/备件信息、产品能力规则等，再生成分析、缺失信息、追问建议、处理建议与回复草稿。

### Knowledge Maintenance — background capability
负责发现 ITR 新增/变化与既有 Knowledge 之间的关系，形成候选，而不是无条件自动改写正式知识。

当前处于 GPT + 飞书智能体 + PIE 人工审核的规则验证阶段。规则稳定、重复成本明显后，再评估由 Codex 工程化为 Workbench/PIE ITR 系统的后台模块。

## 2. Responsibilities

### GPT
- 业务与知识规则设计
- 架构判断
- Evidence/Lifecycle 规则维护
- 飞书智能体任务设计与结果审查
- Codex 阶段定义和验收

### Feishu agent
- 在授权范围内读取飞书 ITR、标签、附件和 KB 数据
- 根据明确任务生成/更新 Knowledge candidate 或 Knowledge 数据
- 输出审计报告
- 不作为长期唯一规则存储位置

### Codex
- Workbench 软件工程实现
- 稳定规则的自动化/工程化
- 测试、集成、回归、Git 状态维护

### PIE human
- 对知识正确性和可复用性作最终判断
- 决定发布、退回、历史化等关键状态

## 3. Operational principle

Prompt-first, code-after-stability：

1. GPT + 飞书智能体低成本验证规则。
2. PIE 人工审核暴露错误与边界。
3. GPT 修正规则并记录到 GitHub。
4. 规则稳定且需要重复运行后，Codex 再工程化。

避免同时在 Workbench、飞书 Prompt 和独立脚本中形成三套不同知识规则。

## 4. Long-term direction

Workbench 可以成为统一用户入口，但后台数据资产继续解耦。飞书可以继续作为 ITR 与正式 Knowledge 的承载层；未来 Knowledge Maintenance Engine 即使工程化，也不意味着必须迁移飞书数据或重新建设第二套知识平台。
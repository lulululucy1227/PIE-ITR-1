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

### Case-to-knowledge abstraction
维修/诊断类 Knowledge 的目标不是记录“这个案例最后坏了什么”，而是尽可能提炼“下一个类似案例应该如何判断”。优先组织为：症状 → 判断条件 → 排查/交叉验证路径 → 确认故障对象 → 处理动作 → 结果验证。

具体案例中的最终坏件应作为 Evidence/案例结果保留，不得自动成为同类症状的固定 Root Cause。

### Symptom/decision-path first
对于维修和诊断类知识，标题和主体应优先围绕客服可观察到的症状与决策路径，而不是围绕某个历史案例的最终坏件。料号、兼容性、明确的软件工具规则、版本事实和正式流程政策可以保持事实型表达。

### No invented reusable path
“知识复用”不等于把单案例补写成完整 SOP。任何被提炼出的通用排查节点、顺序、分支和替代根因，都必须有 Evidence 支持。

- 一个案例中没有执行/讨论过的检查项，不得为了让路径更完整而加入。
- 一个案例只证明了某一条路径时，只能作为该路径的参考，不能自动扩展成所有可能根因清单。
- 如果要从多个 ITR 组合成更通用的诊断路径，必须明确引用/核对多个独立 Evidence，再形成聚合 Knowledge。
- 若当前 Evidence 只能支持“该案例的验证方法”，应保留窄范围，而不是虚构通用 troubleshooting tree。

### Generalization level
可复用性需要控制抽象层级：

1. **Case result**：该案例最终是什么问题。
2. **Reusable validation method**：该案例中哪些验证动作可以用于同类问题。
3. **General diagnostic path**：只有多案例或更强 Evidence 支持时，才可提升为更通用的排查路径。

AI/智能体不得直接从第 1 层跳到第 3 层。

### Level 3 aggregation must be node-level evidence covered
“有 2 条以上 ITR”只是 Level 3 的必要条件之一，不代表可以把多个案例中的不同步骤自动串成一条完整 SOP。

形成 Level 3 General Diagnostic Path 时，必须对每个诊断节点逐项建立 Evidence 映射：

- 每一个检查项、测量项、Cross-test、分支判断和处理节点，都必须明确由哪一条或哪几条独立 Evidence 支持；
- 多个 ITR 只共同支持其中一部分路径时，只能聚合那一部分，不得把各案例中零散出现的节点拼成一条看似完整的统一流程；
- 节点之间的先后顺序本身也需要 Evidence 支持，不能仅因为工程上“看起来合理”就排序；
- 跨机型聚合时，必须确认该诊断节点确实可跨这些机型复用，否则应保持机型限定或拆分 Knowledge；
- 无法做到 node-level evidence coverage 时，降级为多个 Level 2 Knowledge，而不是强行保留 Level 3。

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
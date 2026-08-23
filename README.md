# PIE ITR

PIE Technical Support Intelligence System 的规则、架构与治理仓库。

## Repository role

本仓库是 PIE ITR **系统规则与架构的 Source of Truth**，不是业务数据仓库。

- 飞书 ITR：业务事实 Source of Truth（case、PIE reply、Case History、附件等）。
- 工单速查 / Knowledge Base：经过 Evidence Gate 与人工审核形成的 Derived Knowledge Store。
- PIE ITR Workbench：PIE 日常处理工单的 Application Layer。
- 本 GitHub 仓库：系统规则、架构决策、知识治理规则、接口契约与阶段状态。

## Core architecture

```text
Nextop / WhatsApp / Lark / Email
              |
              v
          Feishu ITR
      (Source of Truth)
              |
      Evidence / Candidate
              v
   Knowledge Maintenance
              |
       Human Review Gate
              v
       工单速查 / KB
              |
       Retrieval / Context
              v
      PIE ITR Workbench
```

## Tool responsibilities

- GPT：业务规则设计、知识治理、架构判断、审查、Codex 阶段定义与验收。
- 飞书智能体：读取 ITR/附件/表结构，并按明确指令执行飞书侧轻量数据操作；当前用于知识沉淀试运行。
- Codex：实现已经明确并稳定的软件工程规则，包括 Workbench、测试、集成以及未来可能工程化的 Knowledge Maintenance 模块。
- PIE 人工审核：Knowledge 发布与关键知识生命周期变更的最终 Gate。

原则：**规则仍在讨论时优先用 GPT 验证；规则稳定且需要重复执行时再由 Codex 工程化。**

## Documentation

- `docs/architecture/PIE_ITR_SYSTEM_ARCHITECTURE.md` — 系统边界与组件关系
- `docs/knowledge/KNOWLEDGE_GOVERNANCE.md` — 工单速查治理总则
- `docs/knowledge/EVIDENCE_POLICY.md` — Evidence 使用规则
- `docs/knowledge/KNOWLEDGE_LIFECYCLE.md` — Knowledge 生命周期与版本变化
- `docs/knowledge/CANDIDATE_CLASSIFICATION.md` — 新 ITR 与现有知识的关系分类
- `docs/knowledge/IMAGE_EVIDENCE_POLICY.md` — 图片/附件 Evidence 原则
- `decisions/` — 重要架构决策记录（ADR）

## Data and security boundary

本仓库当前为 public。禁止提交真实客户/代理身份信息、邮箱、电话、原始 Case History、飞书附件、API key/token、公司内部凭据以及未经确认可公开的内部业务资料、SOP、固件信息或完整 ITR 数据。

文档中的案例必须抽象或脱敏。
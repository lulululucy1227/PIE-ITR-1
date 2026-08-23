# ADR-002: Prompt-first, code-after-stability for Knowledge Maintenance

Status: Accepted
Date: 2026-08-23

## Decision

Knowledge Maintenance 当前不单独建立新的 Codex 软件项目。

规则验证阶段继续使用：

GPT -> 飞书智能体 -> PIE 人工审核

当规则稳定、重复执行成本明显，并且工程边界明确后，再由 Codex 将稳定部分实现为 PIE ITR / Workbench 架构下的 Knowledge Maintenance 模块。

## Rationale

当前主要不确定性来自业务语义，而非代码：Evidence 强度、单案例边界、Knowledge 拆分、版本历史化、Conflict/Reinforcement 等规则仍会随人工审核修正。过早编码会固化错误规则并增加返工。

## Constraint

未来工程化时避免形成三套独立逻辑：Workbench 代码规则、飞书 Prompt 规则、独立 Knowledge 脚本规则必须共享同一治理定义。
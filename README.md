# PIE ITR

PIE Technical Support Intelligence System 的规则、架构、知识治理与项目状态仓库。

## Source-of-truth map

- **Nextop / Feishu ITR / Case History** — 完整真实工单、设备、代理、聊天、维修历史与业务事实的 Source of Truth。
- **工单速查 / Knowledge Base** — 经 Evidence Gate 与人工审核形成的正式业务知识。
- **PIE ITR Workbench** — PIE 日常技术客服工作入口。
- **本 GitHub 仓库** — 系统规则、诊断知识、维修策略、回归规则、架构与项目交接状态；不是第二套工单数据库。

Canonical repository: `lulululucy1227/PIE-ITR-1`.
如果任何任务准备写入其他仓库，先停止并确认。

## Current operating structure

- `GPT_HANDOFF.md` — 精炼项目入口，只保存当前阶段、关键边界、权威来源、优先级和下一步门槛。
- Issue #1 — **Learning Candidate intake**：收集从真实案例中提炼出的新知识、规则修正、冲突、回归发现和 Workbench 缺陷；不保存完整案例历史。
- Issue #2 — 诊断架构变更的讨论与索引；正式架构以文件为准。
- `docs/knowledge/` — 已晋升的可复用知识与知识治理规则。
- `docs/regression/REAL_CASE_REGRESSION.md` — 代表性回归条件与断言，不以完整工单镜像为目标。
- `docs/architecture/` — 当前系统与诊断架构基线。
- `docs/workbench/` — Workbench 关键契约。
- `governance/` / `decisions/` — 稳定治理规则与 ADR。

## Knowledge flow

```text
Daily case
   |
   v
Use ticket/context to read the full case from Nextop / ITR when needed
   |
   v
Diagnose current case
   |
   v
Learning detection
   |
   +--> no reusable learning: no GitHub write
   |
   +--> reusable learning / correction / conflict / regression value
                |
                v
        Issue #1 Learning Candidate
                |
                +--> stable diagnostic/service rule --> docs/knowledge/
                +--> regression assertion --> docs/regression/
                +--> workflow/system rule --> docs/workbench/ / governance/ / architecture/
```

## What GitHub should retain

优先保存能够让未来案例“举一反三”的信息：
- 产品/机型范围；
- 故障现象、错误码、部件或功能路径；
- 关键前置条件；
- 已验证的 decisive evidence；
- known-good cross-validation 或其他有效验证方法；
- repair-vs-replace / next-action 策略；
- 适用范围、版本边界和 guardrail；
- PIE 权限/路由边界；
- 可复用的回复原则或 regression assertion；
- 用户明确确认的修正。

## What GitHub normally does not need

以下内容通常不需要长期存入 GitHub，因为完整上下文可从 Nextop / ITR 重新读取，而且它们本身不能提高同类问题的诊断能力：
- 设备名称 / device identifier；
- 工单号 / CaseID / work-order reference；
- 代理个人姓名；
- 代理公司名称（除非其能力/权限本身构成规则条件）；
- 完整原始邮件/聊天；
- 完整已发送回复（除非精确措辞本身就是需要验证的 Reply Regression 对象）。

不要为了“以后判断是不是同一台设备又回来”在 GitHub 建立设备级历史；当前案例需要历史时，应根据当前工单在 Nextop / ITR 重新读取完整上下文。

## Daily-case GitHub write gate

每个 Daily Case 都应检查是否产生可沉淀知识，但不意味着每个案例都需要 GitHub 写入。

使用：`NEW / REINFORCEMENT / CONFLICT / POSSIBLE_SUPERSEDED / DUPLICATE / INSUFFICIENT / NO_ACTION`。

- `NO_ACTION` / `DUPLICATE` -> 不写新的知识项。
- `REINFORCEMENT` -> 仅当它显著增强 Evidence、Scope、置信度或回归覆盖时更新现有知识/候选。
- `NEW` / `CONFLICT` / `POSSIBLE_SUPERSEDED` -> 形成最小但足够的 Learning Candidate。
- `INSUFFICIENT` -> 不强行沉淀规则；继续在当前工单中补证据。

单案例不能直接升级成宽泛通用 SOP；知识晋升必须保留适用范围与 Evidence。

## Core operating principles

- PIE 负责远程诊断、技术判断、指导和建议；代理/服务人员执行现场维修、换件、插拔和测量。
- `already replaced` 不等于 `ruled out`；Known-good cross-test 和实际行为变化通常证据更强。
- Evidence routing 必须结合问题类型、当前设备位置、执行者能力和聊天上下文；不要所有问题都要求日志。
- `cannot reproduce` 不等于故障已排除，也不自动等于 NFF。
- 内部分析可以充分；对代理回复遵循 **minimum sufficient response**。
- 当前案例事实与长期知识分层：当前工单用于解决问题，GitHub 用于沉淀以后可复用的方法。

## Security boundary

禁止提交 API key / token / 密码 / 下载口令等凭据。
如果用户明确说某项信息不要记录/不要上传，则必须排除。

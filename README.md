# PIE ITR

PIE Technical Support Intelligence System 的规则、架构、知识治理与项目状态仓库。

## Source-of-truth map

- **Feishu ITR** — 业务事实 Source of Truth。
- **工单速查 / Knowledge Base** — 经 Evidence Gate 与人工审核形成的正式业务知识。
- **PIE ITR Workbench** — PIE 日常技术客服工作入口。
- **本 GitHub 仓库** — 系统规则、架构、候选知识、回归案例与项目交接状态。

Canonical repository: `lulululucy1227/PIE-ITR-1`.
如果任何任务准备写入其他仓库，先停止并确认。

## Current operating structure

- `GPT_HANDOFF.md` — 精炼项目入口，只保存当前阶段、关键边界、权威来源、优先级和下一步门槛。
- Issue #1 — 每日真实案例 / Workbench 缺陷 / 新观察的 intake inbox。
- Issue #2 — 诊断架构变更的讨论与索引；正式架构以文件为准。
- `docs/knowledge/` — 已晋升的可复用知识与知识治理规则。
- `docs/regression/REAL_CASE_REGRESSION.md` — 代表性真实案例回归集。
- `docs/architecture/DIAGNOSTIC_ARCHITECTURE.md` — 当前诊断架构基线。
- `docs/architecture/PIE_ITR_SYSTEM_ARCHITECTURE.md` — 系统层级与组件边界。
- `docs/workbench/` — Workbench 关键契约。
- `governance/` / `decisions/` — 稳定治理规则与 ADR。

## Knowledge flow

```text
Daily real case / defect
        |
        v
Issue #1 intake
        |
        +--> case-specific / pending validation stays here
        |
        +--> stable reusable rule --> docs/knowledge/
        |
        +--> representative case --> docs/regression/
        |
        +--> system-level stable change --> docs/architecture/
```

不要把 Issue #1 当长期知识库，也不要把完整知识堆进 `GPT_HANDOFF.md`。

## Core operating principles

- PIE 负责远程诊断、技术判断、指导和建议；代理/服务人员执行现场维修、换件、插拔和测量。
- `already replaced` 不等于 `ruled out`；Known-good cross-test 和实际行为变化通常证据更强。
- Evidence routing 必须结合问题类型、当前设备位置、执行者能力和聊天上下文；不要所有问题都要求日志。
- `cannot reproduce` 不等于故障已排除，也不自动等于 NFF。
- 内部分析可以充分；对代理回复遵循 **minimum sufficient response**。
- 单案例不能直接升级成通用 SOP；知识晋升必须保留适用范围与 Evidence。

## Security boundary

本仓库当前为 **public**。

禁止提交：
- API key / token / 密码 / 下载口令等凭据；
- 客户或代理个人身份信息、邮箱、电话；
- 原始完整 Case History、附件或未经脱敏的聊天记录；
- 未确认可公开的内部敏感业务资料。

真实案例用于规则/回归时应尽量只保留必要技术事实并脱敏。若后续需要长期保存更完整的内部案例证据，应优先将仓库调整为 private，而不是放宽 public 仓库的安全边界。

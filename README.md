# PIE ITR

PIE Technical Support Intelligence System 的规则、架构、知识治理与项目状态仓库。

## Source-of-truth map

- **Feishu ITR** — 业务事实 Source of Truth。
- **工单速查 / Knowledge Base** — 经 Evidence Gate 与人工审核形成的正式业务知识。
- **PIE ITR Workbench** — PIE 日常技术客服工作入口。
- **本 GitHub 仓库** — 系统规则、架构、候选知识、回归案例、必要的案例追溯信息与项目交接状态。

Canonical repository: `lulululucy1227/PIE-ITR-1`.
如果任何任务准备写入其他仓库，先停止并确认。

## Current operating structure

- `GPT_HANDOFF.md` — 精炼项目入口，只保存当前阶段、关键边界、权威来源、优先级和下一步门槛。
- Issue #1 — 每日真实案例 / Workbench 缺陷 / 新观察的 **learning intake inbox**；不是要求机械复制所有工单的原始数据库。
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
Feishu ITR / Case History (business-fact Source of Truth)
        |
        v
Learning detection + provenance/value check
        |
        +--> no durable learning value: no new knowledge artifact required
        |
        +--> useful learning / traceability / regression value -> Issue #1
                    |
                    +--> stable reusable rule --> docs/knowledge/
                    |
                    +--> representative case --> docs/regression/
                    |
                    +--> system-level stable change --> docs/architecture/ / docs/workbench/ / governance/
```

不要把 Issue #1 当成无差别的工单复制区，也不要把完整知识堆进 `GPT_HANDOFF.md`。

## Daily-case GitHub write gate

每个 Daily Case 默认都要检查是否产生新的知识、证据强化、冲突、回归价值或回复规则。
可继续使用 `NEW / REINFORCEMENT / CONFLICT / POSSIBLE_SUPERSEDED / DUPLICATE / INSUFFICIENT / NO_ACTION` 做分类，但分类的作用是决定“如何沉淀”，不是为了自动删除案例信息。

Default behavior:
- `NO_ACTION` / `DUPLICATE` -> 通常不新增知识条目。
- `REINFORCEMENT` -> 若该案例显著增强 Evidence、Scope、模型适用性或回归价值，可以保留案例引用/关键证据。
- `NEW` / `CONFLICT` / `POSSIBLE_SUPERSEDED` -> 应形成可审核的 Learning Candidate。
- 单案例不能直接升级成宽泛通用 SOP；需要保留适用范围与 Evidence。
- Issue #1 comment 不是最终正式规则；确认后的稳定规则应晋升到对应 tracked file。

## Case information value

以下信息不能因为“仓库是 public”就默认删除；是否保留应看它是否帮助后续追溯、比较、回归、诊断或回复学习：
- 设备名 / device identifier：用于同一设备跨多次返修、重复故障、前后日志/维修历史串联。
- 工单号 / CaseID / work-order reference：用于把 GitHub 学习和原始业务工单重新对应起来。
- 代理姓名 / 公司：技术泛化价值通常低于设备和工单号，但可帮助维持同一代理的上下文连续性、工具能力和沟通历史。
- 完整实际回复：当我们要学习“什么回复真的被 PIE 使用”“什么措辞过长/过弱/越权”时，价值很高，可作为 Reply Regression Evidence。
- 原始问题/关键对话：当上下文顺序本身决定正确答案时，有较高价值。

默认规则：用户没有明确说“不记录/不要上传”的信息，应先判断其知识与追溯价值，而不是自动脱敏或删除。

## Core operating principles

- PIE 负责远程诊断、技术判断、指导和建议；代理/服务人员执行现场维修、换件、插拔和测量。
- `already replaced` 不等于 `ruled out`；Known-good cross-test 和实际行为变化通常证据更强。
- Evidence routing 必须结合问题类型、当前设备位置、执行者能力和聊天上下文；不要所有问题都要求日志。
- `cannot reproduce` 不等于故障已排除，也不自动等于 NFF。
- 内部分析可以充分；对代理回复遵循 **minimum sufficient response**。
- 单案例不能直接升级成通用 SOP；知识晋升必须保留适用范围与 Evidence。

## Security boundary

无论仓库可见性如何，禁止提交 API key / token / 密码 / 下载口令等凭据。

对于用户提供的案例信息：
- 若用户明确说 `不要记录` / `不用上传` / `这个信息不需要沉淀`，则不进入 GitHub。
- 若用户没有排除，默认可用于案例追溯、Learning Candidate、Regression 或规则沉淀。
- 不要仅因为设备名、工单号、代理姓名、公司或完整回复具有识别性就自动删除。
- 仍应避免无价值的噪音堆积：保留的信息应该能帮助诊断、复盘、查找、回归或规则形成。

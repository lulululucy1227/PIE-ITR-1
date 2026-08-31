# Knowledge Candidate Classification

Status: Draft baseline

当新增或变化的 ITR 与现有 Knowledge 比较时，不应只有“新增/不新增”两个结果。

分类决定的是“这个案例产生了什么学习价值、应该如何晋升”，不是“是否要自动删除案例信息”。

## NEW
存在可复用的新事实/诊断/处理知识，且没有等价现有 Knowledge。

动作：形成新 Knowledge candidate，经过 Evidence Gate 和人工审核后再发布。保留足够的案例追溯信息和 Evidence，使后续可以理解该规则为什么成立。

## REINFORCEMENT
与现有 Knowledge 核心结论一致，但提供新的独立 Evidence、机型/版本实例、PIE 真实回复或其他增强信息。

动作：默认不重复创建同主题 Knowledge；评估是否增强 Evidence、适用范围或置信度。

对于 Daily Case -> GitHub：`REINFORCEMENT` 不需要复制一个相同的新规则，但如果新的设备实例、工单结果、实际回复、回归结果或重复故障对置信度、适用范围、回归覆盖或生命周期判断有实质价值，可以保留案例引用和关键 Evidence。

## CONFLICT
新 Evidence 与当前 Knowledge 的事实性结论存在实质冲突。

动作：不得自动覆盖。进入人工 review，检查版本、机型、上下文、Evidence 强度和是否存在原知识错误。应保留足够的新旧案例来源信息，避免失去冲突的可追溯性。

## POSSIBLE_SUPERSEDED
旧 Knowledge 在当时可能正确，但新版本、固件、工具、备件或产品政策变化表明它可能不再是当前答案。

动作：进入 lifecycle review；AI 不直接历史化正式 Knowledge。保留版本、案例和原规则来源，便于确认什么时候发生变化。

## DUPLICATE
新 ITR 没有带来足够新的知识价值，与现有 Knowledge 实质等价。

动作：通常不新建规则；必要时可以作为额外来源 Evidence、重复出现次数或案例追溯记录。是否保留取决于它是否对后续统计、复发判断或回归有价值。

## INSUFFICIENT
Evidence 不足以形成可靠、可复用 Knowledge。

动作：不自动补全；可以进入待评估队列。若后续结果可能改变判断，可以保留案例/Evidence 作为未完成学习，而不是强行形成规则。

## NO_ACTION
即使 ITR 内容真实，也没有形成/改变 Knowledge 的必要。

动作：通常不创建新的知识条目。如果案例本身没有追溯、回归或复发价值，也无需额外写 GitHub。

## Daily-case GitHub retention rule
Candidate classification is the learning/promotion gate for Issue #1, but it is **not an automatic anonymization gate**.

- Feishu ITR / Case History remains the business-fact Source of Truth.
- Issue #1 retains case-derived learning, supporting Evidence and useful provenance when they help future diagnosis/review.
- Device name, work-order/CaseID/ticket reference, agent/partner name/company, relevant partner wording and exact accepted/sent PIE reply may be retained when they provide traceability, recurrence, regression, conversation-continuity or reply-learning value.
- Do not strip those fields only because they are identifiable or because the repository is public.
- If the user explicitly says `不要记录` / `不用上传` / `这个信息不需要沉淀`, that explicit exclusion overrides retention.
- Credentials/secrets are never retained.
- An explicit PIE correction can justify `NEW` Workbench/System behavior even from one case; once confirmed, the stable rule should be promoted to the relevant tracked rule file, while the source case may remain as provenance/regression evidence if useful.

## Matching rule

Candidate matching must compare the independent fact itself, not only Topic ID or fault taxonomy.

At minimum consider model, part/component, error code, version, knowledge title/conclusion, compatibility/supply fact, and the underlying evidence meaning when relevant.

Important constraints:
- Different Topic IDs do **not** prove that two entries cannot conflict or supersede one another.
- A unique/new Topic ID does **not** prove that `POSSIBLE_SUPERSEDED = 0`.
- Same Topic ID does **not** automatically imply REINFORCEMENT/DUPLICATE.
- Conflict/supersession review is semantic and time-aware, especially for firmware, software/tool versions, compatibility, supply rules and product/service behavior.

## Design note

分类算法未来可以工程化，但在当前阶段分类规则仍通过 GPT + 飞书智能体 + PIE 人工审核验证。

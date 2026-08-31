# Knowledge Candidate Classification

Status: Draft baseline

当新增或变化的 ITR 与现有 Knowledge 比较时，不应只有“新增/不新增”两个结果。

分类的目标是回答：**这个案例产生了什么可复用的新知识，未来同类问题需要知道什么？**

## NEW
存在可复用的新事实、诊断方法、维修策略、工具能力或业务边界，且没有等价现有 Knowledge。

动作：形成新的 Knowledge Candidate，保留支持结论所需的 Evidence、Scope、Confidence 和 Guardrail。

## REINFORCEMENT
与现有 Knowledge 核心结论一致，但提供新的独立 Evidence、机型/版本实例或验证结果。

动作：默认不创建重复规则。只有当新 Evidence 实质增强置信度、适用范围、反例边界或 regression coverage 时，更新对应知识。

## CONFLICT
新 Evidence 与当前 Knowledge 的事实性结论存在实质冲突。

动作：不得自动覆盖。进入人工 review，比较机型、版本、上下文、Evidence 强度和原规则范围，并保留冲突双方的技术条件。

## POSSIBLE_SUPERSEDED
旧 Knowledge 在当时可能正确，但新固件、工具、备件、流程或产品政策变化表明它可能不再是当前答案。

动作：进入 lifecycle review；保留版本/时间/适用范围变化，不需要保存完整源工单历史。

## DUPLICATE
新 ITR 没有带来新的可复用知识，与现有 Knowledge 实质等价。

动作：不新建 GitHub 知识项。

## INSUFFICIENT
Evidence 不足以形成可靠、可复用 Knowledge。

动作：不自动补全，也不为了“沉淀”而创建规则；继续在当前工单中收集证据。

## NO_ACTION
案例本身真实，但没有形成/改变任何可复用 Knowledge。

动作：不写 GitHub。

## Daily-case GitHub retention rule
Candidate classification 是知识写入门槛，不是工单归档机制。

完整案例历史应从 Nextop / ITR / Case History 读取。GitHub 不需要为了未来找回同一设备或同一工单而保存：
- device name / identifier；
- work-order / CaseID / ticket reference；
- agent personal name；
- partner/company name，除非其能力/权限本身是规则条件；
- full raw email/chat；
- full accepted/sent reply，除非精确措辞本身就是 regression 对象。

GitHub Candidate 应优先保留：
- model/product scope；
- symptom/error/component/path；
- decisive evidence；
- validated action/result；
- reusable diagnostic/service strategy；
- version/scope/guardrail；
- Workbench/reply/business-boundary correction。

## Matching rule
Candidate matching must compare the independent technical fact itself, not only Topic ID or fault taxonomy.

At minimum consider model, part/component, error code, version, knowledge conclusion, compatibility/supply fact and underlying evidence meaning when relevant.

Important constraints:
- Different Topic IDs do **not** prove that two entries cannot conflict or supersede one another.
- A unique/new Topic ID does **not** prove that `POSSIBLE_SUPERSEDED = 0`.
- Same Topic ID does **not** automatically imply REINFORCEMENT/DUPLICATE.
- Conflict/supersession review is semantic and time-aware, especially for firmware, software/tool versions, compatibility, supply rules and product/service behavior.

## Design note
分类算法未来可以工程化，但当前阶段仍通过 GPT + 飞书智能体 + PIE 人工审核验证。

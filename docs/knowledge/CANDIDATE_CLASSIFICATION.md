# Knowledge Candidate Classification

Status: Draft baseline

当新增或变化的 ITR 与现有 Knowledge 比较时，不应只有“新增/不新增”两个结果。

## NEW
存在可复用的新事实/诊断/处理知识，且没有等价现有 Knowledge。

动作：形成新 Knowledge candidate，经过 Evidence Gate 和人工审核后再发布。

## REINFORCEMENT
与现有 Knowledge 核心结论一致，但提供新的独立 Evidence、机型/版本实例、PIE 真实回复或其他增强信息。

动作：默认不重复创建同主题 Knowledge；评估是否增强 Evidence、适用范围或置信度。

## CONFLICT
新 Evidence 与当前 Knowledge 的事实性结论存在实质冲突。

动作：不得自动覆盖。进入人工 review，检查版本、机型、上下文、Evidence 强度和是否存在原知识错误。

## POSSIBLE_SUPERSEDED
旧 Knowledge 在当时可能正确，但新版本、固件、工具、备件或产品政策变化表明它可能不再是当前答案。

动作：进入 lifecycle review；AI 不直接历史化正式 Knowledge。

## DUPLICATE
新 ITR 没有带来足够新的知识价值，与现有 Knowledge 实质等价。

动作：通常不新建；必要时仅作为额外来源 Evidence。

## INSUFFICIENT
Evidence 不足以形成可靠、可复用 Knowledge。

动作：不自动补全；可以进入待评估队列或忽略。

## NO_ACTION
即使 ITR 内容真实，也没有形成/改变 Knowledge 的必要。

动作：不写 KB。

## Design note

分类算法未来可以工程化，但在当前阶段分类规则仍通过 GPT + 飞书智能体 + PIE 人工审核验证。
# Evidence Policy

Status: Active baseline

## Principle

Knowledge 中的事实、料号、兼容性、维修判断、版本状态和处理方法必须与 Evidence 强度匹配。

“存在于某字段”不等于“已被确认”。

## Evidence handling

### Strong / preferred evidence
优先使用能够直接证明事实的原始或人工确认 Evidence，例如：

- PIE 人工确认的 Comment/Reply
- Case History 中可追溯的真实沟通证据
- 原始邮件/聊天正文
- ITR 附件中的可验证信息
- 明确的人工作业/结论记录

具体飞书字段名称可能随表结构演进，字段契约应另行维护，不在本文件硬编码为永久 Schema。

### Legacy fields
Solutions、历史解决方案回复模板、历史 ITR SOP/逻辑分析等 Legacy/AI-derived 字段可以作为线索，但如果缺少允许的原始 Evidence，不应自动把其中新增的料号、兼容性、诊断步骤、SOP 或结论升级为 confirmed fact。

尤其注意：
- “某个 SOP 字段里存在测试步骤”不等于“该案例真实执行了该步骤”；
- AI/历史 SOP 中出现的通用检查项不得直接补进 Case-based Knowledge；
- 若希望把某个测试步骤沉淀为独立可复用的 `诊断/排查` Knowledge，必须找到独立的真实 PIE/Support Reply、官方 SOP/产品资料或其他一级 Evidence 支持该步骤本身。

正确做法是标记 Evidence gap / 待人工确认。

### Missing evidence
Evidence 不足时：

- 不补写推测事实；
- 不用常识替代公司内部事实；
- 不把“建议尝试”改写为“确认解决”；
- 保留待审核/待确认状态；
- 必要时记录缺失 Evidence 的具体内容。

## Version claims

“当时告知后续版本将修复”只能证明当时的计划/回复，不能自动改写为“新版本已经修复”。

只有新 Evidence 明确证明发布/修复状态后，才能更新 Currentness/Lifecycle。

## Scope discipline

Evidence 只支持其实际证明的范围。例如某一台设备通过特定更换顺序恢复，只能首先作为单案例 Evidence；除非有更强证据，不得自动升级为所有同类问题的标准维修顺序。

Case-based Knowledge 应区分：
1. 案例真实执行/观察到的路径；
2. PIE 明确建议但尚未执行的动作；
3. Legacy/AI SOP 中仅作为参考出现的通用步骤。

三者不得混写成同一“已验证诊断路径”。
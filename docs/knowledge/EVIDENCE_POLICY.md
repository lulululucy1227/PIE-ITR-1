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
Solutions、历史解决方案回复模板等 Legacy 字段可以作为线索，但如果缺少允许的原始 Evidence，不应自动把其中新增的料号、兼容性或结论升级为 confirmed fact。

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
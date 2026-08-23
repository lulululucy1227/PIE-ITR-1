# Knowledge Content Format Policy

Status: Active

## Purpose
Knowledge content must be easy to scan in Feishu table views. Multi-point content must use explicit line breaks so each independent condition, conclusion, diagnostic requirement or processing step is visually separated.

## One-point-per-line rule
For the following fields, when content contains multiple independent points, each point must occupy its own line:

- 已知结论
- 分析所需信息
- 处理方法
- 注意事项（when it contains multiple separate points）
- other structured multi-point Knowledge text fields where the same readability problem applies

Preferred format:

```text
1. 第一项
2. 第二项
3. 第三项
```

Do not write:

```text
1. 第一项 2. 第二项 3. 第三项
```

or:

```text
1) 第一项 2) 第二项
```

## Single-point content
If a field contains only one natural statement, do not add numbering merely for formatting consistency.

## Fact-preservation boundary
Formatting corrections must not change:

- technical facts;
- Evidence strength;
- scope or applicability;
- sequence semantics;
- Knowledge type;
- source ITR;
- review state.

A formatting task is text-layout-only unless a separate task explicitly authorizes content correction.

## Generation requirement
All newly generated Knowledge must follow this rule at creation time. The Feishu agent or future Knowledge Maintenance implementation should validate multi-point fields before writing records.

## Review requirement
If a batch creates or modifies Knowledge, the final validation should check that no multi-point field remains compressed into a single line due to numbering or delimiter formatting.

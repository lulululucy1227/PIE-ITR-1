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

## Scanability and information density
One-point-per-line is necessary but not sufficient. In narrow Feishu table columns, long prose still becomes visually dense and difficult for support agents to scan.

For customer-support-facing Knowledge, prefer short decision-oriented points over explanatory paragraphs.

### 已知结论
- Prefer 1–3 short points.
- Put the strongest current conclusion first.
- Separate case-specific evidence from reusable conclusion.
- Avoid repeating the full diagnostic path here; that belongs in 处理方法.

### 分析所需信息
- Prefer only the minimum information required to choose or execute the diagnostic path.
- Usually 2–4 points.
- Do not request SN / logs / screenshots / video mechanically unless they are actually needed.
- Use short nouns or questions rather than explanatory sentences.

### 处理方法
- Prefer 3–6 executable steps when the Evidence supports them.
- One action / one decision per line.
- Use concise verbs: 确认 / 检查 / 测试 / 交叉验证 / 比较 / 更换 / 验证.
- Where useful, express decision branches compactly: `若 A → ...；若 B → ...` but do not place several unrelated actions on one line.
- Do not repeat background, Evidence narrative, or case history inside the procedure.

### Avoid duplication across fields
The same sentence or fact should not be repeated in 已知结论、分析所需信息、处理方法 unless repetition is necessary for safe execution.

Typical division:
- 已知结论 = what we currently know / what this method can determine.
- 分析所需信息 = what support needs before choosing the path.
- 处理方法 = what the agent/dealer should actually do next.
- 注意事项 = scope limits / case-specific result / warnings.

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
If a batch creates or modifies Knowledge, the final validation should check that:

- no multi-point field remains compressed into a single line due to numbering or delimiter formatting;
- 已知结论 / 分析所需信息 / 处理方法 are not unnecessarily repetitive;
- text remains compact enough to scan in the Feishu table view;
- shortening did not remove required Evidence boundaries or diagnostic conditions.

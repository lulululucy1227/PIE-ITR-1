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
- Prefer 1–3 short points only when the content naturally has multiple independent conclusions.
- Do not force every record into three points. A single clear conclusion should remain one natural statement.
- Put the strongest current conclusion first.
- Separate case-specific evidence from reusable conclusion.
- Avoid repeating the full diagnostic path here; that belongs in 处理方法.

### 分析所需信息
- Prefer only the minimum information required to choose or execute the diagnostic path.
- Usually 2–4 points.
- Do not request SN / logs / screenshots / video mechanically unless they are actually needed.
- Use short nouns or questions rather than explanatory sentences.

### 处理方法
- Prefer 3–6 executable steps when the Evidence supports them; 7+ is allowed when each step is an independent necessary action or branch and compression would damage meaning.
- One action / one decision per line.
- Use concise verbs: 确认 / 检查 / 测试 / 交叉验证 / 比较 / 更换 / 验证.
- Where useful, express a single decision branch compactly, but do not stack several unrelated actions or branches on one line.
- Do not repeat background, Evidence narrative, or case history inside the procedure.

### 注意事项
- Keep this field lightweight. Its purpose is only scope limits, case-specific result, Evidence boundary, or safety/risk warning.
- Do not move removed prose from other columns into 注意事项 merely to preserve text volume.
- Prefer 0–3 short points. More points are acceptable only when each one changes safe interpretation or applicability.
- If an Evidence note is useful only for audit and not for frontline support, prefer 内容审核备注 rather than 注意事项.

### Avoid duplication across fields
The same fact should not be repeated in 已知结论、分析所需信息、处理方法、注意事项 unless repetition is necessary for safe execution.

Duplication review must be semantic. Comparing only exact strings, prefixes, or the first N characters is insufficient because the same meaning can be paraphrased differently.

Typical division:
- 已知结论 = what we currently know / what this method can determine.
- 分析所需信息 = what support needs before choosing the path.
- 处理方法 = what the agent/dealer should actually do next.
- 注意事项 = only scope limits / case-specific result / warnings.

## Single-point content
If a field contains only one natural statement, do not add numbering merely for formatting consistency.

## Whole-row scanability
Readability must be evaluated across the whole Knowledge row, not field-by-field only. A change is not a successful compression if information is simply shifted from 已知结论 or 处理方法 into a long 注意事项 cell.

When reviewing a row, ask whether support can identify within a few seconds:
1. what is known;
2. what is missing;
3. what to do next;
4. what limitation matters.

If not, the row remains TOO_DENSE even if every field individually satisfies line-break rules.

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
- 已知结论 / 分析所需信息 / 处理方法 / 注意事项 are not semantically repetitive;
- single-point content was not mechanically expanded into numbered bullets;
- 注意事项 did not become a dumping ground for text removed elsewhere;
- text remains compact enough to scan in the Feishu table view as a whole row;
- shortening did not remove required Evidence boundaries or diagnostic conditions.

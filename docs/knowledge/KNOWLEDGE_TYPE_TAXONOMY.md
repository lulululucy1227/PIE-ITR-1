# Knowledge Type Taxonomy

Status: Active — grounded in current Feishu KB usage

## Decision

Knowledge Type must follow real support content in Feishu and remain shallow enough for customer support to understand at a glance.

The original five Feishu types remain valid, but V3.7/V3.7R produced multiple real Knowledge entries that could not be accurately described as either `维修解决方案` or `流程/政策` because they are diagnostic facts, log-analysis conclusions, troubleshooting sequences or inspection steps without a verified repair result.

Based on this repeated real-content mismatch, one additional type is now authorized:

`诊断/排查`

This is an evidence-driven change, not a theoretical taxonomy expansion.

## Active Feishu types

1. 维修解决方案
2. 诊断/排查
3. 历史版本问题
4. 料号/兼容性
5. 软件/工具操作
6. 流程/政策

Do not add a seventh type unless repeated real Knowledge again demonstrates a material usability gap.

## Practical meaning

### 维修解决方案
Use only when evidence supports a concrete problem, an action that was actually performed, and an explicit result/resolution.

A recommendation, suspected root cause, log diagnosis or troubleshooting sequence without a confirmed result must not be labeled as `维修解决方案`.

### 诊断/排查
Use when the reusable value is helping support determine or narrow down the fault, including:
- log-analysis conclusions;
- troubleshooting/inspection sequences;
- cross-tests;
- pre-repair checks;
- PIE-recommended next diagnostic steps;
- technical diagnostic boundaries where no final repair result is established.

This type exists specifically so diagnostic content is not incorrectly forced into `维修解决方案` or `流程/政策`.

### 历史版本问题
Knowledge whose main value is explaining an issue, behavior or workaround tied to an older firmware/software/tool/product version.

### 料号/兼容性
Part numbers, replacement relationships, interchangeability/compatibility, supply/ordering facts and closely related spare-part facts.

### 软件/工具操作
Mammotion Kit, ToolSuite/MammoSuite, flashing, upgrade, software/tool operation and tool-specific handling.

### 流程/政策
Actual support/business/process rules or policies that agents need to follow. Do not use this type merely because a technical troubleshooting item does not fit elsewhere.

## Classification rule

Classify by the primary practical use of the Knowledge entry:
- `维修解决方案`: what was actually done and confirmed to resolve the case;
- `诊断/排查`: how to determine/narrow down the fault when the final repair result is not established;
- `历史版本问题`: what applies specifically to an older version/history state;
- `料号/兼容性`: what part to order/use and whether parts can be interchanged;
- `软件/工具操作`: how to use or handle software/tools;
- `流程/政策`: what operational/business rule should be followed.

Do not create multiple Knowledge Types for one entry merely because several concepts are mentioned. Use the type representing its primary reusable value.

## Evidence-driven examples from V3.7R

The following entries demonstrated the need for `诊断/排查`:
- NO.165: LUBA 2 charging-interruption log analysis + diagnostic steps, without a verified repair result;
- NO.166: cutting-disc/motor-shaft inspection before driver-board replacement, without a verified repair result;
- NO.167: cable -> driver board -> mainboard troubleshooting sequence, without a verified repair result;
- NO.168: IR-interference technical diagnosis and site check;
- NO.169: motor-temperature diagnostic threshold boundary and data-collection guidance.

These should not be forced into `流程/政策` merely to preserve the old five-type taxonomy.

## Change rule

Do not create another Knowledge Type until all of the following are true:
- multiple real Knowledge entries repeatedly fail to fit the current six types;
- the mismatch creates a real support usability/filtering problem;
- adding a type makes entries easier to understand at a glance;
- the same need cannot already be represented by Topic ID, fault category/module, model, version, status or other existing fields.

Before another taxonomy change, run a read-only audit of current Knowledge records and report the actual examples that do not fit. No future taxonomy change should be based only on theoretical classification design.

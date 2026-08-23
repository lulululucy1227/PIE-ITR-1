# Knowledge Type Taxonomy

Status: Active — preserve current Feishu taxonomy unless evidence from real KB usage justifies change

## Decision correction
A previously proposed six-type taxonomy was too abstract and was not sufficiently grounded in the actual ITR/工单速查 records. It is withdrawn.

Knowledge Type must follow the real support content already present in Feishu, not an imagined ontology. Do not add new types merely because they seem conceptually clean.

## Current Feishu types

The currently observed active options are:

1. 维修解决方案
2. 历史版本问题
3. 料号/兼容性
4. 软件/工具操作
5. 流程/政策

These remain the baseline until a real-content audit shows a repeated, material class of Knowledge that cannot be understood or filtered well with the existing options.

## Practical meaning

### 维修解决方案
Knowledge whose practical value is helping support resolve or handle a technical case. The exact evidence boundary remains governed by Evidence Policy; a recommendation must not be silently upgraded into a verified repair result.

### 历史版本问题
Knowledge whose main value is explaining an issue, behavior or workaround tied to an older firmware/software/tool/product version. This is kept as a current user-facing type because it already exists in the real KB and is useful to support old-version cases.

### 料号/兼容性
Part numbers, replacement relationships, interchangeability/compatibility, supply/ordering facts and closely related spare-part facts.

### 软件/工具操作
Mammotion Kit, ToolSuite/MammoSuite, flashing, upgrade, software/tool operation and tool-specific handling.

### 流程/政策
Support/business/process rules that agents need to follow, when these are genuinely reusable operational knowledge rather than AI governance instructions.

## Change rule

Do not create a new Knowledge Type until all of the following are true:
- multiple real Knowledge entries repeatedly fail to fit the current types;
- the mismatch causes a real support usability/filtering problem;
- adding a type makes entries easier to understand at a glance;
- the same need cannot already be represented by Topic ID, fault category/module, model, version, status or other existing fields.

Before any taxonomy change, run a read-only audit of current Knowledge records and report the actual examples that do not fit. No taxonomy change should be based only on theoretical classification design.

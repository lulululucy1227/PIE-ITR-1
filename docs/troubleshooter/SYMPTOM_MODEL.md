# PIE Troubleshooter — Controlled Symptom Model

Status: Active product architecture
Owner: Troubleshooter｜主管

## Purpose

PIE Troubleshooter must work even when an agent has no Error Code. The symptom path cannot rely on unrestricted free-text diagnosis because wording noise, mixed causes and incomplete descriptions can distort the repair recommendation.

The product therefore uses a controlled symptom model derived from real support evidence.

## Dual entry architecture

`MODEL CONTEXT -> ERROR ENTRY or SYMPTOM ENTRY -> CONTROLLED PATH -> PART/ACTION -> REPAIR -> VERIFICATION -> FIXED / STILL NOT FIXED`

### Error entry

Agent may enter:
- exact Error Code;
- exact/known Error Message;
- fuzzy text that only returns candidate Error Code/Message matches.

Fuzzy matching must not silently choose a repair path.

### Symptom entry

Agent does not freely describe the issue for diagnosis.

Preferred interaction:
1. choose observable area/category;
2. choose one controlled symptom;
3. choose one qualifier only when it materially changes the repair path.

The selected controlled symptom then resolves into the same canonical repair knowledge used by Error Code paths.

## Model context

A model/product selector should be available as persistent page context because the same symptom or code may map to different serviceable parts or actions across products.

Do not force repeated model selection inside every step. Ask once or only when the chosen path requires scope disambiguation.

## What counts as a symptom

A controlled symptom is what the agent can directly observe or confirm before diagnosis.

Good shape:
- one drive wheel does not move;
- mower cannot charge;
- mower does not power on;
- cutting disc does not rotate;
- positioning unavailable;
- Wi-Fi/Bluetooth cannot connect;
- error appears but mower otherwise works normally.

Bad shape:
- mainboard defective;
- motor failure;
- CAN problem;
- firmware bug;
- replace X;
- contact R&D.

Bad examples encode cause, component, repair action or internal routing instead of observation.

## Boundary rules

Every controlled symptom must satisfy:
1. observable/confirmable without requiring root-cause knowledge;
2. cause-neutral;
3. repair-neutral;
4. one primary phenomenon;
5. short and human-readable;
6. materially different from adjacent options;
7. useful for choosing the next repair path;
8. scoped by model/product when necessary;
9. supported by real ITR/knowledge evidence;
10. not created merely for taxonomy completeness.

## Hierarchy

Default hierarchy:

`OBSERVABLE_AREA -> CONTROLLED_SYMPTOM`

Optional qualifier:

`OBSERVABLE_AREA -> CONTROLLED_SYMPTOM -> QUALIFIER`

Use a qualifier only when it changes the recommended part/action. Examples of possible qualifiers include side/location, persistent vs intermittent, or post-repair recurrence, but only where real evidence supports the distinction.

Do not automatically expose ITR L1/L2/L3 as this hierarchy. Internal labels are source evidence and may mix symptoms, causes, components and business classification.

## Vocabulary and aliases

Each canonical symptom may retain controlled aliases/synonyms from real agent language.

Example concept:
- canonical: `One drive wheel does not move`
- aliases: known wording variants that mean the same observable condition and lead to the same path.

If the product offers text search for symptoms, text is used only to match against this controlled alias library. Arbitrary free text must not directly generate a part or repair recommendation.

## Unknown / other

Every area should provide a safe `None of these / Other issue` escape.

Optional free text may be collected only as taxonomy feedback:
- it creates a review candidate;
- it may help discover a missing controlled symptom;
- it does NOT automatically diagnose a fault;
- it does NOT automatically recommend a replacement part.

Unknown/high-ambiguity cases route to PIE.

## Convergence with Error Code knowledge

Error Code and symptom-only entry are not separate knowledge bases.

Examples:

`Error Code -> Controlled Symptom -> Repair Card`

and

`Controlled Symptom -> Repair Card`

must point to the same canonical repair/action/verification content when they represent the same scoped problem.

This prevents conflicting advice between Error Code lookup and symptom lookup.

## Feishu evidence sources

Build the symptom model from:
1. ITR main table — actual recurring observable descriptions and outcomes;
2. 工单速查 — reviewed reusable problem/repair knowledge;
3. 信息同步库 — newer technical/service conclusions and updates;
4. ITR taxonomy/labels — candidate vocabulary/grouping input only.

When sources conflict, retain the conflict for review. Do not silently select whichever wording looks cleaner.

## Desktop UX target

Current priority is desktop web.

Suggested primary layout:
- persistent model selector/context;
- two large entry choices: `I have an Error Code` / `I do not have an Error Code`;
- Error path: search -> symptom if required -> repair card;
- Symptom path: area -> controlled symptom -> optional qualifier -> repair card;
- repair result emphasizes `Most likely faulty part`, `What to do`, `After repair`;
- desktop scan speed is more important than mobile-specific optimization in this phase.

## Acceptance gate for a symptom

A controlled symptom is publishable only when:
- wording is observable and unambiguous enough for an agent to choose;
- synonyms have been normalized;
- its scope is known enough for the relevant products;
- it either leads to a stable self-service repair/action or clearly routes to PIE;
- verification/fallback exists for any published repair action.

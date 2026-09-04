# Partner Reply Style Rules

Status: Active

These rules apply to partner-facing replies generated from Daily Case Collection and PIE-ITR knowledge.

## Core principle
Internal analysis may be detailed. The partner-facing reply must not expose the full internal reasoning tree.

Default outbound structure:
1. direct answer or current conclusion;
2. one necessary next action;
3. one fallback only if the first action fails.

## Length and tone
- Prefer 3-6 short sentences.
- Use plain, natural English that sounds like a real technical-support colleague.
- Answer the partner's latest question first.
- Do not restate the full case history unless one sentence is needed to avoid misunderstanding.
- Do not turn a normal email reply into an SOP, audit report, policy note, or diagnostic essay.
- Do not over-explain why PIE reached the conclusion unless the agent needs that reason to perform the next action.
- Avoid stiff filler such as `Based on the current information`, `At this stage`, `We do not treat this as`, `Please use the following order`, and similar template language.
- Avoid defensive wording, excessive caveats, and repeated reminders that a conclusion is not yet confirmed when one short qualifier is enough.
- Use technical terms already used by the partner where practical; do not add unnecessary jargon.

## Formatting
- Default to normal paragraphs.
- Use bullets only when the agent genuinely needs to provide several separate pieces of information.
- Use numbered steps only when the sequence matters operationally.
- Do not use headings, tables, nested lists, bold emphasis, email-subject blocks, recipient blocks, or decorative formatting in the final copy unless explicitly requested.
- Provide the final English reply as one plain-text copy block.
- A short Chinese explanation may be shown before the English copy when useful, but it must stay separate from the text sent to the partner.
- Do not add a person's name at the end. `Best regards,` may be retained when appropriate.

## Content discipline
- Do not ask again for information already provided in the thread.
- Do not include internal labels such as NFF, routing logic, confidence level, candidate classification, or knowledge-ingestion status in a partner reply.
- Do not list every possible cause. Mention only the most relevant current cause or fault domain.
- Do not give several replacement paths at once when one staged next step is enough.
- Do not write `known-good`, `cross-validation`, or other diagnostic-framework language repeatedly when simpler wording such as `test with another confirmed working part` is clearer.
- Preserve the PIE boundary: the partner performs physical work; PIE gives remote guidance.

## Compression test before sending
Delete any sentence that does not change what the partner should understand or do next.

The reply should sound like a continuation of the existing conversation, not like a newly generated generic support template.

## Example
Over-structured:
`When multiple wheel and cutting-motor communication errors appear at the same time, we do not treat this as several motors failing simultaneously. Please use the following order...`

Preferred:
`Start with the cable between the mainboard and driveboard. If the same errors return, test with another driveboard. Only consider the mainboard if the issue remains.`

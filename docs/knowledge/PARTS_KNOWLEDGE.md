# PIE-ITR Parts / SBOM Knowledge

## Repair-strategy rule
Use:
`problem or visible damage -> model -> component -> Parts/SBOM -> serviceable part? -> standard repair route`

Do not jump to whole-unit replacement only because the agent requests it or says module-level repair is time-consuming.

Agent frustration/effort can change tone, not the technical conclusion.

## SBOM vs exploded-view consistency rule
For part-number, compatibility, orderability, replacement-part, or material questions, do not trust the partner-provided part number by default.
Use this route first:
`model -> SBOM -> confirmed component / part number -> exploded view / published material comparison -> MSCS/orderability check where needed`

- SBOM is the source of truth when SBOM and exploded-view/material information conflict.
- If the exploded view shows a different part number from SBOM, use the SBOM part number for technical/ordering guidance and flag the exploded-view data as incorrect.
- The Workbench should proactively detect this mismatch rather than only answering the partner's stated part number.
- When a documentation mismatch is found, remind PIE to report it to the China repair-strategy group and generate a concise internal correction note containing: model/component, wrong published value, correct SBOM value, and the document/material that needs correction.
- Latest spare-parts/material reference site: `https://toolsuite-dcdn.mammotion.com/`.

### Confirmed LUBA mini RTK antenna example
- Incorrect exploded-view part number: `W.Z.RF.000050000`
- Correct SBOM part number: `C.P.SH.000255000`
- `C.P.SH.000255000` was confirmed searchable/orderable in MSCS with stock visible.
- Correct partner guidance: use `C.P.SH.000255000` to order in MSCS; inform the partner that the exploded-view information will be corrected.

## Confirmed example
- `C.P.SH.000220000 — LUBA 3 Chassis Module`
- In a cracked-chassis case, existence of a serviceable chassis module supports chassis replacement as the standard repair path before considering whole-machine exchange.

## Future image-to-part chain
`image -> component candidate -> product/model -> Parts/SBOM -> part candidate/number -> source -> human confirmation`

Do not treat image inference as confirmed part identification without model/context validation.

# Centered text-input homepage — historical, superseded

Status: NOT_ACCEPTED / SUPERSEDED by EC-MT-20260908-CONTROLLED-SELECTION-UI-007. Retained only as historical evidence; this is not the current product or final report.

Authorization: direct user request after task 006. The user requested a simpler homepage, a mandatory observed symptom, optional error code, centered content, and explicitly rejected dropdowns. This refinement does not claim a new Issue #5 task or change the accepted knowledge-promotion gate.

The homepage now uses plain text fields for the observation, model, error code/message and firmware. The title, form, field content and action are centered. Firmware is initially collapsed and expands when an existing guide requires its scope. Category tiles, quick codes, product panel and repeated status instructions were removed. At most one primary Continue button is visible in each identification state.

The required observation is checked both by the form and solution navigation. Whitespace is rejected. Exact approved labels/aliases use the existing symptom resolver. Other English wording uses the existing lexical search only to offer explicit symptom choices, including None of these; it does not automatically infer a repair. Unmatched descriptions go to PIE. Optional code/message lookup still preserves signed codes and code-specific condition choices. A symptom-guide message inconsistent with the recognized observation goes to PIE. Model matching remains the existing exact normalized scope check; free typing does not broaden applicability.

No canonical data, candidate reviews, source mappings, repair instructions, engine or publication policy changed. Page 1/2 separation, qualifier checks, firmware/model gating, failure/return guards and 1202 freeze remain intact. Input edits invalidate old history entries; model edits clear previous firmware and qualifier confirmation.

Verification: 69 Node tests; 30 adapted two-page browser checks (including all 25 controlled symptoms and unlisted descriptions); 21 stable-guidance browser checks; 9 focused homepage checks; actual 125% browser zoom at 1366 and 1920 widths, including all 10 new guidance cards. Screenshots at 1366, 1920 and 390 widths show centered fields without horizontal overflow. The actual user-browser HTTP preview was opened and visually inspected with enabled text inputs. Self-review found no unresolved issue within this change's scope.

Package: `error-code-pilot-20260908-110248.zip`, SHA256 `3135f909932f800f191a981094f5bc97074b855dfb461099a2f49824ee928fde`. Eight allowlisted entries; extracted standalone HTTP check, all-entry hash comparison and privacy scan passed. The full private data remains outside the package.

The user's screenshot came from opening `src/index.html` via a file URL, where the module/data workflow cannot run normally. The functional entry is the local HTTP preview at port 8796. Browser policy blocked control of that file tab; it was left untouched and a new HTTP tab was opened successfully. The owned preview is left running for the user. MAIN, production systems and default branch were not changed.

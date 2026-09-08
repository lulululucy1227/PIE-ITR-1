# Service guidance UI and extension release

2026-09-08 — user follow-up to EC-MT-20260908-CONTROLLED-SELECTION-UI-007.

Result: TROUBLESHOOTER_CONTROLLED_SELECTION_GREEN retained after fresh regression. Local specialist self-review and independent code review are complete; this is not a claim of supervisor acceptance or authorization for external deployment.

## Delivered

- Restrained visual refinement using the applicable principles from the user-requested taste-skill; the skill's explicit exclusion of product wizards is documented in the architecture note.
- Numbered, unchanged approved actions with adjacent desktop verification, consistent form contrast/spacing and a clear failure fallback.
- Tested presentation adapter and exact step-resource contract for future parts, tools, reasoning, disassembly and expected observations. No real resource source is connected; empty resources produce no UI.
- Parts require confirmed fitment and replacement target, disassembly requires access-safety and procedure-scope facts. Resources cannot select or authorize repairs.
- [Architecture and staged integration plan](SERVICE_GUIDANCE_ARCHITECTURE_2026-09-08.md).

## Fresh verification

All commands ran against the final runtime changes in this follow-up:

- `node --test test/*.test.mjs`: 84/84 passed, including eight new service-plan cases.
- `node test/browser.mjs`: 32/32 two-page cases.
- `node test/controlled-browser.mjs`: 17/17 controlled-selection cases.
- `node test/stable-browser.mjs`: 21/21 stable guidance cases, ten scoped guidance cards at both desktop sizes.
- `node test/refinement-browser.mjs`: 3/3 viewport/picker cases.
- `node test/service-browser.mjs`: 3/3 viewport cases; exact approved action/verification parity, no resource placeholders, verification gate, preserved Back selections, Other-to-PIE and no horizontal overflow. Primary button contrast measured 7.87:1.
- `node test/browser-zoom.mjs`: actual Edge browser zoom 1.25 at 1366×768 and 1920×1080, including native picker and ten guidance cards. Desktop, 125% and basic mobile screenshots visually inspected.
- Import check: 19 candidates plus separately frozen 1202, nine promoted portions, ten retained PIE_ONLY candidates; source parity passed.
- Lifecycle: two owned start/exit/relaunch cycles on specialist port 8806.
- Standalone build: six public assets, 31 cards and 25 projected symptoms. Public/private allowlists and request restrictions passed in the tests above.
- After correcting the ZIP README alternate-port command to use its bundled runtime, the portable-package unit check passed again; final build and package validation passed.
- `git diff --check`: passed. Canonical data, candidate data and engine have no changes from baseline `3cd3c3f`.

Independent reviewer `service_architecture_review` inspected the local diff read-only, ran the eight adapter tests and found no blocking issues. The reviewer confirmed the post-resolver/exact-guard placement, exact attachment binding, no live provider and no empty-resource UI. Their approval is limited to this interface/layout; future resource ingestion/publication needs its own evidence review.

## Standalone package

`artifacts/error-code-pilot-20260908-194153.zip`

SHA256: `74f7ef0596ec87a32c4decd9ad1351bf2f8914dfdbd77cb9693945677eb56ef6`

Ten allowlisted entries, including the bundled Windows Node runtime and new presentation module. Extracted copy starts with its own runtime on 8797; HTTP operation, knowledge parity, every extracted entry hash, content privacy checks and owned process exit passed. Recipients extract the ZIP, double-click `run-pilot.cmd`, then open `http://127.0.0.1:8796`. The ZIP includes `LOCAL_README.txt` with operation and rollback instructions. No Node installation is required.

Evidence under ignored `artifacts/`: service-browser-verification.json, controlled-browser-verification.json, two-page-verification.json, stable-browser-verification.json, refinement-verification.json, zoom-verification.json, lifecycle-verification.json and package-verification.json. Visual examples: service-1366-guide.png, service-390-guide.png and zoom125-1366-guide-wheel-movement.png.

This release does not invent part numbers, tools, tests or disassembly methods. Existing procedural detail is the limit of current newcomer guidance. No MAIN runtime or shared business state changed; no Issue #3 report, production write, push/merge or public deployment.

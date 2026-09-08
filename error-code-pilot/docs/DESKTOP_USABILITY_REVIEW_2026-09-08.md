# Desktop usability self-review

Task EC-MT-20260908-DESKTOP-LONGRUN-003. Actual Edge screenshots and interaction results reviewed on 2026-09-08; browser assertions supplement visual inspection.

| Question | Observed result and evidence |
| --- | --- |
| Fast code route? | One search submission opens an exact code/message; only materially different conditions require a choice. 1202 and 5510 exercised on desktop and mobile. Fuzzy matches remain explicit candidates. |
| No-code route understandable? | All ten observable areas are visible on the 1366x768 home together with model and search. Selecting an area exposes only its controlled symptoms, with an Other issue exit. No binary entry toggle. |
| Labels distinguishable? | The approved labels distinguish charging from docking, network connection from positioning, and visible damage from inferred failure causes. No internal tools, account, warranty or parts taxonomy appears as a symptom area. Broad SYM-026/027/028 are excluded from the normal picker. |
| Card emphasizes action? | The common card shows target/part, What to do, After repair / verification, then Still not fixed. Software guidance is confined to the exact version and test-only condition. Evidence states, CN metadata, source IDs and confidence labels are absent. |
| Branching necessary? | The software repair uses one decisive observable qualifier after exact model/version gating. Safe code checks use their existing meaningful condition choices. A model or firmware change invalidates confirmation and removes stale action. |
| PIE routes clear? | Uncovered symptoms and withheld repairs show Next step with PIE and concrete requested context. They do not render empty cards or invent a repair. Approved 5501 guidance is identical through code and SYM-021 entry. |
| Common laptop and 125% zoom? | Fresh checks at 1366x768 and 1920x1080, plus actual browser zoom 1.25 at both sizes, passed with no horizontal overflow or page error. At 125% a laptop uses normal vertical scrolling; text and controls remain readable. Mobile 390px remains usable. |

Screenshots: `artifacts/desktop-home.png`, `desktop-repair.png`, `wide-desktop-home.png`, `wide-desktop-repair.png`, `mobile-home.png`, `mobile-repair.png`, and native `zoom125-1366-*` / `zoom125-1920-*`. The native zoom test uses Chromium's actual tab zoom (measured 1.25 and DPR 1.25); CDP viewport capture avoids Playwright full-page clipping artifacts at non-default browser zoom. Its temporary extension and profile are test-only and excluded from the eight-file package.

Refinements made after inspection: opening a symptom clears an unrelated prior error query; screenshots start at a known scroll position; native zoom captures use the real viewport. Failure/returned state is retained across entry routes and mower detail changes. The verification checkbox remains a local self-report, never an ITR/NFF decision.

The screenshots demonstrate local usability, not a measured partner acceptance rate. Wider field trials and additional candidate knowledge are future work under separate authorization.

# Task 010 independent final review

Task: `EC-MT-20260916-HARDWARE-TOP10-010`
Review date: 2026-09-16
Baseline: `2c9f7ef` in the isolated Error Code specialist workspace.
Reviewer scope: read-only source/code/evidence review; this report is the reviewer's only edited file. No Reply Assistant source, production code, test, build, or package was changed by this reviewer.

## Disposition

**Independent final review passed. No unresolved blocking findings.** Fresh source, automated, browser, lifecycle, privacy and extracted-package evidence supports the owner's local claim of `TROUBLESHOOTER_HARDWARE_TOP10_GREEN`. This is local implementation approval, not supervisor acceptance.

## Ranking and source validity

The ranking is explicitly **priority-based**, not a measured frequency ranking. The inspected audit contains 28 normalized candidates, 10 selected management priorities, and 18 exclusions/merges. Every selected item has an observable symptom, a bounded solution/investigation route, verification, failure fallback, model boundary, and selection rationale. Pure update/app/network software problems do not occupy a Top 10 slot.

The actual dated case evidence is a convenience sample of 13 distilled cases from **2026-08-18 through 2026-08-21**, four days. It is not a complete intake denominator or a 90-day cohort. Technical/acceptance authority separately extends to **2026-09-14**. The audit does not convert September archive timestamps into September case dates, sum overlapping historical aggregate counts, or invent success percentages. These limitations must remain prominent in the supervisor report.

Eight GUIDED management groups reuse nine existing hardware cards; shared CAN/drive failures and LiDAR readiness remain two `TOP10_PIE_GUIDED` / `PIE_ONLY` investigation items. The docking management group shares one ranking position but preserves two actual symptom/card branches. No new confident public repair path was created merely to reach ten. Management `TOP10_GAP=0` therefore does not mean ten self-service repairs: two stable self-service coverage gaps remain.

Current sources were resolved from `C:/Users/Reggie/Desktop/ITR工单助手/工单助手交接包/ticket_assist` and its sibling `维修与售后知识库`. The archived Workbench reference copy and pilot-imported guidance are distinguished from independent current evidence. The reviewer independently recomputed all 17 ranking-source entries (16 unique files): their original bytes and SHA-256 matched both recorded reads. For the 31 resource-source entries, all 29 external originals and the local reuse snapshot matched their recorded bytes/SHA-256. The local canonical source hash intentionally identifies the pre-change baseline and is not falsely represented as an unchanged external source.

The reviewer directly read current NFF SOP section 7, the September 11 Burn-in business source updated September 14, the official maintenance source, scoped action text, candidate rationales and field dispositions. Source snapshots remain management evidence; runtime does not read the Reply Assistant vault.

## Published content and resource boundaries

The inspected public catalog remains 31 cards and 25 controlled symptoms. Its knowledge version is `2026-09-16-hardware-top10.1`. It contains 32 exact model/action resource bindings across nine hardware cards: 22 reasoning bindings, seven basic cleaning-tool bindings, and three visible safety bindings. These implement nine optional detail subjects plus one power-safety subject, expanded across exact model names.

Published detail explains existing checks and results: single-variable comparisons, motor-versus-channel observations, safe cleaning, power-loss timing, RTK station versus mower observations, compatible bumper checks, and SBOM/diagram lookup boundaries. It does not invent electrical thresholds, torque, tool versions, connector pinouts, or an opening procedure. MammoSuite and Mammotion Kit are not treated as interchangeable.

No real SKU, repair quantity, or disassembly record is published. The private evidence preserves conflicting HM441 regional adapter/wheel/vision references and uncertain LiDAR variants. A part mention, `PCS` unit or product-name `QTY14` is not treated as one-repair quantity. Existing broad model choices cannot uniquely identify capacity, region, failed side and hardware variant; extra mandatory questions were not added to manufacture eligibility.

Projection requires approved/current/safety/scope review, matching provenance digest, an existing confirmed card/path, exact model/firmware/knowledge version, and exact action index/instruction. It emits an explicit public allowlist. Public resource IDs and SKU syntax are bounded; prerequisite values use an explicit four-value allowlist. Part and disassembly resources additionally require their existing fitment/target or safe-opening/procedure facts. Rendering rechecks current bindings and prerequisites. An escalated result cannot acquire repair resources.

The normal input flow remains `Model -> Controlled Symptom -> Repair`; optional error text cannot bypass a valid controlled symptom. There is no Top 10 selection panel or extra mandatory Area/parts question. Optional learning details are collapsed; power safety appears before the first instruction. The default action and verification remain readable without opening details.

## Findings resolved during review

| Finding | Verified correction |
| --- | --- |
| Public resource IDs/SKU values and prerequisite strings could bypass the title/body privacy check. | IDs/SKUs now have bounded syntax and prerequisites use explicit allowed fact identifiers; mutation tests cover rejected private/invalid values. |
| Critical power stop conditions and power-off-before-cleaning appeared only in optional details. | Power stop conditions render as visible safety text before action zero; docking action explicitly requires power-off; cutter action explicitly requires protective gloves. |
| The log-upload paraphrase omitted the current source's evidence timing fields. | Verification retains fresh post-test logs, upload confirmation/time and Log ID when available. |
| The existing software repair retained a blanket ultrasonic-failure exemption contrary to the current sole acceptance rule. | Current applicable-test obligations replace that exemption on the active scoped repair; the conflict is recorded privately. Frozen/private paths remain unchanged and cannot authorize repair. |

Current acceptance requires the applicable Functional Test, Communication Check and Auto Map Run reports, Connect Checking screenshot, and fresh post-test logs. Burn-in is conditional on actual relevant motor/driver/battery/power repair; replacing a charging station or charging contacts alone is explicitly exempt. RTK supply verification is conditional on actual power-supply repair. Unsupported, unrun, failed, or missing required verification cannot be treated as completion. These changes do not supply tool parameters or grant a new hardware repair route.

## Final verification reviewed

- `artifacts/task010/node-tests.txt`: fresh **104/104 passed**, zero failures; read directly by the reviewer.
- `artifacts/task010/source-ranking-verification.json`: 28 candidates, ten selected, 90 field dispositions, 17 source entries, two PIE-only items, and explicit incomplete evidence window.
- `git diff --check`: no whitespace errors.
- Direct comparison with baseline `2c9f7ef` confirmed the frozen `ec-1202` object, card identities and controlled symptom identities are unchanged.
- Final browser logs in `artifacts/task010/` and fresh JSON reports were read directly: Simple Knowledge 3 viewports; Controlled Selection 19 checks; two-page flow 32 checks; Refinement 3 viewports; Service 3 viewports; Single Panel passed; Stable Guidance 21 checks; Hardware resources 27 card/viewport checks. The hardware suite checks all nine resource-bearing cards at 1366x768, 1920x1080 and basic mobile width 390, including collapsed defaults, exact detail, visible safety ordering and stale-resource clearing. The single-panel log is `artifacts/task010/single-panel-browser.log`.
- Actual Windows Edge 125% zoom passed at 1366x768 and 1920x1080, with DPR 1.25, all ten scoped guidance cards checked per size, no horizontal overflow, no browser errors and no external application requests. `artifacts/zoom-verification.json` and `artifacts/task010/browser-zoom.log` were inspected directly.
- Visual inspection of the fresh 1366-wide power card and 125% wheel card confirmed the safety stop precedes the powered check, primary instructions remain distinct, and optional detail adds no dashboard or speculative parts list. Expanded detail remains readable.
- `artifacts/lifecycle-verification.json` and `artifacts/task010/lifecycle.log`: two owned start/stop/relaunch cycles on port 8806 both returned HTTP 200; owned children exited and relaunch passed. The owner's initial attempt on occupied 8796 did not terminate the existing user instance; the isolated 8806 rerun supplies the successful lifecycle evidence.
- `artifacts/package-verification.json`: 11 allowlisted files, bundled runtime, 31 cards / 25 symptoms, exact extracted hashes, extracted HTTP success, launcher start and reuse on port 8840, all six HTTP public files matching, and the owned process exited. The reviewer independently opened the ZIP read-only and compared every one of its six public assets against the final `dist`: **6/6 hashes matched**. The ZIP has no `data/`, `docs/` or `lib/` entries. Targeted public-content readback contains none of the private provenance fields, Reply Assistant paths or withheld example SKUs.
- Final ZIP: `artifacts/error-code-pilot-20260916-005145.zip`.
- Independently recomputed ZIP SHA-256: `cf3260b7662bb7df28945741ae1269d0b4b5af10e6a3771d1bc6dbfbb8fad1dd`, matching the package report.

## Approval boundary

This is an independent local review of the scoped implementation and evidence reconciliation. It is not supervisor acceptance, permission for default-branch integration/public deployment, or promotion of withheld SKU/procedure/CAN/LiDAR facts. The documented narrow case window and two stable self-service gaps remain limitations of the content, not hidden completed work or fabricated evidence.

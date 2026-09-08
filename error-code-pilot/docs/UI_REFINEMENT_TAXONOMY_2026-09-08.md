# UI detail refinement and taxonomy vocabulary — 2026-09-08

Follow-up to EC-MT-20260908-CONTROLLED-SELECTION-UI-007. User requested improved visual details and reference to the existing first/second-level ITR labels, then explicitly confirmed use of the 2026-09-07 local snapshot. This is a presentation refinement, not a new taxonomy publication or repair knowledge promotion.

## Source and interpretation

Read-only source: C:/Users/Reggie/Desktop/PIE-ITR-1/knowledge/desktop_reference_20260907/data/tables/tags.json, the existing parsed ITR标签体系 spreadsheet. The source metadata identifies it as an unreviewed local reference with unverified currentness; it is not claimed to be the current live Feishu taxonomy. User confirmation permits this snapshot as the vocabulary reference. No original spreadsheet was reparsed, no source rows were copied into public assets, and no MAIN files or live table were changed.

The snapshot mixes observable symptoms, components, diagnosed causes, tools and business processes. We retain the controlled observable-symptom boundary. The following presentation mapping references relevant source groups without treating every L2 label as a supported diagnostic option:

| Existing area value | Visible category | Referenced ITR groups |
|---|---|---|
| Movement | Wheels & movement | 轮毂问题 |
| Cutting | Cutting disc & height | 刀盘问题、升降问题 |
| Charging | Charging | 充电问题 |
| Docking | Returning to the station | 回充问题 |
| Power | Power & battery | 开关机问题、电池问题 |
| Positioning | Positioning & maps | 定位问题、建图问题、RTK问题 |
| Connectivity | Connections | 连接与通讯问题 |
| Sensors | Safety & obstacle sensors | 安全与碰撞传感器问题、视觉/LiDAR问题 |
| Physical | Body & visible damage | 机身组件问题、保修与定损支持中的可见损伤现象 |
| Software | App & firmware | Mammotion APP问题中的固件升级现象 |

These remain ten compact controlled categories. The existing 25 public symptoms and their model filtering are preserved. Specific options still describe observed behavior: e.g. disc not spinning, height not adjusting, wheel not moving, charging stopping before full, Wi-Fi not connecting. SYM-005's displayed English grammar becomes “Cutting height does not adjust”; its meaning and ID are unchanged. Summaries use the same display vocabulary. Source labels such as charging mainboard/driver-board faults are not offered as observed symptoms. Taxonomy-only categories without an approved symptom remain outside normal navigation; Other still leads to PIE without repair inference.

## Visual changes

The centered form is 620px maximum width with closer header spacing, restrained shadow, consistent rounded controls, lighter field borders and a green keyboard focus ring. Action buttons and optional firmware have clearer spacing; the Back/Continue row has a subtle separator. No extra instruction panels, quick-code cards or dashboard elements were added.

Supporting desktop browsers use a CSS-styled native select picker: rounded white surface, bounded scrolling, soft green selected rows, a checkmark and separated Other option. The select DOM, controlled values, validation, native keyboard behavior and input events are retained. Unsupported browsers and small screens keep the native picker. Error Code remains an optional text input. This follows the browser's documented customizable-select feature: https://developer.chrome.com/blog/a-customizable-select . No component library or new network dependency was added.

## Fresh verification and review

- 75 Node tests passed.
- 3 new browser viewport scenarios passed at 1366×768, 1920×1080 and 390×844: vocabulary, stable controlled IDs, optional code, keyboard cancellation on styled desktop pickers, tab order, no premature solution, Back preservation and no overflow.
- 17 controlled-selection, 32 two-page and 21 stable-guidance browser checks passed after final runtime changes.
- Actual Edge 125% browser zoom passed at both desktop sizes, including open picker screenshots, preserved selection on Escape and visible Continue, plus the ten stable guidance cards.
- Interactive Chrome inspection confirmed the styled menu and the selected Cutting-height example. Desktop and zoom screenshots were visually reviewed.
- Import/source parity passed for 19 candidates plus frozen 1202. Two owned lifecycle cycles passed on 8806. Standalone package privacy, extraction, all-entry hash parity, HTTP operation and owned process exit passed.
- Targeted self-review found no outstanding issue. Prior independent task-007 review is historical evidence for the underlying routing implementation, not a claimed independent review of this new visual diff.

New package: artifacts/error-code-pilot-20260908-162529.zip.
SHA256: b06f3a41004281d83deb8c4d5ea1578380541e9d8d0961a29dada5c0eb9e008a.
Visual evidence: artifacts/refinement-1366-open.png, refinement-1366-details.png, refinement-1920-open.png, refinement-390-details.png and zoom125-1366-picker.png. Automated evidence: refinement-verification.json, controlled-browser-verification.json, two-page-verification.json, stable-browser-verification.json, zoom-verification.json and package-verification.json.

Knowledge data and engine are unchanged: nine mature portions / ten scoped guidance cards, PIE_ONLY and 1202 freeze remain intact. MASTER_PLAN and AGENT_REGISTRY are unchanged because this follow-up changes no ownership, workspace or milestone status. Task/report isolation remains Issue #5 / Issue #6, with no production writes, default-branch push/merge or public deployment.

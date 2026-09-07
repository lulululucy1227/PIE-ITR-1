# PIE Troubleshooter — Builder Handoff

Status: READY_FOR_DESKTOP_PHASE_2
Owner: Troubleshooter｜主管
Date: 2026-09-08

## 1. Product direction

PIE Troubleshooter is a desktop-first agent repair portal, not an Error Code encyclopedia.

Homepage structure:
1. persistent Product / Model context;
2. prominent Error Code / Error Message search box;
3. controlled `Choose by symptom` navigation visible on the same page;
4. both routes converge on the same canonical Repair Card;
5. no forced `I have / I do not have an Error Code` toggle;
6. mobile only needs basic compatibility in this phase.

Reason: Feishu audit found 737 ITR records, only 38 with Error Code. Symptom navigation is the primary coverage path; Error Code search remains a fast shortcut.

## 2. Controlled symptom architecture

Agent-facing symptom navigation must use controlled observable symptoms only. Free text must not directly generate repair recommendations.

Current approved navigation skeleton contains these areas:
- Movement
- Cutting
- Charging
- Docking
- Power
- Positioning
- Connectivity
- Sensors
- Physical
- Software

Current controlled symptom candidates approved for implementation of navigation/UI:

Movement
- SYM-001 One wheel does not move / 单个轮子不转
- SYM-002 Multiple wheels not moving / 多个轮子不转
- SYM-003 Wheel makes unusual noise / 轮子异响

Cutting
- SYM-004 Cutting disc does not spin / 割草盘不转
- SYM-005 Cutting height cannot adjust / 切割高度无法调节
- SYM-006 Cutting disc makes unusual noise / 割草盘异响

Charging
- SYM-007 Robot does not charge / 不充电
- SYM-008 Charging stops before full / 充电中断/充不满
- SYM-009 Charging station not recognized / 无法识别充电桩

Docking
- SYM-010 Cannot return to charging station / 无法回桩

Power
- SYM-011 Robot does not power on / 不开机
- SYM-012 Battery drains quickly / 电池耗电过快
- SYM-013 Robot shuts down unexpectedly / 意外关机

Positioning
- SYM-014 Positioning failed or inaccurate / 定位失败/定位不准
- SYM-015 Cannot connect to RTK station / 连不上RTK基站
- SYM-016 Map lost or cannot load / 地图丢失/无法加载

Connectivity
- SYM-017 Cannot connect to WiFi / 连不上WiFi
- SYM-018 Cannot connect to 4G/mobile network / 连不上4G/移动网络
- SYM-019 Bluetooth connection fails / 蓝牙连接失败

Sensors
- SYM-020 Bumper triggers falsely / 碰撞传感器误触发
- SYM-021 LiDAR not working / 激光雷达不工作

Physical
- SYM-022 Visible water ingress / 可见进水痕迹
- SYM-023 Visible cable or harness damage / 线缆/排线可见损坏
- SYM-024 Visible physical impact damage / 物理撞击损坏

Software
- SYM-025 Firmware update fails / 固件升级失败

PIE-only / do not expose as direct self-service path yet:
- SYM-026 行走异常/抖动
- SYM-027 视觉/摄像头异常
- SYM-028 工作中异常停机

## 3. Knowledge promotion policy

Read and enforce `docs/troubleshooter/EVIDENCE_PROMOTION_POLICY.md`.

Important:
- explicit `solved` feedback is NOT required before a repair path can be considered usable;
- `VERIFIED_RESOLUTION` is strongest evidence;
- `STABLE_OPERATIONAL_GUIDANCE` is also publishable when guidance has remained materially stable in active PIE/KB/service use, with adequate scope and no meaningful contradiction/reopen/supersession signal;
- do not equate `no explicit solved reply` with `no evidence`;
- do not equate mere silence/age with stability either.

For candidate Feishu repair paths, Builder must support evidence states in the data model, but must not auto-promote all candidates to agent-facing cards.

## 4. Existing canonical knowledge to preserve

Builder must read current promoted knowledge before adding or changing repair cards:
- `docs/knowledge/ERROR_CODES.md`
- `docs/knowledge/KNOWN_FIXES.md`

Known examples include:
- 1000022 historical verified firmware fix with narrow product/version scope;
- 5501 LiDAR/data-path upgrade-failure diagnostic pattern;
- 6401 replacement-history lesson / vision-module case;
- 1008 STOP/locked-state handling;
- 1202 promoted cable -> mainboard service path, but model scope remains unresolved.

Never overwrite promoted canonical knowledge with a conflicting Feishu candidate without supervisor reconciliation.

## 5. 1202 gate

1202 remains FROZEN for agent-facing repair publication because current promoted knowledge conflicts with the Feishu candidate and model scope is unresolved.

Allowed now:
- keep exact code/message searchable;
- show safe non-destructive first guardrail if already canonical (e.g. confirm no real physical blockage);
- route the unresolved repair path to PIE / supervisor review.

Not allowed:
- publish cutting-motor -> driver-board -> mainboard from the Feishu candidate;
- publish cable -> mainboard as universal across models until scope is confirmed.

## 6. Feishu repair-path candidates

The corrected Feishu build contains 19 candidate repair paths. Treat them as candidate structured knowledge, not automatically publishable truth.

Builder should import/support these fields where useful:
- symptom_id
- repair_path_id
- product/model scope
- part/action
- repair steps
- verification
- fallback
- evidence_state
- agent_visibility
- conflict/supersession status

Do not force P0/P1 visibility solely from the Feishu labels. Promotion depends on the evidence policy and existing canonical knowledge.

## 7. Desktop UX requirement

Target the shortest practical repair flow.

Home:
- Product/Model selector
- Error Code / Error Message search
- symptom area cards immediately visible

Symptom flow:
`Area -> Controlled Symptom -> optional qualifier only if it changes repair path -> Repair Card`

Error flow:
`Error Code/Message -> matched candidate(s) -> controlled symptom if needed -> Repair Card`

Repair Card should prioritize:
1. Most likely faulty part / target area
2. What to do
3. After repair / verification
4. Still not fixed

Internal metadata such as evidence state, source, taxonomy, conflict details and engineering notes must not clutter the normal agent page.

## 8. Safety / boundaries

- no production Feishu/Nextop writes;
- no MAIN Workbench mutation;
- no public deployment in this task;
- no raw ITR, raw chat, SN/Device Name, PII or proprietary case mirror;
- no free-text LLM diagnosis;
- no graph DB / CMS / large expert system;
- keep standalone lightweight SPA/runtime posture unless there is a concrete blocker.

## 9. Phase-2 success condition

Builder may now proceed with desktop Phase 2 when:
- the new homepage and controlled symptom navigation are implemented;
- the canonical schema supports Error Code + Symptom convergence;
- evidence-state/promotion logic is represented in data;
- existing promoted Error Code knowledge remains intact;
- 1202 remains safely gated;
- candidate Feishu repair paths can be loaded/reviewed without becoming automatically agent-visible;
- agent-facing cards are shown only for promoted/stable knowledge;
- desktop usability, exact/fuzzy search, internal/public projection, privacy and local packaging regressions remain green.

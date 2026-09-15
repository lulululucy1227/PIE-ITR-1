# 硬件 Top 10 · 2026-09-16

本表是PIE/主管内容管理清单，不进入前端选择流程。**优先级排序，非频次Top10**；10项中8项为GUIDED管理组（复用9张硬件卡），2项为TOP10_PIE_GUIDED / PIE_ONLY调查项。未用软件填位；管理项TOP10_GAP=0，尚无稳定自助修复的缺口为2。

## 来源与实际窗口

工单回复助手：`C:/Users/Reggie/Desktop/ITR工单助手/工单助手交接包/ticket_assist`。当前知识库：`C:/Users/Reggie/Desktop/ITR工单助手/工单助手交接包/维修与售后知识库`。已按settings.py重新解析环境/config/sibling；本次无vault override，未导入或运行Reply Assistant。

**可验证连续案例窗口：2026-08-18—2026-08-21（4天，13条蒸馏样本，不代表完整收单）。技术与验收依据更新至2026-09-14。** 两者不是同一统计窗口。543份历史ITR、91份自动归档、116个知识聚合节点缺统一可验证发生日期/去重分母；归档至9月14日不能视作案例发生至该日。不能宣称90天完整覆盖，也不汇总重叠case_count或发明百分比。

标准知识86篇、故障案例140篇、产品料号1271篇、工具版本45篇、流程32篇、来源54篇已纳入分层检索范围；详细阅读与section hash清单在审计JSON。其余目录数量仅表示检索范围，不表示逐条技术审批。新增9月已审核引导路径来自Troubleshooter导入，按重复循环来源处理，未计独立复用证据。

## 当前排序

| 排名 | 可见症状 / 型号范围 | 维修方法 | 验证 | 状态 / 复用 | 主证据与缺口 |
|---|---|---|---|---|---|
| 1 | 机器人正确入桩仍不充电；LUBA 1 / 2 / 2X / 3 | 确认触点与桩供电；使用兼容良品分别交叉适配器和充电桩，仅更换被定位的故障件。 | 恢复稳定充电指示及该型号正常充电行为。；完整验收见下 | GUIDED；guide-no-charge | 07-标准知识/03-标准SOP/充电与回充标准SOP.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 2 | 机器人不开机；LUBA 2 / 2X / 3；LUBA 1打火观察仅PIE | 按机型检查安全钥匙/开关/座充和供电；先识别故障节点，打火、短路、进水、发热即停止并交PIE。 | 开关机和原故障条件下负载运行稳定。；完整验收见下 | GUIDED；guide-power | 07-标准知识/03-标准SOP/电池与开关机标准SOP.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 3 | 一个或多个轮子不转/运动异常；LUBA 2 / 2X / 3 | 先排机械卡阻与断电线束检查；用机型支持的电机测试定位，多个执行器同时失败转共享链路PIE检查。 | 受影响轮正常运动，适用Motor Test和原负载工况通过。；完整验收见下 | GUIDED；guide-wheel-movement | 07-标准知识/03-标准SOP/轮毂与行走标准SOP.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 4 | 多个驱动/执行器一起停转且重复通信失败；仅PIE确认主板—CAN—驱动板拓扑的精确变体；不是所有LUBA/YUKA | PIE先确认拓扑；断电检查连接器/线束，再以兼容已知良好CAN线交叉；只有仍失败且故障随驱动板移动才定位板件。 | 原负载下通信及执行器稳定；相关感知/回充分别复测，不能只凭维修台短时Pass放行。；完整验收见下 | PIE_ONLY / TOP10_PIE_GUIDED；新增管理调查项 | 07-标准知识/03-标准SOP/轮毂与行走标准SOP.md；精确机型/变体、稳定修后闭环与公开可执行范围不足，保持PIE_ONLY。 |
| 5 | 实际割草时刀盘不转或卡阻；LUBA 1 / 2 / 2X / 3；1202冻结路径除外 | 停机断电戴手套清除实物卡阻；复测实际割草；仅在电机故障及可维修总成确认后更换。 | 实际割草刀盘运动及声音正常，适用功能测试通过。；完整验收见下 | GUIDED；guide-cutting-operation | 07-标准知识/03-标准SOP/刀盘与割草标准SOP.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 6 | 回桩对位失败或到桩后无法识别；LUBA 2 / 2X / 3；两个症状保留各自卡 | 先区分进桩失败与已到桩不识别；清洁触点/IR窗口并排障，识别分支仅用兼容良品隔离桩/适配器。 | 对应分支的进桩、识别、接触与充电表现恢复稳定。；完整验收见下 | GUIDED；guide-docking, guide-station-recognition | 07-标准知识/03-标准SOP/充电与回充标准SOP.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 7 | 没有障碍物时防撞持续误触发；LUBA 2 / 2X / 3 | 先清除异物并确认回弹；仍误触发用机型支持的检查确认组件，仅换确认为故障且可单独维修的部件。 | 防撞响应正常且无误触发，安全传感器及STOP测试通过。；完整验收见下 | GUIDED；guide-bumper | 07-标准知识/03-标准SOP/传感器与防撞标准SOP.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 8 | 可见电缆或线束破损；LUBA 2 / 2X / 3 | 断电确认受损线束、精确型号及可维修性；按对应服务规程更换确认损坏段。 | 安装无挤压/连接异常，相关功能与通信通过。；完整验收见下 | GUIDED；guide-visible-cable-damage | 07-标准知识/07-机型结构/01-机械优先故障树.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 9 | 无法连接RTK基站；LUBA 2 / 2X / 3的适用RTK配置 | 先看基站电源/指示及遮挡，按机型检查兼容电源；仅换定位明确的站端故障件，站端正常转PIE。 | RTK稳定连接，原定位/地图操作通过。；完整验收见下 | GUIDED；guide-rtk-connection | 07-标准知识/03-标准SOP/定位与RTK标准SOP.md；需精确项目/目标/区域/侧别及当前SBOM才能发布SKU；无通用数量或拆装序列。 |
| 10 | LiDAR未就绪或无法正常工作；只有确认配备LiDAR的精确项目与硬件变体；PIE判定 | PIE核对硬件变体与模块状态；先检查遮挡/污染/安装；有必要时按机型断电检查连接，良品交叉前确认兼容性。 | 对应雷达自检、定位/避障及原故障场景恢复；需完成适用验收。；完整验收见下 | PIE_ONLY / TOP10_PIE_GUIDED；新增管理调查项 | 07-标准知识/03-标准SOP/视觉-雷达与X5标准SOP.md；精确机型/变体、稳定修后闭环与公开可执行范围不足，保持PIE_ONLY。 |

所有项的“仍未解决”：仍失败、复发、无法执行适用测试或证据不足时转 PIE；保留现象、交叉测试和修后结果，不自动追加换件。

## 统一验收与边界

原症状在原使用条件下消失；完成适用 Functional Test、Communication Check、AutoMap Run 三报告、Connect Checking 截图、修后最终测试的新日志；驱动板/电机/电池/电源维修另需 Burn-in 通过，换充电桩或充电极片除外。

09-14 NFF第7节明确：Communication Check报告不能由Connect Checking截图替代。工具不支持、未运行、证据缺失或任一适用项失败，不得声明维修完成。返修/有明确日志的视频未复现，不能用短时Pass将问题关单。

第6项只是管理层合并同域优先级，实际前端保留回桩与已到桩不识别两个不同症状和各自模型范围。第4项要求重复通信失败且多执行器共同异常，不把一般不开机重复算入。第10项不从雷达码直接换LiDAR。1202硬件冻结维持。

## 字段覆盖

分类指字段发布决策，不是“有无找到提及”。PUBLISH_SCOPED_NOTE=可发表范围限制说明；PRIVATE_ONLY=仅主管调查；NEEDS_SCOPE_REVIEW=证据未达到精确发布门。下表每一格的理由、值、sourcefile/section hash见hardware-top10-audit.json。精确部件工具挖掘与CONFLICT处置另见task010资源审计。

| 排名 | Part | SKU | Qty | Tool | Usage | Disassembly | Expected | Verification | Fallback |
|---|---|---|---|---|---|---|---|---|---|
| 1 | PUBLISH_SCOPED_NOTE | CONFLICT | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 2 | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 3 | PUBLISH_SCOPED_NOTE | CONFLICT | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 4 | PRIVATE_ONLY | NEEDS_SCOPE_REVIEW | NEEDS_SCOPE_REVIEW | PRIVATE_ONLY | PRIVATE_ONLY | NEEDS_SCOPE_REVIEW | PRIVATE_ONLY | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 5 | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 6 | PUBLISH_SCOPED_NOTE | CONFLICT | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 7 | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 8 | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 9 | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | NEEDS_SCOPE_REVIEW | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |
| 10 | PRIVATE_ONLY | CONFLICT | NEEDS_SCOPE_REVIEW | PRIVATE_ONLY | PRIVATE_ONLY | NEEDS_SCOPE_REVIEW | PRIVATE_ONLY | PUBLISH_SCOPED_NOTE | PUBLISH_SCOPED_NOTE |

本Top10跨型号管理表不发SKU或数量：找到了某SKU不等于绑定当前精确型号、维修目标与兼容版本。安全断电/外观检查不等于授权拆装顺序。维修工具名不跨MammoSuite/Mammotion Kit通用，模块更换后版本同步仅作为硬件维修条件。

## 候选及主要排除

共28个经归并的可观测候选，选10，排除/并入18。候选数为本轮可审计筛选清单数，不是全部知识库故障类型或工单数。

- 续航差/电池健康度下降：NEEDS_SCOPE_REVIEW；低于Top10优先级：SOH与售后判据缺精确型号、稳定修理和区域策略；不凭续航直接换电池。
- 充电提前停止/充不满：DUPLICATE；归入不充电的受限调查；无独立确诊硬件修复，不重复占位。
- 割草高度不能调整：NEEDS_SCOPE_REVIEW；硬件候选保留；当前独立模型/升降修理证据及验证成熟度低于已选卡。
- FPV黑屏/偏色：NEEDS_SCOPE_REVIEW；硬件候选保留；与LiDAR同属感知但不得共用换件路径；本轮优先新LiDAR诊断缺口。
- 可见进水/腐蚀：PRIVATE_ONLY；安全隔离与PIE定损可执行，但无稳定可复用修理终点，不能作为修复卡填数。
- 可见壳体/结构撞击损坏：NEEDS_SCOPE_REVIEW；需精确损伤总成及安全定损；不将所有撞击归于一个修理方法。
- 4G注册后无数据：PRIVATE_ONLY；多件更换仍未闭环，运营商/服务/天线和板卡混合；不直接推硬件。
- 无法连接WiFi：NOT_RELEVANT；连接配置/服务/工具混合；没有比已选硬件路径更强的稳定硬件证据。
- 蓝牙连接失败：NEEDS_SCOPE_REVIEW；核心手册有型号隔离方向，但跨工具/变体症状混合且无单一稳定修理授权。
- 固件更新失败：NOT_RELEVANT；纯软件/工具路径不进入硬件Top10；既有guide-update-failure保留。
- 地图丢失/不能加载：NOT_RELEVANT；存储/版本/地图服务混合，未确诊硬件，不能替代硬件候选。
- IoT离线/日志上传失败：NOT_RELEVANT；网络服务和工具状态不属于稳定硬件修理。
- 换主板后写号失败：NOT_RELEVANT；维修工具流程，不是独立硬件可观测故障。
- RTK固件更新失败：NOT_RELEVANT；固件更新问题不以高频为由入硬件Top10。
- 固件变更后侧灯不亮：PRIVATE_ONLY；只有相关性与换件无效观察，最终处理未回填。
- SPINO样机/充电器异常：NEEDS_SCOPE_REVIEW；机型不在当前图谱且结果未闭环，不能套用LUBA/YUKA。
- 1202刀盘卡阻独立换件：PRIVATE_ONLY；冻结仍有效；不得借实际割草通用卡放开硬件分支。
- 随机掉电/电量跳变：DUPLICATE；按可观测分支归入供电或共享通信调查；不重复计独立硬件根因。

## 审计交付

- data/hardware-top10-audit.json：排序、字段处置、限定、来源/section hash。
- artifacts/task010/source-ranking-manifest.json：只读来源before/after hash与116聚合节点指纹，不含原始工单内容。
- 新公开维修路径由实现阶段单独审核，本审计未将两个PIE项提升为自助维修。

## 最终实现与验收

本表的10项管理优先级已落实：8个GUIDED组复用9张硬件卡，2项保持PIE_ONLY；新公开维修路径0。发布9项可折叠工具/排障说明和1项始终可见的供电安全提示，按准确机型绑定为32条资源记录。新增SKU、数量、拆装序列均为0；不是未检索，而是精确范围、兼容性、数量或安全步骤尚未达到发布条件。

11张适用卡同步当前维修验收口径；原软件指导仍保留但不参与硬件排序。首页必选项仍为Model和Controlled Symptom。1202、既有型号边界与分离路径未放宽。

本文件是来源筛选与管理合同；完整应用、浏览器、生命周期和Windows包证据见[Task010最终交接报告](HANDOFF_HARDWARE_TOP10_010.md)。独立审查通过，最终本地门禁为 **TROUBLESHOOTER_HARDWARE_TOP10_GREEN**。该门禁不等于主管验收或将两项PIE调查自动提升为自助维修。

# Hardware Top 10 — Task010 主管验收报告

EC-MASTER_TASK_ID: EC-MT-20260916-HARDWARE-TOP10-010

FINAL_GATE: TROUBLESHOOTER_HARDWARE_TOP10_GREEN

本轮在有效008成果上完成010；起始工作区干净，没有需恢复的009未提交成果。依据 Issue #5 最新010任务放开旧009“仅现有成熟卡”的范围上限，但新路径仍需实际证据。结果为 **8个GUIDED管理组、复用9张硬件卡，另2个高价值问题保持PIE_ONLY**；新增公开维修路径0。管理项TOP10_GAP=0；稳定自助维修证据缺口2，没有用软件问题补位。

## 本轮达到的效果

- 首页正常流程仍是 **Model → Controlled Symptom → Repair**，必选输入2项；同一窗口逐步展开并保留已选值。错误码可选，Area不新增必选步骤。
- 9张硬件卡增加9项默认折叠的工具/排障说明，以及1项始终可见的供电安全提示。按机型展开为32条绑定记录，不是32种维修方案。安全提示在通电检查前显示。
- 原9个成熟Guidance / 10张scoped guidance cards保持；31张公开卡、25项受控症状。既有软件更新指导仍可用，但不占硬件Top10。
- 当前验收口径补入11张适用卡：适用三项测试报告、Connect Checking截图、最终测试后新日志；按实际维修对象要求Burn-in。仅更换充电桩或充电极片不强制Burn-in。缺失、未运行或失败的适用测试不能作为完成。
- 未新增SKU、数量、拆装序列或推测性换件链。32条资源均绑定卡/路径/型号/固件范围/版本/具体动作；修改选择或旧结果失效时资源一起清空。

## 来源、窗口及排序

只读工单回复助手：`C:/Users/Reggie/Desktop/ITR工单助手/工单助手交接包/ticket_assist`。

实际活动知识库：`C:/Users/Reggie/Desktop/ITR工单助手/工单助手交接包/维修与售后知识库`。按当前settings.py配置解析，未运行助手或修改其资料。

可核实的连续案例窗口为 **2026-08-18—2026-08-21，4天、13条蒸馏样本**，不是完整收单数据。技术/验收依据更新至2026-09-14。没有完整90天的事件日期与去重分母，故采用 **priority-based优先级排序，非统计频次排行**。不以文件复制日期、归档日期或重叠聚合case_count推算频率。

筛选清单28个候选，选10，排除/合并18。主要排除：纯软件更新、地图/网络服务问题；无精确维修闭环的续航、升降、FPV等；进水/撞击仍按安全定损；1202独立换件仍冻结。详细排序、逐项型号、方法、验证、fallback和90项字段处置见[硬件Top10管理表](HARDWARE_TOP10_2026-09-16.md)与[审计数据](../data/hardware-top10-audit.json)。

## 最终硬件Top10表

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

## 实际发布与保留缺口

| 范围 | 本次增加内容 | 发布边界 |
|---|---|---|
| 不充电 | 单变量兼容良品交叉；空载读数不能证明带载充电正常 | EU适配器来源冲突，SKU不发 |
| 不开机 | 区分不开机、启动后关闭、离桩关闭；安全停止条件常显 | 不从症状直接判电池 |
| 轮子不转 | 故障随电机还是测试通道变化的解释 | 不新增交换接线或无型号工具指令 |
| 多执行器同时停转且通信失败 | 主管调查方法、验证及失败转PIE记录 | PIE_ONLY，无公开板件链 |
| 实际割草刀盘不转 | 断电、手套、软刷/湿布及保护视觉部件 | 1202冻结；左右刀盘SKU范围不足 |
| 回桩 / 到桩不识别 | 断电清洁触点/IR；记录站端指示与组合 | 两张原卡保持分离 |
| 防撞误触发 | 兼容良品交叉的解释；新件不等于良品 | 密封组件不推拆散修理 |
| 线束破损 | 按功能与两端连接核对SBOM | 型号/料号冲突转PIE，不猜线束 |
| RTK连接异常 | 站端供电/状态与机器人定位分开判断 | 不合并为宽泛定位维修 |
| LiDAR未就绪 | 精确硬件变体的主管调查与验证要求 | PIE_ONLY，不因错误码自动换模块 |

每个管理项均有症状、维修/调查方法、验证和未修复后处理。Part/SKU/数量/工具/用法/拆装/预期结果/验证/fallback的逐项处置矩阵位于管理表；[资源审核](../data/hardware-resources-review.json)保留9项候选及15项未发布/冲突记录，[发布绑定](../data/hardware-step-support.json)说明实际上屏内容。[验收依据审核](../data/hardware-verification-review.json)保存当前口径和旧口径冲突处理。以上审计文件只交主管，不进入独立运行包。

仍需后续真实来源/业务输入：多执行器共享通信和LiDAR的精确变体与稳定修后闭环；精确型号/区域/目标/兼容版本对应的SKU；明确数量、安全拆装与工具能力。它们只阻止相应事实发布，不阻塞当前安全指导集。

## 逐项字段处置

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

## 本次验证

| 检查 | 新鲜结果 / 证据 |
|---|---|
| 自动化、schema、公开投影、exact/message/fuzzy/unsupported、PIE/Other/1202、模型与资源绑定 | 104/104，0失败：[日志](task010-evidence/node-tests.txt) |
| 来源窗口、排序、字段覆盖 | 28候选、10项、90字段；17来源条目和聚合指纹：[来源审计](task010-evidence/source-ranking-verification.json) |
| 简化选择 / Controlled Selection | 3 / 19项通过：[简单流程](task010-evidence/simple-knowledge-browser.json)、[受控选择](task010-evidence/controlled-browser-verification.json) |
| 两页 / 条件细化 / 服务资源 / 单面板 | 32 / 3 / 3及单面板通过：[两页](task010-evidence/two-page-verification.json)、[条件](task010-evidence/refinement-verification.json)、[资源](task010-evidence/service-browser-verification.json)、[单面板](task010-evidence/single-panel-browser.txt) |
| 原Stable Guidance | 21项通过：[结果](task010-evidence/stable-browser-verification.json) |
| 本轮硬件资源与状态 | 27项；9张卡×1366×768、1920×1080、390×844，折叠/展开/旧结果失效/无横向溢出：[结果](task010-evidence/hardware-browser-verification.json) |
| 实际Windows Edge 125% | 1366×768与1920×1080，全部10张scoped guides；页面异常0、外部请求0：[结果](task010-evidence/zoom-verification.json) |
| 生命周期 | 8806端口两轮启动→停止→重启，退出的仅本轮子进程：[结果](task010-evidence/lifecycle-verification.json) |
| 独立包、隐私、运行时、资源一致性 | 11项白名单、runtime/node.exe存在；全部解压条目hash一致，六项HTTP资源一致；启动器启动/复用通过：[结果](task010-evidence/package-verification.json) |
| 独立审查 | [最终独立审查](FINAL_HARDWARE_TOP10_REVIEW_2026-09-16.md) |

生命周期首次使用默认8796时发现已有本机实例占用，未停止它；改用独立8806完成两轮复验。包测试用8797/8840，仅清理本轮拥有的进程。MAIN/8787、生产系统、Reply Assistant状态均未修改。

浏览器截图：[125%首页](task010-evidence/zoom125-1920-home.png)、[125%供电安全与指导](task010-evidence/zoom125-1366-guide-power.png)、[硬件详情完整页](task010-evidence/hardware-1366-guide-power.png)。首屏保持简洁，细节可展开；125%下允许正常纵向滚动。

## 独立包与交付范围

知识版本：`2026-09-16-hardware-top10.1`。

本地ZIP：`C:/Users/Reggie/Desktop/PIE-ITR-ErrorCode/error-code-pilot/artifacts/error-code-pilot-20260916-005145.zip`

SHA256：`cf3260b7662bb7df28945741ae1269d0b4b5af10e6a3771d1bc6dbfbb8fad1dd`

本次按任务生成并验证本地独立包；没有发给同事或公开部署。GitHub仅提交专项代码、管理审计和测试证据；沿用Error Code专项分支，不合并main，不写Issue #3。MASTER_PLAN / AGENT_REGISTRY未改变：负责人、task/report channel及隔离规则均未变化。

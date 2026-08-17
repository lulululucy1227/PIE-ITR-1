# 飞书多维表格里各单选字段的可选项（用于约束模型输出）

DISTI_DEALER = [
    "Alpex", "MowerMagic", "Mina", "RizenTech", "Wekato", "Medjimurka", "Robot24",
    "Datanova DK", "MultiTec", "Davidmag", "LysterLawn", "CDPM", "Treerain", "Aflverlar",
    "Berema", "Datanova SE", "Greenlook", "Fowa", "iRobotics", "Deinmaher", "Blakar",
    "SuomiTrading", "Everest", "PAB", "Dach Dealer", "ASYST automatisierungs-systeme",
    "Superservice Handelsagentur GmbH", "Vogl Motorist", "Handel Meier GmbH",
    "Pamberger Landmaschinentechnik Gmb", "L&L-Lenksysteme GmbH (Mowy)", "Kreisel OG",
    "Pölzl GmbH", "Dorner GmbH", "Ademax Deutschland GmbH & Co. KG", "Börger GmbH",
    "Müllenhoff GmbH", "deinmäher.de GmbH", "BVA Ingolf Müller GmbH", "Online-Handel-Breuer",
    "Mähroboter Experte Rottenburg", "Horst Staiger & Söhne GmbH", "Netherlands Dealer",
    "CINNO-PL", "New-Ouda", "BSR-DE", "CINNO-DE", "lTR",
]
# 注：经销商选项以飞书字段为准，运行时由 feishu_api.get_select_field_options 实时读取；
# 上面这份仅作离线回退用，可能不完整。

# 发件人别名 / 电话号 → 飞书 Disti 字段里的规范经销商名。
# 这是人工维护的确定性规则，命中后直接覆盖 AI 的判断（比模型猜测可靠）。
# 电话号匹配时会自动忽略空格和横线。新增规则直接往下加即可。
DEALER_ALIASES = {
    "qianwen li":        "BSR-DE",
    "lihain":            "New-Ouda",
    "+447355292412":     "MowerMagic",
    "eddie":             "deinmäher.de GmbH",
    "+49 160 95894890":  "deinmäher.de GmbH",
    "notes.ee":          "Okomi",
    "okomi":             "Okomi",
    "pab servis":        "PAB",
    "+386 40 232 257":   "PAB",
    "blanka":            "Blakar",
    "+36 30 863 9721":   "Treerain",
}

# 型号识别补充规则：正则命中就强制用指定的 Model Type（覆盖 AI 判断）。
# 起因：「LUBA 2 AWD 3000X EU」这类带 X 后缀的属于 2X 系列，
# AI 容易只看到 "LUBA 2" 就误选 LUBA 2。按顺序匹配，命中第一条即用。
# ⚠ 右侧的值必须和飞书 Model Type 字段里的规范标签完全一致（大小写、空格）。
MODEL_RULES = [
    (r"luba\s*2\s*x",                          "LUBA 2X"),  # 直接写 LUBA 2X
    (r"luba\s*2\b[^\n]{0,20}?\d{3,5}\s*x\b",   "LUBA 2X"),  # LUBA 2 AWD 3000X EU
]

STATUS = ["Open", "Processing", "Closed", "Replied"]

MODEL_TYPE = [
    "luba 2", "luba 2x", "luba mini", "luba mini lidar", "yuka", "yuka mini",
    "Luba 3 1500", "luba 3 3000 -> 10000", "luba mini 2 1500", "luba mini 2 1000",
    "yuka mini 2 1000 / 600", "yuka mini 2 800", "luba 1", "Spino E1",
    "luba 3 5000", "8nx", "luba3",
]

PIE_CATEGORY = [
    "Account & Permission",
    "MammoSuite",
    "Mammotion Kit",
    "Connection & Communication",
    "Spare Parts / Part Numbers / SBOM / Compatibility",
    "Hardware Failure / Repair Diagnosis",
    "Warranty / Scrap / Damage Assessment Process",
    "Training / Documentation / Issue Escalation",
]

PIE_ISSUE_TYPE = [
    # Account & Permission
    "Account Creation", "Login Failure", "ID Error", "User Not Exist",
    "Insufficient Permission", "Password Reset", "Binding / Unbinding Issue",
    # MammoSuite
    "Suite Login Issue", "Suite Device Connection Issue", "Suite Version Compatibility Issue",
    "Functional Test Issue", "Auto Map Run Issue", "Battery Test / SOH",
    "Boundary Map / Map Visualization Request", "Suite Log Upload", "Suite UI Bug",
    # Mammotion Kit
    "Kit Login / Permission Issue", "Kit Device Connection Issue", "Kit Version Update Issue",
    "Mainboard Flashing Issue", "Device Name Flashing Issue", "Motor Flag Flashing",
    "RTK Firmware Update Issue", "Robot Firmware Update Issue", "Kit Log Upload",
    # Connection & Communication
    "Bluetooth Connection Failure", "Wi-Fi / Network Connection Failure", "4G / SIM Issue",
    "USB / Type-C / Wired Connection", "Failed to Read Device Information",
    "RTK / LoRa Communication Failure",
    # Spare Parts
    "SBOM Inquiry", "Part Number Inquiry", "Missing Part Number",
    "Alternative Parts / Old-New Part Difference", "Compatibility Confirmation",
    "Common Spare Parts List", "Test Board / Adapter Tool",
    # Hardware Failure
    "Hub Motor / Wheel / Drive Board", "Mainboard / Control Board",
    "Vision / Camera / LiDAR / iNavi / Positioning Module / X3 Board / X5 Board",
    "Battery / Charging / Power Supply / Docking Issue", "Cutting Disc / Cutting Motor",
    "Safety Key / Bumper / IR", "Cable / Ribbon Cable / Connector",
    "Grass Collection Box / Roller Brush / Accessory Module",
    # Warranty / Scrap
    "Damage Assessment", "Scrap Confirmation", "Warranty Coverage Confirmation",
    "Replacement / Refund Process", "Return-to-Customer Confirmation After Repair",
    "Service Handling Due to Spare Parts Shortage",
    # Training / Escalation
    "Disassembly Manual", "Repair Training", "Tool Usage Guidance",
    "Structural Feedback", "Issue Escalation", "R&D Escalation",
]

# Fault Symptom（多选）——设备故障现象标签，可多选；非故障类工单（账号开通/知识咨询/兼容性问询等）留空
FAULT_SYMPTOM = [
    "不开机", "不充电", "连不上WIFI/4G", "连不上RTK", "蓝牙连接失败",
    "定位失败", "无法回桩", "工作中异常停机", "碰撞/传感器误触发",
    "割草盘故障", "行走系统故障", "集草框/滚刷不工作", "视觉/摄像头异常",
    "激光雷达故障", "电池/供电异常", "排线/线缆故障", "固件升级失败",
    "账号/登录异常", "地图异常", "充电异常", "定位异常",
]

# Error Code（多选）——只允许 ITR 表里已存在的这 17 个错误码选项；
# 其余错误码（含图片里的）由 scan_errors.py 单独处理，不在此自动填写
ERROR_CODE = [
    "392", "609", "619", "1004", "1028", "1030", "1100", "1200", "1201",
    "1202", "1207", "1217", "1000020", "5501", "6001605", "40103", "E58012",
]

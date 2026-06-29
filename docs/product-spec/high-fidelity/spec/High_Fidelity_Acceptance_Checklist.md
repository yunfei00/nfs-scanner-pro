# 高保真验收清单 — Release 010.5 候选定稿

Release 010（扫描页定稿）+ Release 010.5（四页统一 + 状态补全）· **候选定稿版（v1.0 Final Candidate）**

> 扫描：[index.html](../../../../prototypes/high_fidelity/index.html) · 设备：[device.html](../../../../prototypes/high_fidelity/device.html) · 分析：[analysis.html](../../../../prototypes/high_fidelity/analysis.html) · 报告：[report.html](../../../../prototypes/high_fidelity/report.html)

## 验收项

| # | 检查项 | 通过标准 | 结果 |
|---|---|---|---|
| 1 | **扫描页完成** | index.html 定稿；PCB 未缩小；布局未大改 | ✅ |
| 2 | **设备页完成** | 四设备卡片 + 设备配置 Dock + 操作入口清晰 | ✅ |
| 3 | **分析页完成** | PCB 视觉与扫描页一致；径向热力图；芯片/焊盘/走线/过孔 | ✅ |
| 4 | **报告页完成** | 列表 + PDF 风预览；PCB+热力图缩略图（非纯渐变块） | ✅ |
| 5 | **准备就绪状态** | [01_Ready_State.md](../states/01_Ready_State.md) | ✅ |
| 6 | **扫描中状态** | [02_Scanning_State.md](../states/02_Scanning_State.md) | ✅ |
| 7 | **完成状态** | [03_Completed_State.md](../states/03_Completed_State.md) | ✅ |
| 8 | **设备异常状态** | [04_Device_Error_State.md](../states/04_Device_Error_State.md) | ✅ |
| 9 | 四页简体中文 | 无英文主界面文案（标识符 ST-001 等除外） | ✅ |
| 10 | 四页无左侧「项目」 | 导航仅扫描/设备/分析/报告 | ✅ |
| 11 | **统一主窗口框架** | 菜单栏/工具栏 64px/设备状态栏/导航/Dock/状态栏一致 | ✅ |
| 12 | 导航 64↔180px | 默认仅图标；Hover 展开；无设置/帮助/项目 | ✅ |
| 13 | 无浏览器滚动条 | body overflow hidden；1920×1080 scale | ✅ |
| 14 | Dock 不被遮挡 | 内部滚动；底部状态栏不覆盖内容 | ✅ |
| 15 | 日志/频谱/统计隐藏 | 四页均不默认显示 | ✅ |
| 16 | 无外部依赖 | 无 CDN/外链 | ✅ |
| 17 | **可进入 Release_011** | 010 + 010.5 视觉闭环完整 | ✅ |

## 验证步骤

1. 依次全屏打开四页 HTML，确认框架一致
2. 确认分析页 PCB 细节与扫描页风格一致
3. 确认报告预览缩略图为 PCB + 热力图 SVG
4. 确认无浏览器纵向/横向滚动条
5. 阅读 states/ 四份状态说明

## 结论

**17/17 通过** — Release 010.5 标记为 **候选定稿版**，可进入 **Release 011 MainWindow PySide6 Prototype**。

## Release 011 门禁

- 视觉输入：**Release 010 + Release 010.5**（禁止仅用 AI 图片）
- ADR-0022、ADR-0023 Accepted
- 011 不重画扫描页 PCB 尺寸

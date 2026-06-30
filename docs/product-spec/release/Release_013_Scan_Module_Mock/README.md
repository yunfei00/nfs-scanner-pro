# Release 013 — Scan Module Mock

## 1. Release 目标

在 **Release 011 主窗口** 与 **Release 012 设备页** 基础上，将扫描页升级为 **Scan Module Mock**：Mock 扫描状态机、开始/停止交互、进度与坐标更新、画布当前点高亮、参数 Dock 只读切换。**不接真实设备，不做真实扫描**。

## 2. 本次实现范围

- 扫描状态机：`未就绪 / 准备就绪 / 扫描中 / 停止中 / 已完成 / 错误`（默认准备就绪）
- 工具栏「开始扫描 / 停止扫描」Mock 行为（QTimer 驱动）
- 底部状态栏动态更新：状态、进度、扫描点、预计剩余时间
- 画布：当前扫描点高亮、已扫描区域轻量 Mock、坐标浮窗随点变化、完成提示 2 秒
- 右侧扫描参数 Dock：扫描中锁定，完成/停止后恢复可编辑
- Mock 数据：`SCAN_TOTAL_POINTS`、`SCAN_START/END_POSITION`、`SCAN_STEP` 等

## 3. 本次不做什么

- ❌ 串口 / 运动平台 / 频谱仪 / 相机 / 舵机控制
- ❌ 真实扫描线程、raw 写盘、热力图算法
- ❌ 修改设备页 / 分析页 / 报告页结构
- ❌ 修改 frameless 标题栏、左侧导航、high_fidelity HTML

## 4. 输入规范

- Release 011：[Release_011_MainWindow_PySide6_Prototype/README.md](../Release_011_MainWindow_PySide6_Prototype/README.md)
- Release 012：[Release_012_Device_Module_Mock/README.md](../Release_012_Device_Module_Mock/README.md)
- 扫描状态机：[domain/04_State_Machines/Scan_State_Machine.md](../../domain/04_State_Machines/Scan_State_Machine.md)
- ScanTask 生命周期：[domain/05_Lifecycle/ScanTask_Lifecycle.md](../../domain/05_Lifecycle/ScanTask_Lifecycle.md)
- 扫描页高保真：[high-fidelity/pages/01_Scan_Page.md](../../high-fidelity/pages/01_Scan_Page.md)

## 5. 输出文件

```text
src/nfs_scanner_pro/ui/scan_state.py
src/nfs_scanner_pro/ui/scan_task_mock.py
src/nfs_scanner_pro/ui/pages/scan_page.py
src/nfs_scanner_pro/ui/scan_canvas_view.py
src/nfs_scanner_pro/ui/scan_parameter_dock.py
src/nfs_scanner_pro/ui/main_window.py
src/nfs_scanner_pro/ui/mock_data.py
src/nfs_scanner_pro/resources/styles/dark_theme.qss
docs/product-spec/release/Release_013_Scan_Module_Mock/README.md
```

## 6. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

1. 默认进入扫描页
2. 点击工具栏「开始扫描」观察进度、坐标、画布高亮
3. 扫描中点击「停止扫描」或等待自动完成

## 7. 验收标准

- [ ] `python scripts/run_mock_ui.py` 可启动
- [ ] 开始扫描 → 状态「扫描中」，进度/点数增长
- [ ] 坐标浮窗与画布当前点随 Mock 更新
- [ ] 扫描中右侧参数只读/禁用
- [ ] 停止扫描 → 状态「已停止」，参数恢复可编辑
- [ ] 扫完 6461 点 → 100%，「扫描完成」提示
- [ ] 非扫描页点击开始 → 「请切换到扫描页后开始扫描」
- [ ] 设备页 / 报告页布局未破坏
- [ ] `python -m compileall src/nfs_scanner_pro` 通过

## 8. 后续 Release_014 建议

- **分析页 Mock**：热力图切换、迹线选择、统计面板占位
- **暂停/继续** 扫描态（对齐 Scan_State_Machine 七态中的 Paused）
- **未就绪** 态与设备页联动 Mock（设备断开 → 扫描不可开始）
- **日志 Dock** Mock：扫描状态转换写入日志面板

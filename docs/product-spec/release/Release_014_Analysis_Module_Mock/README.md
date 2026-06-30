# Release 014 — Analysis Module Mock

## 1. Release 目标

在 **Release 011~013** 主窗口与扫描 Mock 基础上，将分析页升级为 **Analysis Module Mock**：PCB + 热力图画布、Trace/频率/LUT/显示参数 Mock、光标读数、导出占位。**不接真实设备，不实现真实算法**。

## 2. 本次实现范围

- 分析页画布：复用 PCB Mock + 热力图 + 色带 + 小地图 + 十字线 + 光标浮窗
- 右侧「分析参数」Dock：数据源 / 显示设置 / 光标 / 导出 / 高级
- Trace、频率、显示模式、LUT、vmin/vmax、透明度 Mock 联动
- 光标读数面板：锁定、复制（仅状态栏 Mock）
- 导出按钮：仅更新状态栏，不生成文件
- 分析页工具栏 Mock 提示（网格切换、拍照拒绝等）
- Mock 数据：`ANALYSIS_TASK`、`ANALYSIS_CURSOR`、`ANALYSIS_TRACES`、`ANALYSIS_FREQUENCIES`

## 3. 本次不做什么

- ❌ 真实频谱分析 / 热力图计算 / 数据读盘
- ❌ 真实报告生成 / 剪贴板 / 文件导出
- ❌ 修改扫描状态机、设备页、报告页结构
- ❌ 修改 frameless、导航、high_fidelity HTML

## 4. 输入规范

- Release 011：[Release_011_MainWindow_PySide6_Prototype/README.md](../Release_011_MainWindow_PySide6_Prototype/README.md)
- Release 013：[Release_013_Scan_Module_Mock/README.md](../Release_013_Scan_Module_Mock/README.md)
- 分析状态机：[domain/04_State_Machines/Analysis_State_Machine.md](../../domain/04_State_Machines/Analysis_State_Machine.md)
- 分析页高保真：[high-fidelity/pages/analysis/Analysis_Page_High_Fidelity.md](../../high-fidelity/pages/analysis/Analysis_Page_High_Fidelity.md)

## 5. 输出文件

```text
src/nfs_scanner_pro/ui/analysis_state.py
src/nfs_scanner_pro/ui/analysis_mock.py
src/nfs_scanner_pro/ui/pages/analysis_page.py
src/nfs_scanner_pro/ui/scan_canvas_view.py
src/nfs_scanner_pro/ui/main_window.py
src/nfs_scanner_pro/ui/mock_data.py
src/nfs_scanner_pro/ui/widgets/analysis_control_panel.py
src/nfs_scanner_pro/ui/widgets/cursor_readout_panel.py
src/nfs_scanner_pro/ui/widgets/lut_selector.py
src/nfs_scanner_pro/resources/styles/dark_theme.qss
docs/product-spec/release/Release_014_Analysis_Module_Mock/README.md
```

## 6. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

左侧点击「分析」，切换 Trace/频率/LUT，拖动透明度滑块，移动鼠标观察光标读数。

## 7. 验收标准

- [ ] 分析页 PCB + 热力图 + 十字线 + 小地图
- [ ] 右侧 Dock「分析参数」五分组
- [ ] Trace / 频率 / 模式 / LUT / 透明度 Mock 切换
- [ ] 光标读数 X/Y/Z/频率/幅度/相位
- [ ] 导出按钮仅更新状态栏
- [ ] 不破坏扫描页 / 设备页

## 8. 后续 Release_015 建议

- **报告页 Mock**：报告预览、PDF/Word 导出占位、报告设置 Dock 联动
- **分析 ↔ 扫描联动**：扫描完成后自动 Mock 加载 Heatmap
- **频谱 Dock Mock**：底部频谱面板静态曲线
- **日志 Dock Mock**：分析/扫描状态转换写入日志

# Release 015 — Report Module Mock

## 1. Release 目标

在 **Release 011~014** 主窗口与 Mock 模块基础上，将报告页升级为 **Report Module Mock**：报告列表、PDF 风预览、报告设置 Dock、工具栏导出 Mock。**不生成真实文件**。

## 2. 本次实现范围

- 报告列表三条 Mock，点击更新预览与状态栏
- 白色 PDF 预览：基本信息、PCB+热力图缩略图、结论摘要
- 右侧「报告设置」Dock：模板 / 导出 / 内容 / 高级
- 报告页工具栏：新建报告 / 预览 / 导出 PDF·Word·Excel
- `ReportMock` + QTimer 导出状态 Mock
- 沿用单一 `rightDock` + `QStackedWidget`，不新增 QDockWidget

## 3. 本次不做什么

- ❌ 真实 PDF / Word / Excel 生成
- ❌ 真实报告引擎 / 扫描数据读盘
- ❌ 修改扫描状态机、设备页、分析页结构
- ❌ 修改 frameless、导航、high_fidelity HTML

## 4. 输入规范

- Release 011：[Release_011_MainWindow_PySide6_Prototype/README.md](../Release_011_MainWindow_PySide6_Prototype/README.md)
- Release 014：[Release_014_Analysis_Module_Mock/README.md](../Release_014_Analysis_Module_Mock/README.md)
- 报告状态机：[domain/04_State_Machines/Report_State_Machine.md](../../domain/04_State_Machines/Report_State_Machine.md)
- 报告页高保真：[high-fidelity/pages/report/Report_Page_High_Fidelity.md](../../high-fidelity/pages/report/Report_Page_High_Fidelity.md)

## 5. 输出文件

```text
src/nfs_scanner_pro/ui/report_state.py
src/nfs_scanner_pro/ui/report_mock.py
src/nfs_scanner_pro/ui/pages/report_page.py
src/nfs_scanner_pro/ui/report_settings_dock.py
src/nfs_scanner_pro/ui/main_window.py
src/nfs_scanner_pro/ui/mock_data.py
src/nfs_scanner_pro/ui/widgets/report_list_panel.py
src/nfs_scanner_pro/ui/widgets/report_preview_panel.py
src/nfs_scanner_pro/resources/styles/dark_theme.qss
docs/product-spec/release/Release_015_Report_Module_Mock/README.md
```

## 6. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

左侧点击「报告」，选择列表项，使用工具栏导出 Mock。

## 7. 验收标准

- [ ] 报告列表 3 条，点击更新预览
- [ ] PDF 风预览含热力图缩略图与结论
- [ ] 右侧「报告设置」四分组
- [ ] 工具栏报告按钮 Mock 状态栏
- [ ] 切换扫描页工具栏恢复
- [ ] 仅 1 个 QDockWidget（rightDock）
- [ ] compileall 通过

## 8. 后续 Release_016 建议

- **项目文件菜单 Mock**：新建/打开/保存项目文件夹占位
- **日志 / 频谱 Dock Mock**：底部面板静态内容
- **扫描→分析→报告联动**：扫描完成后 Mock 自动生成报告草稿

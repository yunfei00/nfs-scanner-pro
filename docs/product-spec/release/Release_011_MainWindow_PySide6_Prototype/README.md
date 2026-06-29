# Release 011 — MainWindow PySide6 Prototype

## 1. Release 目标

将 **Release 010 高保真设计** 落地为可运行的 **PySide6 主窗口 Mock 原型**，用于视觉对齐与后续业务开发前的 UI 壳层验收。

| 产出 | 路径 |
|---|---|
| 应用入口 | [src/nfs_scanner_pro/main.py](../../../../src/nfs_scanner_pro/main.py) |
| 启动脚本 | [scripts/run_mock_ui.py](../../../../scripts/run_mock_ui.py) |
| QSS 主题 | [src/nfs_scanner_pro/resources/styles/dark_theme.qss](../../../../src/nfs_scanner_pro/resources/styles/dark_theme.qss) |
| UI 模块 | [src/nfs_scanner_pro/ui/](../../../../src/nfs_scanner_pro/ui/) |

## 2. 输入规范

须同时参考：

- Release 008 线框尺寸：[ui-wireframe/01_Main_Window_1920x1080.md](../../ui-wireframe/01_Main_Window_1920x1080.md)
- Release 009.5 Design System：[design-system/](../../design-system/README.md)
- Release 010 高保真：[high-fidelity/](../../high-fidelity/README.md) · [prototypes/high_fidelity/](../../../../prototypes/high_fidelity/)
- ADR-0022：[ADR-0022-High-Fidelity-Before-PySide6.md](../../decision/ADR-0022-High-Fidelity-Before-PySide6.md)

## 3. 本次实现范围

- QMainWindow 主窗口（默认 1600×1000，启动最大化）
- 菜单栏 / 工具栏 / 设备状态栏 / 底部状态栏
- 左侧 64px 图标导航，Hover 180px 展开
- 中央 QGraphicsView PCB 画布 Mock（整图热力图 QPixmap 叠加）
- 色带、小地图、坐标浮窗、扫描区域手柄 Mock
- 右侧 QDockWidget 扫描参数面板（360px）
- 视图菜单「显示参数面板」控制 Dock 显隐
- Mock 数据（CPU_Area、6461 pts 等）

## 4. 本次不做什么

- ❌ 真实串口 / 频谱仪 / 相机 / 运动控制
- ❌ 真实扫描线程与热力图算法
- ❌ 数据持久化 / 数据库
- ❌ 左侧「项目」导航；日志/频谱/统计默认显示
- ❌ 逐格绘制热力图
- ❌ 修改 Release 010 高保真原型

## 5. 输出文件

```text
src/nfs_scanner_pro/
  __init__.py
  main.py
  ui/
    main_window.py
    navigation_bar.py
    device_status_bar.py
    scan_canvas_view.py
    scan_parameter_dock.py
    status_bar.py
    mock_data.py
  resources/styles/dark_theme.qss
scripts/run_mock_ui.py
docs/product-spec/release/Release_011_MainWindow_PySide6_Prototype/README.md
```

## 6. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

## 7. 验收标准

| # | 项 | 标准 |
|---|---|---|
| 1 | 可启动 | `python scripts/run_mock_ui.py` 正常打开窗口 |
| 2 | 简体中文 | 全部 UI 主文案为中文 |
| 3 | 导航 | 仅扫描/设备/分析/报告；无「项目」 |
| 4 | Hover 导航 | 64px → 180px 动画 |
| 5 | 项目入口 | 仅在「文件」菜单 |
| 6 | 设备状态栏 | 单行四设备 + 元数据 |
| 7 | 参数 Dock | QDockWidget，360px |
| 8 | 画布 | QGraphicsView + 整图热力图 |
| 9 | 默认隐藏 | 日志/频谱/统计不默认显示 |
| 10 | 视图菜单 | 「显示参数面板」可切换 Dock |
| 11 | Mock only | 无真实设备代码 |
| 12 | QSS | dark_theme.qss 生效 |
| 13 | 视觉 | 接近 Release 010 高保真 |

## 8. 后续 Release 012 建议

- ScanTask 七态状态机驱动工具栏 enabled/disabled
- 设备页 Mock 连接流程（仍不接真实硬件）
- 日志 / 频谱 / 统计 Dock 壳层与视图菜单联动
- 项目文件夹 Mock 读写（project.json）
- 单元 / smoke UI 测试

---

**依赖**：Release 008、009.5、009.8、009.9、010  
**任务入口**：[spec/Task_Guide/Build_MainWindow.md](../../../spec/Task_Guide/Build_MainWindow.md)

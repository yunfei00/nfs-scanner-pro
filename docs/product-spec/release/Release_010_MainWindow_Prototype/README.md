# Release 010 — MainWindow Prototype

## 1. Release 目标

在 **不接真实设备、不实现扫描业务** 的前提下，交付可运行的 **PySide6 企业级主窗口 Mock 原型**，严格遵循 Release 008~009.9 的 UI / Qt / ADR 约束。

## 2. 本次实现范围

| 组件 | 说明 |
|---|---|
| QMainWindow | 标题「近场扫描系统」，默认 1600×1000 |
| 菜单栏 | 文件 / 编辑 / 视图 / 工具 / 设置 / 帮助（简体中文） |
| 工具栏 | 开始扫描、停止扫描、拍照、区域对齐、网格、测量 |
| 左侧导航 | 扫描 / 设备 / 分析 / 报告；56px 图标，Hover 180px |
| 设备状态栏 | 单行四设备 + 探头/高度/区域/频率/点数 |
| 中央画布 | QGraphicsView + 整图热力图 QPixmap 占位 |
| 参数 Dock | QDockWidget 340px，扫描/区域设置 Mock |
| 底部状态栏 | 状态、进度、点数、剩余时间、日期时间 |
| 视图菜单 | 「显示参数面板」可切换 Dock 显隐 |
| Mock 数据 | `src/nfs_scanner_pro/ui/mock_data.py` |

## 3. 不做什么

- ❌ 真实串口 / 频谱仪 / 相机 / 舵机
- ❌ 扫描线程、热力图算法、文件持久化
- ❌ 左侧「项目」导航
- ❌ 默认显示日志 / 频谱 / 统计 Dock
- ❌ 逐格绘制热力图
- ❌ 修改历史 Release 文档结构

## 4. 输入规范

实现前必读（见 [spec/Task_Guide/Build_MainWindow.md](../../../../spec/Task_Guide/Build_MainWindow.md)）：

- `spec/AI_INDEX.md`
- `spec/Registry/UI.yaml`、`Qt.yaml`
- `docs/product-spec/ui-wireframe/`
- `docs/product-spec/design-system/02_Components/`
- `docs/product-spec/design-system/07_Qt_Implementation/`

## 5. 输出文件

```text
src/nfs_scanner_pro/
├── main.py
└── ui/
    ├── main_window.py
    ├── navigation_bar.py
    ├── device_status_bar.py
    ├── scan_canvas_view.py
    ├── scan_parameter_dock.py
    └── mock_data.py
src/nfs_scanner_pro/resources/styles/dark_theme.qss
scripts/run_mock_ui.py
requirements.txt
```

## 6. 运行方式

```bash
pip install -r requirements.txt
python scripts/run_mock_ui.py
```

或：

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

## 7. 验收标准

- [ ] PySide6 主窗口可启动
- [ ] 全部 UI 文案简体中文
- [ ] 左侧无「项目」；项目在文件菜单
- [ ] 导航 56px / Hover 180px 动画
- [ ] 设备状态栏单行
- [ ] 中央 QGraphicsView；热力图单 QPixmapItem
- [ ] 参数 Dock 为 QDockWidget；视图菜单可隐藏
- [ ] 日志 / 频谱 / 统计不默认显示
- [ ] 无真实设备与扫描逻辑

## 8. 后续 Release_011 建议

- 完善 log / spectrum / statistics Dock 内容与视图菜单联动
- QSS 与 Design Token 自动对照测试
- Mock ScanTask 七态驱动工具栏 enabled 态
- 单元测试：objectName 快照、导航宽度动画
- 可选：打包脚本与 CI smoke test

---

**状态**：In Progress  
**依赖**：Release 008、009、009.5、009.8、009.9  
**AI 入口**：[spec/AI_INDEX.md](../../../../spec/AI_INDEX.md)

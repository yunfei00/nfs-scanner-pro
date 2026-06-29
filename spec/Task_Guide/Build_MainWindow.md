# Build MainWindow — Release 011 主窗口 PySide6 原型

## 任务目标

实现 **PySide6 QMainWindow Mock 壳层**：对齐 Release 010 / 010.5 高保真视觉，包含左侧导航、顶栏菜单/工具栏、设备状态栏、**四页**中央工作区、右侧按页切换 Dock、底部状态栏。**不接真实设备，不实现扫描业务**，Mock 数据即可。

## 开始前必须阅读

1. [spec/AI_INDEX.md](../AI_INDEX.md)
2. [spec/Registry/UI.yaml](../Registry/UI.yaml)
3. [spec/Registry/Qt.yaml](../Registry/Qt.yaml)
4. [spec/Context_Pack/UI_Context.md](../Context_Pack/UI_Context.md)
5. [docs/product-spec/release/Release_010_High_Fidelity_Design/README.md](../../docs/product-spec/release/Release_010_High_Fidelity_Design/README.md)
6. [docs/product-spec/high-fidelity/main-window/01_Main_Window_High_Fidelity_Spec.md](../../docs/product-spec/high-fidelity/main-window/01_Main_Window_High_Fidelity_Spec.md)
7. [prototypes/high_fidelity/index.html](../../prototypes/high_fidelity/index.html)（视觉对照）
8. [docs/product-spec/ui-wireframe/01_Main_Window_1920x1080.md](../../docs/product-spec/ui-wireframe/01_Main_Window_1920x1080.md)
9. 组件规范：
   - [NavigationBar.md](../../docs/product-spec/design-system/02_Components/NavigationBar.md)
   - [06_Toolbar_System.md](../../docs/product-spec/design-system/06_Toolbar_System.md)
   - [DockPanel.md](../../docs/product-spec/design-system/02_Components/DockPanel.md)
   - [StatusBar.md](../../docs/product-spec/design-system/02_Components/StatusBar.md)
   - [Qt_GraphicsView_Rules.md](../../docs/product-spec/design-system/07_Qt_Implementation/Qt_GraphicsView_Rules.md)
10. [docs/product-spec/qt-spec/02_Qt_Object_Names.md](../../docs/product-spec/qt-spec/02_Qt_Object_Names.md)

## 运行

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

入口代码：`src/nfs_scanner_pro/main.py`

## 不要阅读的内容

- 整个 `docs/product-spec/domain/`（本任务只需 UI 壳层）
- 设备驱动、频谱仪 SDK、运动控制实现细节
- `docs/product-spec/data/` 全量（除非 Mock 项目路径）
- 旧版 `wireframe/` 文字线框（以 `ui-wireframe/` 为准）

## 允许修改的目录

- `src/nfs_scanner_pro/`（UI 包与 QSS）
- `scripts/run_mock_ui.py`
- `docs/product-spec/release/Release_011_MainWindow_PySide6_Prototype/`（Release 说明）
- `spec/Registry/Release.yaml`、`spec/AI_INDEX.md`（索引同步）

## 禁止修改的目录

- `prototypes/high_fidelity/`（Release 010 已定稿）
- 已有 ADR 正文（除非用户明确要求）

## 实现步骤

1. **QMainWindow 骨架**：菜单栏（文件/编辑/视图/工具/设置/帮助）、central widget。
2. **左侧 NavigationBar**：仅四项——扫描、设备、分析、报告；64px 默认，Hover 180px。
3. **文件菜单**：新建/打开/保存项目（Mock 对话框即可）。
4. **视图菜单**：「显示参数面板」控制当前页 Dock；日志/频谱/统计 **默认隐藏**。
5. **工具栏**：扫描/设备/分析页 Mock 扫描动作；报告页 Mock 导出动作。
6. **设备状态栏**：单行四设备 + 探头/区域/频率/点数。
7. **四页 QStackedWidget**：扫描（QGraphicsView）、设备（四卡片）、分析（PCB+热力图）、报告（列表+预览）。
8. **中央 QGraphicsView + QGraphicsScene**：深绿 PCB Mock；热力图 **QGraphicsPixmapItem** 整图叠加。
9. **右侧 Dock**：扫描参数 / 设备配置 / 分析参数 / 报告设置，按页切换。
10. **底部 QStatusBar**：按页 Mock 状态与统计。
11. **objectName**：按 qt-spec / Qt_ObjectName_Rules。
12. **QSS**：`resources/styles/dark_theme.qss`，Fusion + Token。

## 验收标准

- [ ] `python scripts/run_mock_ui.py` 可启动
- [ ] 四页可切换，工具栏/状态栏/Dock 联动
- [ ] 左侧仅四个一级模块，无「项目」页
- [ ] 项目操作仅在文件菜单
- [ ] 日志/频谱/统计默认不可见
- [ ] QGraphicsView 为主画布，热力图整图 QPixmap
- [ ] 所有关键控件有 objectName
- [ ] 无真实设备连接代码
- [ ] 无 ScanTask 状态机业务逻辑（按钮 Mock 即可）

## 常见错误

| 错误 | 正确做法 |
|---|---|
| 左侧加「项目」导航 | Project 仅文件菜单 + 文件夹模型 |
| 启动即显示日志 Dock | 视图菜单控制，默认隐藏 |
| 热力图逐格 QGraphicsRectItem | 整张 QPixmap/QImage 一次绘制 |
| 跳过线框/高保真自由改比例 | 以 010 高保真 + 008 线框为准 |
| 修改 prototypes/high_fidelity | 010 已定稿，011 只写 PySide6 |

## 推荐 commit message

```
feat(ui): add Release 011 MainWindow PySide6 mock prototype

Mock-only QMainWindow aligned with Release 010 high-fidelity design.
No device or scan business logic.
```

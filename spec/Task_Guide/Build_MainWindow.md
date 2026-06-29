# Build MainWindow — Release 010 主窗口原型

## 任务目标

实现 **PySide6 QMainWindow 壳层**：1920×1080 布局、左侧导航、顶栏菜单/工具栏、设备状态栏、中央 QGraphicsView 画布、右侧参数 Dock、底部状态栏。**不接真实设备，不实现扫描业务**，Mock 数据即可。

## 开始前必须阅读

1. [spec/AI_INDEX.md](../AI_INDEX.md)
2. [spec/Registry/UI.yaml](../Registry/UI.yaml)
3. [spec/Registry/Qt.yaml](../Registry/Qt.yaml)
4. [spec/Context_Pack/UI_Context.md](../Context_Pack/UI_Context.md)
5. [docs/product-spec/ui-wireframe/01_Main_Window_1920x1080.md](../../docs/product-spec/ui-wireframe/01_Main_Window_1920x1080.md)
6. [docs/product-spec/ui-wireframe/02_Left_Navigation.md](../../docs/product-spec/ui-wireframe/02_Left_Navigation.md)
7. [docs/product-spec/ui-wireframe/03_Top_Menu_And_Toolbar.md](../../docs/product-spec/ui-wireframe/03_Top_Menu_And_Toolbar.md)
8. [docs/product-spec/ui-wireframe/06_Dock_System.md](../../docs/product-spec/ui-wireframe/06_Dock_System.md)
9. 组件规范：
   - [NavigationBar.md](../../docs/product-spec/design-system/02_Components/NavigationBar.md)
   - [06_Toolbar_System.md](../../docs/product-spec/design-system/06_Toolbar_System.md)
   - [DockPanel.md](../../docs/product-spec/design-system/02_Components/DockPanel.md)
   - [StatusBar.md](../../docs/product-spec/design-system/02_Components/StatusBar.md)
   - [Qt_GraphicsView_Rules.md](../../docs/product-spec/design-system/07_Qt_Implementation/Qt_GraphicsView_Rules.md)
10. [docs/product-spec/qt-spec/02_Qt_Object_Names.md](../../docs/product-spec/qt-spec/02_Qt_Object_Names.md)

## 不要阅读的内容

- 整个 `docs/product-spec/domain/`（本任务只需 UI 壳层）
- 设备驱动、频谱仪 SDK、运动控制实现细节
- `docs/product-spec/data/` 全量（除非 Mock 项目路径）
- 旧版 `wireframe/` 文字线框（以 `ui-wireframe/` 为准）

## 允许修改的目录

- 新建 `src/` 或项目约定的 UI 包目录（若尚无，按 qt-spec 创建）
- `resources/qss/`（主题文件）
- `tests/ui/`（可选 smoke test）

## 禁止修改的目录

- `docs/product-spec/**`（除非用户明确要求补文档）
- `spec/Registry/**`（除非同步更新索引任务）
- 已有 ADR 正文

## 实现步骤

1. **QMainWindow 骨架**：菜单栏（文件/编辑/视图/设备/扫描/分析/报告/设置/帮助）、central widget 占位。
2. **左侧 NavigationBar**：仅四项——扫描、设备、分析、报告；**不含项目**。
3. **文件菜单**：新建/打开/保存项目（Mock 对话框即可）。
4. **视图菜单**：日志、频谱、统计、数据表格 Dock **默认隐藏**，勾选后显示。
5. **工具栏**：连接常用动作（Mock enabled/disabled）。
6. **设备状态栏**：线框 04 尺寸与占位图标。
7. **中央 QGraphicsView + QGraphicsScene**：PCB 背景 Mock 图；区域框 Mock；热力图用 **QGraphicsPixmapItem** 整图叠加。
8. **右侧 Dock**：参数面板壳层（PropertyPanel 结构，表单可空）。
9. **底部 QStatusBar**：坐标、扫描态 Mock。
10. **objectName**：全部按 qt-spec / Qt_ObjectName_Rules 设置。
11. **QSS**：引用 Design Token，深色主题；不散落 inline style。
12. **dynamic property**：扫描态等用 `setProperty("scanState", ...)` 配合 QSS。

## 验收标准

- [ ] 窗口默认 1920×1080 比例可缩放，布局与线框一致
- [ ] 左侧仅四个一级模块，无「项目」页
- [ ] 项目操作仅在文件菜单
- [ ] 日志/频谱/统计/数据表格默认不可见
- [ ] QGraphicsView 为主画布，非 QLabel 缩放
- [ ] 所有关键控件有 objectName
- [ ] 无真实设备连接代码
- [ ] 无 ScanTask 状态机业务逻辑（按钮 Mock 即可）
- [ ] 通过 [Review_Code.md](Review_Code.md) 清单

## 常见错误

| 错误 | 正确做法 |
|---|---|
| 左侧加「项目」导航 | Project 仅文件菜单 + 文件夹模型 |
| 启动即显示日志 Dock | 视图菜单控制，默认隐藏 |
| 热力图逐格 QGraphicsRectItem | 整张 QPixmap/QImage 一次绘制 |
| 跳过线框自由改比例 | 以 01_Main_Window_1920x1080 为准 |
| 全仓库复制粘贴旧 wireframe/ | 用 ui-wireframe/ + design-system |

## 推荐 commit message

```
feat(ui): add MainWindow shell prototype for Release 010

Mock-only QMainWindow with navigation, dock, and QGraphicsView canvas.
No device or scan business logic.
```

# Qt Widget Mapping — 组件映射表

## 设计目标

Pattern/Component 文档到 Qt 类的一一映射。

## MainWindow Pattern

| 逻辑 | Qt 类 |
|---|---|
| 主窗口 | QMainWindow |
| 菜单 | QMenuBar, QMenu, QAction |
| 工具栏 | QToolBar, QToolButton |
| 中央 | QWidget + QVBoxLayout / QHBoxLayout |
| 页面栈 | QStackedWidget |
| 底部状态 | QStatusBar |
| 设备状态条 | QWidget (custom) |
| 左侧导航 | QWidget + QToolButton ×4 |
| 画布 | QGraphicsView, QGraphicsScene |
| 参数 Dock | QDockWidget |
| 辅助 Dock | QDockWidget (hidden) |

## Component → Qt

| Component 文档 | Qt |
|---|---|
| Button | QPushButton, QToolButton |
| Input | QLineEdit, QSpinBox, QDoubleSpinBox |
| ComboBox | QComboBox |
| CheckBox | QCheckBox |
| Table | QTableView + QAbstractTableModel |
| Dialog | QDialog, QMessageBox |
| ProgressBar | QProgressBar |
| PropertyPanel | QToolBox / custom Accordion |
| Breadcrumb | QLabel / QWidget |

## 禁止事项

- 禁止 Scan 页用 QML 为主（V1 QWidget）
- 禁止 MDI QMdiArea 为主壳

## 相关

- `../../qt-spec/01_Qt_Layout_Spec.md`
- `../03_Patterns/MainWindow_Pattern.md`

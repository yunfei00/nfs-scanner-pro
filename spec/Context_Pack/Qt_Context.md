# Qt Context — PySide6 实现上下文

## 壳层组件

| Qt 类 | 用途 |
|---|---|
| QMainWindow | 主窗口 |
| QMenuBar / QMenu / QAction | 文件/视图/设置 |
| QToolBar / QToolButton | 扫描快捷 |
| QStackedWidget | 四页：扫描/设备/分析/报告 |
| QWidget | deviceStatusBar, leftNavigationBar |
| QDockWidget | scanParamDock, log/spectrum/… |
| QGraphicsView / QGraphicsScene | 画布 |
| QStatusBar | 底部状态 |

## objectName 规则

camelCase，全局唯一；见 `qt-spec/02` 与 `domain/07` 命名规则。

核心：`mainWindow`, `navScanButton`, `scanCanvasView`, `scanParamDock`, `toolbarStartScanButton`

## dynamic property（QSS）

- `variant`: primary | secondary | danger
- `error="true"` on QLineEdit
- `accordionHeader="true"` on Accordion 标题

## 样式

Fusion + 全局 QSS；Token 见 design-system/01_Foundation/Design_Tokens.md

## 禁止

- 热力图逐格 QGraphicsRectItem
- 不 load QSS 用原生浅色控件

## 细节入口

- [qt-spec/01_Qt_Layout_Spec.md](../../docs/product-spec/qt-spec/01_Qt_Layout_Spec.md)
- [qt-spec/02_Qt_Object_Names.md](../../docs/product-spec/qt-spec/02_Qt_Object_Names.md)
- [design-system/07_Qt_Implementation/](../../docs/product-spec/design-system/07_Qt_Implementation/README.md)

## Registry

[spec/Registry/Qt.yaml](../Registry/Qt.yaml)

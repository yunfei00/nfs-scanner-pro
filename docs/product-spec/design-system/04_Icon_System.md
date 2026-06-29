# 04 图标体系规范

> **历史兼容**：该文档已迁移到 `02_Components/` 各组件文档，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Icon System

## 设计目标

建立简洁、单色、工业风格的图标语言，保证 24px 导航与 20px 工具栏尺度下清晰可辨，视觉密度接近 Keysight / NI LabVIEW 类桌面仪器软件。

## 使用场景

- 左侧导航四项：扫描、设备、分析、报告
- 工具栏：开始/停止扫描、拍照、对齐、网格、测量
- 设备状态栏连接指示
- Dock 标题栏折叠/关闭
- 菜单项前缀（可选，低频项可不加）

## 尺寸规则

| 场景 | 图标尺寸 | 可点区域 |
|---|---:|---:|
| 左侧导航 | 24 × 24 | 48 × 48 行高 |
| 工具栏 | 20 × 20 | 36 × 36 |
| 菜单项（可选） | 16 × 16 | 随菜单行 |
| Dock 标题按钮 | 16 × 16 | 28 × 28 |
| 状态栏 | 不放置装饰图标 | — |

## 颜色与状态

| 状态 | 颜色 |
|---|---|
| 默认 | `--color-text-secondary` |
| 悬停 | `--color-text-primary` |
| 选中 / 激活 | `--color-primary` |
| 禁用 | `--color-status-idle` |
| 危险（停止/急停） | `--color-status-error` |

图标默认**单色 SVG**，通过 `currentColor` 或 QSS `color` 着色，禁止多色 emoji 作为正式导航图标。

## 导航图标语义（建议）

| 模块 | 语义 | 备注 |
|---|---|---|
| 扫描 | 靶心 / 扫描框 | 默认首页 |
| 设备 | 模块 / 连接 | 非“设置”齿轮 |
| 分析 | 波形 / 热力 | 区别于报告 |
| 报告 | 文档 / 导出 | 只读输出 |

## Qt/PySide6 推荐组件

- 矢量：`QSvgRenderer` + `QIcon` from SVG path
- 工具栏 / 导航：`QToolButton` + `setIconSize(QSize(20,20))` 或 24
- 统一图标目录（Release 010 实现）：`resources/icons/`
- 高 DPI：`QIcon::addFile(..., QSize(), QIcon::Normal, QIcon::Off)` 提供 @2x

## objectName 命名建议

```text
navScanButton
navDeviceButton
navAnalysisButton
navReportButton
toolbarStartScanButton
toolbarStopScanButton
toolbarCaptureButton
toolbarAlignButton
toolbarGridButton
toolbarMeasureButton
```

## 禁止事项

- 禁止使用 emoji（◎、📈、📄）作为 Release 010 正式交付图标（线框文档中的 emoji 仅为占位说明）。
- 禁止导航图标使用“首页/dashboard”房子图标替代扫描。
- 禁止在 PCB 画布内放置大尺寸装饰图标遮挡被测区域。
- 禁止各页面自行引入不同 icon pack 混用风格。

## 相关文档

- 导航：`07_Navigation_System.md`
- 工具栏：`06_Toolbar_System.md`

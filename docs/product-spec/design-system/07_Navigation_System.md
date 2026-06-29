# 07 左侧导航规范

> **历史兼容**：该文档已迁移到 `02_Components/NavigationBar.md` 与 `05_Animation/Navigation_Animation.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Navigation System

## 设计目标

左侧导航仅负责**业务页面切换**，默认图标模式最大化 PCB 画布宽度；悬停展开提供文字标签，交互参考 Altium / Cadence 紧凑工具轨。

## 使用场景

- 扫描 / 设备 / 分析 / 报告 四页切换
- 当前页高亮反馈
- 鼠标悬停临时展开

## 导航项（固定四项）

```text
扫描
设备
分析
报告
```

**不包含**：项目、样品、区域、设置、Dashboard。

## 尺寸与动画

| 属性 | 值 |
|---|---|
| 默认宽度 | 56 px（仅图标） |
| 展开宽度 | 180 px |
| 展开动画 | 150 ~ 200 ms，`QEasingCurve.OutCubic` |
| 项高度 | 48 px |
| 图标 | 24 × 24 |
| 展开左 padding | 16 px |
| 背景 | `--color-nav-bg` |
| 选中背景 | `--color-nav-selected` |
| 悬停背景 | `--color-nav-hover` |
| 选中指示 | 左侧 3px `--color-primary` 竖条 |

## 状态规则

| 状态 | 表现 |
|---|---|
| 默认 | 56px，仅图标 |
| 鼠标进入导航区 | 展开至 180px，显示文字 |
| 鼠标离开 | 收起至 56px |
| 当前页 | 高亮 + 左侧指示条 |
| 无项目打开 | 仍允许进入设备页；扫描/分析/报告可显示空状态 |

默认首页：**扫描页**。

## Qt/PySide6 推荐组件

- 自定义 `QWidget`（`LeftNavigationBar`），非 `QListWidget` 全行选中样式
- 按钮：`QToolButton` 垂直排列 或 `QPushButton` flat
- 宽度动画：`QPropertyAnimation` on `minimumWidth` / `maximumWidth`
- 页面切换：`QStackedWidget` 与导航 `buttonGroup` 互斥

## objectName 命名建议

```text
leftNavigationBar
navScanButton
navDeviceButton
navAnalysisButton
navReportButton
pageStack
scanPage
devicePage
analysisPage
reportPage
```

## 禁止事项

- 禁止默认 180px 常开导航。
- 禁止添加「项目」「设置」「Dashboard」为一级导航项（ADR-0013）。
- 禁止导航区放置扫描参数或设备详细配置。
- 禁止用 `QTabWidget` 顶部 Tab 替代左侧导航（不符合线框）。
- 禁止导航展开后永久锁定（除非 Release 010 设置项显式提供，V1 不需要）。

## 相关文档

- 线框：`ui-wireframe/02_Left_Navigation.md`
- ADR：`decision/ADR-0013-Project-In-File-Menu.md`
- 布局：`03_Spacing_And_Layout.md`

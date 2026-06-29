# NavigationBar — 左侧导航组件

## 设计目标

四页切换，56px 图标默认，悬停 180px 展开，最大化画布。

## 使用场景

扫描 / 设备 / 分析 / 报告；默认首页扫描。

## 尺寸/颜色/状态规则

宽 56↔180；项高 48；图标 24；动画 `motion.fast`~`motion.normal`；选中左 3px `color.nav.indicator`。

## Qt/PySide6 推荐组件

`LeftNavigationBar` 自定义 `QWidget`；`QToolButton` 垂直；`QPropertyAnimation` 宽度；`QStackedWidget` 切页。

## objectName 命名建议

```text
leftNavigationBar
navScanButton
navDeviceButton
navAnalysisButton
navReportButton
```

## 禁止事项

- 禁止含项目/设置/Dashboard
- 禁止默认常开 180px
- 禁止 QTabWidget 顶栏替代

## 相关文档

- [../05_Animation/Navigation_Animation.md](../05_Animation/Navigation_Animation.md)
- 历史：`../07_Navigation_System.md`

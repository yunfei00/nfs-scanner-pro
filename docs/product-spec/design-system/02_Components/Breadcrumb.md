# Breadcrumb — 面包屑组件

## 设计目标

画布顶部上下文条，单行展示当前项目/Region/通道/频率/点数。

## 使用场景

扫描页默认显示。

## 尺寸/颜色/状态规则

高 28px；半透明 `color.bg.panel` 80%；13px body；分隔 `>`。

示例：

```text
项目 > CPU_Area > Hx Probe > 2.450 GHz > 6461 pts
```

单项 max 24 字符省略。

## Qt/PySide6 推荐组件

`QLabel` 或 `QWidget#breadcrumbBar` 在 Overlay 层 / 画布顶栏；`QGraphicsProxyWidget` 可选。

## objectName 命名建议

```text
breadcrumbBar
```

## 禁止事项

- 禁止放菜单栏/工具栏
- 禁止多行换行

## 相关文档

- [../03_Patterns/Scan_Workbench_Pattern.md](../03_Patterns/Scan_Workbench_Pattern.md)

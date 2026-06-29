# ToolBar — 工具栏组件

## 设计目标

扫描高频动作一行可达：开始/停止/拍照/对齐/网格/测量。

## 使用场景

全局工具栏，56px 固定高。

## 尺寸/颜色/状态规则

高 56px；图标 20px；可点 36px；背景 `color.bg.toolbar`。默认按钮顺序：

```text
开始扫描 | 停止扫描 | 拍照 | 区域对齐 | 网格 | 测量
```

停止：`variant=danger`；网格/测量：checkable。

## Qt/PySide6 推荐组件

`QToolBar` + `QToolButton`；`addSeparator()` 分组。

## objectName 命名建议

```text
mainToolBar
toolbarStartScanButton
toolbarStopScanButton
toolbarCaptureButton
toolbarAlignButton
toolbarGridButton
toolbarMeasureButton
```

## 禁止事项

- 禁止高度换行增长
- 禁止放项目 Breadcrumb
- 禁止 >8 个默认可见按钮

## 相关文档

- 历史：`../06_Toolbar_System.md`
- [../04_Interaction/Keyboard_Shortcuts.md](../04_Interaction/Keyboard_Shortcuts.md)

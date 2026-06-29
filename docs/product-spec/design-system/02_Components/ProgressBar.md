# ProgressBar — 进度条组件

## 设计目标

扫描进度在底部状态栏紧凑展示。

## 使用场景

扫描运行中 chunk 进度；可选 Dock 统计区。

## 尺寸/颜色/状态规则

高 16px（statusBar 内）；轨道 `color.bg.app`；chunk `color.status.running`；文字居中 13px。

## Qt/PySide6 推荐组件

`QProgressBar`；`setTextVisible(True)`；扫描服务信号更新 value。

## objectName 命名建议

```text
statusBarProgressBar
scanProgressBar
```

## 禁止事项

- 禁止全屏大进度条占画布
- 禁止 indeterminate 长时间无点数信息

## 相关文档

- [../05_Animation/Loading_Progress_Animation.md](../05_Animation/Loading_Progress_Animation.md)
- [StatusBar.md](StatusBar.md)

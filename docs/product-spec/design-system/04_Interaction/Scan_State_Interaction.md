# Scan State Interaction — 扫描状态交互

## 设计目标

开始/暂停/停止/完成状态与 UI 启用态严格联动。

## 使用场景

工具栏、状态栏、参数锁定、进度反馈。

## 状态机

```text
idle → running ⇄ paused → completed | failed | cancelled
```

| 状态 | 开始 | 停止 | 参数 Dock | 进度条 |
|---|---|---|---|---|
| idle | 启用 | 禁用 | 可编辑 | 隐藏 |
| running | 禁用 | 启用 | 部分锁定 | 显示 |
| paused | 继续 | 启用 | 部分锁定 | 显示 |
| completed | 启用 | 禁用 | 可编辑 | 100% |

## Qt

Controller 信号 → 更新 ToolBar enabled、ProgressBar、statusBarMessage。

## objectName

`toolbarStartScanButton`、`toolbarStopScanButton`、`statusBarProgressBar`。

## 禁止事项

- 禁止 running 时关闭项目无确认
- 禁止 failed 无 statusBar 消息

## 相关

- [Error_Recovery_Pattern.md](../03_Patterns/Error_Recovery_Pattern.md)
- [Loading_Progress_Animation.md](../05_Animation/Loading_Progress_Animation.md)

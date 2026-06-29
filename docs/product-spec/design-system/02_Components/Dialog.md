# Dialog — 对话框组件

## 设计目标

低频阻塞决策：新建项目、确认停止、关于。

## 使用场景

文件菜单项目操作、Region 创建、设备连接、导出、危险确认。

## 尺寸/颜色/状态规则

宽 480~720；圆角 `radius.dialog`；padding `spacing.5`；蒙层 #000 50%。按钮区右对齐 [取消][确定]。

## Qt/PySide6 推荐组件

`QDialog`、`QMessageBox`、`QFileDialog`；`ApplicationModal`。

## objectName 命名建议

```text
dialogNewProject
dialogOpenProject
dialogConfirmStopScan
dialogAbout
dialogButtonOk
dialogButtonCancel
```

## 禁止事项

- 禁止日常扫描参数用 Dialog（用 Dock）
- 禁止宽 > 720px
- 禁止扫描中 modal 挡停止

## 相关文档

- 历史：`../14_Dialog_System.md`

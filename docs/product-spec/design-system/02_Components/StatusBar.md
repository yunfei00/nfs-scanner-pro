# StatusBar — 状态栏与设备状态栏

## 设计目标

双层状态：设备状态栏（40px）+ 底部状态栏（32px），仪器式实时反馈。

## 使用场景

连接状态、扫描上下文、进度、时间。

## 尺寸/颜色/状态规则

**设备状态栏 40px：**

```text
●运动 ●频谱 ●相机 ●舵机 | 探头 高度 区域 频率 点数
```

**底部状态栏 32px：**

```text
消息 | 进度 点数 已用 剩余 | 日期 时间
```

状态色见 `State_Tokens.md`；相机离线 = idle 灰。

## Qt/PySide6 推荐组件

`QWidget#deviceStatusBar` + `QStatusBar`；`addPermanentWidget` 右对齐时间。

## objectName 命名建议

```text
deviceStatusBar
deviceStatusMotionIndicator
deviceStatusSpectrumIndicator
statusBar
statusBarMessageLabel
statusBarProgressBar
statusBarDateTimeLabel
```

## 禁止事项

- 禁止设备栏多行
- 禁止大段日志在 statusBar
- 禁止相机离线红色 error

## 相关文档

- [../03_Patterns/Device_Status_Pattern.md](../03_Patterns/Device_Status_Pattern.md)
- 历史：`../09_Status_System.md`

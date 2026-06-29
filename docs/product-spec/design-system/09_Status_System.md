# 09 状态系统规范

> **历史兼容**：该文档已迁移到 `02_Components/StatusBar.md` 与 `03_Patterns/Device_Status_Pattern.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Status System

## 设计目标

分两层呈现系统状态：**设备状态栏**（硬件连接与扫描上下文）与 **底部状态栏**（任务进度与时间），信息密度高但不喧宾夺主，参考 NI / Keysight 底部状态区。

## 使用场景

- 运动平台 / 频谱仪 / 相机 / 舵机连接状态
- 当前探头、Z 高度、Region、频率、点数
- 扫描进度、当前点、耗时
- 全局消息与日期时间

## 设备状态栏（Central 顶部，40px）

布局：

```text
●运动平台  ●频谱仪  ●相机  ●舵机  |  探头  高度  区域  频率  点数
```

| 指示 | 尺寸 | 颜色规则 |
|---|---|---|
| 状态圆点 | 8 px 直径 | 绿/蓝/黄/红/灰 见 `01_Color_System.md` |
| 设备名 | 13px | `--color-text-secondary` |
| 上下文数值 | 13px 等宽 | `--color-text-primary` |
| 分隔符 `\|` | — | `--color-divider` |

点击设备名可跳转设备页或打开工具菜单「设备管理」（Release 010 实现交互）。

## 底部状态栏（32px）

```text
状态消息  |  扫描进度  扫描点  已用时间  剩余时间  |  日期  时间
```

| 区段 | 说明 |
|---|---|
| 左 | 最近操作结果、错误摘要（单行省略） |
| 中 | 扫描运行时显示，空闲时可隐藏或显示「就绪」 |
| 右 | 固定右对齐日期时间 |

## 状态规则

| 场景 | 设备状态栏 | 底部状态栏 |
|---|---|---|
| 空闲 | 灰/绿点 | 「就绪」 |
| 扫描中 | 运动+频谱蓝/绿 | 进度、点数、ETA |
| 设备断开 | 对应红点 | 错误消息 |
| 相机离线 | 灰点，不阻塞 | 可选提示，非 error |

## Qt/PySide6 推荐组件

- 设备状态栏：自定义 `QWidget` + `QHBoxLayout` + `QLabel` 指示点
- 底部：`QStatusBar` + `addPermanentWidget` 放置右对齐时间
- 进度：`QProgressBar` 嵌入 statusBar 或 `QLabel` 文字进度
- 定时刷新：`QTimer` 更新时间，扫描进度由 service 信号驱动

## objectName 命名建议

```text
deviceStatusBar
deviceStatusMotionIndicator
deviceStatusSpectrumIndicator
deviceStatusCameraIndicator
deviceStatusServoIndicator
deviceStatusProbeLabel
deviceStatusHeightLabel
deviceStatusRegionLabel
deviceStatusFrequencyLabel
deviceStatusPointCountLabel
statusBar
statusBarMessageLabel
statusBarProgressBar
statusBarPointLabel
statusBarElapsedLabel
statusBarRemainingLabel
statusBarDateTimeLabel
```

## 禁止事项

- 禁止设备状态栏高度超过 40px 或多行换行。
- 禁止在状态栏显示大段日志（日志进 logDock）。
- 禁止相机未连接显示为红色 error（相机可选，ADR-0003）。
- 禁止底部状态栏按钮过多（动作用工具栏/菜单）。
- 禁止状态栏遮挡画布（必须在布局流内，非 overlay）。

## 相关文档

- 线框：`ui-wireframe/04_Device_Status_Bar.md`
- 颜色：`01_Color_System.md`

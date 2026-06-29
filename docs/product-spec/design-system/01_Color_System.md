# 01 颜色规范

> **历史兼容**：该文档已迁移到 `01_Foundation/Color_Tokens.md` 与 `01_Foundation/Design_Tokens.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · 颜色令牌

## 设计目标

建立 NFS Scanner Pro 深色工业主题的统一颜色令牌，使菜单、工具栏、画布、Dock、状态指示与 Keysight / R&S / NI 类仪器软件视觉一致，避免普通后台管理系统的灰白扁平风格。

## 使用场景

- 全局 QSS 主题（见 `qss/dark_theme_tokens.qss.md`）
- 设备状态指示灯、扫描进度、热力图色带
- 主按钮、危险按钮、表单聚焦态
- 画布网格线与 Region 边框叠加色

## 基础色板（Release 008 继承）

| 用途 | 颜色 | 令牌名 |
|---|---|---|
| 主蓝 | #0D6EFD | `--color-primary` |
| 深蓝背景 | #07111D | `--color-bg-deep` |
| 面板背景 | #0B1724 | `--color-bg-panel` |
| 面板边框 | #1E2D3D | `--color-border` |
| 文字主色 | #EAF2FF | `--color-text-primary` |
| 文字次级 | #A8B3C2 | `--color-text-secondary` |
| 正常 | #22C55E | `--color-status-ok` |
| 运行中 | #3B82F6 | `--color-status-running` |
| 警告 | #FACC15 | `--color-status-warning` |
| 错误 | #EF4444 | `--color-status-error` |
| 停止 | #6B7280 | `--color-status-idle` |

默认 LUT：Turbo。

## 扩展色板（Release 009）

| 用途 | 颜色 | 令牌名 |
|---|---|---|
| 主蓝悬停 | #0B5ED7 | `--color-primary-hover` |
| 主蓝按下 | #0A58CA | `--color-primary-pressed` |
| 主蓝禁用 | #0D6EFD40 | `--color-primary-disabled` |
| 画布背景 | #050A12 | `--color-canvas-bg` |
| 工具栏背景 | #0A1520 | `--color-toolbar-bg` |
| 菜单栏背景 | #07111D | `--color-menubar-bg` |
| 导航背景 | #0B1724 | `--color-nav-bg` |
| 导航选中 | #0D6EFD26 | `--color-nav-selected` |
| 导航悬停 | #1E2D3D80 | `--color-nav-hover` |
| Dock 标题栏 | #0B1724 | `--color-dock-title-bg` |
| 分隔线 | #1E2D3D | `--color-divider` |
| 输入框背景 | #0B1724 | `--color-input-bg` |
| 输入框聚焦边框 | #0D6EFD | `--color-input-focus` |
| 表格斑马纹 | #0F1A28 | `--color-table-stripe` |
| 表格选中行 | #0D6EFD33 | `--color-table-selected` |
| 热力图叠加默认透明度 | 70% | `--heatmap-overlay-opacity` |

## 状态颜色规则

| 状态 | 颜色 | 应用位置 |
|---|---|---|
| 已连接 / 正常 | `#22C55E` | 设备状态栏圆点、状态栏文字 |
| 运行中 / 扫描中 | `#3B82F6` | 进度条、扫描指示灯 |
| 警告 | `#FACC15` | 参数越界、设备降级 |
| 错误 / 未连接 | `#EF4444` | 急停、连接失败 |
| 禁用 / 未启用 | `#6B7280` | 不可用菜单项、离线设备 |

## Qt/PySide6 推荐组件

- 全局：`QApplication.setStyle("Fusion")` + 自定义 QSS
- 状态指示：`QLabel` + `setStyleSheet` 或 SVG 图标着色
- 进度：`QProgressBar` 使用 `--color-status-running` 作为 chunk 色
- 画布层：不在 Widget 上硬编码颜色，通过 Scene 层 `QPen` / `QBrush` 引用令牌常量

## objectName 命名建议

颜色令牌本身不绑定 objectName；状态色常用于：

```text
deviceStatusBar
deviceStatusMotionIndicator
deviceStatusSpectrumIndicator
scanProgressBar
statusBarMessageLabel
```

## 禁止事项

- 禁止在画布区域使用高饱和渐变背景，PCB 与热力图必须是视觉主角。
- 禁止引入浅色主题为默认（Settings 可预留主题切换，但 V1 默认深色）。
- 禁止各页面自行定义主色，必须引用本令牌表。
- 禁止用纯红 `#FF0000` 替代 `--color-status-error`。
- 禁止热力图逐格 Widget 着色，颜色映射在 QPixmap 生成阶段完成（见 `13_Heatmap_System.md`）。

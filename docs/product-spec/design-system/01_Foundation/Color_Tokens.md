# Color Tokens — 颜色令牌

> 完整索引见 [Design_Tokens.md](Design_Tokens.md) §2

## 设计目标

深色工业主题，Keysight/R&S 风格，PCB 与热力图为视觉焦点。

## 使用场景

全局 QSS、设备指示灯、进度条、画布网格、Region 边框、热力图 LUT。

## 尺寸/颜色/状态规则

见 Design_Tokens §2 与 §7。相机离线用 `color.status.idle`，非 error。

## Qt/PySide6 推荐组件

`QApplication` + Fusion + QSS；Scene 层 `QPen`/`QBrush` 引用 Token 常量。

## objectName 命名建议

`deviceStatusMotionIndicator`、`scanProgressBar` 等，见 `02_Components/StatusBar.md`。

## 禁止事项

- 禁止画布高饱和渐变背景
- 禁止 `#FF0000` 替代 `color.status.error`
- 禁止浅色默认主题

## 历史内容

吸收自 `../01_Color_System.md`。

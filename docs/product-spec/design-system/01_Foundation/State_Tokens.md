# State Tokens — 状态令牌

> 完整索引见 [Design_Tokens.md](Design_Tokens.md) §7

## 设计目标

统一设备、扫描、控件三类状态视觉，避免每页自定义颜色语义。

## 使用场景

设备状态栏圆点、扫描进度、按钮/输入框、表格行选中。

## 状态规则

### 设备状态

| 状态 | Token 映射 | 视觉 |
|---|---|---|
| 已连接 | color.status.success | 绿点 |
| 运行中 | color.status.running | 蓝点 |
| 警告 | color.status.warning | 黄点 |
| 错误/未连接 | color.status.error | 红点 |
| 禁用/未启用 | color.status.idle | 灰点 |

### 扫描状态

`idle` → `running` → `paused` → `completed` | `failed`

### 控件状态

`default` / `hover` / `pressed` / `focus` / `disabled` / `checked` / `error`

## Qt/PySide6 推荐组件

QSS 伪状态 + 动态属性 `error="true"`、`variant="danger"`；设备点用 `QLabel` + property class。

## objectName 命名建议

`deviceStatus*Indicator`、`toolbarStopScanButton[variant=danger]`。

## 禁止事项

- 禁止相机离线示为 error 红（ADR-0003）
- 禁止停止扫描用绿色

## 相关文档

- [../04_Interaction/Scan_State_Interaction.md](../04_Interaction/Scan_State_Interaction.md)
- [../07_Qt_Implementation/Qt_State_Property_Rules.md](../07_Qt_Implementation/Qt_State_Property_Rules.md)

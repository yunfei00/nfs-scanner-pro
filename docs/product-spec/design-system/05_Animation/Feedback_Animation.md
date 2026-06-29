# Feedback Animation — 反馈动效

## 设计目标

按钮 pressed、设备状态变化、扫描开始/停止有即时视觉反馈。

## 规则

| 事件 | 反馈 | 时长 |
|---|---|---|
| 按钮 press | 背景 → press token | instant |
| 开始扫描 | 工具栏开始禁用+状态栏蓝 | instant |
| 设备连接成功 | 指示点灰→绿 | 150ms color |
| 设备断开 | 绿→红 | 150ms |
| 错误 | statusBar 闪红一次 | 200ms |

## Qt

QSS `:pressed`；`QPropertyAnimation` on label color 可选。

## 禁止事项

- 禁止成功 Dialog 弹窗每次保存
- 禁止 blocking animation dialog

## 相关

- [State_Tokens.md](../01_Foundation/State_Tokens.md)

# Animation Principles — 动效原则

## 设计目标

动效**功能性**为主，仪器软件拒绝花哨过渡；快、短、不挡操作。

## 使用场景

导航、Dock、按钮反馈、进度。

## 规则

| 原则 | 说明 |
|---|---|
| 短 | 150~300ms，无 >500ms 常规 UI |
| 省 | 扫描运行中减少非必要动画 |
| 一致 | easing 默认 OutCubic |
| 可关 | Settings 预留「减少动画」(V2) |

## Motion Token

```text
motion.fast    = 150ms
motion.normal  = 200ms
motion.slow    = 300ms
motion.easing  = OutCubic
```

## Qt

`QPropertyAnimation` + `QEasingCurve.OutCubic`；禁用 `QApplication.effectEnabled` 仅当用户设置。

## 禁止事项

- 禁止页面切换全屏 fade 500ms+
- 禁止导航 spring 弹跳
- 禁止动画阻塞扫描停止

## 相关

- 各子文档

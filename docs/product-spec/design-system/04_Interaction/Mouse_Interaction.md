# Mouse Interaction — 鼠标交互

## 设计目标

画布优先；导航悬停展开；不抢 PCB 操作。

## 使用场景

全局点击、拖拽、悬停。

## 规则

| 区域 | 左键 | 中键 | 滚轮 |
|---|---|---|---|
| 画布 | 选择/测量 | 平移 | 缩放（光标中心） |
| 左侧导航 | 切页 | — | — |
| 导航区悬停 | 展开 180px | — | — |
| 工具栏 | 执行/切换 | — | — |
| Dock 标题 | 拖放 | — | — |

## Qt

`QGraphicsView` 手势；Nav `enterEvent`/`leaveEvent` 触发动画。

## objectName

见各 Component。

## 禁止事项

- 禁止导航 click 外仍永久 180px
- 禁止画布左键拖拽与 Region 框选冲突未定义

## 相关

- [Canvas_Interaction.md](Canvas_Interaction.md)
- [Navigation_Animation.md](../05_Animation/Navigation_Animation.md)

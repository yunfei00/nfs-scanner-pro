# Navigation Animation — 导航动效

## 设计目标

56↔180 宽度过渡平滑，不挤跳画布。

## 规则

- 触发：鼠标 enter/leave `leftNavigationBar`
- 时长：`motion.fast` (150ms) ~ `motion.normal` (200ms)
- 属性：`minimumWidth` / `maximumWidth`
- 曲线：`OutCubic` 展开，`InCubic` 收起
- 文字：展开后 fade in 可选 50ms delay

## Qt

`QPropertyAnimation(leftNavigationBar, b"maximumWidth")`。

## objectName

`leftNavigationBar`。

## 禁止事项

- 禁止永久 180px
- 禁止 >300ms 展开

## 相关

- `../02_Components/NavigationBar.md`
- `../../ui-wireframe/02_Left_Navigation.md`

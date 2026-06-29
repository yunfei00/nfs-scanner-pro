# ADR-0012 UI 先线框后高保真

## 状态

Accepted

## 决策

从 Release 008 开始，UI 设计流程改为：

```text
Wireframe
↓
Design System
↓
Component Rules
↓
High Fidelity
↓
PySide6 Implementation
```

## 约束

1. 先固定 1920×1080 主窗口线框。
2. 先固定导航、Dock、菜单、工具栏、状态栏尺寸。
3. 高保真必须遵守线框，不允许自由发挥。
4. 项目入口只在“文件”菜单，不在左侧导航。
5. 左侧导航默认图标模式，悬停展开。
6. 辅助面板默认隐藏，通过“视图”菜单调出。

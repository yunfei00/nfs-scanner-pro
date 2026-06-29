# UI Context — 界面上下文

## UI 总原则

- PCB 画布 ≥70% 宽，永远是主角
- 深色工业风（Keysight/R&S 类）
- 一页一事；Release 009.5 Design System 为 UI 权威

## 1920×1080 线框（Release 008 最高布局权威）

| 区域 | 高度/宽度 |
|---|---|
| MenuBar | 32px |
| ToolBar | 56px |
| DeviceStatus | 40px |
| Left Nav | 56 ↔ 180px |
| Param Dock | 340px |
| StatusBar | 32px |

## 左侧导航（仅 4 项）

扫描 · 设备 · 分析 · 报告（**无 Project**）

## 顶部菜单

文件 · 编辑 · 视图 · 工具 · 设置 · 帮助

## 工具栏（默认）

开始扫描 | 停止 | 拍照 | 区域对齐 | 网格 | 测量

## 设备状态栏

四设备指示 + 探头/高度/区域/频率/点数

## 右侧 Dock

scanParamDock 默认开；Accordion 五组

## 底部状态栏

消息 | 进度/点数/时间 | 日期时间

## 默认隐藏面板（视图菜单）

日志 · 频谱 · 统计 · 数据表格 · 色带 · 小地图（后两者可选显）

## 细节入口

- [ui-wireframe/README.md](../../docs/product-spec/ui-wireframe/README.md)
- [design-system/README.md](../../docs/product-spec/design-system/README.md)
- [design-system/01_Foundation/Design_Tokens.md](../../docs/product-spec/design-system/01_Foundation/Design_Tokens.md)

## Registry

[spec/Registry/UI.yaml](../Registry/UI.yaml)

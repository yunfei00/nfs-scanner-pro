# 05 菜单栏规范

> **历史兼容**：该文档已迁移到 `02_Components/MenuBar.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Menu System

## 设计目标

将低频系统级操作收敛到顶部菜单，释放左侧导航与画布空间；项目生命周期完全由「文件」菜单承载，符合 ADR-0013。

## 使用场景

- 项目新建 / 打开 / 保存 / 关闭
- 视图面板显隐（Dock）
- 工具与设备维护入口
- 系统设置与帮助

## 菜单结构（固定）

```text
文件(F)  编辑(E)  视图(V)  工具(T)  设置(S)  帮助(H)
```

### 文件

```text
新建项目...
打开项目...
打开最近项目 >
─────────────
保存项目          Ctrl+S
关闭项目
─────────────
打开项目文件夹
退出
```

### 编辑

```text
撤销
重做
─────────────
复制
粘贴
```

### 视图

```text
显示参数面板
显示日志面板
显示频谱面板
显示统计面板
显示数据表格
显示色带
显示小地图
─────────────
重置布局
全屏显示
```

### 工具

```text
设备管理
运动平台回零
拍照
区域对齐
Hx/Hy 校准
数据检查
导出日志
```

### 设置

```text
系统设置
主题
语言
授权许可
存储路径
日志设置
```

### 帮助

```text
用户手册
快捷键
关于 NFS Scanner Pro
```

## 尺寸与样式

| 属性 | 值 |
|---|---|
| 菜单栏高度 | 32 px |
| 字号 | 14 px |
| 背景 | `--color-menubar-bg` |
| 文字 | `--color-text-primary` |
| 悬停项背景 | `--color-nav-hover` |
| 分隔线 | `--color-divider` |
| 禁用项 | `--color-status-idle` |

## 状态规则

- 无打开项目时：保存、关闭、打开项目文件夹 禁用。
- 扫描运行中：新建/打开项目 禁用或二次确认。
- 视图菜单项为 **checkable**，与对应 Dock 显隐同步。

## Qt/PySide6 推荐组件

- `QMenuBar` + `QMenu` + `QAction`
- 快捷键：`QAction.setShortcut(QKeySequence(...))`
- 最近项目：`QMenu` 动态子菜单
- 视图联动：`QAction.setCheckable(True)` + `toggled` 信号控制 Dock

## objectName 命名建议

```text
menuBar
menuFile
menuEdit
menuView
menuTools
menuSettings
menuHelp
actionNewProject
actionOpenProject
actionSaveProject
actionCloseProject
actionShowScanParamDock
actionShowLogDock
actionShowSpectrumDock
actionShowStatisticsDock
actionShowDataTableDock
actionResetLayout
```

## 禁止事项

- 禁止在菜单栏放置「扫描」「设备」等业务页切换（属于左侧导航）。
- 禁止将「新建项目」「打开项目」放入工具栏（ADR-0013）。
- 禁止将设置放入左侧导航一级入口。
- 禁止视图菜单默认勾选日志/频谱/统计/数据表格（默认隐藏）。

## 相关文档

- 线框：`ui-wireframe/03_Top_Menu_And_Toolbar.md`
- ADR：`decision/ADR-0013-Project-In-File-Menu.md`
- Dock：`08_Dock_System.md`

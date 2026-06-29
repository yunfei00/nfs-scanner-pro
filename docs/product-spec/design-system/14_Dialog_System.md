# 14 对话框系统规范

> **历史兼容**：该文档已迁移到 `02_Components/Dialog.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Dialog System

## 设计目标

对话框用于**低频、阻塞式**决策：新建项目、打开文件、向导式配置；风格与主窗口深色主题一致，宽度适中，不采用网页式大 Modal。

## 使用场景

| 对话框 | 触发 | 类型 |
|---|---|---|
| 新建项目 | 文件 → 新建项目 | 表单 + 确认 |
| 打开项目 | 文件 → 打开项目 | `QFileDialog` 定制 |
| 新建 Region | 工具/画布上下文 | 小表单 |
| 扫描设置向导 | 可选，高级 | 多步 Wizard |
| 设备连接 | 设备页 / 工具 | 表单 |
| 导出报告 | 报告页 | 选项 + 路径 |
| 关于 | 帮助 → 关于 | 信息只读 |
| 确认停止扫描 | 停止 / 关闭项目 | Question |

## 尺寸规则

| 类型 | 最小宽 | 最大宽 | 备注 |
|---|---:|---:|---|
| 简单表单 | 480 | 560 | 新建 Region |
| 项目表单 | 560 | 640 | 新建项目 |
| 向导 | 640 | 720 | 多步 |
| 关于 | 400 | 480 | 固定 |

- 圆角：8px（窗口 frame 由 OS 提供时，内容区 8px）
- 内边距：`--space-5`（24px）
- 按钮区：右对齐，主按钮在最右，间距 `--space-2`
- 标题：16px 600

## 按钮顺序（Windows）

```text
[ 取消 ]  [ 确定 ]
```

危险确认：

```text
[ 取消 ]  [ 停止扫描 ]  （红色主按钮）
```

## 样式

| 元素 | 规则 |
|---|---|
| 背景 | `--color-bg-panel` |
| 边框 | 1px `--color-border` |
| 标题 | `--color-text-primary` |
| 蒙层 | `#000000` 50% opacity（应用级 overlay 或 QDialog modal） |

## Qt/PySide6 推荐组件

- 模态：`QDialog` + `exec()` 或 非模态 `show()` 仅进度类
- 文件：`QFileDialog.getExistingDirectory` 选项目文件夹
- 向导：`QWizard`（V1 可简化为单页 QDialog）
- 消息：`QMessageBox` 定制 icon 与 QSS
- 父窗口：`setWindowModality(Qt.ApplicationModal)`

## objectName 命名建议

```text
dialogNewProject
dialogOpenProject
dialogNewRegion
dialogDeviceConnect
dialogExportReport
dialogAbout
dialogConfirmStopScan
dialogButtonOk
dialogButtonCancel
```

## 禁止事项

- 禁止扫描参数日常编辑依赖对话框（应在 scanParamDock）。
- 禁止对话框宽度 > 720px 占满屏幕（非仪器软件习惯）。
- 禁止浅色系统原生对话框不套 QSS。
- 禁止在扫描运行中 modal 对话框阻塞停止按钮可达性。
- 禁止用 WebView 弹窗做核心流程（V1 不用 Figma/Web UI）。

## 相关文档

- 菜单：`05_Menu_System.md`
- 表单：`10_Form_System.md`
- 线框：`wireframe/dialog/`

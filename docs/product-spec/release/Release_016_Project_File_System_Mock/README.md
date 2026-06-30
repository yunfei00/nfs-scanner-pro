# Release 016 — Project File System Mock

## 1. Release 目标

在 **Release 011~015** 主窗口与四页 Mock 基础上，完善**文件菜单中的项目 Mock 能力**：新建 / 打开 / 最近 / 保存 / 关闭 / 打开项目文件夹。全部为**内存 Mock**，不写真实文件、不打开系统资源管理器。

## 2. 为什么项目不进入左侧导航

- **Project 是文件夹，是数据容器**（见 ADR-0018），不是与扫描/设备/分析/报告并列的「功能页」。
- 用户通过**文件菜单**管理项目生命周期；左侧导航保持四页工作流：扫描 → 设备 → 分析 → 报告。
- 复制项目文件夹即备份；**不设计 Import / Export Project 作为主路径**。

## 3. 本次实现范围

- `project_mock.py`：当前项目、最近项目、create/open/save/close 内存 API
- 文件菜单 7 项可点击（含「打开最近项目」子菜单 3 条 Mock 项目）
- 深色主题对话框：新建项目、打开项目
- 项目变更后同步：窗口标题、扫描/分析/报告 Breadcrumb、报告预览项目名、底部状态栏
- `mock_data.apply_project()` 动态 Breadcrumb 辅助函数

## 4. 本次不做什么

- ❌ 不把「项目」加入左侧导航
- ❌ 不新增 Project 页面
- ❌ 不修改扫描页 PCB 画布、设备/分析/报告页结构
- ❌ 不接真实设备、不实现真实扫描、不生成真实报告
- ❌ 不重构主窗口布局、不修改 high_fidelity HTML
- ❌ 不在磁盘创建复杂项目目录（推荐纯内存 Mock）

## 5. 输入规范

- ADR-0018：[decision/ADR-0018-Project-As-Folder-Domain.md](../../decision/ADR-0018-Project-As-Folder-Domain.md)
- 项目对象：[domain/02_Core_Objects/Project.md](../../domain/02_Core_Objects/Project.md)
- 项目生命周期：[domain/05_Lifecycle/Project_Lifecycle.md](../../domain/05_Lifecycle/Project_Lifecycle.md)
- 域到文件系统映射：[domain/07_Implementation_Guide/Domain_To_File_System_Mapping.md](../../domain/07_Implementation_Guide/Domain_To_File_System_Mapping.md)
- Release 015：[Release_015_Report_Module_Mock/README.md](../Release_015_Report_Module_Mock/README.md)

## 6. 输出文件

```text
src/nfs_scanner_pro/project_mock.py
src/nfs_scanner_pro/ui/dialogs/project_dialogs.py
src/nfs_scanner_pro/ui/widgets/recent_project_menu.py
src/nfs_scanner_pro/ui/main_window.py
src/nfs_scanner_pro/ui/mock_data.py
src/nfs_scanner_pro/resources/styles/dark_theme.qss
docs/product-spec/release/Release_016_Project_File_System_Mock/README.md
```

## 7. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

使用顶部 **文件(F)** 菜单测试项目 Mock 动作；观察 Breadcrumb 与底部状态栏变化。

## 8. 验收标准

- [ ] `python scripts/run_mock_ui.py` 可启动
- [ ] 文件菜单含：新建 / 打开 / 打开最近 / 保存 / 关闭 / 打开项目文件夹 / 退出
- [ ] 新建、打开项目弹出深色 Mock 对话框（简体中文）
- [ ] 打开最近项目子菜单 3 项可用
- [ ] 保存 / 关闭 / 打开文件夹仅更新状态栏，无真实 IO
- [ ] 项目变更后扫描/分析/报告 Breadcrumb 首段更新
- [ ] 左侧导航仍无「项目」
- [ ] 四页结构与画布未破坏
- [ ] `python -m compileall src` 通过

## 9. 后续 Release_017 建议

- **日志 / 频谱 / 统计 Dock Mock**：底部面板静态内容
- **扫描→分析→报告联动**：扫描完成后 Mock 自动关联当前项目生成报告草稿
- **项目文件夹结构预览**（只读 Mock 树，仍不接真实 FS 写入）

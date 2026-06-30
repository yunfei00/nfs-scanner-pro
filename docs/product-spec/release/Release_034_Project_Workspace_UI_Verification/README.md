# Release 034 — Project Workspace UI Verification

## 1. Release 目标

为项目 / 工作区 UI 交互建立自动验收，覆盖文件菜单项目操作、新建 / 打开项目 Mock 对话框、最近项目菜单、保存 / 关闭 / 打开项目文件夹 Mock、Breadcrumb 同步与 workspace 状态持久化，且全部写入 `runtime/verification/R034/` 隔离目录。

## 2. 为什么需要 Project / Workspace UI 自动验收

- Release 016~017 引入了 `project_mock` 与 `workspace_state_mock`，但缺少针对 **文件菜单 + 对话框 + Breadcrumb + 重启恢复** 的专项 UI 回归。
- 工作区状态若误写入默认 `runtime/`，会污染共享 Mock 数据并干扰其它 Release 验收。
- 需确保 **不接真实文件系统、不打开资源管理器**，左侧导航仍不含「项目」。

## 3. 覆盖范围

| 区域 | 检查项 |
|---|---|
| 文件菜单 | 新建 / 打开 / 最近 / 保存 / 关闭 / 打开文件夹 / 退出 |
| 对话框 | `NewProjectDialog`、`OpenProjectDialog` 字段与 Mock 行为 |
| Breadcrumb | 扫描 / 分析 / 报告页项目名同步 |
| Workspace | `workspace_state_mock.json` 保存与 MainWindow 重启恢复 |
| 页面回归 | 四页切换、rightDock、工具栏 |
| 隔离 | `runtime/verification/R034/` |

## 4. 本次不做什么

- ❌ 不接真实设备 / 不打开串口 / 不发送 SCPI
- ❌ 不读取真实项目文件夹 / 不调用 `os.startfile`
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口视觉布局
- ❌ 不把「项目」加入左侧导航

## 5. verify_release_034.py 检查项

```
compileall / runtime_isolation / mainwindow_boot
file_menu_project_actions / create_project_dialog / open_project_dialog
recent_project_menu / save_close_open_folder_mock / breadcrumb_sync
workspace_state_persistence / mainwindow_restore / page_switch_regression
no_real_device_access / no_high_fidelity_changes
```

## 6. 与 project_mock.py 的关系

`project_mock.py` 提供内存态项目数据（当前项目、最近项目、新建 / 打开 / 保存 / 关闭），不写真实磁盘。验收脚本通过菜单动作与对话框触发 MainWindow handler，验证 Mock 状态与 UI 同步。

## 7. 与 workspace_state_mock.py 的关系

`workspace_state_mock.py` 将工作区 JSON 持久化到 `app_paths.get_workspace_state_path()`。在 `NFS_SCANNER_RUNTIME_DIR=runtime/verification/R034` 下，文件为 `runtime/verification/R034/workspace_state_mock.json`。

## 8. 与 NFS_SCANNER_RUNTIME_DIR / R034 的关系

`verify_release_034.py` 调用 `verification_runtime.enter_release_runtime("R034")`，所有 workspace / mock 扫描产物仅写入 `runtime/verification/R034/`，不污染 `runtime/mock_projects/`。

## 9. 本地运行方式

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_034.py
python scripts/verify_all.py --only 034
```

## 10. CI 运行方式

GitHub Actions 执行全量 `python scripts/verify_all.py`，Release 034 已注册。

## 11. 后续 Release 约束

1. 项目 / 工作区相关 Mock 数据必须写入隔离 runtime。
2. 禁止在验收脚本中硬编码 `runtime/mock_projects`。
3. 新增项目 UI 检查时优先扩展 `verify_release_034.py` 或新建 Release 脚本，勿破坏左侧导航结构。

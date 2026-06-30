# Release_034 验收报告

## 执行时间

2026-06-30 15:53:49 UTC

## 执行命令

```bash
python scripts/verify_release_034.py
python scripts/verify_all.py --only 034
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.23s)
- [PASS] `runtime_isolation` (0.08s) — runtime/verification/R034/workspace_state_mock.json; ok
- [PASS] `mainwindow_boot` (0.44s) — menus=6
- [PASS] `file_menu_project_actions` (0.45s)
- [PASS] `create_project_dialog` (0.67s)
- [PASS] `open_project_dialog` (0.70s)
- [PASS] `recent_project_menu` (0.62s)
- [PASS] `save_close_open_folder_mock` (1.36s)
- [PASS] `breadcrumb_sync` (1.04s)
- [PASS] `workspace_state_persistence` (0.01s) — runtime/verification/R034/workspace_state_mock.json
- [PASS] `mainwindow_restore` (2.12s)
- [PASS] `page_switch_regression` (1.82s)
- [PASS] `no_real_device_access` (0.01s)
- [PASS] `no_high_fidelity_changes` (0.05s)

## 结果

PASS

## runtime 隔离路径

- `runtime/verification/R034/`

## workspace_state_mock.json 路径

- `runtime/verification/R034/workspace_state_mock.json`

## 是否接真实设备

否

## 是否打开系统资源管理器

否

## 是否生成真实 PDF / Word / Excel

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是

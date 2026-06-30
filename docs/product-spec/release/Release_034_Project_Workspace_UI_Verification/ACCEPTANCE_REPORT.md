# Release_034 验收报告

## 执行时间

2026-06-30 23:08:21 UTC

## 执行命令

```bash
python scripts/verify_release_034.py
python scripts/verify_all.py --only 034
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.55s)
- [PASS] `runtime_isolation` (0.12s) — runtime/verification/R034/workspace_state_mock.json; ok
- [PASS] `mainwindow_boot` (0.70s) — menus=6
- [PASS] `file_menu_project_actions` (0.62s)
- [PASS] `create_project_dialog` (1.31s)
- [PASS] `open_project_dialog` (0.85s)
- [PASS] `recent_project_menu` (0.72s)
- [PASS] `save_close_open_folder_mock` (1.56s)
- [PASS] `breadcrumb_sync` (1.31s)
- [PASS] `workspace_state_persistence` (0.02s) — runtime/verification/R034/workspace_state_mock.json
- [PASS] `mainwindow_restore` (1.93s)
- [PASS] `page_switch_regression` (1.84s)
- [PASS] `no_real_device_access` (0.01s)
- [PASS] `no_high_fidelity_changes` (0.08s)

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

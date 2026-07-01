# Release_037 验收报告

## 执行时间

2026-07-01 23:49:11 UTC

## 执行命令

```bash
python scripts/verify_release_037.py
python scripts/check_real_devices_safe.py
python scripts/verify_all.py --only 037
```

## 检查项

- [PASS] `compileall` (0.61s)
- [PASS] `real_motion_imports` (0.00s)
- [PASS] `default_real_hardware_disabled` (0.00s)
- [PASS] `grbl_status_parser` (0.00s)
- [PASS] `motion_commands_blocked` (0.00s)
- [PASS] `safe_command_whitelist` (0.02s) — writes=['?']
- [PASS] `check_real_devices_safe_default` (0.77s)
- [PASS] `mock_ui_unchanged` (6.07s)
- [PASS] `top_menu_always_visible` (0.58s) — menus=['文件(F)', '编辑(E)', '视图(V)', '工具(T)', '设置(S)', '帮助(H)']
- [PASS] `no_high_fidelity_changes` (0.11s)

## 结果

PASS

## 默认是否连接真实设备

否

## 是否执行真实运动

否

## 是否允许读取位置

是，仅在 NFS_ENABLE_REAL_HARDWARE=1 下通过 `?` 查询 MPos/WPos

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是

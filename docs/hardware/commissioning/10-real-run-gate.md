# 10 — Real-run 门禁

## 前置条件（全部满足才允许 real-run，本 Release 仍不执行）

1. `NFS_HARDWARE_MODE=real`
2. `NFS_ENABLE_REAL_HARDWARE=1`
3. `NFS_ENABLE_REAL_SCAN_EXECUTION=1`
4. motion_status **passed**
5. spectrum_idn **passed**
6. spectrum_marker **passed**
7. joint_sample **passed**
8. scan_plan_dry_run **passed**
9. scan_fake_run **passed**
10. failure_records 为空或已确认关闭
11. 用户 manual confirm 完成

## 默认

`ready_for_real_run = false`

## 评估

```powershell
python scripts/start_hardware_commissioning.py --mode fake --show-gates
```

Release_048 仅输出 gate 结果，**绝不执行 real-run**。

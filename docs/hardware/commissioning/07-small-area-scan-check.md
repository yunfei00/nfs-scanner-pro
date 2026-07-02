# 07 — 小区域扫描检查

## 步骤

- scan_plan_dry_run：校验 3x3 计划
- scan_fake_run：9 点 fake 结果

## 命令

```powershell
python scripts/run_real_scan_offline.py --dry-run
python scripts/run_real_scan_offline.py --fake-run
```

## PASS

dry-run ok；fake-run completed_points=9。

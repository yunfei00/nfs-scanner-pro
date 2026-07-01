# Release_032 验收报告

## 执行时间

2026-07-01 23:25:05 UTC

## 执行命令

```bash
python scripts/verify_release_032.py
python scripts/verify_all.py --list
python scripts/verify_all.py --only 030
python scripts/verify_all.py --from 030 --keep-runtime
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall` (0.08s)
- [PASS] `app_paths_runtime_override` (0.01s) — runtime\verification\R032
- [SKIP] `verify_all_isolated_only` — NFS_VERIFY_NESTED=1
- [SKIP] `verify_all_isolated_from` — NFS_VERIFY_NESTED=1
- [PASS] `runtime_no_mock_projects_pollution` (0.05s) — new_st_verify=0 isolated_json=True
- [PASS] `legacy_scripts_no_hardcoded_runtime` (0.01s) — checked 9 scripts
- [SKIP] `verify_all_cli` — NFS_VERIFY_NESTED=1
- [PASS] `runtime_gitignore` (0.00s) — ok
- [PASS] `no_real_device_access` (0.01s)
- [PASS] `no_high_fidelity_changes` (0.10s)

## 结果

PASS

## 被迁移的脚本

- `verify_release_022.py`
- `verify_release_023.py`
- `verify_release_024.py`
- `verify_release_025.py`
- `verify_release_026.py`
- `verify_release_027.py`
- `verify_release_028.py`
- `verify_release_029.py`
- `verify_release_030.py`

## runtime 隔离路径

- `runtime/verification/R022/` … `runtime/verification/R032/`

## 是否污染 runtime/mock_projects

否

## 是否接真实设备

否

## 是否生成真实 PDF / Word / Excel

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是

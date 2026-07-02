# Release_046 验收报告

## 执行时间

2026-07-02 02:39:45 UTC

## 执行命令

```bash
python scripts/verify_release_046.py
python scripts/verify_all.py --only 046
python scripts/verify_all.py --from 045
python scripts/verify_all.py
```

## PASS / FAIL 项

- [PASS] `compileall` (0.51s)
- [PASS] `real_scan_console_imports` (0.00s)
- [PASS] `console_model` (0.00s)
- [PASS] `controller_default_safe` (0.01s)
- [PASS] `console_widget_offscreen` (0.03s)
- [PASS] `scan_page_integration` (0.22s)
- [PASS] `fake_run_outputs` (0.03s) — D:\code_2026\nfs-scanner-pro\runtime\verification\R046\real_scan_runs\RS-5438991B
- [PASS] `real_run_blocked_by_default` (0.00s)
- [PASS] `pause_resume_stop_state` (0.00s)
- [PASS] `source_safety_guards` (0.00s)
- [PASS] `mock_ui_unchanged` (68.08s)
- [PASS] `no_high_fidelity_changes` (0.08s)

## 是否默认连接真实设备

否

## 是否默认执行真实运动

否

## 是否支持 dry-run

是

## 是否支持 fake-run

是

## 是否提供 real-run 入口

是，但默认 blocked

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是

## 结果

PASS

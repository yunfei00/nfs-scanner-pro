# Release_045 验收报告

## 执行时间

2026-07-02 01:44:11 UTC

## 执行命令

```bash
python scripts/verify_release_045.py
python scripts/verify_all.py --only 045
python scripts/verify_all.py --from 044
python scripts/verify_all.py
python scripts/hardware_debug_wizard.py
python scripts/hardware_debug_wizard.py --fake-check
```

## PASS / FAIL 项

- [PASS] `compileall` (0.43s)
- [PASS] `hardware_mode_imports` (0.00s)
- [PASS] `hardware_mode_default_mock` (0.03s)
- [PASS] `hardware_mode_env_override` (0.00s)
- [PASS] `hardware_mode_persistence` (0.04s)
- [PASS] `device_page_mode_ui` (0.31s)
- [PASS] `real_probe_default_disabled` (0.13s)
- [PASS] `hardware_debug_wizard_default` (0.43s)
- [PASS] `hardware_debug_wizard_fake_check` (2.84s)
- [PASS] `hardware_debug_guide_exists` (0.00s)
- [PASS] `source_safety_guards` (0.01s)
- [PASS] `mock_ui_unchanged` (64.85s)
- [PASS] `no_high_fidelity_changes` (0.06s)

## 默认硬件模式

Mock

## 是否默认连接真实设备

否

## 是否支持 Fake Hardware

是

## 是否支持 Real 模式安全探测

是

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是

## 结果

PASS

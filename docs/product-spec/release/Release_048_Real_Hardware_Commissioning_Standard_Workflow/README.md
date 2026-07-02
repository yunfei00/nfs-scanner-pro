# Release 048 — Real Hardware Commissioning Standard Workflow

## 1. Release 目标

标准化真实硬件现场联调：阶段划分、PASS/FAIL 判定、session 持久化、real-run 门禁。

## 2. 为什么需要

Release_047 提供了文档与诊断；本 Release 将联调过程 **流程化、可记录、可复盘**。

## 3. commissioning workflow

`config/commissioning.workflow.example.yaml` — 14 个标准阶段。

## 4. 三种模式

- **offline**：不连设备
- **fake**：FakeTransport
- **real-safe**：仅 test_all_safe（需 NFS_ENABLE_REAL_HARDWARE=1）

## 5–7. 核心模块

- `CommissioningSession` / `CommissioningStep`
- `CommissioningRunner`
- `commissioning_persistence`

## 8. start_hardware_commissioning.py

```bash
python scripts/start_hardware_commissioning.py --mode offline
python scripts/start_hardware_commissioning.py --mode fake
python scripts/start_hardware_commissioning.py --mode real-safe
```

## 9–10. 其他脚本

- `validate_commissioning_readiness.py`
- `generate_commissioning_template.py`

## 11. real_run_gate

评估 11 项前置条件，**默认 ready_for_real_run=false**，不执行 real-run。

## 12. 本次不做什么

不连接真实设备、不运动、不 sweep、不改 UI 布局。

## 13. 下一步 Release_049

真实硬件现场联调 UI 页面与一键诊断入口。

## 验收

```bash
python scripts/verify_release_048.py
```

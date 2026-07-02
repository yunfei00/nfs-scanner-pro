# Release 043 — Manual Step By Step 3x3 Point Sampling

## 1. Release 目标

在 Release_042 的 3×3 扫描计划基础上，实现**逐点手动确认采样**：用户手动移动平台到计划点附近，确认后读取位置与频谱单点，保存该点结果，支持断点继续。

## 2. 为什么先做逐点手动确认采样

自动连续扫描风险高。逐点确认可在每步验证位置容差与幅度，再逐步完成 9 点。

## 3. 与 Release_041 的关系

复用 `JointSampleAdapter` 的**只读**联合采样逻辑（当前位置 + Marker 幅度），不运动、不 sweep。

## 4. 与 Release_042 的关系

从 `scan_plan.json` 创建 `ManualScanSession`，按计划点逐点采样。

## 5. ManualScanSession 数据结构

含 `session_id`、`plan_id`、`position_tolerance_mm`（默认 0.2 mm）、9 个 `ManualScanPointStatus`。

## 6. 点位状态

| 状态 | 说明 |
|------|------|
| pending | 待采样 |
| sampled | 已采样 |
| failed | 位置校验失败等 |
| skipped | 跳过 |

## 7. 位置容差检查

`error_mm = sqrt(dx² + dy² + dz²)`，需 ≤ `NFS_MANUAL_SCAN_POSITION_TOLERANCE_MM`（默认 0.2）。

## 8. manual_3x3_point_sample_safe.py 用法

**默认（安全提示）：**
```bash
python scripts/manual_3x3_point_sample_safe.py
```

## 9. --create-session

```bash
python scripts/manual_3x3_point_sample_safe.py --create-session --plan <scan_plan.json>
```

## 10. --status

```bash
python scripts/manual_3x3_point_sample_safe.py --session <manual_scan_session.json> --status
```

## 11. --fake-sample

```bash
python scripts/manual_3x3_point_sample_safe.py --session <path> --point-index 0 --fake-sample
```

## 12. --confirm-sample 真实采样

```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
python scripts/manual_3x3_point_sample_safe.py --session <path> --point-index 0 --confirm-sample
```

需同时满足：硬件开关、`--confirm-sample`、`--point-index`、位置容差通过。

## 13. 本次禁止行为

自动连续运动、move_to、home、G-code、自动 jog、自动采 9 点、sweep、完整 Trace。

## 14. 后续 Release_044 建议

**3×3 手动采样结果转标准 ScanTask 数据集** — 将 session 样本汇总为 Mock/真实扫描任务数据格式。

## 15. 本地验收

```bash
python scripts/verify_release_043.py
python scripts/verify_all.py --only 043
```

# Release 042 — Real Small Area 3x3 Scan Dry Run Planner

## 1. Release 目标

在 Release_041 联合单点采样基础上，生成 **3×3 小区域扫描 dry-run 计划**，做软限位与路径点安全校验，保存 JSON / CSV，**不连接设备、不运动、不采样**。

## 2. 为什么先做 3x3 dry-run 扫描计划

真实扫描前需验证路径、限位与落盘格式。dry-run 只生成计划文件，零运动风险。

## 3. generate_3x3_scan_plan 说明

- 9 点固定，围绕中心 `(center_x, center_y, z)`
- 步距 `step_mm`，蛇形顺序：第 1 行左→右，第 2 行右→左，第 3 行左→右
- `dry_run=True`，`safe_mode=True`

## 4. 软限位配置

默认来自 `hardware_config` / 环境变量：

| 轴 | 默认范围 |
|----|----------|
| X | 0 ~ 200 |
| Y | -200 ~ 0 |
| Z | 0 ~ 50 |

扫描限制：`NFS_SCAN_MAX_POINTS=9`，`NFS_SCAN_MAX_STEP_MM=1.0`，`NFS_SCAN_MAX_AREA_MM=5.0`

## 5. 扫描计划 JSON 格式

`runtime/verification/R042/scan_plans/{plan_id}/scan_plan.json`

含 `plan_id`、`points[]`、`dry_run`、`safe_mode`、`validation`。

## 6. 扫描计划 CSV 格式

同目录 `scan_plan.csv`：表头 + 9 行点位。

## 7. plan_small_area_scan_dry_run.py 用法

```bash
python scripts/plan_small_area_scan_dry_run.py
python scripts/plan_small_area_scan_dry_run.py --center-x 50 --center-y -50 --z 5 --step 0.5
```

## 8. --no-save 用法

```bash
python scripts/plan_small_area_scan_dry_run.py --no-save
```

只打印 9 点与校验结果，不写文件。

## 9. 本次禁止行为

自动连续运动、move_to、home、G-code、jog、sweep、完整 Trace、相机、舵机。

## 10. 与 Release_041 的关系

Release_041 支持当前位置 + 频谱单点联合采样。Release_042 **仅生成计划**，不调用 `JointSampleAdapter`。

## 11. 后续 Release_043 建议

**3×3 扫描计划逐点手动确认采样** — 用户显式确认每点后移动并采样，仍不自动连续运动。

## 12. 本地验收

```bash
python scripts/verify_release_042.py
python scripts/verify_all.py --only 042
```

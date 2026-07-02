# 00 — 联调总览

## 阶段

1. 环境 / 配置（offline）
2. 运动 / 频谱 / 相机 / 舵机（fake → real-safe）
3. 联合采样（manual confirm）
4. 扫描 dry-run / fake-run（offline/fake）
5. real-run 门禁（仅评估）

## PASS / FAIL

- **passed**：检查项满足 pass_criteria
- **failed**：不满足，写入 failure_records
- **skipped**：offline/fake 跳过或 optional
- **blocked**：缺少安全开关或 real-safe 未启用

## 输出

`runtime/commissioning_sessions/{session_id}/`

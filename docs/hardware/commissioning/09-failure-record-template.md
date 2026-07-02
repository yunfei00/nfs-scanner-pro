# 09 — 故障记录模板

## failure_records.jsonl 格式

```json
{"step_id":"motion_status","stage_id":"motion_status","name":"运动平台状态读取","reason":"COM6 无法打开","timestamp_iso":"..."}
```

## 字段

- step_id / stage_id / name
- reason（必填）
- timestamp_iso

## 关闭条件

- 根因已修复并 re-run 步骤 passed
- 或标记为 known issue 且不影响 fake-run

## 与 Gate 关系

未关闭的 failure 会阻止 ready_for_real_run。

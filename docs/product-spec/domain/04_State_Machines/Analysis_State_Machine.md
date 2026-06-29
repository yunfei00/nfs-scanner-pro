# Analysis State Machine — 分析状态机

## 1. 状态列表
Created | Configured | Generating | Generated | Reviewed | Exported | Error

## 2–3. Generating 失败 → Configured 可 regenerate。

## 4–5. 禁止修改 ScanTask raw。

## 6. UI
analysisPage 进度与预览。

## 7. 日志
AnalysisGenerated / ERROR

## 8. 错误恢复
源 ScanTask 缺失 → [Data_Error_Recovery.md](../06_Error_Recovery/Data_Error_Recovery.md)

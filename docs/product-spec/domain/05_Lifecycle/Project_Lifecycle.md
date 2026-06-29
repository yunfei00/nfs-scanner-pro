# Project Lifecycle — 项目生命周期

| 阶段 | 含义 | 触发 |
|---|---|---|
| Created | 文件夹与 project.json 已建 | 新建项目 |
| Configured | PCB 信息与 Profile 已选 | 保存样品/配置 |
| Active | 已有 Region 或 ScanTask 活动 | 首次扫描或编辑 |
| Completed | 用户标记主要测试完成 | 手动/向导 |
| Archived | 只读归档 | 归档命令 |

持久化字段：`project.json.lifecycleStage`

日志：`logs/project_{timestamp}.log`

扩展 [../../data/Life_Cycle.md](../../data/Life_Cycle.md)

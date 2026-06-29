# NFS Scanner Pro — AI Specification Layer

> **所有 AI 任务从 [AI_INDEX.md](AI_INDEX.md) 开始。** 不要无目标全仓库扫描。

## 目录

| 路径 | 用途 |
|---|---|
| [AI_INDEX.md](AI_INDEX.md) | **第一入口**（200~300 行） |
| [Architecture_Handbook.md](Architecture_Handbook.md) | 架构摘要 + 细节文档链接 |
| [Context_Pack/](Context_Pack/README.md) | 分域快速上下文（100~200 行/文件） |
| [Registry/](Registry/README.md) | 机器可读 YAML 索引 |
| [Task_Guide/](Task_Guide/README.md) | 任务级执行入口（含 Release 010） |
| [Maintenance/](Maintenance/README.md) | 增文档、更 Registry、AI 规则 |

## 与 docs/product-spec 的关系

| 层 | 角色 |
|---|---|
| `docs/product-spec/` | **权威规范**（完整细节） |
| `spec/` | **AI 导航层**（摘要 + 索引 + 任务） |

## 校验

```bash
python scripts/check_spec_registry_paths.py
```

说明：[Maintenance/Registry_Path_Check.md](Maintenance/Registry_Path_Check.md)

## Release

[Release 009.9 README](../docs/product-spec/release/Release_009_9_AI_Knowledge_Index/README.md)

# Review Documentation — 文档审查

## 任务目标

检查新增/修改文档是否：**目录正确、Registry 已更新、无孤立文档、路径有效**。

## 开始前必须阅读

- [spec/AI_INDEX.md](../AI_INDEX.md)
- [spec/Maintenance/How_To_Add_New_Document.md](../Maintenance/How_To_Add_New_Document.md)
- [spec/Maintenance/How_To_Update_Registry.md](../Maintenance/How_To_Update_Registry.md)

## 不要阅读的内容

- 无需读全部历史 Release

## 允许修改的目录

- 被审查的 `docs/`、`spec/` 文档
- `spec/Registry/*.yaml`

## 禁止修改的目录

- 无授权不删除历史文档

## 实现步骤

1. 运行 `python scripts/check_spec_registry_paths.py`。
2. 检查 README 索引链接。
3. 核心决策是否需新 ADR。
4. 命名：PCB/ScanTask vs Sample/Scan。

## 验收标准

- [ ] 路径校验脚本 exit 0
- [ ] Registry 含新文档
- [ ] 无 broken link

## 常见错误

- 只写 md 不更新 YAML
- 创建 spec/ 外孤立文档

## 推荐 commit message

```
docs: add spec and update registry indexes
```

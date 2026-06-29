# 如何准备 Release

## Release 文档位置

`docs/product-spec/release/Release_XXX_名称/README.md`

## 检查清单

1. **背景与范围**：本 Release 解决什么、不做什么。
2. **输出清单**：新增目录与文件列表。
3. **与上一 Release 关系**：权威层级是否变化。
4. **ADR**：架构决策是否需新 ADR。
5. **更新索引**：
   - [docs/product-spec/README.md](../../docs/product-spec/README.md)
   - [spec/Registry/Release.yaml](../Registry/Release.yaml)
   - 根 [README.md](../../README.md)（若对外入口变化）
6. **AI 层**：若影响 AI 工作流，更新 `spec/AI_INDEX.md` 或 Context_Pack。
7. **Task_Guide**：若开启新实现阶段，新增或更新 Task 文档（如 Release 010 → Build_MainWindow）。
8. **路径校验**：`python scripts/check_spec_registry_paths.py`

## Release 010 前置

- Release 009.8 Domain 已完成
- Release 009.5 UI 已完成
- **Release 009.9 AI Index 完成且校验通过**
- 从 [Build_MainWindow.md](../Task_Guide/Build_MainWindow.md) 进入实现

## 禁止

- 跳过 009.9 直接全库扫描式开发
- 删除旧 Release 文件夹

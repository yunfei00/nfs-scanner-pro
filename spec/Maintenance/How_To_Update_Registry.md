# 如何更新 Registry

## 文件位置

`spec/Registry/*.yaml`

## 更新规则

| 变更类型 | 更新文件 |
|---|---|
| 新增 UI 组件/模式/QSS | `UI.yaml` → `related_docs` 对应 key |
| 新增领域对象/状态机 | `Domain.yaml` |
| 新增业务流程 | `Workflow.yaml` |
| 新增/引用 data 历史模型 | `Data.yaml` |
| 新增 ADR | `Decision.yaml` + 各 Registry 的 `adr` 若相关 |
| 新增 Release | `Release.yaml` |
| Qt/objectName/GraphicsView | `Qt.yaml` |

## 每个 YAML 字段

- `must_read`：任务最小必读（保持精简）
- `related_docs`：按主题分组的路径列表
- `adr`：相关 ADR 路径
- `forbidden`：AI/开发禁止项
- `output_expected`：任务产出期望

## 路径要求

- 使用仓库相对路径：`docs/product-spec/...` 或 `spec/...`
- **路径必须真实存在**
- 提交前运行：

  ```bash
  python scripts/check_spec_registry_paths.py
  ```

## 同步更新

- 新 Release → `Release.yaml` + `docs/product-spec/release/Release_XXX/README.md`
- 新 Task → `spec/Task_Guide/` + [Task_Guide/README.md](../Task_Guide/README.md)

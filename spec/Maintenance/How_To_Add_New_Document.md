# 如何新增文档

## 原则

不允许创建 **孤立文档**（无 README / Registry 入口的 md）。

## 步骤

1. **确定类别**，放入正确目录：
   - UI → `docs/product-spec/design-system/` 或 `ui-wireframe/`
   - 领域 → `docs/product-spec/domain/`
   - 流程 → `docs/product-spec/workflow/`
   - 决策 → `docs/product-spec/decision/`（ADR）
   - Qt → `docs/product-spec/qt-spec/` 或 `design-system/07_Qt_Implementation/`

2. **更新目录 README**：在对应文件夹 README 增加链接一行。

3. **更新 Registry**：见 [How_To_Update_Registry.md](How_To_Update_Registry.md)。

4. **核心决策**：若改变产品原则、导航、对象关系、状态机，**必须新增 ADR**，并更新 `Decision.yaml`。

5. **Context Pack**：若影响 AI 高频上下文，酌情更新 `spec/Context_Pack/` 摘要（保持 100~200 行，不复制全文）。

6. **校验**：

   ```bash
   python scripts/check_spec_registry_paths.py
   ```

7. **product-spec README**：重大模块变更时更新 [docs/product-spec/README.md](../../docs/product-spec/README.md)。

## 禁止

- 在仓库根或随意路径新建 spec 副本
- 删除历史 Release / data 兼容文档
- 无 ADR 推翻 ADR-0013、0018 等已接受决策

# ADR-0021 AI Knowledge Index

## 状态

已接受

## 背景

Release 008~009.8 后，`docs/product-spec/` 已有 ui-wireframe、design-system（七层）、domain（54+ 文件）、workflow、data、rules、decision（20 ADR）等大量 Markdown。Cursor / ChatGPT / Codex 若每次全仓库搜索或通读，会导致：

- 上下文窗口浪费与截断
- 重复读取、结论互相矛盾
- 不知道改 UI 应先读 wireframe 还是 design-system
- 任务级入口缺失，Release 010 无法标准化启动

## 问题

1. **AI 上下文过大**：数百 md 无法一次读完。
2. **文档入口分散**：权威在 ui-wireframe、design-system、domain 多处。
3. **Cursor 重复搜索**：无固定第一入口。
4. **模块修改路径不清**：缺 Registry 与 Task_Guide。
5. **后续开发缺任务级入口**：MainWindow 等实现无标准必读清单。

## 决策

建立 **`spec/` AI 入口层**（Release 009.9）：

| 组件 | 路径 | 职责 |
|---|---|---|
| 第一入口 | `spec/AI_INDEX.md` | 所有 AI 任务从这里开始 |
| 架构摘要 | `spec/Architecture_Handbook.md` | 15~20 节总览 + 原文链接 |
| 快速上下文 | `spec/Context_Pack/*.md` | 100~200 行摘要 |
| 机器索引 | `spec/Registry/*.yaml` | must_read / related_docs / adr / forbidden |
| 任务入口 | `spec/Task_Guide/*.md` | Release 010+ 执行清单 |
| 维护 | `spec/Maintenance/*.md` | 增文档、更 Registry 规则 |
| 校验 | `scripts/check_spec_registry_paths.py` | Registry md 路径存在性 |

**规则**：

- 任何 AI 任务先读 `AI_INDEX`，再读对应 Registry，再读 Task_Guide，最后按需打开 listed docs。
- 新增文档必须更新 Registry；核心决策必须 ADR。
- 不删除历史文档；data/ 保持历史兼容，domain/ 为领域权威。

## 后果

### 正面

- AI 阅读成本可控（索引 + 摘要 + 按需深入）。
- Release 010 MainWindow 有标准入口 [Build_MainWindow.md](../../../spec/Task_Guide/Build_MainWindow.md)。
- Registry 可机器校验，减少死链。

### 负面

- 维护负担：新文档需同步 Registry（通过 Maintenance 文档与脚本缓解）。
- Context_Pack 可能与原文短暂不同步（需 Release 维护时更新摘要）。

## 替代方案

| 方案 | 未采纳原因 |
|---|---|
| 继续全仓库 @docs | 上下文爆炸，无任务边界 |
| 单一大 handbook 复制全部规范 | 仍过长，且与原文双源维护 |
| 仅 README 索引 | 非机器可读，AI 难结构化执行 |
| 向量数据库/RAG | 超出当前纯文档仓库范围 |

## 约束

- 本 ADR **不写 PySide6 业务代码**。
- **不删除** 已有 `docs/product-spec/**`。
- **不修改** 已接受业务 ADR 的结论，仅增加入口机制。
- Registry 中 `.md` 路径必须存在（校验脚本 exit 0）。

## 与 Release_010 的关系

Release 010（MainWindow Prototype）**必须在 Release 009.9 完成且路径校验通过后**启动。

实现者顺序：

1. `spec/AI_INDEX.md`
2. `spec/Registry/UI.yaml` + `Qt.yaml`
3. `spec/Task_Guide/Build_MainWindow.md`
4. ui-wireframe + design-system 列出的组件规范

Release 010 **不得**跳过 AI Index 机制；代码审查使用 `Task_Guide/Review_Code.md`。

## 相关文档

- [Release 009.9 README](../release/Release_009_9_AI_Knowledge_Index/README.md)
- [spec/AI_INDEX.md](../../../spec/AI_INDEX.md)
- [AI_Context_Rules.md](../../../spec/Maintenance/AI_Context_Rules.md)

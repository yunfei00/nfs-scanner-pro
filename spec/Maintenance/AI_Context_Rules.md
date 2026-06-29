# AI Context Rules — AI 上下文规则

## 强制入口

**任何 AI 任务必须先读** [spec/AI_INDEX.md](../AI_INDEX.md)。

## 阅读顺序

1. `spec/AI_INDEX.md`
2. 任务对应 `spec/Registry/{UI|Domain|Workflow|Qt|Decision|Data|Release}.yaml`
3. `spec/Task_Guide/{Task}.md`（若有）
4. Registry 列出的 **具体 md**，按需打开，禁止全仓库通读

## 禁止行为

- 不允许无目标全仓库扫描
- 不允许跳过 Registry 直接改代码
- 不允许在不了解 ADR 时推翻核心设计（Project 文件夹、四项导航、热力图整图等）
- 不允许重复创建已有规范文档
- 不允许自由发明目录结构

## 任务完成后

- 若新增文档 → 更新 Registry（见 [How_To_Update_Registry.md](How_To_Update_Registry.md)）
- 若改变架构 → 新增 ADR
- 运行路径校验脚本

## 与 Cursor / ChatGPT / Codex

- 将 `spec/AI_INDEX.md` 作为 system/context 第一条链接
- 大任务拆为 Task_Guide 单次执行
- 代码审查使用 [Review_Code.md](../Task_Guide/Review_Code.md)

## 权威层级（冲突时）

1. ADR
2. ui-wireframe（布局尺寸）
3. design-system / domain（UI 与领域各自权威）
4. data/（历史兼容）
5. 旧 wireframe/、product-design/（参考）

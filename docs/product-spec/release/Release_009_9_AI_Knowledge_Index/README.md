# Release 009.9 — AI Knowledge Index

## 1. Release 背景

Release 008 ~ 009.8 已积累 **150+ Markdown**：线框、Design System、Domain Model、Workflow、ADR 等。人类可逐目录浏览，但 Cursor / ChatGPT / Codex **无法一次读全**，常重复搜索、误读旧文档或违反 ADR。

Release 009.9 建立 **AI 入口层**（`spec/`），不增加业务规范，只提供索引、摘要、任务入口与路径校验。

## 2. 为什么文档增多会让 AI 再次混乱

| 现象 | 后果 |
|---|---|
| 上下文窗口被占满 | 漏读 ADR、误用旧版 `data/` |
| 入口分散 | 不知先读 wireframe 还是 domain |
| 每次会话重新 grep | 耗时、结果不一致 |
| 无任务级清单 | Release 010 易写业务代码过头 |
| 孤立新增 md | Registry 未更新，索引失效 |

## 3. 本次解决的 5 个问题

1. **AI 上下文过大** → Context_Pack 每文件 100~200 行
2. **文档入口分散** → `spec/AI_INDEX.md` 唯一第一入口
3. **Cursor 重复搜索** → Registry YAML 机器可读
4. **不知先读哪些** → Task_Guide 按任务列 must_read
5. **缺少任务级入口** → Build_MainWindow 等 10 篇

## 4. 本次不做什么

- ❌ 不写 PySide6 业务代码
- ❌ 不生成高保真图片
- ❌ 不改业务规则 / workflow 正文
- ❌ 不删除历史文档
- ❌ 不自动 git commit

## 5. 本次输出

| 产出 | 路径 |
|---|---|
| AI 第一入口 | [spec/AI_INDEX.md](../../../../spec/AI_INDEX.md) |
| 架构摘要 | [spec/Architecture_Handbook.md](../../../../spec/Architecture_Handbook.md) |
| 上下文包 | [spec/Context_Pack/](../../../../spec/Context_Pack/README.md) |
| Registry | [spec/Registry/](../../../../spec/Registry/README.md) |
| 任务指南 | [spec/Task_Guide/](../../../../spec/Task_Guide/README.md) |
| 维护说明 | [spec/Maintenance/](../../../../spec/Maintenance/README.md) |
| 路径校验 | [scripts/check_spec_registry_paths.py](../../../../scripts/check_spec_registry_paths.py) |

## 6. Release 010 前为什么必须先做本步

MainWindow Prototype 需同时遵守 **UI 009.5 + Domain 009.8 + ADR**。无 AI Index 时，实现者（或 AI）易：

- 把 Project 加回左侧导航
- 默认显示 log/spectrum Dock
- 逐格绘制热力图
- 跳过 Scan 七态

**Release 010 必须从 `spec/AI_INDEX.md` → `Task_Guide/Build_MainWindow.md` 开始。**

## 7. 验收标准

- [x] `spec/AI_INDEX.md` 存在且 ≤300 行
- [x] 7 个 Registry YAML 路径经 `python scripts/check_spec_registry_paths.py` **零缺失**
- [x] `Build_MainWindow.md` 含 must_read / forbidden / 验收标准
- [x] ADR-0021 Accepted
- [x] 根 README 与 product-spec README 指向 `spec/AI_INDEX.md`

---

**状态**：Accepted  
**版本**：Release 009.9  
**依赖**：Release 008、009、009.5、009.8

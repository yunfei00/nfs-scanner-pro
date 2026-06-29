# Registry — 机器可读文档索引

AI 任务：**先读 AI_INDEX → 再读对应 `{Name}.yaml` → 只打开列出的 md 路径。**

| 文件 | 任务类型 |
|---|---|
| [UI.yaml](UI.yaml) | 主窗口、Dock、导航、QSS |
| [Domain.yaml](Domain.yaml) | 领域对象、状态机、Recovery |
| [Workflow.yaml](Workflow.yaml) | 业务流程 |
| [Data.yaml](Data.yaml) | 首版 data/（历史兼容） |
| [Decision.yaml](Decision.yaml) | ADR |
| [Qt.yaml](Qt.yaml) | Qt / PySide6 |
| [Release.yaml](Release.yaml) | Release 008~009.9 |

校验：`python scripts/check_spec_registry_paths.py`

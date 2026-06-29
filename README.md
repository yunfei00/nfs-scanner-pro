# NFS Scanner Pro

面向 PCB 近场电磁扫描的桌面工作台软件（文档仓库 + 后续 PySide6 实现）。

## AI 第一入口（必读）

**所有 Cursor / ChatGPT / Codex 任务从以下开始，不要全仓库通读：**

| 入口 | 说明 |
|---|---|
| [**spec/AI_INDEX.md**](spec/AI_INDEX.md) | AI 唯一第一入口 |
| [spec/Architecture_Handbook.md](spec/Architecture_Handbook.md) | 架构摘要（15~20 节） |
| [spec/Registry/](spec/Registry/README.md) | 机器可读 YAML 索引 |
| [spec/Task_Guide/](spec/Task_Guide/README.md) | 任务级执行入口（含 Release 010 MainWindow） |
| [spec/Maintenance/](spec/Maintenance/README.md) | 增文档、更 Registry、AI 规则 |

路径校验：`python scripts/check_spec_registry_paths.py`

## 产品规范

完整规范见 [docs/product-spec/README.md](docs/product-spec/README.md)。

| Release | 入口 |
|---|---|
| 008 UI Wireframe | [ui-wireframe/](docs/product-spec/ui-wireframe/README.md) |
| 009 Design System | [Release_009](docs/product-spec/release/Release_009_Enterprise_Design_System/README.md) |
| 009.5 UI Foundation | [Release_009_5](docs/product-spec/release/Release_009_5_Enterprise_UI_Foundation/README.md) |
| 009.8 Domain Model | [Release_009_8](docs/product-spec/release/Release_009_8_Enterprise_Domain_Model/README.md) |
| **009.9 AI Index** | [Release_009_9](docs/product-spec/release/Release_009_9_AI_Knowledge_Index/README.md) |
| **010 MainWindow** | [Release_010](docs/product-spec/release/Release_010_MainWindow_Prototype/README.md) |

## 运行 Mock UI（Release 010）

```bash
pip install -r requirements.txt
python scripts/run_mock_ui.py
```

## Release 010 MainWindow Prototype

Mock 主窗口已从 [spec/Task_Guide/Build_MainWindow.md](spec/Task_Guide/Build_MainWindow.md) 启动；详见 [Release_010 README](docs/product-spec/release/Release_010_MainWindow_Prototype/README.md)。

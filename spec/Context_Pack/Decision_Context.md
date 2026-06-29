# Decision Context — ADR 上下文

## 关键 ADR 摘要

| ADR | 决策要点 |
|---|---|
| 0001 | 1 Project = 1 PCB |
| 0003 | Camera 可选，不阻扫描 |
| 0004 | 整区 Hx → 整区 Hy |
| 0005/0019 | Alignment **属 Region** |
| 0007 | ScanTask raw 不覆盖 |
| 0008/0018 | Project = **文件夹**；文件菜单；复制=备份 |
| 0010 | Heatmap 与 raw 分离，整图 |
| 0012 | 先 Wireframe 后高保真 |
| 0013 | 项目不在左侧导航 |
| 0014 | Enterprise Design System |
| 0017 | Scan **七态**状态机 |
| 0020 | ScanTask 绑定 DeviceSnapshot |
| **0021** | **AI_INDEX 为 AI 第一入口** |

## 不可推翻（无新 ADR 禁止）

- Project 非左侧一级页
- 辅助 Dock 默认隐藏
- QGraphicsView 主画布
- 热力图 QPixmap 单层
- Alignment 非 Project 级唯一

## 细节入口

- [decision/README.md](../../docs/product-spec/decision/README.md)

## Registry

[spec/Registry/Decision.yaml](../Registry/Decision.yaml)

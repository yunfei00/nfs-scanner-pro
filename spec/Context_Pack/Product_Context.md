# Product Context — 产品上下文

## 产品目标

为 PCB **近场 EMC 扫描** 提供商业级桌面工作台：项目数据可归档、扫描可复现、报告可交付。

## 用户真实流程

1. 新建/打开 Project（文件夹）
2. 放置 PCB，连接运动平台 + 频谱仪
3. 可选拍照、建 Region、对齐
4. Hx 整区扫描 → Hy 整区扫描（可选）
5. 热力图与分析
6. 导出报告

## 一级模块

| 模块 | UI |
|---|---|
| 扫描 | 默认页，画布+参数 Dock |
| 设备 | 连接与 Profile |
| 分析 | Heatmap/Analysis |
| 报告 | Report |
| Project | **文件菜单** |

## 不做什么（Non-Goals）

- 不是纯 GRBL 控制器、不是纯热力图 Viewer
- 不是 Web SaaS 后台
- 不是 Import/Export 专有工程格式为主路径（文件夹复制为主）

## 商业化目标

实验室可追溯（DeviceSnapshot）、多 Region 工程、Keysight/R&S 类工业 UI。

## 细节入口

- [docs/product-spec/01_Product_Vision.md](../../docs/product-spec/01_Product_Vision.md)
- [docs/product-spec/02_Product_Goals.md](../../docs/product-spec/02_Product_Goals.md)
- [docs/product-spec/04_Object_Model.md](../../docs/product-spec/04_Object_Model.md)

## Registry

[spec/Registry/Release.yaml](../Registry/Release.yaml)

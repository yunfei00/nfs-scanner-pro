# Domain Principles — 领域原则

> Release 009.8 · 所有领域对象与状态机必须遵守。

## 1. PCB 是扫描系统的视觉中心

PCB 照片与热力图叠加占据主画布 ≥70%。领域对象中的 **PCB** 承载样品身份与图像；UI 不以 Project 表单替代 PCB 展示。

## 2. Project 是数据容器，不是一级业务页面

Project 对应一个文件夹（ADR-0008），包含 PCB、Region、ScanTask 等。新建/打开/保存经**文件菜单**（ADR-0013），不作为左侧导航页。

## 3. Region 是扫描和分析的最小业务区域

Region 有独立名称（CPU、WiFi…）、几何范围、扫描配置。无 Region 不可 ScanTask。

## 4. Alignment 属于 Region

物理坐标 ↔ 图像坐标映射存于 Region 的 `alignment.json`，非 Project 级。

## 5. ScanTask 绑定五元组

每次 ScanTask 必须关联：

- Project
- PCB（样品上下文）
- Region
- Probe（Hx 或 Hy）
- DeviceSnapshot（扫描开始时冻结）

## 6. Hx / Hy 是 Probe 方向，不是两个 Project

同一 Region 下可有多条 ScanTask（Hx 一条、Hy 一条）。V1 整区域 Hx 后整区域 Hy（ADR-0004）。

## 7. Camera 可选

Camera 离线不阻止 ScanTask；无 PCB 图仍可生成非叠加热力图（ADR-0003）。

## 8. DeviceProfile vs DeviceSnapshot

- **DeviceProfile**：系统级模板，可复用。
- **DeviceSnapshot**：某次 ScanTask 的设备状态冻结，不可因 Profile 变更而改写。

## 9. Report 派生，不改原始数据

Report 引用 ScanTask / Analysis / Heatmap；重新导出不覆盖 raw data（ADR-0010）。

## 10. 运行期状态可恢复、可诊断、可日志

所有状态机转换应写入 `project/logs/`；异常走 `06_Error_Recovery/` 模型，UI 经 statusBar + logDock 反馈。

## 禁止事项

- 禁止 Project 保存实时设备连接态
- 禁止覆盖 ScanTask 原始数据
- 禁止 Region 删除静默删除 ScanTask 原始目录

## 相关文档

- [Domain_Map.md](Domain_Map.md)
- [Object_Relationships.md](Object_Relationships.md)

# Domain Map — 领域地图

## 上下文边界

```text
┌─────────────────────────────────────────────────────────┐
│ System（NFS Scanner Pro 安装实例）                        │
│  ├── DeviceProfile*（系统级，Settings 管理）              │
│  └── Project*（文件夹，用户工程）                         │
│       ├── PCB（1:1 被测板）                             │
│       ├── Region*（扫描区域）                             │
│       │    ├── Alignment（0..1）                         │
│       │    └── ScanTask*                                 │
│       │         ├── Probe + DeviceSnapshot               │
│       │         ├── ScanPoint* / FrequencyData*           │
│       │         ├── Heatmap*                             │
│       │         └── Analysis* → Report*                  │
│       ├── DeviceSnapshot（项目级，可选）                  │
│       └── logs / reports / exports                       │
└─────────────────────────────────────────────────────────┘

运行期设备（非持久化根对象）：
  MotionSystem · SpectrumAnalyzer · CameraSystem · ServoSystem
  连接态由 Device_State_Machine 管理，配置来自 DeviceProfile
```

## 核心域 vs 支撑域

| 域 | 对象 | 说明 |
|---|---|---|
| 工程域 | Project, PCB, Region | 用户数据容器 |
| 扫描域 | ScanTask, ScanPoint, Probe | 采集执行 |
| 测量域 | FrequencyData, Heatmap | 频谱与场分布 |
| 分析域 | Analysis, Report | 派生结果 |
| 设备域 | DeviceProfile, DeviceSnapshot, Motion… | 硬件抽象 |
| 对齐域 | Alignment, HxHyCalibration | 坐标与探头 |

## 与 UI 页映射（非一级 Project 页）

| UI 页（009.5 导航） | 主要 Domain 对象 |
|---|---|
| 扫描 | PCB, Region, ScanTask, Probe |
| 设备 | MotionSystem, SpectrumAnalyzer, CameraSystem |
| 分析 | Heatmap, Analysis |
| 报告 | Report |

Project 操作：**文件菜单** ↔ Project 文件夹。

## 相关文档

- [Object_Relationships.md](Object_Relationships.md)
- [../07_Implementation_Guide/Domain_To_UI_Mapping.md](../07_Implementation_Guide/Domain_To_UI_Mapping.md)

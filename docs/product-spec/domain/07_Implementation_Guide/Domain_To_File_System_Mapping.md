# Domain To File System Mapping — 领域对象到文件系统

> **Project 即文件夹**（ADR-0008 / ADR-0018）。备份 = **复制整个 Project 文件夹**。不设计 Import/Export Project 为主路径。

## 逻辑目录结构（Release 009.8）

```text
ProjectFolder/
├── project.json              # Project 元数据 + lifecycle
├── pcb/                      # PCB（兼容旧 sample/）
│   ├── pcb.json
│   └── images/
├── regions/                  # Region 容器
│   └── {regionId}/
│       ├── region.json
│       ├── alignment.json    # Alignment 属 Region
│       ├── scan_config.json
│       ├── scans/            # ScanTask（逻辑上亦属 Project 聚合）
│       │   └── {scanTaskId}/
│       │       ├── scan.json
│       │       ├── raw/
│       │       └── processed/
│       └── analysis/
├── device_snapshots/         # DeviceSnapshot（任务级+项目级）
│   └── {snapshotId}.json
├── reports/
│   └── {reportId}/
├── logs/
│   ├── domain.log
│   ├── device.log
│   └── scan_{scanTaskId}.log
└── cache/                    # 可删重建：热力图预览、缩略图
```

## 与历史 `07_File_System.md` 对照

| 009.8 路径 | 历史路径 | 对象 |
|---|---|---|
| `pcb/` | `sample/` | PCB |
| `regions/{id}/alignment.json` | 同左 | Alignment |
| `regions/{id}/scans/` | 同左 | ScanTask |
| `device_snapshots/` | `devices/` | DeviceSnapshot |
| `cache/` | （新增） | 非权威缓存 |

**说明**：逻辑上的 `alignment/`、`scans/` 在物理上**位于** `regions/{regionId}/` 下，不单独占 Project 根目录（Alignment 归属 Region，ADR-0019）。

**DeviceProfile** 存系统目录 `{appData}/device_profiles/`，**不在** ProjectFolder（仅 Snapshot 入库）。

## 对象 → 文件速查

| 对象 | 主文件 |
|---|---|
| Project | `project.json` |
| PCB | `pcb/pcb.json`, `pcb/images/*` |
| Region | `regions/{id}/region.json` |
| Alignment | `regions/{id}/alignment.json` |
| ScanTask | `regions/{id}/scans/{scanTaskId}/scan.json` |
| ScanPoint | `…/raw/points.csv` |
| DeviceSnapshot | `device_snapshots/{id}.json` |
| Heatmap | `…/processed/heatmap_*.png` + `.json` |
| Analysis | `regions/{id}/analysis/{id}.json` |
| Report | `reports/{id}/report.json` + `exports/` |

## 规则

- raw **不可覆盖**；重扫新 `scanTaskId` 目录
- `cache/` 丢失不影响权威数据
- 复制 ProjectFolder = 完整备份

## 相关 ADR

[ADR-0018](../../decision/ADR-0018-Project-As-Folder-Domain.md)

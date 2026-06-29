# Domain To Qt Model Mapping

| Domain | Qt 层（Release 010+ 建议） |
|---|---|
| Project | ProjectRepository + ProjectService |
| Region | RegionModel : QAbstractItemModel（可选） |
| ScanTask | ScanTaskController + signals |
| ScanPoint | ScanPointTableModel : QAbstractTableModel |
| Heatmap | QPixmap via HeatmapService |
| Device drivers | MotionDriver interface… |

Mock 阶段：内存 dict + JSON 读写，无 ORM。

## 线程
设备 IO 工作线程；UI 主线程；ScanTask progress 信号 QueuedConnection。

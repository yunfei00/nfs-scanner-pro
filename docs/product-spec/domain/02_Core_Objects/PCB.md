# PCB — 被测印刷电路板

## 1. 对象定义

PCB 表示 Project 中被测的 **物理样品**，Release 009.8 统一历史 `Sample` 概念；是扫描系统的**视觉中心**引用对象。

## 2. 为什么需要这个对象

- 区分「工程容器」(Project) 与「被测物本身」(PCB)
- 承载样品照片、版本、放置方向，供 Region/Alignment 引用
- 画布主图层数据源

## 3. 关键字段

| 字段 | 说明 |
|---|---|
| pcbId | UUID |
| name, sampleId | 样品名/编号 |
| hardwareVersion, softwareVersion | 可选 |
| photoPath | sample/images/ |
| placementNotes | 放置方向 |
| imagedAt | 拍照/导入时间 |

## 4. 所属关系

- 1:1 属于 Project

## 5. 与其它对象关系

- 多 Region 共享同一 PCB 照片
- Alignment 引用 PCB 图像
- ScanTask 绑定 PCB 上下文（经 Project）

## 6. 生命周期

Created → Imaged → Used → Archived（随 Project）

## 7. 状态

Imaged 表示有可用照片；无照片仍可 ScanTask（普通热力图）

## 8. 文件系统映射

```text
{project}/sample/
  pcb.json
  images/pcb_photo.png
```

## 9. UI 映射

- `scanCanvasView` PCB Photo Layer
- 工具栏「拍照」更新 PCB 图像

## 10. Qt/PySide6 实现建议

- `QGraphicsPixmapItem` 加载 photoPath
- PCB 变更发 `DomainEvent` pcbPhotoUpdated

## 11. 禁止事项

- 禁止相机失败阻止 ScanTask（ADR-0003）
- 禁止 PCB 图仅存于 Region 目录（全局在 sample/）

## 相关

- 历史：[../../data/Sample.md](../../data/Sample.md)

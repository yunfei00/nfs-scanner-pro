# Region — 扫描区域

## 1. 对象定义

Region 表示 **PCB 上的一个命名扫描区域**，是扫描与分析的最小业务单元。Region **不等于** ScanTask：Region 描述「扫哪里、怎么扫」，ScanTask 描述「某次实际采集执行」。

## 2. 为什么需要这个对象

- 一块 PCB 需分 CPU、WiFi、PMIC 等多区测试（ADR-0009）
- 每区独立起点/终点、对齐、Hx/Hy 扫描历史
- UI 画布上 Region 矩形与 Breadcrumb 上下文依赖此对象

## 3. 关键字段

| 字段 | 类型 | 说明 |
|---|---|---|
| regionId | string | UUID，目录名 |
| name | string | CPU / WiFi / PMIC… |
| description | string | 可选 |
| startPoint | {x,y,z} | 运动坐标起点 |
| endPoint | {x,y,z} | 运动坐标终点 |
| stepX, stepY | number | 步进 mm |
| zHeight | number | 扫描高度 |
| probeChannelDefault | enum | Hx / Hy / Sequence |
| alignment | Alignment | 嵌入或引用 alignment.json |
| scanConfigRef | path | scan_config.json |
| lifecycleStage | enum | 见 05_Lifecycle |
| createdAt, updatedAt | datetime | |

## 4. 所属关系

- **属于** Project（及 PCB 上下文）
- **包含** 0..1 Alignment
- **包含** 0..N ScanTask（历史保留）

## 5. 与其它对象关系

- 一个 Project 可有 **多个** Region
- 一个 Region 有 **独立名称**（业务语义，非 Area001）
- 一个 Region 可对应 **多次** ScanTask（重扫新建，ADR-0007）
- Alignment **作为 Region 属性**保存（alignment.json）
- Hx / Hy 为不同 ScanTask，共享同一 Region 几何

## 6. 生命周期

Created → Positioned → Aligned（可选）→ Configured → Scanned → Analyzed → Reported。详见 [Region_Lifecycle.md](../05_Lifecycle/Region_Lifecycle.md)。

## 7. 状态

持久化阶段见 Lifecycle；运行期「当前选中 Region」为 UI 会话态，**不写入** region.json。

## 8. 文件系统映射

```text
{project}/regions/{regionId}/
  region.json
  alignment.json
  scan_config.json
  scans/          → ScanTask 目录
  analysis/
  exports/
```

## 9. UI 映射

- 画布 `regionLayer` 矩形
- Breadcrumb：`项目 > {Region.name} > …`
- `regionSettingsGroup` / `fieldRegionName`
- 非左侧一级「Region 页」（ADR-0013）

## 10. Qt/PySide6 实现建议

- 领域类 `Region`（dataclass / pydantic，Release 010+）
- Scene：`QGraphicsRectItem` 按 Region 范围绘制
- ViewModel 绑定 PropertyPanel，不直接写磁盘

## 11. 禁止事项

- **禁止** Region 删除时静默删除 ScanTask 原始数据；须提示归档或保留历史
- 禁止无起点/终点创建 ScanTask
- 禁止 Region 跨 Project 移动（应复制工程）
- 禁止 Region 替代 Project 保存 PCB 全局图（PCB 图在 sample/）

## 相关文档

- [Alignment.md](Alignment.md)
- [ScanTask.md](ScanTask.md)
- 历史：[../../data/Region.md](../../data/Region.md)

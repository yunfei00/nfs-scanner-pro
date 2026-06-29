# Region Lifecycle — 区域生命周期

## 生命周期流程

```text
创建区域
  ↓
命名区域（CPU / WiFi / PMIC …）
  ↓
设置物理范围（起点、终点、Z、步进）
  ↓
设置对齐（Alignment，可选）
  ↓
扫描（一条或多条 ScanTask：Hx / Hy）
  ↓
分析（Analysis / Heatmap）
  ↓
复用 / 修改 / 禁用
```

## 各阶段说明

| 阶段 | 字段/文件 | 说明 |
|---|---|---|
| 创建区域 | region.json created | 归属 Project |
| 命名区域 | name | ADR-0009 语义化名称 |
| 设置物理范围 | startPoint, endPoint, stepX/Y | 无起终点不可 ScanTask |
| 设置对齐 | alignment.json | 可选；见 Alignment 状态机 |
| 扫描 | scans/ 下 N 个 ScanTask | 重扫新建目录 |
| 分析 | analysis/ | 引用 ScanTask |
| 复用/修改/禁用 | lifecycleStage | 修改范围→对齐需重新确认；禁用不再默认选中 |

## 删除与归档

存在 ScanTask raw 时：

1. **禁止**静默删除
2. 选项：归档整个 `regions/{id}/` 到 `exports/archive/`
3. 或保留历史只禁用 Region（UI 灰显）

## 相关

- [Region.md](../02_Core_Objects/Region.md)
- [Region_State 持久化](../04_State_Machines/README.md)

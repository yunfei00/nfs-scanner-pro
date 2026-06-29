# Region Editing Interaction — Region 编辑交互

## 设计目标

在画布上定义 Region 起点/终点与矩形，而非独立 Region 页。

## 使用场景

创建/编辑 CPU、WiFi 等区域。

## 规则

1. 工具菜单或画布上下文「新建 Region」→ Dialog 命名
2. 手动移动探头 →「记录起点」「记录终点」或工具栏流程
3. Region 矩形在 regionLayer 可拖拽调整（Release 010+）
4. 无 Alignment 可扫描，有 Alignment 可叠加热力图
5. Breadcrumb 随 Region 切换更新

## Qt

Scene `regionLayer` QGraphicsRectItem；PropertyPanel regionSettingsGroup。

## objectName

`regionLayer`、`fieldRegionName`、`regionSettingsGroup`。

## 禁止事项

- 禁止仅能在表格编辑 Region 坐标
- 禁止无确认删除 Region

## 相关

- `../../workflow/Create_Region.md`

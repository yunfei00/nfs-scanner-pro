# Domain Naming Rules — 领域命名规则

## ID
- 持久化实体：`{entity}Id`，UUID v4 字符串
- 枚举：PascalCase 常量 `ProbeChannel.Hx`

## JSON 键
camelCase：`scanTaskId`, `regionId`, `lifecycleStage`

## 文件夹
`regions/{regionId}/scans/{scanTaskId}/`

## 代码类（Release 010 建议）
PascalCase 单数：`ScanTask`, `DeviceSnapshot`

## 与 UI objectName 区别
objectName：camelCase Qt 控件名；domain id 不得用作 widget objectName。

## 历史别名
| 旧 | 新 |
|---|---|
| Sample | PCB |
| Scan | ScanTask |
| scanId | scanTaskId |

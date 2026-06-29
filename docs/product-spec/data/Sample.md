# Sample

## 定义

Sample 表示 Project 中被测试的实物样品。

在当前产品阶段，Sample 通常是一块 PCB。

## 职责

Sample 负责描述被测对象本身，而不是描述扫描行为。

Sample 可以保存：

- 样品名称
- 样品编号
- 硬件版本
- 软件版本
- 样品备注
- 样品图片
- 放置方向说明

## 规则

- 一个 Project 默认只有一个主 Sample。
- Sample 图片属于 Project。
- Region 使用 Sample 图片进行区域标定和热力图叠加。
- 没有相机时，Sample 仍然可以存在，只是没有实时拍摄图片。

## 与 Camera 的关系

Camera 可以用于获取 Sample 图片。

Camera 失败不能阻止 Project、Region、Scan 的创建。

如果没有 Sample 图片，软件仍然允许扫描和生成普通热力图。

## 生命周期

- Created：样品信息已建立。
- Imaged：样品图片已采集或导入。
- Used：已有 Region 或 Scan 使用该样品。
- Archived：随 Project 一起归档。

## 关联对象

- Project：Sample 属于一个 Project。
- Region：多个 Region 可以引用同一个 Sample 图片。

# Build Navigation — 左侧导航

## 任务目标

实现左侧 NavigationBar：扫描、设备、分析、报告四项；切换 central 区域或 stacked widget。

## 开始前必须阅读

- [spec/AI_INDEX.md](../AI_INDEX.md)
- [spec/Registry/UI.yaml](../Registry/UI.yaml)
- [NavigationBar.md](../../docs/product-spec/design-system/02_Components/NavigationBar.md)
- [02_Left_Navigation.md](../../docs/product-spec/ui-wireframe/02_Left_Navigation.md)

## 不要阅读的内容

- domain 全量

## 允许修改的目录

- UI 源码中导航相关模块

## 禁止修改的目录

- `docs/product-spec/decision/`（不改 ADR）

## 实现步骤

1. 四项按钮 + icon + 选中态 property。
2. 信号切换主内容区。
3. objectName 按 qt-spec。

## 验收标准

- [ ] 无「项目」项
- [ ] 选中态与 QSS 一致

## 常见错误

- 增加「设置」到左侧（应在顶栏菜单）

## 推荐 commit message

```
feat(ui): implement left navigation bar
```

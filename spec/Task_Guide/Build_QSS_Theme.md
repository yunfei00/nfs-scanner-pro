# Build QSS Theme — 深色主题

## 任务目标

统一 QSS：主窗口、导航、Dock、表单、表格；映射 Design Token。

## 开始前必须阅读

- [spec/AI_INDEX.md](../AI_INDEX.md)
- [spec/Registry/UI.yaml](../Registry/UI.yaml)
- [spec/Registry/Qt.yaml](../Registry/Qt.yaml)
- [design-system/06_QSS/README.md](../../docs/product-spec/design-system/06_QSS/README.md)
- [Design_Tokens.md](../../docs/product-spec/design-system/01_Foundation/Design_Tokens.md)

## 不要阅读的内容

- 业务 domain

## 允许修改的目录

- `resources/qss/` 或项目 QSS 目录

## 禁止修改的目录

- Token 源文档（改样式先改 QSS 映射）

## 实现步骤

1. 按 06_QSS 拆分文件。
2. token_mapping_qss 对照。
3. 加载顺序：base → components → docks。

## 验收标准

- [ ] 无大量 widget 内 setStyleSheet 硬编码
- [ ] 状态 property 有对应 QSS 选择器

## 常见错误

- 每个文件重复定义同色 Token

## 推荐 commit message

```
feat(ui): apply dark theme QSS from design tokens
```

# Review Code — 代码合规审查

## 任务目标

对 PySide6 实现做 **ADR / Design System / qt-spec** 合规检查，输出问题清单。

## 开始前必须阅读

1. [spec/AI_INDEX.md](../AI_INDEX.md)
2. [spec/Registry/Decision.yaml](../Registry/Decision.yaml)
3. [spec/Registry/UI.yaml](../Registry/UI.yaml)
4. [spec/Registry/Qt.yaml](../Registry/Qt.yaml)
5. [spec/Context_Pack/Decision_Context.md](../Context_Pack/Decision_Context.md)

## 不要阅读的内容

- 无需通读全部 domain（除非审查扫描/设备逻辑）

## 允许修改的目录

- 被审查的 `src/` 代码
- 可选：在 PR 评论中引用 ADR，不擅自改 ADR

## 禁止修改的目录

- 无用户授权时不改 `docs/product-spec/decision/` 已接受 ADR

## 审查清单

### ADR 合规

- [ ] **ADR-0013 / ADR-0018**：Project 不在左侧导航；新建/打开/保存在文件菜单
- [ ] **ADR-0010**：热力图整图 QPixmap，非逐格
- [ ] **ADR-0003**：Camera 离线不阻断 ScanTask 数据采集路径
- [ ] **ADR-0004**：Hx/Hy 切换考虑偏移与 Alignment 状态
- [ ] **ADR-0012**：布局以 ui-wireframe 为准，非随意高保真
- [ ] **ADR-0021**：实现任务是否从 AI_INDEX / Registry 进入（流程层面）

### objectName

- [ ] QMainWindow、NavigationBar、各 Dock、GraphicsView 有规范 objectName
- [ ] 与 [Qt_ObjectName_Rules.md](../../docs/product-spec/design-system/07_Qt_Implementation/Qt_ObjectName_Rules.md) 一致

### Design Token / QSS

- [ ] 颜色、间距来自 Token，非硬编码散落 `#RRGGBB`
- [ ] 主窗口/导航/Dock QSS 在 `resources/qss/` 或约定目录
- [ ] dynamic property 状态与 [Qt_State_Property_Rules.md](../../docs/product-spec/design-system/07_Qt_Implementation/Qt_State_Property_Rules.md) 一致

### UI 结构

- [ ] 左侧导航仅：扫描、设备、分析、报告
- [ ] 日志、频谱、统计、数据表格 **默认隐藏**
- [ ] 右侧参数区为 QDockWidget
- [ ] 中央为 QGraphicsView + QGraphicsScene

### 领域边界（若涉及业务代码）

- [ ] 使用 PCB / ScanTask 命名，非 Sample / Scan
- [ ] DeviceSnapshot 绑定 ScanTask
- [ ] Alignment 归属 Region

## 实现步骤

1. 列出变更文件。
2. 按清单逐项 grep / 人工检查。
3. 标注：违反 ADR / 缺少 objectName / Token 违规 / 结构错误。
4. 给出修复建议并引用具体 doc 路径。

## 验收标准

- [ ] 清单全覆盖
- [ ] 每项结论有 doc 或代码引用
- [ ] 无「应该可以」类模糊结论

## 常见错误

- 只查样式不查 ADR
- 把 Project 页误当作「方便开发」保留
- 默认 `show()` 所有 Dock

## 推荐 commit message

```
chore(review): UI compliance check against ADR and qt-spec
```

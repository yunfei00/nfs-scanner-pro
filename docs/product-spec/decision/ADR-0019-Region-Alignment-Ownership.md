# ADR-0019 Region Alignment Ownership

## 背景
Alignment 曾被误解为 Project 级或独立页面实体，且 Hx/Hy 切换后叠加是否仍有效无规则。

## 决策
1. **Alignment 属于 Region**；持久化 `regions/{id}/alignment.json`。
2. **不是独立一级业务对象**；无左侧「对齐」页，经工具栏/Region 上下文编辑。
3. **Hx/Hy 切换后**：
   - 若 **HxHyCalibration** valid 且偏移 ≤ threshold → Alignment 保持**已对齐**。
   - 若无补偿或超阈 → **需重新确认**，用户确认后回已对齐。
4. PCB 图变更、Region 范围大改 → **需重新确认**或**失效**。

## 后果
- 热力图叠加语义清晰。
- Servo/校准模块与 Alignment 状态机联动。

## 替代方案
- Project 级全局 Alignment：否决（ADR-0005）。
- 切换 Hy 强制重对齐：否决（效率低，忽略物理补偿）。

## 与已有 Release 关系
- domain Alignment_State_Machine
- 009.5 toolbarAlignButton
- workflow Alignment.md（不改写，引用本 ADR）

## 相关
[Alignment.md](../domain/02_Core_Objects/Alignment.md)

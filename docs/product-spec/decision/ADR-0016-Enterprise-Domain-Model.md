# ADR-0016 Enterprise Domain Model（统一目录）

## 背景
ADR-0015 决定建立 `domain/` 目录。Release 009.8 扩展后需一份**产品级统一目录**：12 核心对象、5 设备对象、10 状态机、6 生命周期、8 类异常恢复，供 Release 010 Mock 与 JSON 推导。

## 决策
1. `docs/product-spec/domain/` 为领域**唯一权威入口**（高于分散的 `data/` 片段）。
2. 命名：`Sample→PCB`，`Scan→ScanTask`；Alignment 属 Region。
3. 必须文档化：关系文字说明、状态机八要素、生命周期链、Event 模型。
4. `data/` 保留不删，顶部指向 domain。

## 后果
- 正面：开发可单页查表（UI/文件/事件/状态）。
- 负面：与旧 workflow 用词并存，需查 Domain_Naming_Rules。

## 替代方案
- 仅扩 `data/`：否决，缺状态机与 Recovery。
- 直接用代码类作文档：否决，Release 010 前无代码。

## 与已有 Release 关系
| Release | 关系 |
|---|---|
| 008 | 线框尺寸不变 |
| 009.5 | UI↔Domain 映射在 07_Implementation_Guide |
| 009.8 | 本 ADR 覆盖的完整 domain 树 |
| 010 | 依赖本 ADR 与 0017–0020 |

## 相关
[ADR-0015](ADR-0015-Enterprise-Domain-Model.md)、[domain/README.md](../domain/README.md)

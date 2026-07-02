# Release 047 — Real Hardware Bring-up Readiness Pack

## 1. Release 目标

整理真实硬件联调所需的配置模板、接口审计、诊断报告与分设备 bring-up 文档，**不要求连接真实设备成功**。

## 2. 为什么需要本 Release

Release_044~046 已完成功能层与 UI 控制台。接设备前需要统一的配置、清单、审计与离线诊断能力。

## 3. hardware.example.yaml

项目模板：`config/hardware.example.yaml` — 全部 enabled=false，可复制参考。

## 4. hardware.local.example.yaml

本机示例：`config/hardware.local.example.yaml` — 复制为 `hardware.local.yaml`（已 gitignore）。

## 5. 接口完整性审计

`python scripts/check_hardware_interface_inventory.py` — 检查 Adapter / Manager / Executor 方法清单。

## 6. 诊断报告

`python scripts/generate_hardware_bringup_report.py` — 离线 JSON + MD 报告。

## 7. Adapter snapshot

统一字段：enabled / connected / fake / safe_mode / config / last_error / timestamp_iso。

## 8. docs/hardware 文档目录

分设备 bring-up、安全开关、命令映射、故障排查。

## 9. 本次不做什么

- ❌ 不连接真实设备 / 不运动 / 不 sweep / 不拍照 / 不控舵机 / 不 real-run
- ❌ 不改 high_fidelity / 主窗口布局

## 10. 下一步 Release_048 建议

**真实硬件接入后的首轮现场联调流程** — 按设备逐项 checklist 与自动化记录。

## 验收

```bash
python scripts/verify_release_047.py
python scripts/verify_all.py --only 047
```

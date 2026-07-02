# 硬件现场联调（Commissioning）

Release_048 标准化现场联调流程。

## 三种模式

| 模式 | 说明 |
|------|------|
| offline | 配置/文档/脚本/接口，不连设备 |
| fake | FakeTransport 跑通链路 |
| real-safe | 需 NFS_ENABLE_REAL_HARDWARE=1，仅 test_all_safe |

## 入口

```powershell
python scripts/start_hardware_commissioning.py --mode offline
python scripts/start_hardware_commissioning.py --mode fake
python scripts/start_hardware_commissioning.py --mode real-safe
python scripts/validate_commissioning_readiness.py
python scripts/generate_commissioning_template.py
```

## 文档索引

- [00-overview.md](00-overview.md)
- [01-environment-check.md](01-environment-check.md) … [10-real-run-gate.md](10-real-run-gate.md)

## Real-run

本 Release **不执行 real-run**。见 [10-real-run-gate.md](10-real-run-gate.md)。

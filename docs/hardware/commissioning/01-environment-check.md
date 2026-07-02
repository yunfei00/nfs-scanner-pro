# 01 — 环境检查

## 检查项

- 项目目录 scripts / config / docs
- Python 可 import commissioning 模块
- verify_all 最近 PASS

## 命令

```powershell
python scripts/validate_commissioning_readiness.py
python scripts/check_hardware_interface_inventory.py
```

## PASS 标准

readiness PASS，inventory 无 MISSING 接口。

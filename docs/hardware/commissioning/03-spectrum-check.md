# 03 — 频谱仪检查

## 步骤

- spectrum_idn：`*IDN?`
- spectrum_marker：Marker 幅度

## 命令

```powershell
python scripts/debug_real_spectrum.py --idn --fake
python scripts/debug_real_spectrum.py --marker --fake
```

## 禁止（默认）

sweep、trace 全读、SCPI 写 — 需独立开关。

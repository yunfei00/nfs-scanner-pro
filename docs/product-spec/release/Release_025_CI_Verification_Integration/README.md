# Release 025 — CI Verification Integration

## 1. Release 目标

将 Release 022~024 建立的自动验收体系接入 **GitHub Actions**，使每次 `push` / `pull_request` 到 `main` 时自动运行 `verify_all.py`。

## 2. 为什么需要 CI 自动验收

- 本地 PASS 不能保证其他环境/协作者未引入回归。
- Windows + PySide6 offscreen 与项目主开发环境一致。
- 后续 Release 可依赖 CI 作为合并门禁。

## 3. GitHub Actions 工作流说明

| 项 | 值 |
|---|---|
| 文件 | `.github/workflows/verify.yml` |
| 名称 | NFS Scanner Verification |
| 触发 | `push` / `pull_request` → `main` |
| 运行器 | `windows-latest` |
| 环境变量 | `QT_QPA_PLATFORM=offscreen` |

步骤：checkout → setup-python 3.12 → `pip install -r requirements.txt` → compileall → verify_all。

## 4. 本次实现范围

- `.github/workflows/verify.yml`
- `scripts/verify_release_025.py` — CI 配置与回归检查
- `verify_all.py` 注册 Release 025
- Release 文档与索引

## 5. 本次不做什么

- ❌ 不接真实设备 / 串口 / SCPI / 相机
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改主窗口布局 / high_fidelity HTML / 业务代码
- ❌ 不上传 CI artifact（除非后续调试需要）
- ❌ 不使用复杂 matrix

## 6. verify_release_025.py 检查项

- workflow 文件存在与关键片段
- verify_all 注册 022~025
- .gitignore runtime 规则
- 串行运行 022 / 023 / 024（**不**递归调用 verify_all）
- high_fidelity 未被修改
- 禁止真实外设访问字符串

## 7. verify_all.py 集成

```bash
python scripts/verify_all.py
```

串行：022 → 023 → 024 → 025，任一 FAIL 则 exit 1。

## 8. 本地运行方式

```bash
pip install -r requirements.txt
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_025.py
python scripts/verify_all.py
```

## 9. CI 运行方式

推送到 `main` 或发起 PR 后，GitHub Actions 自动执行 `NFS Scanner Verification` 工作流。

## 10. 后续 Release 约束

1. **每个新 Release 必须** 新增 `scripts/verify_release_XXX.py`。
2. **必须** 注册到 `verify_all.py`。
3. **只有** `verify_all.py` PASS 才允许 commit / push。
4. CI 中 **不接真实设备**，**不生成真实导出文件**。

## 强调

- runtime/ 产物可在 CI 工作区生成，**不提交 Git**。
- verify_release_025 **不得** 调用 verify_all，避免递归。

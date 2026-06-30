# Release 033 — Release Verification Script Generator

## 1. Release 目标

新增 `scripts/scaffold_verify_release.py`，自动生成新 Release 的 `verify_release_NNN.py`、文档目录、验收报告模板，并注册到 `verify_all.py` 与项目索引。

## 2. 为什么需要 Release 验收脚手架

- Release 022~032 的验收脚本与文档结构高度重复，手工复制易漏项、路径硬编码。
- 统一模板可强制 `QT_QPA_PLATFORM`、`verification_runtime` 隔离、`VerificationReport` 输出格式。
- 降低后续 Release 启动成本，开发者只需在模板基础上追加特定检查。

## 3. scaffold_verify_release.py 用法

```bash
python scripts/scaffold_verify_release.py --release 034 --name "Project Workspace UI Verification"
```

或指定 slug / title：

```bash
python scripts/scaffold_verify_release.py --release 034 --slug project_workspace_ui_verification --title "Project Workspace UI Verification"
```

预览（不写入）：

```bash
python scripts/scaffold_verify_release.py --release 034 --name "Demo" --dry-run
```

## 4. 参数说明

| 参数 | 说明 |
|---|---|
| `--release` | 必填，三位 Release 编号（`34` 自动格式化为 `034`） |
| `--name` | 人类可读名称，用于文档标题与目录 slug |
| `--title` | 可选，默认等同 `--name` |
| `--slug` | 可选，目录 slug，默认从 name 推导 |
| `--dry-run` | 只打印将创建/修改的文件 |
| `--force` | 目标已存在时允许覆盖 |
| `--remove` | 删除指定 Release 脚手架产物（内部清理用） |

## 5. 生成文件说明

| 输出 | 路径 |
|---|---|
| 验收脚本 | `scripts/verify_release_NNN.py` |
| Release README | `docs/product-spec/release/Release_NNN_<Slug>/README.md` |
| 验收报告模板 | `docs/product-spec/release/Release_NNN_<Slug>/ACCEPTANCE_REPORT.md` |

## 6. verify_all.py 注册说明

脚手架在 `VERIFY_SCRIPTS` 元组中按编号顺序插入：

```python
(NNN, "Release NNN", SCRIPTS / "verify_release_NNN.py"),
```

若无法安全定位插入点，脚手架失败并提示手动修改。

## 7. 本次不做什么

- ❌ 不接真实设备 / 不新增业务 UI 功能
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局
- ❌ 不修改 `src/` 业务代码

## 8. 本地运行方式

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_033.py
python scripts/scaffold_verify_release.py --help
python scripts/verify_all.py
```

## 9. CI 运行方式

GitHub Actions 仍执行：

```bash
python -m compileall src/nfs_scanner_pro
python scripts/verify_all.py
```

## 10. 后续 Release 约束

1. **新 Release 优先使用脚手架** 生成骨架，再追加 Release 特定检查。
2. 禁止硬编码 `runtime/mock_projects`；使用 `NFS_SCANNER_RUNTIME_DIR` 或 `verification_runtime`。
3. 脚手架生成后必须 `python scripts/verify_release_NNN.py` 与 `verify_all.py --only NNN` 验证 PASS。
4. 嵌套调用 `verify_all` 时设置 `NFS_VERIFY_NESTED=1` 避免递归自验。

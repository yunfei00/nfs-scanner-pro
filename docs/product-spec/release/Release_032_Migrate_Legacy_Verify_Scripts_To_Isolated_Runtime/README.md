# Release 032 — Migrate Legacy Verify Scripts to Isolated Runtime

## 1. Release 目标

将 `verify_release_022.py` ~ `verify_release_030.py` 中仍写入共享 `runtime/mock_projects` 的验收逻辑，迁移到 Release_031 引入的 `runtime/verification/Rxxx/` 隔离目录；通过 `NFS_SCANNER_RUNTIME_DIR` 让应用 Mock 路径自动指向隔离 runtime，**不新增业务功能**。

## 2. 为什么要迁移旧验收脚本

- 多个 Release 脚本共用 `runtime/mock_projects`，`ST-VERIFY-*` 与冒烟扫描数据会 **互相干扰** 后续验收。
- CI 全量 `verify_all.py` 难以判断某次失败是脚本问题还是 **历史 runtime 污染**。
- 隔离后每个 Release 只读写自己的 `Rxxx` 目录，便于本地调试与 `--keep-runtime` 留档。

## 3. runtime/verification/Rxxx 约定

| 路径 | 用途 |
|---|---|
| `runtime/verification/R022/` | Release 022 隔离 runtime |
| … | … |
| `runtime/verification/R032/` | Release 032 自检 |
| `runtime/mock_projects/` | 应用默认 Mock（验收脚本不再写入） |

清理：`clean_release_runtime(release_id)` **仅**删除对应 `Rxxx/`，不触碰 `runtime/mock_projects/`。

## 4. NFS_SCANNER_RUNTIME_DIR

`src/nfs_scanner_pro/app_paths.py` 中 `get_runtime_dir()` 优先读取环境变量：

```bash
set NFS_SCANNER_RUNTIME_DIR=D:\repo\runtime\verification\R026
```

未设置时仍使用仓库根下 `runtime/`。`get_mock_scan_dir()` 等自动在隔离目录下创建 `mock_projects/`。

## 5. verify_all.py 隔离策略

每个 Release 子进程：

1. `clean_release_runtime(release_id)`（除非 `--keep-runtime`）
2. `build_release_env(release_id)` 设置 `NFS_SCANNER_RUNTIME_DIR` 与 `QT_QPA_PLATFORM=offscreen`
3. 输出 `Runtime: runtime/verification/Rxxx` 与耗时

```bash
python scripts/verify_all.py --only 026
python scripts/verify_all.py --from 029 --keep-runtime
```

## 6. 迁移范围 022~030

最小改动原则：

- 将 `ROOT / "runtime"`、`runtime/mock_projects` 硬编码改为 `app_paths.get_runtime_dir()` 或 `verification_utils.describe_*`
- `verify_release_025.py` 重跑 022~024 时为每个脚本注入对应 `build_release_env`
- 仅检查 workflow/gitignore 的脚本无需强改

## 7. 本次不做什么

- ❌ 不接真实设备 / 不打开串口 / 不发送 SCPI
- ❌ 不实现真实扫描算法 / 不生成真实 PDF·Word·Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局
- ❌ 不把「项目」加入左侧导航

## 8. 本地运行

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_032.py
python scripts/verify_all.py
```

## 9. CI 运行方式

GitHub Actions 仍只执行：

```bash
python -m compileall src/nfs_scanner_pro
python scripts/verify_all.py
```

## 10. 后续 Release 约束

1. 新 Release 注册到 `verify_all.py` 的 `VERIFY_SCRIPTS`。
2. 验收写入 Mock 数据必须通过 `NFS_SCANNER_RUNTIME_DIR` 或 `verification_runtime` 工具。
3. 嵌套调用 `verify_all` 时设置 `NFS_VERIFY_NESTED=1` 避免递归自验。
4. 禁止在 legacy 脚本中硬编码 `runtime/mock_projects`。

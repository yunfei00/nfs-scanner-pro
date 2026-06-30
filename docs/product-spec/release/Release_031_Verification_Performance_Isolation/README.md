# Release 031 — Verification Performance & Isolation

## 1. Release 目标

优化自动验收体系：为 `verify_all.py` 增加耗时统计、失败摘要、命令行筛选，并引入 `runtime/verification/Rxxx/` 隔离约定，避免各 Release 脚本互相污染 runtime 数据。

## 2. 为什么需要验收性能与隔离

- Release 022~030 串行运行已耗时数十秒，缺少 **每项 / 总耗时** 不便于 CI 与本地诊断。
- 多个脚本写入 `runtime/mock_projects`，`ST-VERIFY-*` 与冒烟扫描任务可能 **累积干扰** 后续验收。
- CI 失败时需要 **fail-fast + stdout 尾部摘要** 快速定位 Release。

## 3. runtime/verification/Rxxx 约定

| 路径 | 用途 |
|---|---|
| `runtime/verification/R027/` | Release 027 隔离数据（推荐新脚本使用） |
| `runtime/verification/R031/` | Release 031 自检 |
| `runtime/mock_projects/` | 应用默认 Mock 持久化（旧脚本可保留） |

原则：清理只针对 `runtime/verification/Rxxx/`，不删除用户/旧脚本使用的 `runtime/mock_projects/`。

## 4. verification_runtime.py

- `get_release_runtime_dir(release_id)` — 创建隔离根目录
- `clean_release_runtime(release_id)` — 仅清理对应 Rxxx
- `make_project_scan_dir` / `make_project_report_dir` — 隔离扫描/报告目录
- `assert_runtime_ignored_by_git()` — 确认 `.gitignore` 覆盖 runtime

## 5. verification_report.py

`VerificationReport` 统一输出：

```
Release_031 Verification

[PASS] compileall 0.45s
...
RESULT: PASS
TOTAL: 12.34s
```

兼容旧脚本：`CheckResult`（verification_utils）仍可使用。

## 6. verify_all.py 参数

```bash
python scripts/verify_all.py              # 全部（fail-fast）
python scripts/verify_all.py --list       # 列出 022~031
python scripts/verify_all.py --only 026   # 仅 Release 026
python scripts/verify_all.py --from 026   # 026 到最新
python scripts/verify_all.py --no-fail-fast
```

输出包含 `Running Release ...`、每项耗时、`TOTAL`、`RESULT`。

## 7. 本次不做什么

- ❌ 不接真实设备 / 不新增业务功能
- ❌ 不大范围重写 022~030 脚本
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局

## 8. 本地运行

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_031.py
python scripts/verify_all.py
```

## 9. CI 运行方式

GitHub Actions 仍执行 `python scripts/verify_all.py`（无参数，全量 + fail-fast）。

## 10. 后续 Release 约束

1. 新 Release 注册到 `verify_all.py` 的 `VERIFY_SCRIPTS`。
2. 新创建的 `ST-VERIFY-*` 优先写入 `runtime/verification/Rxxx/`。
3. 嵌套调用 `verify_all` 时设置 `NFS_VERIFY_NESTED=1` 避免递归验收。

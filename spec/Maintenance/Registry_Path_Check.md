# Registry 路径校验

## 用途

检查 `spec/Registry/*.yaml` 中引用的 `.md` 文件是否在仓库中存在，避免 AI 索引指向死链。

## 运行

在仓库根目录执行：

```bash
python scripts/check_spec_registry_paths.py
```

## 预期结果

- **成功**：输出 `All registry markdown paths exist.` 退出码 `0`
- **失败**：列出缺失路径，退出码非 `0`

## 何时运行

- 新增或修改 Registry YAML 后
- 新增 product-spec 文档并写入 Registry 后
- Release 009.9 验收前
- CI 可选集成（本脚本仅用 Python 标准库）

## 修复

1. 修正 YAML 中的错误路径，或
2. 创建缺失的文档（若确实需要）

详见 [How_To_Update_Registry.md](How_To_Update_Registry.md)。

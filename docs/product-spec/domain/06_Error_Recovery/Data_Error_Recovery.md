# Data Error Recovery — 数据与文件异常恢复

## 异常场景与处理

| 场景 | 检测 | 处理 | UI |
|---|---|---|---|
| **project.json 损坏** | JSON parse 失败 | 尝试 `.bak`；失败则禁止打开 | Dialog「工程损坏」 |
| **scan 数据缺失** | raw/ 不存在 | scan.json status=Failed；只读元数据 | 分析页灰显 |
| **CSV 格式错误** | 列数/类型不对 | 标记 ScanTask Error；保留文件供人工 | log ERROR |
| **trace re/im 不匹配** | 数组长度不一致 | Skip 点或暂停 | WARN |
| **文件路径丢失** | 相对路径无效 | 提示「重新链接文件夹」 | 文件菜单 |
| **历史 Report 找不到原始数据** | Analysis 引用失效 | Report 预览水印「源数据缺失」 | 报告页警告 |

## 备份策略

- 保存 Project：`project.json.bak`
- 大操作前：可选 zip 整个 Project 文件夹（**主备份=复制文件夹**，ADR-0018）

## 禁止

- 自动删除损坏 scans/
- 静默忽略 CSV 列错误填 0

## 相关

[Domain_To_File_System_Mapping.md](../07_Implementation_Guide/Domain_To_File_System_Mapping.md)

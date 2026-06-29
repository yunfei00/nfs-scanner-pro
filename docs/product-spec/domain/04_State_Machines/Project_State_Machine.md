# Project State Machine — 项目状态机

## 1. 状态列表
Created | Configured | Active | Completed | Archived

## 2. 状态说明
| 状态 | 说明 |
|---|---|
| Created | 文件夹与 project.json 已建 |
| Configured | PCB 与 Profile 已配置 |
| Active | 有 Region/ScanTask 活动 |
| Completed | 用户标记测试完成 |
| Archived | 只读归档 |

## 3. 状态转换表
| 从 | 事件 | 到 |
|---|---|---|
| Created | savePcb | Configured |
| Configured | firstScan | Active |
| Active | userComplete | Completed |
| * | archive | Archived |

## 4. 允许动作
Active：扫描/分析/保存。Archived：只读打开。

## 5. 禁止动作
Archived 修改 Scan raw；无 Project 时扫描。

## 6. UI 表现
文件菜单保存/关闭；Breadcrumb 项目名；Archived 标题加「只读」。

## 7. 日志
`ProjectOpened/Closed/Saved` → domain.log

## 8. 错误恢复
project.json 损坏 → [Data_Error_Recovery.md](../06_Error_Recovery/Data_Error_Recovery.md)

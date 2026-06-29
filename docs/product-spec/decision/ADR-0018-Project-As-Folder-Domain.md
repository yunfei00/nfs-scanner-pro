# ADR-0018 Project As Folder Domain

## 背景
Project 在领域与 UI 上角色易混淆：既是数据根，又被误认为一级页面。

## 决策
1. **Project 是文件夹**；`project.json` + 子目录（见 Domain_To_File_System_Mapping）。
2. **Project 不是左侧导航一级页面**（ADR-0013 延续）。
3. **新建/打开/保存/关闭/最近项目/打开项目文件夹** 全部在**文件菜单**。
4. **备份 = 复制整个 Project 文件夹**到 U 盘/网盘。
5. **不设计 Import/Export Project 作为主路径**；交换数据用文件夹复制或 exports/ 内报告/导出文件。
6. 可选「另存为文件夹」= 复制，非专有导入导出格式（V2 再评估 .nfsp 包）。

## 后果
- 正面：实验室运维简单、git-friendly（若需）。
- 负面：无单文件双击打开（除非关联 project.json）。

## 替代方案
- 单文件 SQLite 工程：否决，不符合 ADR-0008 与备份习惯。
- Project Dashboard 一级页：否决。

## 与已有 Release 关系
| 文档 | 对齐 |
|---|---|
| 008 线框 | 文件菜单项目入口 |
| 009.5 MenuBar | actionNewProject 等 |
| 007_File_System | pcb/regions 兼容 sample |

## 相关
[Project.md](../domain/02_Core_Objects/Project.md)

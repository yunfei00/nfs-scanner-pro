# State Machines — 状态机索引

每个状态机文档包含：**状态列表、状态说明、状态转换表、允许动作、禁止动作、UI 表现、日志记录、错误恢复**。

## 扫描域（重点）

| 文档 | 中文重点 |
|---|---|
| [Scan_State_Machine.md](Scan_State_Machine.md) | **未就绪→准备就绪→扫描中→暂停→停止中→已完成→错误** |
| [Device_State_Machine.md](Device_State_Machine.md) | 未配置/未连接/连接中/已连接/忙碌/错误/禁用 |
| [Alignment_State_Machine.md](Alignment_State_Machine.md) | 未对齐/粗对齐/已对齐/需重新确认/失效 + Hx/Hy |

## 其它

| 文档 | 对象 |
|---|---|
| [Project_State_Machine.md](Project_State_Machine.md) | Project |
| [Motion_State_Machine.md](Motion_State_Machine.md) | MotionSystem |
| [Spectrum_State_Machine.md](Spectrum_State_Machine.md) | SpectrumAnalyzer |
| [Camera_State_Machine.md](Camera_State_Machine.md) | CameraSystem |
| [Servo_State_Machine.md](Servo_State_Machine.md) | ServoSystem |
| [Analysis_State_Machine.md](Analysis_State_Machine.md) | Analysis |
| [Report_State_Machine.md](Report_State_Machine.md) | Report |

## 与 UI 对齐

- Scan：`design-system/04_Interaction/Scan_State_Interaction.md`
- Device：`design-system/03_Patterns/Device_Status_Pattern.md`

## ADR

[ADR-0017](../../decision/ADR-0017-Scan-State-Machine.md)

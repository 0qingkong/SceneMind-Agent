# SceneMind Competition Demo Runbook

## Profile decision table

| Profile | Use when | Analyzer | Input | Persistence/Agent | Required dependencies |
| --- | --- | --- | --- | --- | --- |
| A — Full real demo | 摄像头、YOLO 与现场环境均正常 | Real YOLO | 浏览器摄像头 | Real | 摄像头、模型、后端、前端 |
| B — Reliable local-image demo | 摄像头或 HTTPS 不可靠，但 YOLO 正常 | Real YOLO | 获得许可的本地图片 | Real | 模型、许可图片、后端、前端 |
| C — Emergency evidence demo | 摄像头、YOLO、网络任一不可靠 | Mock（不做实时推理） | 持久化预置证据 | Real memory/Agent/stats | 后端、前端 |

Profile C 的所有预置记录都带 `is_demo`、`demo-seed` 引擎、`[演示]` 标题和前端横幅，不会被描述成真实 YOLO 结果。

## Before entering the venue

```powershell
# Open PowerShell in the repository root before running these commands.
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\check-system.ps1
.\scripts\setup.ps1
```

只有在明确允许联网获取模型时才运行：

```powershell
.\scripts\setup.ps1 -DownloadModel
```

准备离线包时参照 `docs/OFFLINE_PACKAGE.md`，并确认 `.runtime`、数据库、权重和演示图片未被 Git 跟踪。

## 3–5 minute Profile A flow

1. 运行 `.\scripts\start-demo.ps1 -Profile A`，展示 `/system` 全部关键依赖状态。
2. 打开 `/live`，明确授权摄像头，说明 `audio: false`。
3. 抓拍真实场景，展示物体框和二维空间关系。
4. 选择“分析并记忆”，打开保存后的证据页。
5. 在 `/agent` 询问刚才物体最后出现在哪里，打开 Agent 返回的同一条图片证据。
6. 展示 `/insights` 或 `/devices` 的真实持久化统计。
7. 运行 `.\scripts\stop-demo.ps1`，确认只停止受管 PID。

## 3–5 minute Profile B flow

1. 运行 `.\scripts\start-demo.ps1 -Profile B`。
2. 在 `/analyze` 选择事先获得许可、已经离线准备的图片。
3. 展示真实 YOLO 检测与二维关系，随后保存记忆。
4. 在 `/memory` 与 `/agent` 展示持久化记录和图片证据。
5. 说明 Profile B 不依赖现场摄像头，但仍使用真实 YOLO。

## 3–5 minute Profile C flow

1. 运行 `.\scripts\start-demo.ps1 -Profile C`。
2. 指出顶部“演示环境 · Profile C”横幅，并打开 `/system`。
3. 打开 `/memory`，展示桌面、教室、图书馆和低频会话证据。
4. 在 `/agent` 询问“我的杯子最后出现在哪里？”及“杯子出现过哪些地方？”。
5. 打开 `/sessions`、`/devices`、`/insights`，说明这些都是同一批数据库记录的真实聚合结果。
6. 可打开 `/glasses` 加载已保存观察，但必须保留模拟器免责声明。
7. 运行 `.\scripts\stop-demo.ps1`，然后按需执行 `.\scripts\reset-demo.ps1 -ConfirmReset`。

## Operator commands

```powershell
.\scripts\check-system.ps1
.\scripts\check-system.ps1 -Json
.\scripts\seed-demo.ps1
.\scripts\smoke-demo.ps1
.\scripts\smoke-demo.ps1 -Extended
.\scripts\stop-demo.ps1
.\scripts\reset-demo.ps1 -ConfirmReset
```

日志：`.runtime\logs\backend.*.log` 和 `.runtime\logs\frontend.*.log`。PID 元数据：`.runtime\pids`。

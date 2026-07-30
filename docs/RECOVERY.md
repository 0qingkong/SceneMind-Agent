# SceneMind Competition Recovery

任何恢复操作都先保留 `.runtime\logs`。不要运行 `Stop-Process -Name python`、`taskkill /IM node.exe` 或其他批量结束命令。

| Symptom | Likely cause | Safe action |
| --- | --- | --- |
| “禁止运行脚本” | PowerShell ExecutionPolicy | 仅在当前终端运行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`，不要修改 LocalMachine |
| Port 8000/5173 occupied | 另一个服务或旧 SceneMind | 先运行 `.\scripts\stop-demo.ps1`；再用 `Get-NetTCPConnection -LocalPort 8000,5173` 查看所有者，不要结束不认识的进程 |
| Missing `.venv` | 尚未安装后端 | 运行 `.\scripts\setup.ps1 -SkipFrontend` |
| Missing `node_modules` | 尚未安装前端 | 运行 `.\scripts\setup.ps1 -SkipBackend`；有 lockfile 时脚本使用 `npm ci` |
| YOLO/model failure or 503 | 权重缺失、依赖或设备问题 | 查看 `backend.err.log`；有明确授权时运行 `setup.ps1 -DownloadModel`，否则切换 Profile C，不会静默伪装真实推理 |
| Camera permission denied | 浏览器权限被拒绝 | 在站点设置中重新允许摄像头，刷新后由用户再次点击连接 |
| Phone camera unavailable over HTTP | 局域网 HTTP 不是安全上下文 | 使用受信任 HTTPS；不要承诺普通 LAN HTTP 可以访问手机摄像头，或改用 Profile B/C |
| Database locked | 另一后端仍持有 SQLite | 先运行 `stop-demo.ps1`，确认没有受管后端，再备份 `backend/data` 后重试；不要删除未知数据库 |
| Blank frontend | Vite 未启动、缓存或 API 配置错误 | 查看 `frontend.err.log`，访问 `/system`，必要时重新运行 `setup.ps1 -SkipBackend` |
| Stale PID metadata | 上次异常退出 | `stop-demo.ps1` 会核对 PID、进程名和启动时间；不匹配时只删除元数据，不结束进程 |
| Missing demo data | 尚未 seed 或已 reset | 运行 `.\scripts\seed-demo.ps1`，重复运行不会复制 |
| Repeated start fails | 已有受管进程或端口占用 | 使用 `stop-demo.ps1` 后重启；脚本不会接管未知进程 |
| Partial startup | 后端成功、前端或 smoke 失败 | `start-demo.ps1` 自动清理本次启动的受管进程并保留日志 |

## Quick emergency switch

```powershell
.\scripts\stop-demo.ps1
.\scripts\start-demo.ps1 -Profile C
```

Profile C 不需要摄像头或实时 YOLO，但仍需要 Python 环境、SQLite、本地图片存储和前端依赖。

## Log-first diagnosis

```powershell
Get-Content .runtime\logs\backend.err.log -Tail 60
Get-Content .runtime\logs\frontend.err.log -Tail 60
.\scripts\check-system.ps1 -Json
```

日志和状态文件可能包含本机运行信息，因此 `.runtime` 整体被 Git 忽略。

# SceneMind Offline Competition Package

离线包是本地备份，不进入 Git。只打包拥有使用许可的内容。

## Suggested contents

- 当前 Git 提交导出的源码归档。
- 与 `.env.example` 对照后的本地 `.env`（单独保管，不上传）。
- 已明确下载并允许使用的 YOLO 权重。
- 获得许可的 Profile B 本地图片。
- Python wheel/pip 缓存和 npm 缓存；仅包含许可证允许重新分发的包。
- 已验证的 Profile C Demo SQLite 备份与生成式演示图片。
- 比赛所需的本地视频、PPT/PDF；这些不属于 Day 13 代码提交。
- `docs/DEMO_RUNBOOK.md`、`docs/RECOVERY.md` 的离线副本。

不要把 `.venv`、`node_modules` 当作跨机器可移植安装包。优先保存依赖缓存与 lockfile，然后在目标机器执行 `setup.ps1`。

## Checksums

在备份目录中生成 SHA-256 清单：

```powershell
Get-ChildItem . -Recurse -File |
  Get-FileHash -Algorithm SHA256 |
  Select-Object Path, Hash |
  Export-Csv .\SHA256SUMS.csv -NoTypeInformation -Encoding UTF8
```

赛前验证：

```powershell
.\scripts\check-system.ps1
.\scripts\start-demo.ps1 -Profile C -NoBrowser
.\scripts\smoke-demo.ps1
.\scripts\stop-demo.ps1
```

数据库、权重、视频、日志和构建产物均必须保持未跟踪状态。

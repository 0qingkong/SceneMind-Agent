# SceneMind Agent Day 2 升级包

本次升级完成：

- Vue Router 正式页面路由
- 首页、场景分析页、空间记忆页
- 图片边界框可视化
- 统一的分析 API 数据结构
- FastAPI 分析服务抽象
- 图片真实性校验与尺寸读取
- 后端测试更新

## 应用方式

```powershell
git checkout -b feature/day2-product-shell
```

将升级包内的 `backend`、`frontend`、`docs`、`scripts` 复制到项目根目录并覆盖同名文件，然后执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
cd frontend
npm install
cd ..
```

启动：

```powershell
.\scripts\dev-backend.ps1
```

另开一个 PowerShell：

```powershell
.\scripts\dev-frontend.ps1
```

检查：

```powershell
.\scripts\day2-check.ps1
```

提交：

```powershell
git add .
git commit -m "feat: add routed product shell and bbox visualization"
git push -u origin feature/day2-product-shell
```

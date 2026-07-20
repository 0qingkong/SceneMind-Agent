# SceneMind Agent

面向移动端的多模态空间记忆与物品追踪智能体。

当前版本是 **Day 1 可运行骨架**：

- Vue 3 + TypeScript + Vite 前端
- FastAPI 后端
- 图片上传与预览
- 前后端联调
- Mock 场景分析结果
- GitHub 友好的目录与忽略规则

> 当前分析接口使用 Mock 数据，目的是先打通完整链路。后续再替换为真实目标检测、视觉语言模型、空间关系和长期记忆。

## 目录

```text
scenemind-agent/
├─ frontend/               # Vue 3 移动端界面
├─ backend/                # FastAPI API
├─ docs/                   # 产品与开发文档
├─ scripts/                # Windows 启动脚本
├─ .env.example
├─ .gitignore
└─ README.md
```

## 环境要求

- Node.js 20.19+ 或 22.12+
- Python 3.11+
- Git

建议 Windows 用户安装 Node.js 22 LTS、Python 3.12、Git、VS Code。

## 一、初始化后端

在项目根目录打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

若 PowerShell 阻止激活脚本，可仅对当前窗口执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

启动后端：

```powershell
cd backend
fastapi dev app\main.py
```

后端地址：

- API：http://127.0.0.1:8000
- Swagger：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health

## 二、初始化前端

另开一个 PowerShell：

```powershell
cd frontend
npm install
npm run dev
```

前端地址：

- http://localhost:5173

## 三、验证 Day 1 闭环

1. 打开前端。
2. 选择一张 JPG、PNG 或 WebP 图片。
3. 点击“开始分析”。
4. 页面应显示 Mock 场景总结、物体列表和 Trace ID。
5. 打开后端 Swagger，确认接口可访问。

## 四、运行测试

```powershell
.\.venv\Scripts\Activate.ps1
pytest backend\tests -q
```

## 五、提交到 GitHub

先在 GitHub 创建一个空仓库，建议名称：

```text
scenemind-agent
```

不要在网页端预先添加 README、`.gitignore` 或 License，然后在项目根目录执行：

```powershell
git init
git add .
git commit -m "chore: initialize SceneMind Agent"
git branch -M main
git remote add origin https://github.com/你的用户名/scenemind-agent.git
git push -u origin main
```

## Day 2 目标

- 建立正式页面路由
- 分析页加入边界框画布
- 设计统一 API 数据结构
- 将 Mock 分析器抽象成可替换服务

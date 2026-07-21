# SceneMind Agent

SceneMind Agent 是一个面向移动端的多模态空间记忆产品。当前 Day 3 版本可上传场景图片，使用 Ultralytics YOLO 进行真实物体检测，并在前端展示归一化边界框、中文标签和基于检测计数生成的场景摘要。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Vue Router
- 后端：FastAPI、Pydantic、Pillow
- 检测器：Ultralytics YOLO（默认 `yolo26n.pt`）
- API 前缀：`/api/v1`

## 后端安装与启动

需要 Python 3.11+。在仓库根目录运行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

后端地址：

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health
- 分析接口：`POST http://127.0.0.1:8000/api/v1/analyze`

首次执行真实推理时，Ultralytics 可能联网下载 `yolo26n.pt` 权重，因此第一次请求会明显更慢。权重、`runs/` 和上传图片已被 Git 忽略，不应提交。

## 检测器配置

后端直接读取以下环境变量；`.env.example` 给出了默认配置。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `ANALYZER_MODE` | `yolo` | 使用 `yolo` 真实检测；可设为 `mock` 使用固定演示数据 |
| `YOLO_MODEL` | `yolo26n.pt` | Ultralytics 模型名或本地权重路径 |
| `YOLO_CONF` | `0.30` | 最低置信度，范围 0 到 1 |
| `YOLO_IMGSZ` | `640` | 推理输入尺寸 |
| `YOLO_MAX_DET` | `30` | 单张图片最大检测数 |
| `YOLO_DEVICE` | `auto` | `auto`、`cpu`、CUDA 设备编号或 Ultralytics 支持的设备值 |

`YOLO_DEVICE=auto` 时，后端使用 `torch.cuda.is_available()` 自动选择 `cuda:0`，否则使用 CPU。健康检查不会触发模型加载；首次推理成功后会报告实际设备。YOLO 模式出错时接口返回明确的 `503`，不会静默回退到 Mock。

PowerShell 临时切换 Mock 示例：

```powershell
$env:ANALYZER_MODE = "mock"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## 前端安装与启动

需要 Node.js 20.19+ 或 22.12+。打开另一个 PowerShell：

```powershell
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173，进入场景分析页，选择 JPG、PNG 或 WebP 图片后开始分析。前端使用 API 返回的 `[x1, y1, x2, y2]` 归一化坐标绘制边界框。

## 检查

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q

cd ..\frontend
npm run build
```

## 当前范围

Day 3 只实现真实目标检测。空间关系、数据库持久化、物体跟踪、VLM、Agent 编排、登录和部署属于后续里程碑。

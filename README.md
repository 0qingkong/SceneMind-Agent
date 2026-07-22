# SceneMind Agent

SceneMind Agent 是一个面向移动端的多模态空间记忆产品。当前 Day 4 版本可上传场景图片，使用 Ultralytics YOLO 进行真实物体检测，并通过可解释的二维几何规则推导空间关系。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Vue Router
- 后端：FastAPI、Pydantic、Pillow
- 检测器：Ultralytics YOLO（默认 `yolo26n.pt`）
- 空间推理：确定性归一化边界框几何规则
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

## 空间推理配置

空间推理独立于检测器，因此 Mock 和 YOLO 使用完全相同的关系规则。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SPATIAL_ENABLED` | `true` | 设为 `false` 时保留检测结果并返回空关系列表 |
| `SPATIAL_NEAR_THRESHOLD` | `0.25` | 归一化图像平面中的中心点距离阈值 |
| `SPATIAL_OVERLAP_IOU_THRESHOLD` | `0.05` | 生成重叠关系的最小 IoU |
| `SPATIAL_CONTAINMENT_THRESHOLD` | `0.90` | 内框与外框相交面积占内框面积的最小比例 |
| `SPATIAL_AXIS_SEPARATION_THRESHOLD` | `0.08` | 水平或垂直中心分离的最小阈值 |
| `SPATIAL_MAX_RELATIONS` | `80` | 确定性排序后保留的最大关系数量 |

支持的谓词为 `left_of`、`right_of`、`above`、`below`、`near`、`overlaps`、`inside` 和 `contains`。关系分数是“较低检测置信度 × 几何强度”：轴向关系使用中心分离量，靠近使用阈值内的反向距离，重叠使用 IoU，包含使用内框覆盖比例。它不是学习模型概率。

这些关系只描述二维图像平面，不能证明物理支撑、真实深度或厘米距离，因此不会生成 `on`、`in_front_of`、`behind` 等谓词。

## 前端安装与启动

需要 Node.js 20.19+ 或 22.12+。打开另一个 PowerShell：

```powershell
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173，进入场景分析页，选择 JPG、PNG 或 WebP 图片后开始分析。前端使用 API 返回的 `[x1, y1, x2, y2]` 归一化坐标绘制边界框，并以中文展示二维关系和几何强度。

## 检查

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q

cd ..\frontend
npm run build
```

## 当前范围

Day 4 实现真实目标检测和可解释的二维空间关系。数据库持久化、跨图物体跟踪、自然语言查询、VLM/深度估计、Agent 编排、登录和部署属于后续里程碑。

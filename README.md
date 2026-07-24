# SceneMind Agent

SceneMind Agent 是一个面向移动端的多模态空间记忆产品。当前 Day 9–12 实现支持图片上传、浏览器实时镜头、低频观察会话、来源设备统计、记忆洞察，以及通过受约束 Agent 返回可打开的图片证据。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Vue Router
- 后端：FastAPI、Pydantic、Pillow
- 检测器：Ultralytics YOLO（默认 `yolo26n.pt`）
- 空间推理：确定性归一化边界框几何规则
- 场景记忆：SQLite 元数据 + 本地文件系统图片
- 记忆 Agent：确定性意图规划 + 只读工具 + 证据约束回答
- 多来源采集：上传、浏览器摄像头、明确标记的 AI Glasses Simulator
- 连续观察：前台低频顺序采样，不传输连续视频或音频
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
- 场景观察：`/api/v1/observations`
- 最近出现：`GET /api/v1/memory/last-seen?q=杯子`
- 历史记录：`GET /api/v1/memory/history?q=cup`
- 记忆 Agent：`POST /api/v1/agent/query`
- 观察会话：`/api/v1/capture-sessions`
- 设备统计：`GET /api/v1/devices/stats`
- 记忆洞察：`GET /api/v1/insights`
- JSON 导出：`GET /api/v1/privacy/export`

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

## 场景记忆与检索

“分析并记忆”只执行一次检测：共享分析服务完成图片校验、目标检测和空间推理，随后将观察快照事务性写入 SQLite，并将原图保存到文件系统。数据库保存相对图片路径，不保存图片字节，也不会向 API 暴露绝对路径。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./data/scenemind.db` | SQLAlchemy 数据库地址 |
| `SCENE_STORAGE_DIR` | `./data/images` | 场景图片目录 |
| `OBSERVATION_DEFAULT_LIMIT` | `20` | 观察列表默认页大小 |
| `OBSERVATION_MAX_LIMIT` | `100` | 观察列表最大页大小 |
| `MEMORY_HISTORY_DEFAULT_LIMIT` | `20` | 历史检索默认页大小 |
| `MEMORY_HISTORY_MAX_LIMIT` | `100` | 历史检索最大页大小 |
| `MEMORY_RELATION_CONTEXT_LIMIT` | `8` | 单条检索结果的最大关系上下文数 |
| `AGENT_DEFAULT_LIMIT` | `3` | Agent 列表类查询的默认结果数 |
| `AGENT_MAX_LIMIT` | `20` | Agent 单次查询允许的最大结果数 |
| `DEMO_MODE` | `false` | 启动时幂等添加带明显标记的生成式演示观察 |
| `CAPTURE_DEFAULT_INTERVAL_SECONDS` | `5` | 新会话默认采样间隔 |
| `CAPTURE_MIN_INTERVAL_SECONDS` | `3` | 最小采样间隔 |
| `CAPTURE_MAX_INTERVAL_SECONDS` | `60` | 最大采样间隔 |
| `CAPTURE_MIN_SAVE_GAP_SECONDS` | `15` | 无其他变化时允许周期保存的最小间隔 |
| `CAPTURE_OBJECT_COUNT_DELTA` | `2` | 触发保存的物体数量差 |
| `CAPTURE_MAX_SESSION_MINUTES` | `60` | 单会话最大持续时间 |

观察 API：

- `POST /api/v1/observations`：multipart 字段 `file`、可选 `title` 和 `location`
- `GET /api/v1/observations`：支持 `limit`、`offset`、`label` 和 `q`
- `GET /api/v1/observations/{id}`：恢复完整观察快照
- `GET /api/v1/observations/{id}/image`：安全读取已保存图片
- `DELETE /api/v1/observations/{id}`：删除观察、子记录和图片

最近出现查询是标签检索，不是跨图片身份跟踪。“最近一次检测到杯子”只表示最新观察包含匹配的 `cup/杯子` 标签，不表示它是现实中的同一个杯子。`last-seen` 无匹配时返回 404；`history` 无匹配时返回空列表。

删除时图片先原子移动到待删除文件，数据库提交成功后再清理；数据库失败会恢复图片。如果最终文件清理失败，API 会明确报错，数据库记录已经删除，隐藏的待删除文件需要运维清理。

SQLite 和本地文件系统是比赛 MVP 基础设施。以后可以替换为 PostgreSQL 和对象存储；当前数据量与查询模式不需要向量数据库或图数据库。

## Grounded Memory Agent

`POST /api/v1/agent/query` 接收：

```json
{"query":"我的杯子最后出现在哪里？"}
```

Agent 支持最后出现、历史场景、最近观察、指定记录详情、物体检测数量、帮助和未知问题七类意图。规划器不调用外部大模型；工具只包装现有 Memory/Observation 服务。响应包含意图、回答、折叠工具轨迹、证据卡和限制声明。无匹配或超出范围时不会猜测。

类别检索不证明跨图片是同一个现实物体，二维关系也不证明真实深度或物理距离。相关回答会明确显示这些限制。

## Demo Mode

演示数据默认关闭：

```powershell
$env:DEMO_MODE="true"
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启用后添加三条由项目代码生成的示例观察。固定 ID 保证重复启动不会重复写入；引擎标记和前端徽标会显示“演示数据”。已有真实记录永远不会被覆盖。仅清理演示数据：

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\reset_demo.py
```

## 文档与评估

- [架构](docs/ARCHITECTURE.md)
- [3–5 分钟演示脚本](docs/DEMO_SCRIPT.md)
- [评估方法](docs/EVALUATION.md)
- [部署](docs/DEPLOYMENT.md)
- [竞赛摘要](docs/COMPETITION_SUMMARY.md)

评估模板中的人工指标默认为 `not_run`，不会被误报为通过。填写 `backend/evaluation/cases.json` 的实测字段后，在 `backend` 运行 `..\.venv\Scripts\python.exe scripts\run_evaluation.py` 生成 JSON 和 Markdown 报告。

## 前端安装与启动

需要 Node.js 20.19+ 或 22.12+。打开另一个 PowerShell：

```powershell
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173，进入场景分析页，选择 JPG、PNG 或 WebP 图片后开始分析。前端使用 API 返回的 `[x1, y1, x2, y2]` 归一化坐标绘制边界框，并以中文展示二维关系和几何强度。

实时镜头位于 `/live`。摄像头权限只能在用户明确点击后请求，约束始终为 `audio: false`。构建期压缩配置：

| 变量 | 默认值 |
| --- | --- |
| `VITE_CAPTURE_IMAGE_TYPE` | `image/jpeg` |
| `VITE_CAPTURE_JPEG_QUALITY` | `0.88` |
| `VITE_CAPTURE_MAX_WIDTH` | `1600` |

手机摄像头通常要求受信任 HTTPS。`http://localhost` 只适用于运行浏览器的本机；物理手机访问电脑局域网 IP 时应使用受信任的 HTTPS 反向代理或开发证书。浏览器拒绝权限、设备占用或不安全上下文时页面会显示明确错误。

## 低频观察会话

`/sessions` 创建持久化会话，`/sessions/{id}` 明确连接摄像头并使用单一 awaited loop 顺序采样。页面隐藏时默认暂停；停止或离开页面会释放全部 MediaStream track 和 Screen Wake Lock。浏览器可能冻结后台标签页，因此产品不承诺后台持续采集。

`meaningful-change` 策略在首个有效样本、目标首次出现、标签多重集合变化、显著物体数量变化、最小保存间隔到达或用户强制保存时保存观察。`manual` 只响应强制保存，`every-analyzed-sample` 保存每个成功分析样本。检测器每个样本只调用一次。

## 设备、模拟器、洞察与隐私

- `/devices` 合并当前浏览器实际枚举的摄像头与后端持久化来源统计，不声称刷新后仍连接。
- `/glasses` 明确标记为 **AI Glasses Simulator / 未来设备交互预览**，不包含厂商 SDK，也不代表真实眼镜连接。
- `/insights` 使用 SQL 聚合真实 Observation/CaptureSession 数据；空数据库显示真实空状态。
- `/privacy` 将非敏感 UI 偏好保存在 localStorage，并支持暂停前端连续采集及 JSON 元数据导出。
- 保留天数自动清理、加密和人脸模糊均未实现；相关界面不会声称已经生效。

## 检查

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q

cd ..\frontend
npm run build
npm run test:capture
```

## 当前范围

Day 9–12 增加浏览器摄像头、多来源低频会话、设备中心、明确标记的眼镜模拟器、真实数据洞察和本地隐私偏好。真实商业眼镜集成、后台 Service Worker 摄像头、麦克风录制、跨图身份跟踪、开放领域聊天、深度估计、加密和人脸模糊不属于本次 MVP。

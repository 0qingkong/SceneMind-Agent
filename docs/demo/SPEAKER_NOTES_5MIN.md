# SceneMind 5-Minute Speaker Notes

Target: 300 seconds. Time every rehearsal and record the actual duration in the recording checklist. Bracketed cues are not spoken.

## 00:00-00:30 — Problem and positioning

[Home hero]

人们经常记得某件物品曾经出现在视野里，却想不起最后一次看到它的地点、时间和周围环境。普通目标检测只回答当前图片中有什么。SceneMind 是面向多设备视觉采集的证据化空间记忆智能体，它进一步让场景成为可保存、可查询、可回到原图的记忆。

## 00:30-01:00 — Product loop and capture boundary

[Four-step loop and source cards]

产品闭环包含看见、理解、形成记忆和证据化检索。现在实现了图片上传和浏览器摄像头静帧；摄像头只在用户点击以后请求权限，始终关闭音频。AI Glasses Simulator 使用相同采集接口，但它只是浏览器交互预览，并不代表真实眼镜硬件。

## 01:00-01:40 — Detection and explainable relations

[Analyze approved image]

真实模式通过 Ultralytics YOLO 检测多个物体，输出类别、置信度和归一化边界框。模型采用懒加载，初始化或推理失败会返回明确的 503，不会静默改用 Mock。随后，独立的 Spatial Reasoner 根据边界框生成左右、上下、靠近、重叠和包含关系。API 保留有方向的完整关系，前端折叠互逆重复。它们是可复现的二维规则，不是深度估计或物理距离。

## 01:40-02:10 — Persistent scene memory

[Save with title/location; Memory]

一次“分析并保存”只执行一次推理，然后把图片、物体、关系、地点、来源和时间作为 Observation 事务性写入。SQLite 保存结构化元数据，图片使用 UUID 文件名存放在本地目录。Last-Seen 和 History 按类别查找最新证据；它们不进行人脸识别，也不能确认跨图片是同一个现实物体。

## 02:10-02:55 — Agent internals and evidence

[Agent query, expand trace, open evidence]

我问：“我的杯子最后出现在哪里？” Planner 把问题映射到受支持的 last-seen 意图，只读工具复用 MemoryService。Formatter 只能描述工具返回的结构化结果，所以界面同时展示回答、工具参数、状态、证据卡和能力限制。点击证据会打开保存的原始图片，而不是仅提供一段无法核查的文本。

## 02:55-03:32 — Continuous observation

[Seeded session timeline]

SceneMind 还支持前台低频观察会话。前端使用单个 awaited loop，后端为每个 session 设置非重叠锁，每个样本只执行一次推理。meaningful-change 策略会在首帧、类别集合变化、明显数量变化、目标首次出现或最小间隔到达时保存，并把每次保存或跳过原因写入时间线。它不传输连续视频和音频，也不承诺浏览器后台持续运行。

## 03:32-04:02 — Devices, simulator, and privacy

[Devices → Glasses → Privacy]

设备中心把上传、浏览器摄像头和模拟器来源分组，持久化统计来自真实数据库。AI Glasses Simulator 页面始终显示“当前为浏览器端模拟，不代表已连接真实 AI 眼镜硬件”。相机激活指示不可关闭，导出不包含图片字节和服务器路径。加密、人脸模糊、账号系统和云同步尚未实现。

## 04:02-04:38 — Reliability and evaluation

[System and evaluation card]

工程层面提供 Profile A、B、C，一键启动、PID 和日志管理、liveness、readiness、幂等 Demo seed、安全 reset、E2E、故障注入和数据库文件完整性检查。Day 15 结果是 Memory 十比十，Agent 十七比十八，关系十一比十二，会话决策六比六，Mock processing 六比六。该数据集规模很小，真实 YOLO 评估没有运行，因此没有检测 mAP、召回率或 F1 结论。

## 04:38-05:00 — Close and roadmap

[Home / closing slide]

下一步首先是采集有合法授权并完成人工标注的真实场景集，在目标电脑和可信 HTTPS 手机上验证 Profile A、B。之后才考虑身份假设、深度证据、认证和真实硬件适配器。SceneMind 当前的价值，是把可检查的视觉感知、持续空间记忆和有证据的自然语言检索做成一个诚实、可复现的完整闭环。

## Optional sections

- Cut the persistence implementation detail if 15 seconds over.
- Cut device-center statistics if 25 seconds over; keep the simulator disclaimer.
- Never cut the Day 15 sample limitation or real-YOLO `not_run` status.

## Fallback narration

- **Profile A camera failure:** “可信 HTTPS 或摄像头路径未通过现场验证，我切换到 Profile B 的批准本地图片；分析器仍是真实 YOLO。”
- **Profile B model/asset failure:** “真实推理路径当前不可用，我切换到明确标记的 Profile C；这只验证编排、记忆和证据链。”
- **Frontend recovery:** continue with the storyboard while the backup operator runs stop → Profile C start → extended smoke.

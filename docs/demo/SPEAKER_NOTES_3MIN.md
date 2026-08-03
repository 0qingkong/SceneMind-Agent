# SceneMind 3-Minute Speaker Notes

Target: 180 seconds. The Chinese text is organized by actual timed blocks; rehearse at the team's natural pace and mark the measured duration. Bracketed cues are not spoken.

## 00:00-00:25 — Problem

[Home hero]

我们经常记得“刚才看见过这个东西”，却想不起它最后出现在哪里、什么时候出现，也找不到原始画面。SceneMind 的目标，是把经过许可的视觉场景变成可查询、可回溯证据的空间记忆。

## 00:25-00:50 — Solution

[Scroll four-step loop]

它通过四步形成闭环：从上传图片或浏览器摄像头看见场景，检测物体并推导二维关系，把图片、时间、地点和关系保存成 Observation，最后由 Agent 调用只读工具返回原始证据。

## 00:50-01:20 — Detect and relate

[Analyze approved image; hold on result]

这里展示分析结果。真实模式使用 YOLO，并返回归一化边界框、类别和置信度；如果模型失败，接口会明确报错，不会悄悄伪装成 Mock。重复类别在界面中显示为人物一、人物二。空间关系来自二维边界框几何规则，因此可以检查，但不代表真实深度或厘米距离。

## 01:20-01:42 — Persist memory

[Save once; open Memory]

保存以后，原始图片、物体、关系、地点和时间进入同一条场景记忆。Memory 可以搜索最近出现和历史记录。这里的类别匹配只说明又检测到了杯子，不能证明两张图片中一定是同一个现实杯子。

## 01:42-02:15 — Grounded Agent

[Ask `我的杯子最后出现在哪里？`; open evidence]

我问：“我的杯子最后出现在哪里？” Agent 不是开放域聊天，它先识别受支持意图，再调用 Last-Seen 只读工具。回答、工具轨迹和证据卡都来自数据库记录。点击证据，可以回到原始场景图片和关系上下文。

## 02:15-02:37 — Continuous observation and device path

[Session timeline, then glasses]

连续观察采用前台低频顺序采样，每个样本只推理一次，并记录为什么保存或跳过。AI Glasses Simulator 只是浏览器端的未来设备交互预览，不代表已经连接真实眼镜；未来硬件会通过同一 CaptureSource 边界接入。

## 02:37-03:00 — Evidence and limits

[Evaluation card and privacy]

Day 15 的小规模确定性结果是：Memory 十比十，Agent 十七比十八，关系人工审阅十一比十二，会话决策六比六。真实 YOLO 正式评估没有运行，因此我们不声称 mAP、召回率或 F1。SceneMind 的差异不是多一个检测页面，而是把感知、记忆、连续观察和证据化检索组合成一个可测试的产品闭环。

## Optional cuts

- If 10 seconds over: remove the future-adapter sentence.
- If 20 seconds over: show session only visually and keep the “low-frequency, one inference” sentence.
- Never cut the category-identity limit, 2D relation limit, simulator disclosure, or `not_run` statement.

## Fallback narration

- **Profile B unavailable:** “当前真实模型或许可素材路径不可用，我切换到明确标记的 Profile C；接下来展示产品编排和证据检索，不代表 YOLO 准确率。”
- **Camera unavailable:** “录制路径不依赖摄像头；现在使用已批准的本地图片继续真实 YOLO 流程。”

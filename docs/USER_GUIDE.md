# User Guide

## Start and choose a profile

From the repository root run `scripts/start-demo.ps1 -Profile C` for a deterministic first tour. Use Profile A only when browser-camera HTTPS and real YOLO are verified; use Profile B for real YOLO with licensed local images. The top banner discloses Demo/Mock state.

## Analyze and save a scene

1. Open **场景分析**.
2. Select an allowed JPG, PNG or WebP image.
3. Optionally enter a scene title and location.
4. Choose **仅查看检测结果** to avoid persistence, or **分析并保存到记忆** to create an Observation.
5. Review analyzer mode, object count, confidence, latency and relation summary.

Relations describe normalized two-dimensional box geometry only. Use object and predicate filters or expand the list to inspect more relations.

## Use Live Lens

Open **实时镜头**, read the purpose/permission notice, and click connect. The browser will request camera permission without audio. The active indicator remains visible. Capture a frame, then analyze or save it. Disconnect before leaving; the app also stops tracks on unmount/error.

Physical phones generally need trusted HTTPS when using a computer's LAN address. If permission fails, use a licensed upload or Profile C.

## Search spatial memory

Open **空间记忆** to search title, location or labels and filter by location, source, session and time. Cards are newest first. Open a detail to inspect objects, relations and source evidence; returning preserves the previous list position. Deletion requires confirmation and permanently removes the record/image.

Repeated categories use presentation-only ordinals such as `人物 1` and `人物 2`; the detector's raw label remains unchanged.

## Ask the Agent

The Agent supports questions about last seen, history, recent observations, one Observation detail and detected-category counts. Example: “我的杯子最后出现在哪里？” The result shows the answer, original evidence first, limitations, and a collapsed tool trace.

“No match” means the supported query found no stored evidence. “Unsupported” means the question is outside the Agent's limited tools. A category match does not prove the same physical instance.

## Continuous observation

Create an **观察会话**, choose an interval and save mode, then open its detail and explicitly connect the camera. Modes:

- `manual`: saves only when forced;
- `meaningful-change`: saves first evidence and configured label/count/time changes;
- `every-analyzed-sample`: saves every successful analyzed sample.

The page displays sampled, analyzed and saved counts plus each save/skip reason. Sessions are foreground-only and can pause when hidden.

## Devices, simulator and insights

**设备中心** separates browser-enumerated cameras, upload and simulator sources. Browser presence is not a durable online claim. **AI Glasses Simulator** is a browser future-interaction preview and is not real eyewear. **记忆洞察** uses persisted SQL aggregates; an empty database shows no fabricated percentage.

## Privacy and recovery

Use **隐私设置** to pause frontend continuous capture preferences and export JSON metadata. The camera indicator cannot be disabled. Encryption, face blur, cloud sync and automatic retention remain planned.

Use **系统状态** for liveness/readiness and copyable recovery commands. Operators can follow [DEMO_RUNBOOK](DEMO_RUNBOOK.md) and [RECOVERY](RECOVERY.md).

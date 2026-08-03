# Device Adapters

SceneMind separates capture from analysis through the frontend `CaptureSource` contract: `connect`, `disconnect`, `captureFrame`, `listDevices`, and `switchDevice`. Every source produces an image Blob plus source metadata for the existing `/analyze`, `/observations`, or capture-session APIs.

## Implemented sources

| Adapter | Status | Behavior |
| --- | --- | --- |
| `UploadCaptureSource` | Implemented | Uses a user-selected JPG/PNG/WebP file; no device connection |
| `BrowserCameraSource` | Implemented | Requests permission only after a click, always sets `audio: false`, owns one MediaStream, captures compressed still frames |
| `GlassesSimulatorSource` | Implemented simulator | Browser interaction preview using upload/camera-like frames; always labeled as simulation |

All MediaStream tracks are stopped on disconnect, connection failure and component unmount. A shared in-flight connect promise prevents duplicate permission requests. Device names/IDs are recorded only when provided by the browser.

## Explicit simulator language

Every simulator view and formal screenshot must show:

```text
AI Glasses Simulator
未来设备交互预览
当前为浏览器端模拟，不代表已连接真实 AI 眼镜硬件。
```

Simulator events are not telemetry from real glasses and must not be described as hardware integration.

## Future adapters

Android XR, vendor Wearable SDKs and custom hardware are extension targets, not current product capabilities. A future adapter must:

1. implement the existing capture lifecycle;
2. never request or transmit audio unless a separately reviewed product change requires it;
3. provide explicit source/device identity without exposing secrets;
4. emit still-image evidence compatible with the current API;
5. stop sensors deterministically on disconnect/error;
6. preserve visible capture and permission indicators;
7. document hardware, OS, network and license requirements;
8. add device-level tests without changing the meaning of existing Profile results.

## Why the boundary matters

The backend depends on images and source metadata, not a particular camera SDK. This keeps memory, relation and Agent contracts reusable while preventing a simulator from being mistaken for connected hardware. See [architecture](ARCHITECTURE.md), [privacy](PRIVACY.md), and [deployment](DEPLOYMENT.md).

# Competition Demo Script (3–5 minutes)

## Preparation

Use an image you own or have permission to demonstrate, ideally a desk or classroom with people, chairs, a laptop and a cup. Start the backend in real YOLO mode and the frontend as documented in `README.md`.

## Live path

1. **Frame the product (20 seconds).** On Home, explain the four stages: 看见场景、理解关系、形成记忆、自然语言检索.
2. **Upload (30 seconds).** Open 分析, choose the permitted desk/classroom image, enter a recognizable title and location, then select “分析并保存到记忆”.
3. **Show real detections (40 seconds).** Point to the engine field, latency, bounding boxes and confidence. If two people or chairs are present, show stable labels such as 人物 1 / 人物 2.
4. **Explain relations (30 seconds).** Show the collapsed UI relation list. State that inverse pairs remain in the API and that these are 2D geometric statements, not depth claims.
5. **Open memory (30 seconds).** Show the saved image, timestamp, location, object count and full scene detail.
6. **Search (30 seconds).** Search for 杯子, 人物 or 电脑. Show last-seen and newest-first history evidence.
7. **Ask Agent (45 seconds).** Ask “我的杯子最后出现在哪里？” and point out the intent, grounded answer, limitation text and image evidence.
8. **Open evidence (20 seconds).** Select “打开原始证据” to return to the exact stored observation.

## Optional multi-device extension

1. Open `/live`, explicitly allow the desktop webcam, and show the visible camera indicator.
2. Grab one analysis-only frame, then one “分析并记忆” frame; return to live preview.
3. Create a `/sessions` observation with a 5-second interval and a target such as 杯子. Show at least one saved and one skipped sample, then introduce the target and show the target-found event.
4. Stop the session and confirm the camera indicator turns off.
5. Open `/devices`, `/insights`, and the clearly labeled `/glasses` simulator.
6. On a physical phone, repeat `/live` through trusted HTTPS and switch front/rear cameras when the browser exposes both devices.

If the phone or browser denies permission, show the recovery error and browser site-permission control; do not claim that camera access succeeded. The simulator is never presented as a real glasses connection.

## Recommended additional questions

- `最近在哪些场景里见过人物？`
- `展示最近两条场景记忆`
- `图书馆那条记录里有什么？`
- `一共检测到多少把椅子？`
- An unsupported question to demonstrate honest scope handling.

## Fallback path

If real inference cannot initialize, do not present Mock output as real detection. Stop the server and restart explicitly with:

```powershell
$env:ANALYZER_MODE="mock"
$env:DEMO_MODE="true"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

State that inference is running in explicit fallback mode. Generated demo observations are visibly marked “演示数据”. They never overwrite real rows. After the presentation:

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\reset_demo.py
```

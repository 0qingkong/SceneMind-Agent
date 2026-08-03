# Deployment Guide

SceneMind currently supports a local Windows competition deployment. It does not ship a production cloud topology, authentication layer or multi-worker database design.

## Requirements and setup

- Windows 10/11 with PowerShell
- Python 3.11 or newer
- Node.js 20.19+ or 22.12+
- Disk space for dependencies, licensed model weights, SQLite data and images

From the repository root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\check-system.ps1
.\scripts\setup.ps1
```

`setup.ps1` creates missing local configuration without overwriting an existing `.env`. It does not download YOLO weights automatically as part of the repository.

## One-click profiles

```powershell
.\scripts\start-demo.ps1 -Profile A
.\scripts\start-demo.ps1 -Profile B
.\scripts\start-demo.ps1 -Profile C
.\scripts\stop-demo.ps1
```

| Profile | Camera | Analyzer | Data |
| --- | --- | --- | --- |
| A | Browser camera | Real YOLO | User-captured evidence |
| B | Local licensed images | Real YOLO | User-selected evidence |
| C | Not required | Explicit Mock | Generated, visibly marked demo evidence |

Use Profile C for deterministic recovery only. It does not measure real detector accuracy.

## Manual development startup

Backend terminal:

```powershell
cd backend
$env:ANALYZER_MODE = "yolo"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Endpoints: frontend `http://127.0.0.1:5173`, API `http://127.0.0.1:8000`, OpenAPI UI `http://127.0.0.1:8000/docs`.

## CPU and CUDA

`YOLO_DEVICE=auto` asks PyTorch whether CUDA is available and otherwise uses CPU. Set `YOLO_DEVICE=cpu` for predictable compatibility or a supported CUDA device such as `0` only after PyTorch, driver and GPU compatibility are verified. CPU startup and inference can be slower. Do not mix cold and warm latency measurements.

The first real inference may need local model weights. Competition machines should be prepared offline with a legally redistributable or locally licensed weight file and `YOLO_MODEL` pointing to it.

## Environment variables

`.env.example` is the canonical list. Important groups are:

- Service: `APP_NAME`, `APP_ENV`, `APP_BUILD`, `ALLOWED_ORIGINS`, `VITE_API_BASE_URL`
- Analyzer: `ANALYZER_MODE`, `YOLO_MODEL`, `YOLO_CONF`, `YOLO_IMGSZ`, `YOLO_MAX_DET`, `YOLO_DEVICE`
- Relations: `SPATIAL_ENABLED` and `SPATIAL_*_THRESHOLD`
- Persistence: `DATABASE_URL`, `SCENE_STORAGE_DIR`, pagination limits
- Demo: `DEMO_MODE`, `DEMO_PROFILE`
- Sessions: `CAPTURE_*`
- Browser build: `VITE_CAPTURE_IMAGE_TYPE`, `VITE_CAPTURE_JPEG_QUALITY`, `VITE_CAPTURE_MAX_WIDTH`

Never commit `.env`, access tokens, user paths or model weights.

## Ports and CORS

Defaults are API `8000` and frontend `5173`. If either changes, rebuild the frontend with the matching `VITE_API_BASE_URL` and include the exact frontend origin in `ALLOWED_ORIGINS`. A port conflict should be resolved by stopping only the owning verified process or selecting another coordinated pair; do not broadly terminate Python or Node.

## Phone HTTPS requirement

Browser camera access requires a secure context. Desktop `localhost` is treated specially, but a physical phone visiting a computer's LAN IP over plain HTTP normally is not. Put frontend and API behind a trusted HTTPS reverse proxy or development certificate, update CORS and API URL, then test on the actual phone. Do not rely on bypassed certificate warnings during judging.

SceneMind requests no audio, sends compressed still frames only, pauses hidden capture by default and does not promise background collection.

## Data directories

Default backend paths are `backend/data/scenemind.db` and `backend/data/images` when launched from `backend`. Managed demo PIDs and logs live under ignored `.runtime/pids` and `.runtime/logs`. Evaluation, test reports and UI-review images also use ignored runtime directories.

## Backup and recovery

The database and image directory form one evidence set. Stop writes, copy both together, record a checksum, and restore both to matching configured paths. Verify with:

```powershell
.\scripts\data-integrity-test.ps1
```

Demo reset is scoped and destructive only to marked demo records:

```powershell
.\scripts\reset-demo.ps1 -ConfirmReset
```

It preserves unmarked user observations. Operational recovery steps are in [RECOVERY.md](RECOVERY.md); offline preparation is in [OFFLINE_PACKAGE.md](OFFLINE_PACKAGE.md).

## Health checks

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
.\scripts\smoke-demo.ps1 -Extended
```

`health` is lightweight liveness. `ready` checks database access, writable image storage and configuration without loading or running the model. Unloaded YOLO is visible but not itself a storage-readiness failure.

## Common failures

| Symptom | Check | Recovery |
| --- | --- | --- |
| WinError 10013 / port unavailable | Existing listener and security policy | Stop the verified owner or choose coordinated ports |
| Frontend says API unavailable | API URL, CORS, `/ready` | Start backend and rebuild with correct `VITE_API_BASE_URL` |
| YOLO returns `503` | Weight path, dependencies, device | Use valid local weight/device; disclose Profile C if switching |
| Camera permission denied | HTTPS, browser permission, device use | Grant permission after explanation or use Profile B/C |
| Missing evidence image | Database/image pairing | Restore matching backup and run integrity validation |
| Stale managed process | `.runtime/pids` identity and logs | Run `stop-demo.ps1`; follow recovery guide if identity fails |

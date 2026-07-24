# Deployment Guide

## Competition workstation

Requirements: Python 3.11+, Node.js 20.19+ or 22.12+, enough disk space for model weights and uploaded demo images.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd frontend
npm install
npm run build
```

Start the backend from `backend`:

```powershell
$env:ANALYZER_MODE="yolo"
$env:DEMO_MODE="false"
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For development, run `npm run dev` in `frontend`. For a packaged demo, serve `frontend/dist` with a static server and set `VITE_API_BASE_URL` before building if the API origin differs.

## Camera access from a physical phone

Browser camera APIs require a secure context. A phone browsing `http://<computer-lan-ip>:5173` is normally not secure even though desktop `localhost` works. Put the frontend and API behind a trusted HTTPS reverse proxy/development certificate, configure `VITE_API_BASE_URL` to the HTTPS API origin, and add that frontend origin to backend CORS before the phone acceptance test. Do not bypass certificate warnings for a competition demo.

SceneMind has no camera Service Worker or background recorder. Keep the capture page visible; the application pauses hidden continuous sessions by default and treats Wake Lock as best-effort.

## Persistent data

Back up both the SQLite file and `SCENE_STORAGE_DIR`; either one alone is incomplete. Stop writes while taking a simple filesystem copy. Never commit the database, uploads or YOLO weights.

## Environment

Copy values from `.env.example` into the process environment. `DEMO_MODE=false` is the safe default. `ANALYZER_MODE=mock` must be an explicit operator choice and must be disclosed during a demo.

If exposing beyond localhost, place both services behind HTTPS, restrict CORS to the deployed frontend origin, run a single application worker for this SQLite MVP, and use an access-controlled host. Authentication and distributed deployment are intentionally outside the competition scope.

## Operational checks

- `/api/v1/health` reports analyzer mode, load state, device and demo mode without loading YOLO.
- A YOLO initialization/inference failure returns `503` and never silently changes engines.
- Ensure the configured data and image directories are writable by the backend process.
- Use `scripts/reset_demo.py` only for demo rows; it deliberately preserves real observations.

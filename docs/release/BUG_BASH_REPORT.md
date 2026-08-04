# Release-candidate bug-bash report

Target: `0.9.0-rc1`. Final automated run: `bug-bash-20260804-101823-65036`, completed 2026-08-04 10:19 Asia/Shanghai. Runtime logs remain under ignored `.runtime/release/` and are not release artifacts.

| Gate | Actual result | Duration | Evidence |
|---|---|---:|---|
| Backend pytest | PASS — 97 tests, 2 known warnings | 5.14s | `backend_pytest.stdout.log` |
| Frontend production build | PASS | 6.85s | `frontend_build.stdout.log` |
| Frontend capture tests | PASS — 4 tests | 4.78s | `frontend_capture_tests.stdout.log` |
| Day 14 E2E/browser | PASS — backend/integrity plus 10 Playwright tests | 35.26s | `day14_e2e.stdout.log` |
| Failure injection/process safety | PASS — 10 API tests plus port/PID/process checks | 4.88s | `failure_injection.stdout.log` |
| Data integrity | PASS — 9 integrity checks | 2.22s | `data_integrity.stdout.log` |
| Profile C prepare | PASS — reset, seed, start, routes and smoke | 31.47s | recording status JSON and service logs |
| Profile C extended smoke | PASS | 0.57s | `profile_c_extended_smoke.stdout.log` |
| Managed stop | PASS; ports released | 1.90s | `profile_c_stop.stdout.log` |
| Release/claim/document consistency | PASS | 2.29s | `release_consistency.stdout.log` |
| Sensitive-data/artifact scan | PASS — zero blocking findings | 0.85s | `sensitive-data.json` |

Automated result: **PASS**. Open P0: **0**. Open P1: **0**.

## Defects found and fixed during the gate

1. **P1 release orchestration, fixed:** `Start-Process -Wait` waited for intentional service descendants, so Bug Bash could stall after successful E2E/Profile C preparation. The runner now waits only for the direct command and treats start, smoke and stop as separate gates.
2. **P1 managed cleanup, fixed:** frontend PID metadata originally tracked the short-lived npm launcher, which could leave the actual Vite listener alive. Startup now resolves and records the verified TCP listener process; E2E also records and stops that listener. Regression rerun confirmed ports 15173/18000 and 5173/8000 were released.
3. **P2 recording preflight, fixed:** strict mode attempted to read an unset `$LASTEXITCODE` after an in-process PowerShell script. Preflight now executes checked child scripts explicitly and records a useful failure status.
4. **Invalid test invocation, corrected:** an early manual pytest command named a basetemp whose parent did not yet exist. After creating the ignored runtime parent, the unchanged suite passed 97/97; this was not an application failure.

## Remaining issues and human gates

Known P2/P3 items remain in `KNOWN_ISSUES.md`; none is an open P0/P1. Profile A camera, Profile B approved real-YOLO images, one physical phone over HTTPS, final recording/voice-over/subtitle/screenshot/video approval and package/license inspection remain **NOT RUN**. The automated result does not convert those gates to PASS.

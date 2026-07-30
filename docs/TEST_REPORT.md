# SceneMind Day 14 Validation Report

## Run identity

- Date: 2026-07-30 (Asia/Shanghai)
- Tested code commit: `33e68d4` plus the documentation-only commit containing this report
- Base: `bad6fcb` (Day 13 merged into `main`)
- OS: Windows, PowerShell 5.1
- Python: 3.12.13
- Node.js: 22.20.0; npm: 10.9.3
- Automated analyzer: Mock/Fake only
- Browser: Microsoft Edge, Playwright 1.55.1

## Actual automated results

| Check | Actual result |
| --- | --- |
| Backend pytest | PASS - 88 tests, 2 existing warnings, 9.38 s |
| Frontend production build | PASS - 128 modules, 425 ms Vite phase |
| Frontend capture tests | PASS - 4 tests |
| Browser E2E | PASS - 6 flows; observed complete run 9.3 s |
| Failure injection | PASS - 10 pytest cases plus port, stale-PID, and owned-process checks |
| Data integrity | PASS - 9 categories over 5 seeded observations |
| Profile C | PASS - startup and built-in nine-endpoint smoke flow |

Runtime reports and browser artifacts remain only under ignored `.runtime/test-results/`.

## Manual acceptance

| Profile | Status | Evidence |
| --- | --- | --- |
| Profile A - camera + real YOLO | NOT RUN | No camera/hardware rehearsal was supplied. |
| Profile B - permitted image + real YOLO | NOT RUN | No team-approved evaluation image set was supplied. |
| Profile C - Mock recovery | PASS | Startup, readiness, seed, and built-in smoke completed. |
| Phone - trusted HTTPS + rear camera | NOT RUN | No phone/trusted HTTPS origin was available. |

## Defects found

1. **P1, fixed:** native `taskkill` stderr could abort stop cleanup before fallback and PID removal.
2. **P1, fixed:** a checksum-corrupt PNG raised Pillow `SyntaxError` and escaped as HTTP 500; it now returns 400.
3. **Test configuration, fixed:** isolated frontend ports require an explicit CORS origin.
4. **Test selector, fixed:** browser object verification now uses `.object-grid`.

## Open defects

- P0: none.
- P1: none.
- P2: none discovered in automated scope.
- P3: existing Starlette/httpx deprecation and a pytest return-value warning.

## Conclusion

The deterministic competition chain and recovery checks pass without touching user data. Real YOLO and phone results remain explicitly unmeasured.

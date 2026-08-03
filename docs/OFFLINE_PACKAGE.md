# Offline Competition Package

The offline package is an operator-controlled backup outside Git. Include only content that is licensed for the target machine and redistribution context.

## Required inventory outside Git

- A source archive at the exact release commit plus its commit SHA.
- A local `.env` derived from `.env.example`, stored separately and never uploaded.
- The selected YOLO weight file and its license/source record.
- Licensed Profile B demonstration images and attribution/consent record.
- A verified Profile C SQLite/image pair produced by the repository's idempotent seed.
- Python wheel/pip and npm dependency caches, subject to their redistribution licenses.
- Presentation PDF/PPT, backup video and speaking notes.
- Offline copies of `DEMO_RUNBOOK.md`, `RECOVERY.md`, `DEPLOYMENT.md` and `SUBMISSION_CHECKLIST.md`.
- A manifest containing filename, size, SHA-256, source/license and verification date.

Do not treat `.venv` or `node_modules` as portable cross-machine installations. Prefer lockfiles plus verified caches and run `setup.ps1` on the destination.

## Build the package

1. Export the release commit and record `git rev-parse HEAD`.
2. Copy only approved external assets into a dedicated offline directory.
3. Install and start on the actual backup computer while internet access is disabled.
4. Run Profile C extended smoke, then Profile B if licensed images and real YOLO are available.
5. Stop services, validate reset, and confirm user evidence is unaffected.
6. Generate and review checksums.

```powershell
Get-ChildItem . -Recurse -File |
  Get-FileHash -Algorithm SHA256 |
  Select-Object Path, Hash |
  Export-Csv .\SHA256SUMS.csv -NoTypeInformation -Encoding UTF8
```

Verify the CSV on a second medium or machine. Keep one read-only copy and one working copy.

## Offline acceptance

```powershell
.\scripts\check-system.ps1
.\scripts\start-demo.ps1 -Profile C -NoBrowser
.\scripts\smoke-demo.ps1 -Extended
.\scripts\stop-demo.ps1
.\scripts\check-release-docs.ps1
```

Then manually confirm: Home disclosure, saved Demo evidence, Agent evidence image, simulator disclaimer, privacy boundaries, stop cleanup and safe Demo reset. Real YOLO and physical-camera acceptance must remain separately recorded.

Databases, images, weights, videos, logs, build output and generated reports remain untracked. See [deployment](DEPLOYMENT.md), [recovery](RECOVERY.md), and the [submission checklist](competition/SUBMISSION_CHECKLIST.md).

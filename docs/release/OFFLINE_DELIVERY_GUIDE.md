# Offline delivery guide

Target: `SceneMind-v0.9.0-rc1`. Build with `scripts/release/package-release.ps1 -Version 0.9.0-rc1`; generated output stays under ignored `.runtime/release/`.

## Package contents

| Path | Purpose |
|---|---|
| `source-code/` | Clean tracked repository snapshot with lockfiles and manifests |
| `docs/` | Operator, architecture, privacy, demo and release documentation |
| `scripts/` | Setup/start/stop/media/release scripts for inspection and recovery |
| `evaluation/` | Actual Day 14/15 reports and evaluation runner sources |
| `sample-data/` | Generated-data instructions; no private real image |
| `presentation/` | Pitch/report sources and reproducible subtitles; only approved screenshots if selected |
| `video/` | Inclusion record; final video remains absent until human approval |
| root files | Start guide, offline guide, version, manifest and SHA-256 checksums |

The package excludes Git history, `.env`, user databases/uploads, `.runtime`, dependency directories, build output, logs, model weights, private recordings and unclear-license images. The repository does not currently provide a unified redistribution license, so external delivery needs explicit rights-holder approval.

## Verify before copying

From the original repository:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\release\verify-release.ps1 `
  -Version 0.9.0-rc1 `
  -PackagePath .\.runtime\release\SceneMind-v0.9.0-rc1
```

Verification copies the directory into a fresh temporary inspection path, checks every SHA-256 entry, required paths, forbidden artifacts, manifest and static version configuration. Pattern scanning and checksums do not replace human privacy/license review.

## Prepare a runnable offline workspace

Copy `source-code/` to a writable directory. On a machine that already has approved Python/Node packages available locally:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\check-system.ps1
$env:PIP_NO_INDEX = "1"
$env:npm_config_offline = "true"
.\scripts\setup.ps1
.\scripts\start-demo.ps1 -Profile C -NoBrowser
.\scripts\smoke-demo.ps1 -Extended
```

This setup succeeds only when every package is already installed or available in approved local caches; otherwise it fails visibly without downloading. If dependencies are already installed in `.venv` and `frontend/node_modules`, skip setup. Remove the two process variables after setup if the shell will be reused. Offline mode never downloads a model. Run `.\scripts\release\offline-check.ps1` from the original prepared repository to enforce process-local offline package-manager flags and verify Profile C without changing adapters, firewall or system networking.

## Local model and Profile B assets

Model weights are never bundled silently. Place a user-supplied, redistribution-approved weight at:

```text
source-code/backend/yolo26n.pt
```

or set `YOLO_MODEL` in a local, untracked `.env`. Record its SHA-256 in the human delivery record. Put at least five team-owned/approved real images in `.runtime/demo-assets/profile-b/` and add the ignored `asset-approval.json` described by `docs/demo/DEMO_ASSET_MANIFEST.md`.

## Profile decision table

| Profile | Choose when | Local requirements | Release status |
|---|---|---|---|
| A | Full competition camera rehearsal | approved YOLO weight, camera, permission; trusted HTTPS for physical phone | Human hardware gate: NOT RUN |
| B | Deterministic real-image YOLO recording | approved local images, approval manifest and local weight | Human asset/detection gate: NOT RUN |
| C | Offline/emergency rehearsal | installed dependencies only; generated Mock evidence | Automated deterministic target; never detector accuracy evidence |

## Stop, reset and recover

```powershell
.\scripts\stop-demo.ps1 -Force
.\scripts\reset-demo.ps1 -ConfirmReset
.\scripts\start-demo.ps1 -Profile C -NoBrowser
```

Reset deletes only demo-marked rows and demo image files; it does not erase real user Observations. If readiness fails, read `.runtime/logs`, run `scripts/check-system.ps1`, stop verified SceneMind PID metadata, and use the recovery order in `docs/RECOVERY.md`. Do not kill unrelated Python/Node processes or delete a broad data directory.

## Human delivery approvals

- Profile A camera on competition hardware: **NOT RUN**.
- Profile B approved images and real YOLO: **NOT RUN**.
- Physical phone over trusted HTTPS: **NOT RUN**.
- Package file/license/privacy inspection: **NOT RUN**.
- Final media inclusion and end-to-end playback: **NOT RUN**.
- P2/P3 acceptance, tag and remote publication: **NOT RUN**.

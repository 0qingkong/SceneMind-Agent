# SceneMind 0.9.0-rc1 release notes

Status: **release candidate prepared for verification, not published**. No Git tag, remote branch or GitHub Release is created by the release workflow.

## Product summary

SceneMind is a local-first spatial-memory agent. It turns permitted scene images into evidence-backed Observations: detected objects, explainable two-dimensional relations, source/location/time metadata and an original-image evidence route. Last-Seen/History and a bounded Agent retrieve stored category evidence instead of producing unsupported open-domain answers.

## Major capabilities

- User-selected image upload and user-initiated browser camera still capture.
- Explicit real YOLO and Mock analyzers; real-analyzer failure never silently returns Mock output.
- Deterministic `left/right`, `above/below`, `near`, `overlaps`, `inside/contains` image-plane relations.
- SQLite and local UUID image persistence with Memory list/detail/delete and evidence trace-back.
- Bounded Agent intents, validated parameters, read-only tools, tool traces and Observation citations.
- Foreground low-frequency capture sessions with saved/skipped/error reasons.
- Device statistics, Insights, local privacy preferences and an explicitly labeled AI Glasses Simulator.
- Managed Profile A/B/C startup, health/readiness, deterministic seed/reset, PID/log recovery, E2E/failure/integrity/evaluation gates.

## Architecture

Vue 3, TypeScript, Vite and Vue Router call a versioned FastAPI `/api/v1` API. Analyzer, Spatial Reasoner, Memory, Agent, sessions and dashboard services remain separated. SQLAlchemy/SQLite stores structured metadata and the local filesystem stores original images. See [architecture](../ARCHITECTURE.md) and [technical report](../competition/TECHNICAL_REPORT.md).

## Actual validation evidence

Day 14 validated the isolated API lifecycle, six deterministic browser core flows, responsive UI review, controlled failures and DB/file integrity. Profile A, Profile B and physical-phone hardware were outside that automated run.

The Day 15 small deterministic baseline records:

| Area | Actual result |
|---|---|
| Memory | 10 / 10; ordering, evidence availability and restart persistence 100% |
| Agent | 17 / 18 intent, parameter, tool and evidence matches; 94.44% |
| Relations | 11 / 12 reviewed predictions correct; 91.67% overall precision |
| Sessions | 6 / 6 decisions; 6 / 6 saved |
| Mock processing | 6 / 6 successful |
| Real YOLO formal benchmark | `not_run`; no approved licensed real-scene set and box ground truth |

These results are regression evidence for the stated cases, not detector mAP/recall/F1 or population performance.

## Demo profiles

| Profile | Input/analyzer | Intended use | Current gate |
|---|---|---|---|
| A | browser camera + real YOLO | full target-hardware demo | Human camera/HTTPS rehearsal: NOT RUN |
| B | approved local images + real YOLO | deterministic real-detection recording | Human assets/weight/detection rehearsal: NOT RUN |
| C | generated seeded scenes + explicit Mock | complete emergency/offline flow | Automated release target; not detector evidence |

## Setup and verification

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\check-system.ps1
.\scripts\setup.ps1
.\scripts\start-demo.ps1 -Profile C -NoBrowser
.\scripts\smoke-demo.ps1 -Extended
```

Run `scripts/release/bug-bash.ps1`, then build and verify the offline directory using the [offline delivery guide](OFFLINE_DELIVERY_GUIDE.md).

## Known limits

- Category retrieval cannot confirm the same physical object across images.
- Relations are two-dimensional box geometry, not depth, support or centimetre distance.
- Real detection degrades with detector/domain limits, occlusion, small objects and low light.
- The Agent is bounded deterministic retrieval, not open-domain chat.
- Continuous capture requires the foreground page and does not record continuous video/audio.
- AI Glasses Simulator is a browser preview, not real glasses or vendor SDK integration.
- Authentication, multi-user isolation, automatic retention deletion, cloud encryption/sync and face blurring are not implemented.
- The repository does not supply a unified redistribution license.

See [known issues](KNOWN_ISSUES.md) for workarounds and release impact.

## Upgrade notes

This candidate changes the public app version from `0.18.0` to `0.9.0-rc1` but does not introduce an API version or database-schema migration. Preserve the existing `.env`, database and image directory when upgrading a real workspace. Demo reset remains scoped to demo-marked rows/files. Re-run setup only to reconcile existing dependency manifests; model weights and Profile B assets remain local.

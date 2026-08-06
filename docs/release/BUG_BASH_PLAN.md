# Release-candidate bug-bash plan

Target: `0.9.0-rc1`. Severity is fixed: **P0** startup failure, data corruption or unusable demo; **P1** broken core flow without a practical workaround; **P2** visible defect with a safe workaround; **P3** cosmetic/documentation defect. The candidate cannot pass with an open P0/P1.

## Automated matrix

| Area | Checks | Evidence owner |
|---|---|---|
| Installation/startup | dependency presence, missing setup guidance, repeated start/stop, occupied ports, stale PID, partial cleanup, Profile C offline-local startup | setup and failure scripts |
| Core API | valid/corrupt/empty/large upload, Mock labels, zero/repeated detections, relation cap, save, search, Last-Seen/History, Agent supported/no-result/unsupported, evidence links | pytest and Day 14 E2E |
| Sessions/data | state transitions, device stats, insights, export/delete, DB/image integrity and orphan detection | pytest and integrity test |
| Browser/responsive | six product flows, desktop/tablet/mobile/small overflow, Agent evidence, simulator disclaimer, camera error states | Playwright and capture tests |
| Failure recovery | analyzer error, filesystem/DB failure, corrupt image, occupied port, stale and owned PID | failure injection |
| Privacy/truthfulness | visible Demo/Mock/Simulator states, camera disclosure, category/depth limits, no unsupported accuracy/hardware claim | release consistency scan |
| Packaging | required tree, forbidden artifacts, manifest, SHA-256 and offline Profile C | release package tools |

`scripts/release/bug-bash.ps1` stores each command's output, exit code and duration under ignored `.runtime/release/<run-id>/`. It reuses existing test suites and does not rewrite their logic.

## Manual matrix

Unperformed entries must remain `NOT RUN`.

| Gate | Status | Required evidence |
|---|---|---|
| Fresh setup on a clean competition machine | NOT RUN | setup transcript and restart |
| Profile A camera permission, denial, release-on-navigation and orientation | NOT RUN | competition hardware/browser record |
| Profile B approved images with real YOLO | NOT RUN | approved assets, weight checksum and observed detections |
| Physical phone over trusted HTTPS | NOT RUN | portrait/landscape, keyboard, safe area and permission record |
| Low light/occlusion discussion scene | NOT RUN | reviewed failure behavior without inflated claims |
| Final screenshots, subtitles, voice-over and video | NOT RUN | privacy/content approval |
| Offline package content inspection | NOT RUN | two-person file/license review |
| P2/P3 release acceptance | NOT RUN | release-owner sign-off |

## Exit rule

Automated checks must pass, no P0/P1 may remain, and every unexecuted hardware/media gate must be disclosed. A human may accept documented non-blocking P2/P3 issues. Tags, remote branches and GitHub Releases require separate explicit approval.

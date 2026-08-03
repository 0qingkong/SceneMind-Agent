# Competition Submission Checklist

## Code and Git

- [ ] Release branch contains the five required focused commits.
- [ ] `git diff --check` passes and worktree contents are understood.
- [ ] No `.env`, credentials, personal media, database, weight, log, video, build or runtime artifact is tracked.
- [ ] Release commit SHA is recorded in slides, report export and offline manifest.
- [ ] README links and `scripts/check-release-docs.ps1` pass.

## Automated validation

- [ ] Backend pytest passes.
- [ ] Frontend production build passes.
- [ ] Capture tests pass.
- [ ] Core Playwright flows and four responsive views pass.
- [ ] Profile C start plus extended smoke passes.
- [ ] Managed stop removes verified SceneMind processes.
- [ ] Scoped Demo reset is idempotent and preserves unmarked evidence.
- [ ] E2E, failure and data-integrity scripts pass.

## Manual rehearsal

- [ ] Profile A is marked passed/failed/not-run on the target workstation.
- [ ] Profile B real YOLO is marked passed/failed/not-run with a licensed image set.
- [ ] Physical phone HTTPS/camera path is marked passed/failed/not-run.
- [ ] Profile C Home, Analyze, Memory, Agent, session, simulator, insights, privacy and system flows are rehearsed.
- [ ] Camera indicator and track cleanup are manually observed where a camera is used.
- [ ] Stop/start recovery is timed and speaking fallback is rehearsed.

## Claims and materials

- [ ] Project name and closed loop match README and pitch.
- [ ] Day 15 numbers are exactly Memory 10 / 10, Agent 17 / 18, relations 11 / 12, sessions 6 / 6, Mock processing 6 / 6.
- [ ] Real YOLO evaluation remains `not_run` unless a new separately reviewed report supersedes it.
- [ ] No mAP/recall/F1, same-instance, physical-distance, hardware-glasses or production-cloud claim is added without evidence.
- [ ] Slides, technical report, demo scripts, Q&A and claims ledger use the same Profile/simulator language.
- [ ] Required competition format, length, naming and submission portal rules are checked by the operator.

## Screenshot and asset review

- [ ] Formal screenshots follow [SCREENSHOT_PLAN](SCREENSHOT_PLAN.md).
- [ ] Every image uses synthetic/licensed content and contains no personal data or local path.
- [ ] Mock/Demo/Simulator markings and 2D limitations are not cropped.
- [ ] Resolution, language and typography are consistent.
- [ ] Asset source, license, run ID and release commit are recorded.
- [ ] PPT/PDF/video exports are opened on the offline backup computer.

## Offline recovery pack

- [ ] Licensed YOLO weight and its checksum/license record are available.
- [ ] Licensed Profile B images and generated Profile C evidence are available.
- [ ] Dependency caches and lockfiles install without network access.
- [ ] SQLite and image backup match and pass integrity validation.
- [ ] Read-only and working media copies have verified SHA-256 manifests.
- [ ] Demo Runbook, Recovery, Deployment and this checklist are accessible offline.

## Final operator sign-off

Record: release SHA, workstation, date/time, selected profile, model/weight identity, camera/phone status, all command results, known failures, screenshot source, presenter and backup operator. Any unchecked item must be described explicitly rather than assumed complete.

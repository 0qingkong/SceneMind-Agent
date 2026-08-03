# Recording checklist

Release target: `0.9.0-rc1`. Use Profile B for an approved real-YOLO recording, or Profile C for the deterministic emergency recording. Automation prepares the app and evidence; it never starts an operating-system recorder.

## Automated preflight

- [ ] Run `scripts/media/verify-demo-assets.ps1 -Profile C` (or `-Profile B`).
- [ ] Run `scripts/media/prepare-recording.ps1 -Profile C -NoBrowser` and retain the session-status path.
- [ ] Confirm liveness, readiness, smoke checks and the required routes are reported as ready.
- [ ] Run `scripts/media/capture-demo-screens.ps1`; review ignored staging output before promoting any image.
- [ ] Confirm Demo/Mock/Simulator labels, relation limits and local paths are visible or hidden as intended.
- [ ] Confirm no private observation remains in the demo database.

## Human recording gate

All items below remain **NOT RUN** until a person signs them off.

| Gate | Status | Human evidence required |
|---|---|---|
| Record a real screen video | NOT RUN | Original capture file and operator/date |
| Record or approve voice-over | NOT RUN | Approved audio file or approval note |
| Visually inspect final subtitles | NOT RUN | 3-minute and 5-minute playback review |
| Confirm personal/private data are absent | NOT RUN | Frame-by-frame privacy review |
| Approve selected screenshots | NOT RUN | Explicit selection list before promotion |
| Inspect exported video end to end | NOT RUN | Playback on competition machine and backup device |
| Rehearse the 3-minute talk | NOT RUN | Timed rehearsal duration and issues |
| Rehearse the 5-minute talk | NOT RUN | Timed rehearsal duration and issues |

## Recording settings

- Capture at 1920x1080 when possible; keep browser zoom at 100% and notifications off.
- Use the cue sheet as the timing source. Never crop Demo, Mock, Simulator or geometry-limit disclosures.
- Record Profile B only after approved images and a locally supplied weight pass asset verification.
- Preserve original media. Render and compression scripts always write separate outputs.
- If a live step exceeds its time box, use the named fallback instead of improvising a stronger claim.

## Final export review

- [ ] Speech, click and subtitle timing agree with `VIDEO_STORYBOARD.md`.
- [ ] The cited Memory Observation opens and its evidence image is readable.
- [ ] The Agent answer shows evidence rather than unsupported free-form output.
- [ ] The glasses disclaimer is held long enough to read.
- [ ] Metrics say Memory 10/10, Agent 17/18, relations 11/12 and sessions 6/6; real YOLO benchmark is `not_run`.
- [ ] The final file was not added to Git; release inclusion requires explicit approval.


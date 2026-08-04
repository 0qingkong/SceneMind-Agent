# Release checklist — 0.9.0-rc1

Check an automated row only from the final runtime evidence. Human rows stay `NOT RUN` until signed by a person.

## Automated candidate gate

- [ ] Backend `pytest tests -q` passes.
- [ ] Frontend production build and capture tests pass.
- [ ] Day 14 E2E, failure injection and data-integrity scripts pass.
- [ ] Profile C reset/seed/start, liveness/readiness, extended smoke and managed stop pass.
- [ ] Desktop/mobile demo screenshots are generated in ignored staging, or an honest blocker is recorded.
- [ ] Subtitles regenerate with monotonic, non-overlapping timing.
- [ ] Version is `0.9.0-rc1` in VERSION, backend, health response, frontend package/lock and UI.
- [ ] Project name, routes, A/B/C definitions, simulator disclosure, Day 15 metrics and public claims pass consistency checks.
- [ ] Sensitive-data/artifact scan has zero blocking finding; its detection limitation remains disclosed.
- [ ] Offline package contains the required tree and excludes secrets/runtime data/weights/private media.
- [ ] SHA-256 verification passes in a clean temporary inspection directory.
- [ ] Offline Profile C passes without changing system network configuration.
- [ ] `git diff --check` and forbidden tracked-artifact queries pass.
- [ ] Open P0/P1 count is zero.

## Day 19 human gates

| Gate | Status | Approval |
|---|---|---|
| Record real screen video | NOT RUN | Media owner/date |
| Record or approve voice-over | NOT RUN | Speaker/media owner |
| Inspect subtitles visually | NOT RUN | 3-minute and 5-minute playback |
| Confirm private/personal data absent | NOT RUN | Privacy reviewer |
| Approve selected screenshots | NOT RUN | Explicit file list |
| Inspect final exported video end to end | NOT RUN | Competition machine and backup device |
| Rehearse 3-minute and 5-minute talks | NOT RUN | Timed results |

## Day 20 human gates

| Gate | Status | Approval |
|---|---|---|
| Profile A camera rehearsal on competition hardware | NOT RUN | Hardware/browser record |
| Profile B approved-image real-YOLO rehearsal | NOT RUN | Asset manifest, weight hash, detections |
| One physical phone over trusted HTTPS | NOT RUN | Mobile record |
| Inspect package contents, licenses and external files | NOT RUN | Two-person review |
| Accept unresolved P2/P3 items | NOT RUN | Release owner |
| Approve local annotated tag | NOT RUN | Release owner |
| Approve remote branch/tag/GitHub Release publication | NOT RUN | Repository owner |

No unchecked human row may be described as passed. The automated gate prepares the candidate; it does not approve hardware, private content, media quality, licensing or publication.

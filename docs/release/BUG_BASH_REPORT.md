# Release-candidate bug-bash report

Target: `0.9.0-rc1`.

This checked-in report is updated from the final `.runtime/release/<run-id>/summary.json` after version synchronization. Until that controlled run is recorded, automated status is **NOT RUN**; the repository does not infer success from script presence.

| Gate | Status | Evidence |
|---|---|---|
| Backend pytest | NOT RUN | Final run required |
| Frontend production build | NOT RUN | Final run required |
| Frontend capture tests | NOT RUN | Final run required |
| Day 14 E2E / browser | NOT RUN | Final run required |
| Failure injection | NOT RUN | Final run required |
| Data integrity | NOT RUN | Final run required |
| Profile C prepare/smoke/stop | NOT RUN | Final run required |
| Release/claim/document consistency | NOT RUN | Final run required |
| Sensitive-data scan | NOT RUN | Final run required |

Open P0: none known. Open P1: none known. Human camera, real-YOLO, phone, media and package-review gates remain `NOT RUN` regardless of the automated result.

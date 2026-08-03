# Competition Screenshot Plan

Automated UI-review screenshots are generated under ignored `artifacts/ui-review/desktop` and `artifacts/ui-review/mobile`. Copy only reviewed formal assets into `docs/assets/screenshots/`; do not claim a formal asset exists until that copy is made and inspected.

## Capture procedure

1. Start Profile C with `scripts/start-demo.ps1 -Profile C -NoBrowser`.
2. Run `scripts/e2e-test.ps1`; the UI review uses synthetic evidence and never opens a physical camera.
3. Review desktop 1440x900, tablet 1024x768, mobile 390x844 and small 360x800 for overflow and obstruction.
4. Select a consistent desktop or mobile set, crop only empty browser chrome, and preserve all status disclosures.
5. Verify no personal data, debug UI, error banner or local path appears.
6. Copy approved files to the formal directory and record source run/commit in the submission checklist.

## Formal asset list

| File | Required state | Required disclosure |
| --- | --- | --- |
| `01-home.png` | Hero, loop and evaluation summary visible | Profile C/Demo banner if captured in C |
| `02-live-lens.png` | Permission purpose and disconnected/ready state | Camera not activated for automated capture |
| `03-analysis.png` | Synthetic image, boxes, object/relation result | Mock engine and 2D relation boundary |
| `04-memory.png` | Populated cards, filters, total | Demo badges where applicable |
| `05-agent.png` | Answer, evidence and limits | Tool-grounded scope and category limit |
| `06-session.png` | Session counters/timeline | Foreground low-frequency behavior |
| `07-devices.png` | Source groups and real persisted counts | Browser state is ephemeral |
| `08-glasses-simulator.png` | Simulator HUD | Exact simulator/hardware disclaimer |
| `09-insights.png` | Non-empty real SQL aggregates | No fabricated empty-data percentage |
| `10-privacy-system.png` | Privacy boundary and readiness | Planned controls marked unimplemented |
| `11-evaluation.png` | Day 15 scorecard | Real YOLO `not_run`, sample limits |

## Acceptance

- Consistent Chinese UI and typography; product terms such as Agent/Mock/YOLO remain intentional.
- No horizontal scroll, clipped primary action, content hidden behind navigation, unexpected layout shift or unreplaced token.
- Simulator, Mock and Demo labels are readable at presentation scale.
- Camera indicator is visible whenever a real capture state is active.
- Resolution and aspect ratio are consistent across the selected presentation set.

Runtime screenshots are evidence for review, not committed product data. See [PITCH_DECK](PITCH_DECK.md) for slide mapping.

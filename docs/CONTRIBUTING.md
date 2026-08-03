# Contributing

## Workflow

1. Read `AGENTS.md`, `docs/PROJECT_STATE.md` and related architecture decisions.
2. Update local `main`, then create a focused `feature/*` branch.
3. Preserve `/api/v1` contracts unless a versioned change is explicitly approved.
4. Keep analyzer failures observable; never substitute Mock silently.
5. Add or update tests for backend behavior and critical frontend flows.
6. Update `docs/PROJECT_STATE.md` when a milestone is completed.

## Local checks

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q

cd ..\frontend
npm run build
npm run test:capture

cd ..
.\scripts\e2e-test.ps1
.\scripts\failure-test.ps1
.\scripts\data-integrity-test.ps1
.\scripts\check-release-docs.ps1
```

Run only the proportionate subset during iteration, then the complete required set before release handoff.

## Code and product rules

- Bounding boxes stay normalized and clamped to `[0, 1]`.
- Keep detector labels in the data model; localize and ordinalize only in presentation.
- Preserve directed inverse relations in the API and collapse duplicates only in frontend display.
- Preserve `near`, `overlaps`, `inside` and `contains` semantics.
- Simulator, Mock and Demo states must remain conspicuous.
- Do not present category retrieval as physical-instance tracking or 2D geometry as depth.
- Do not introduce a large UI framework for isolated styling changes.

## Repository hygiene

Never commit `.env`, credentials, personal media, databases, uploads, model weights, `.venv`, `node_modules`, `dist`, runtime logs/reports, Playwright artifacts or generated `runs/`. Use synthetic or explicitly licensed fixtures. Before committing:

```powershell
git diff --check
git status --short --branch
git ls-files "*.pt" "*.db" "*.sqlite" "*.sqlite3" "*.log" "*.mp4" "*.webm"
```

## Pull request handoff

Describe scope, files, architecture decisions, commands, test/build results, limitations, branch and commit SHA. Include manual hardware/model checks as `passed`, `failed`, or `not_run`; never infer them from Mock automation.

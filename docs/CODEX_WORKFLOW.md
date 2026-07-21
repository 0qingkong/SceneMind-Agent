# ChatGPT + Codex Collaboration Workflow

## Role split

### ChatGPT

- product scope
- architecture and technical decisions
- milestone definition
- prompt/specification design
- code review
- debugging strategy
- competition narrative
- resume and interview extraction

### Codex

- inspect the local repository
- edit multiple files
- install dependencies
- run tests and builds
- fix implementation errors
- produce diffs and commits

## One-task loop

1. ChatGPT defines one milestone and acceptance criteria.
2. Create a feature branch.
3. Give Codex the milestone prompt.
4. Codex edits and tests locally.
5. Review the diff.
6. Push the feature branch.
7. Send ChatGPT:
   - pull request URL, or
   - commit SHA,
   - plus Codex's handoff report.
8. ChatGPT reviews the actual implementation and defines the next milestone.

## Important rule

Do not let ChatGPT and Codex independently edit the same milestone at the same time. Use one executor and one reviewer.

## Handoff template

```text
Repository:
Branch:
Commit SHA:

Summary:
Files changed:
Architecture decisions:
Commands run:
Tests/build:
Known limitations:
Open questions:
```

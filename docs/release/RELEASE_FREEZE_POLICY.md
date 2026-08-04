# Release freeze policy — 0.9.0-rc1

The freeze begins after the automated release-candidate gate is recorded. It protects the competition demo from late scope expansion.

## Allowed changes

- P0/P1 fixes with a reproducer, regression coverage and complete gate rerun.
- Verified P2 fixes only when the workaround is insufficient and regression risk is low.
- Text or release-document corrections that preserve supported claims.
- Accessibility or layout corrections that do not change the core product/API behavior.

## Not allowed

- New models, pages, database technology, authentication, cloud deployment or camera modes.
- New vendor glasses SDK, face recognition, identity/depth claims or unverified metrics.
- Dependency upgrades without a release-blocking reason.
- Broad refactors or schema/API contract changes.
- Unapproved real images, weights, recordings, user data or secrets.
- Automatic local/remote tags, remote branches or GitHub Releases.

## Change control

Every post-gate change must name severity, evidence, affected profile, rollback, reviewer and rerun commands. Update the bug-bash report and checksums when content changes. A human release owner must approve remaining P2/P3 issues, package contents, licensing, hardware/media gates and any publication operation.

The recommended tag remains only a command for later approval; this policy does not authorize executing it.

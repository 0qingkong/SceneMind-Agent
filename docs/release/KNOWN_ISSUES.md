# Known issues — 0.9.0-rc1

No open P0 or P1 defect is known. The following entries are actual unresolved release-candidate issues or external validation gaps; they are not silently promoted to passes.

| Severity | Affected flow | Actual issue | Safe workaround | Planned action | Blocks RC? |
|---|---|---|---|---|---|
| P2 | Agent unsupported question | In Day 15, one centimetre-distance question was misrouted to object count and returned four unsupported evidence IDs. Overall matching remains 17/18 and unsupported handling 66.67%. | Avoid physical-distance questions in the supported demo; state that depth/centimetres are unsupported. | Add a focused unsupported-distance intent regression after preserving this baseline. | No; disclosed workaround |
| P2 validation gap | Profile B real YOLO | No team-approved five-image real-scene set and approval manifest is available in the repository. Formal real-YOLO benchmark is `not_run`. | Use visibly labeled Profile C for emergency delivery; use B only after local human approval. | Team supplies owned/licensed images, checksums and real detection rehearsal evidence. | No for Profile C; blocks claiming B ready |
| P2 validation gap | Profile A / physical phone | Competition camera hardware, permission-denied behavior on target hardware and phone-over-HTTPS have not been manually rehearsed for this candidate. | Use Profile B after approval or Profile C. | Run the release checklist on the competition laptop and one physical phone. | No for Profile C; blocks hardware approval |
| P3 | Python test warnings | Starlette/httpx deprecation and a pytest warning about returning `BytesIO` remain visible in the Day 15 environment. | Warnings do not change asserted results; retain logs. | Update test fixture style and compatible framework versions in a later low-risk maintenance change. | No |
| P3 delivery | Repository licensing | No unified source-code redistribution license is checked in. Third-party dependencies, model weights and media retain separate terms. | Keep delivery local/private until rights-holder review; never bundle weights or unapproved images. | Rights holder selects and approves a repository license and asset distribution record. | Human decision before external distribution |
| Human gate | Final video/media | Screen recording, voice-over, selected screenshots, subtitle visual review and final playback are not supplied. | Use live Profile C and committed presentation sources. | Complete every item in `docs/demo/RECORDING_CHECKLIST.md`. | Blocks claiming final video complete |

Severity uses the release plan definitions. Validation gaps and human gates are labeled separately because unavailable hardware/media is not an automatically observed software pass or failure.

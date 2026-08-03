# Privacy and Trust Boundaries

SceneMind is a local-first competition MVP, not a production privacy platform. Use only images and camera feeds for which the operator has permission.

## Implemented protections

- Camera permission is requested only after an explicit user action and the purpose is explained first.
- The camera-active indicator is always visible while capture is active and cannot be disabled in settings.
- Camera constraints always contain `audio: false`; SceneMind neither records nor uploads audio.
- Browser capture sends compressed still frames, not a continuous video stream.
- Leaving a capture page, disconnecting or encountering an error stops every owned MediaStream track.
- Page-hidden continuous observation pauses by default; background collection is not promised.
- Observation images use UUID filenames; API responses never disclose server filesystem paths.
- JSON export contains metadata but excludes image bytes and server paths.
- Demo evidence is visibly marked, uses deterministic IDs and can be reset without selecting unmarked user data.
- Delete operations require a specific Observation/session; destructive UI actions require confirmation.

## Data stored

SQLite stores Observation metadata, detected object labels/boxes, relations, timestamps, optional location/source/device fields, session counters and save reasons. Original images are stored separately under `SCENE_STORAGE_DIR`. Non-sensitive UI preferences are versioned in browser localStorage.

Backups must treat SQLite plus the image directory as one evidence set. Exporting metadata is not a full image backup.

## Not implemented

- account authentication, authorization or tenant isolation;
- database or image encryption managed by the application;
- automatic retention-period deletion;
- face detection, face blur or face recognition safeguards;
- cloud synchronization or production-grade network isolation;
- consent records for people appearing in images;
- secure erasure guarantees for filesystem/database backups.

The UI labels encryption, face blur and cloud sync as planned rather than active. The detector may output the category `person`; SceneMind does not identify who that person is.

## Operator checklist

1. Use synthetic, self-created or explicitly licensed demo material.
2. Explain the capture purpose before requesting camera access.
3. Keep the API on localhost or an access-controlled trusted HTTPS network.
4. Avoid sensitive locations, screens, documents and bystanders.
5. Stop capture before leaving the station.
6. Export only what is required and protect the exported file.
7. Delete specific evidence through the UI/API; use scoped Demo reset only for generated data.
8. Verify matching database/image backups and disposal policies outside the application.

## Trust statements

Category matches do not prove the same physical object across images. Two-dimensional box geometry does not prove depth, support or metric distance. AI Glasses Simulator is not real hardware. Profile C Mock data is not detector accuracy evidence.

See [API](API.md), [deployment](DEPLOYMENT.md), and [limitations](LIMITATIONS.md).

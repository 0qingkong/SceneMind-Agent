# SceneMind limitations

These limits are product facts, not hidden roadmap promises.

- Spatial relations describe normalized 2D image geometry, not real 3D geometry, depth, support, or physical distance.
- Same-class detections across observations are not confirmed as the same physical object. “Last seen cup” means the latest matching class observation.
- SceneMind performs no face recognition and must not claim a person's identity.
- There is no real AI-glasses hardware or vendor SDK integration. The glasses page is an explicitly labeled simulator.
- Browser camera use depends on user permission, device availability and a secure context; a physical phone normally needs trusted HTTPS.
- YOLO speed and detection quality depend on hardware, model weights, thresholds and the scene/domain. The committed synthetic set does not measure real YOLO accuracy.
- SQLite and local image storage are a single-machine MVP choice, not distributed or multi-user infrastructure.
- Browser capture is low-frequency foreground still-image sampling, not real-time video analysis or reliable background capture.
- No biometric tracking, cross-image re-identification, retention automation, image encryption or face blurring is implemented.

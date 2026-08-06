# SceneMind Spatial OS UI System

SceneMind uses the **Aurora Memory System** visual direction: an airy scientific interface with a blue liquid memory core, restrained motion, evidence-first layouts, and explicit system truth.

## Visual foundation

- Default theme: Aurora Light.
- Optional theme tokens: Deep Space.
- Layout: 76 px expandable desktop rail, compact system strip, responsive five-item mobile dock.
- Typography: system-distributed sans-serif and monospace stacks; no font files are committed.
- Icons: Phosphor Vue, selected for consistent scientific line weight and accessible component output.
- Surfaces: cool-white elevated panels, very light borders, restrained shadows, and one shared aurora palette.

## Memory Core

`MemoryCore` maps real UI states to `idle`, `observing`, `analyzing`, `remembering`, `retrieving`, `target-found`, `warning`, and `offline`.

High and balanced modes use one Canvas 2D context. Reduced mode uses a static fallback. The canvas pauses while the document is hidden, and mounting another core disposes the previous active renderer.

## Motion and accessibility

- Motion uses CSS transitions/keyframes and a capability-detected View Transition wrapper.
- Motion never replaces loading, success, error, camera, or Agent status text.
- `prefers-reduced-motion` forces the reduced visual mode and near-instant transitions.
- Keyboard focus remains visible, navigation is semantic, and mobile controls keep touch-sized targets.

## Product-truth rules

- Profile C and Mock states must remain visible.
- AI Glasses Simulator must never be described as real hardware.
- Spatial relations are two-dimensional bounding-box inferences, not depth or physical distance.
- A category match does not establish real-world object identity.
- Agent answers must retain evidence links and real tool records.
- Evaluation numbers may only come from the Day 15 report.

## Performance budget

- One active Canvas Memory Core at a time.
- No background video or global particle layer.
- Mobile uses balanced mode by default.
- Long lists use simple layout without staggered spring animation.
- No online runtime asset is required for the competition demo.

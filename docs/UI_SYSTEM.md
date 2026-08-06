# SceneMind Spatial OS UI System

SceneMind uses the **Aurora Memory System** visual direction: an airy scientific interface with a volumetric blue memory core, state-driven motion, evidence-first layouts, and explicit system truth.

## Visual foundation

- Default theme: Aurora Light.
- Optional theme tokens: Deep Space.
- Layout: 76 px expandable desktop rail, compact system strip, responsive five-item mobile dock.
- Typography: system-distributed sans-serif and monospace stacks; no font files are committed.
- Icons: Phosphor Vue, selected for consistent scientific line weight and accessible component output.
- Surfaces: cool-white elevated panels, very light borders, restrained shadows, and one shared aurora palette.

## Memory Core

`MemoryCore` maps real UI states to `idle`, `observing`, `analyzing`, `remembering`, `retrieving`, `target-found`, `warning`, and `offline`.

High and balanced modes lazy-load a Three.js/WebGL renderer with a custom liquid-surface shader, Fresnel edge light, additive aura, internal lattice, three-dimensional orbits, deterministic particles, pointer response, and interpolated state palettes. A separate static Canvas is always mounted underneath it, so context creation or loss can never leave an empty core. Reduced mode skips the GPU module entirely.

Each route mounts at most one GPU Memory Core. High mode targets 60 FPS with 210 particles and a 1.8 DPR cap. Balanced mode targets 42 FPS with 92 particles and a 1.25 DPR cap. Rendering pauses while the document is hidden, and component-owned cleanup disposes geometries, materials, listeners, observers, and the WebGL context.

## Motion and accessibility

- Motion uses a coordinated stack: WebGL for the Memory Core, one Canvas ambient field, CSS transitions/keyframes, IntersectionObserver reveals, and one delegated pointer handler for kinetic surfaces.
- The ambient field runs at 36 FPS on capable desktops and 24 FPS with fewer particles on mobile, balanced, or low-memory devices; fine pointers and scroll position add subtle spatial depth without moving content.
- System states drive the strongest motion: analysis activates the spatial reticle, results settle in sequence, Agent retrieval energizes the core, and the glasses simulator uses a restrained optical sweep.
- Scroll reveals and card tilt progressively enhance the interface; content remains visible when observers, fine-pointer input, or animation support are unavailable.
- Motion never replaces loading, success, error, camera, or Agent status text.
- `prefers-reduced-motion` or the manual “精简” control forces the reduced visual mode, static canvases, disabled kinetic surfaces, and near-instant transitions.
- Keyboard focus remains visible, navigation is semantic, and mobile controls keep touch-sized targets.

## Product-truth rules

- Profile C and Mock states must remain visible.
- AI Glasses Simulator must never be described as real hardware.
- Spatial relations are two-dimensional bounding-box inferences, not depth or physical distance.
- A category match does not establish real-world object identity.
- Agent answers must retain evidence links and real tool records.
- Evaluation numbers may only come from the Day 15 report.

## Performance budget

- One active WebGL Memory Core and one low-density ambient Canvas at a time.
- The Three.js renderer is code-split and only requested outside reduced mode.
- No background video or remote runtime asset is required.
- Mobile uses balanced mode by default and receives fewer particles, a lower DPR, and a lower ambient frame rate.
- Long lists use one-shot observer reveals rather than perpetual spring simulations.
- No online runtime asset is required for the competition demo.

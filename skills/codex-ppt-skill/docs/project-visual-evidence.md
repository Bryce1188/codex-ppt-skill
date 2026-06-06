# Visual Evidence

Use visuals as proof that the project exists and works.

## Preferred Visuals

Prioritize:

1. Real app screenshots captured from local run or deployment.
2. User-provided project operation photos.
3. Generated charts, model outputs, dashboards, notebook exports, or terminal logs.
4. Architecture diagrams derived from actual code structure.
5. Static assets from the project only when they clarify identity or UI.

## Capture Rules

- Save screenshots with descriptive names such as `01-home-screen.png`, `02-upload-flow.png`, `03-result-dashboard.png`.
- Capture complete UI states, not cropped fragments, unless the slide is about a specific detail.
- Include at least one "hero proof" screenshot for the title or overview section when the project is visual.
- For dark terminal or log screenshots, crop to the meaningful command/output and increase legibility in the deck.
- Avoid using decorative stock images unless the user explicitly asks for a conceptual style.

## Asset Map

Before generating slides, create an asset map:

```text
path | what it shows | slide candidate | evidence strength | notes
```

Evidence strength:

- `strong`: live screenshot, real output, measured result, or user-supplied project photo.
- `medium`: code-derived diagram, static project asset, documented feature.
- `weak`: placeholder, mockup, conceptual image, inferred visual.

## Missing Screenshots

If runtime screenshots are absent:

- Try to find the run command from project manifests.
- Start the app only when dependencies and environment are reasonable.
- If execution fails, capture the error only if it helps explain setup status.
- Use architecture and workflow diagrams to compensate, while explicitly noting that runtime screenshots were unavailable.

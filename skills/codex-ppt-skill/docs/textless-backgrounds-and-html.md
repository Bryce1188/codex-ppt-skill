# Textless Background Workflow

Use this reference when the deck should use generated images as editable slide backgrounds.

## Goal

Generate visuals with no baked-in words, then place text in HTML or PPT as a separate editable layer.

## When To Use

- The user asks for image-driven PPT slides but wants to add or edit text later.
- The project has few strong screenshots and needs polished visual atmosphere.
- A section divider, title slide, closing slide, or conceptual architecture slide needs a custom background.
- The user specifically asks for `image2`, image generation, no-text images, or HTML backgrounds.

## Image Generation Rules

Use the available Codex image generation tool, referred to by the user as `image2` when applicable. If the runtime exposes it as `imagegen` or `image_gen`, use that tool.

Every background prompt must include:

```text
16:9 presentation slide background, no text, no letters, no numbers, no captions,
no UI labels, no logo, no watermark, no signature, clean empty space for editable text
```

Prompt for composition, not slide copy. Good prompts describe:

- scene or metaphor
- subject matter connected to the project
- camera angle or layout
- lighting and color mood
- empty space location for later text
- visual density and style

Avoid prompts that ask the image model to create:

- words, charts with labels, dashboards with readable UI text, code snippets, equations, brand marks, app names, or pseudo-interfaces
- fake screenshots when real project screenshots are needed as evidence

## Prompt Patterns

Title or chapter background:

```text
16:9 presentation slide background for a software project showcase, abstract but concrete visual metaphor of [project domain], refined editorial lighting, modern technical atmosphere, strong empty space on the left for editable title text, no text, no letters, no numbers, no captions, no logo, no watermark, no signature
```

Feature slide background:

```text
16:9 presentation slide background showing [feature/workflow concept] as a clean visual scene, realistic depth, subtle structure, room on the right side for editable bullet text, no readable interface text, no letters, no numbers, no captions, no logo, no watermark
```

Architecture slide background:

```text
16:9 presentation slide background, elegant abstract system architecture environment with connected layers and data flow shapes, no labels, no text, no letters, no numbers, no logo, no watermark, large clean central area for editable diagram overlays
```

## QA

Before using a generated background:

- Inspect it at full size.
- Reject any image with readable or pseudo-readable text, logo-like marks, watermarks, signatures, or unwanted UI labels.
- Check that it has usable negative space for title/body text.
- Check that important visual details will not be hidden by the text area.
- Prefer regenerating over trying to cover accidental text.

## HTML Background Layering

When creating HTML slides:

- Set the generated image with CSS `background-image`, `background-size: cover`, and `background-position`.
- Keep all titles, bullets, labels, and captions as HTML elements above the background.
- For user-editable drafts, use empty `.text-zone` containers or contenteditable elements. Do not draw text into the bitmap.
- Export screenshots only for preview. Keep the source HTML so text can still be edited.

## PPT Layering

When creating PPTX:

- Place each generated image as the full-slide background layer.
- Add text boxes as native editable PPT text.
- Do not flatten the whole slide to a single screenshot unless the user explicitly asks for image-only slides.
- If the user wants to add text themselves, provide blank or lightly guided text zones and keep the slide backgrounds textless.

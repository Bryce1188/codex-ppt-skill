# Codex PPT Skill

Turn repositories, source code, papers and project evidence into editable presentations with a reusable visual system.

[中文说明](README.md) · [Prompts](skills/codex-ppt-skill/prompts/start-here.md) · [Software example](skills/codex-ppt-skill/examples/software-report/README.md)

![A shared design profile applied to an editable architecture](assets/showcase/software-report/slide_01.png)

## Understand the source

Read the actual GitHub revision, README, entry points, relevant implementation and results. For papers, use the available document conversion tool and inspect original pages for important tables, figures and formulas. Build a source brief and map slide claims to evidence. Keep the authors' reported contributions, the repository's implementation and the user's measured results distinct. Ordinary engineering projects do not need invented research novelty.

See the [source workflow](skills/codex-ppt-skill/docs/source-understanding.md).

## Reuse a visual system

Extract typography, palette roles, title positions, margins, diagram conventions, table styling and image treatment from suitable references. Save one versioned design-profile.json, reuse it when appropriate, and adapt layouts to the content. A new deck does not require another search for background templates.

The default engineering profile uses the same fill for peer nodes and adds no automatic production footer. Process and data pages include the implementation details needed to explain the evidence.

The builder reads this profile. Text and diagram nodes reference style roles; tables, charts and connectors inherit shared defaults. Unexplained changes in headings, colors or diagram styling fail the source check. Deliberate exceptions are recorded. Rendered review is still required.

![The same profile applied to a database diagram](assets/showcase/software-report/slide_02.png)

Both pages use an independently constructed warehouse scenario and the [technical editorial profile](skills/codex-ppt-skill/references/design-profiles/technical-editorial.json). They are not a real user's project or measured result. This engineering example is not a universal palette for every topic. See [style extraction and reuse](skills/codex-ppt-skill/docs/style-library.md).

## Generate and revise native PPTX

Text, charts, tables, simple technical diagrams and images remain separate objects. Deliver the final PPTX and previews, with the generation source, used profile and assets for revision. Change specific pages while keeping the current visual profile, or update the profile for a global redesign.

Complex imported masters, animation and equations depend on host support. Package validation and host rendering do not establish that a file has been opened and edited in both PowerPoint and WPS. State what was actually tested. Whole-slide images are an explicit user choice, not the default editable output.

Humanizer is applied at the content and final-editing stages. Superpowers can support intake, planning and verification when installed; neither replaces source reading, visual design or rendering tools.

## Install

Ask Codex to install skills/codex-ppt-skill from https://github.com/Bryce1188/codex-ppt-skill. Install the skill subdirectory rather than the repository root.

Python 3.10+ supports scanning and structural checks. The bundled native builder requires Node.js and the host-provided @oai/artifact-tool runtime. No alternate slide engine is installed automatically. Screenshots, image generation and document conversion use tools actually available in the environment.

## Checks

```text
python -m unittest discover -s skills/codex-ppt-skill/tests -v
node --test skills/codex-ppt-skill/tests/test_design_profile.mjs
node skills/codex-ppt-skill/scripts/design_profile.mjs --spec skills/codex-ppt-skill/examples/software-report/deck.json
```

With the host runtime and Python, also run test_editable_builder.mjs to inspect native connector attachments, arrow direction, table padding and profile values in exported PPTX. CI excludes the proprietary host runtime and does not judge visual quality.

## Attribution

Based on ningzimu/codex-ppt-skill, retaining the MIT license. The pinned Humanizer snapshot retains its own license and provenance.

This edition independently adapts methods from [ppt-master](https://github.com/hugohe3/ppt-master) for combined content and visual planning, and [slides_maker](https://github.com/addsumtech/slides_maker) for comprehension briefs, claim tracing and visual-system analysis. No upstream templates or export engines were transplanted. See [pinned references and implementation notes](skills/codex-ppt-skill/docs/research-provenance.md).

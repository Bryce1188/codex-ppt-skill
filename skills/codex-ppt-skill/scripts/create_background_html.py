#!/usr/bin/env python3
"""Create an HTML slide scaffold from textless background images."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --slide-w: min(100vw, calc(100vh * 16 / 9));
      --slide-h: calc(var(--slide-w) * 9 / 16);
      --text-color: #ffffff;
      --shadow: 0 2px 18px rgba(0, 0, 0, 0.35);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #111;
      font-family: "Inter", "Segoe UI", Arial, sans-serif;
      color: var(--text-color);
    }}
    .deck {{
      display: grid;
      gap: 32px;
      padding: 32px 0;
      justify-items: center;
    }}
    .slide {{
      position: relative;
      width: var(--slide-w);
      height: var(--slide-h);
      overflow: hidden;
      background-image: var(--bg);
      background-size: cover;
      background-position: center;
      box-shadow: 0 18px 60px rgba(0, 0, 0, 0.35);
    }}
    .shade {{
      position: absolute;
      inset: 0;
      background: linear-gradient(90deg, rgba(0,0,0,.46), rgba(0,0,0,.12) 55%, rgba(0,0,0,.02));
      pointer-events: none;
    }}
    .text-zone {{
      position: absolute;
      left: 7%;
      top: 16%;
      width: 42%;
      min-height: 26%;
      padding: 20px;
      outline: 1px dashed rgba(255,255,255,.35);
      border-radius: 4px;
      text-shadow: var(--shadow);
    }}
    .text-zone:empty::before {{
      content: "";
    }}
    .text-zone:focus {{
      outline: 2px solid rgba(255,255,255,.75);
      background: rgba(0,0,0,.12);
    }}
    @media print {{
      body {{ background: white; }}
      .deck {{ display: block; padding: 0; }}
      .slide {{
        width: 100vw;
        height: 56.25vw;
        page-break-after: always;
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
  <main class="deck">
{slides}
  </main>
</body>
</html>
"""


SLIDE_TEMPLATE = """    <section class="slide" style="--bg: url('{image_uri}');">
      <div class="shade"></div>
      <div class="text-zone" contenteditable="true" aria-label="Editable text zone"></div>
    </section>"""


def make_uri(path: Path, html_path: Path) -> str:
    try:
        rel = path.resolve().relative_to(html_path.parent.resolve())
        return html.escape(rel.as_posix())
    except ValueError:
        return html.escape(path.resolve().as_uri())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", help="Background image paths")
    parser.add_argument("--out", required=True, help="Output HTML file")
    parser.add_argument("--title", default="Project PPT Background Draft", help="HTML title")
    args = parser.parse_args()

    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    image_paths = [Path(image).expanduser().resolve() for image in args.images]

    missing = [str(path) for path in image_paths if not path.exists()]
    if missing:
        raise SystemExit("Missing image files:\n" + "\n".join(missing))

    slides = "\n".join(
        SLIDE_TEMPLATE.format(image_uri=make_uri(path, out))
        for path in image_paths
    )
    out.write_text(
        HTML_TEMPLATE.format(title=html.escape(args.title), slides=slides),
        encoding="utf-8",
    )
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

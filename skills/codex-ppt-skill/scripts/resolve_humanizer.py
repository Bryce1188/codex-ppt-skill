#!/usr/bin/env python3
"""Find real Humanizer instructions. No network, installs, or text rewriting."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import os
import re
from pathlib import Path


def inspect_entry(candidate: Path) -> dict:
    entry = candidate / "SKILL.md" if candidate.is_dir() else candidate
    text = entry.read_text(encoding="utf-8-sig")
    if not re.search(r"(?m)^name: *humanizer *$", text):
        raise ValueError(f"Not a humanizer skill: {entry}")
    chinese = entry.parent / "references/chinese-editing.md"
    if not chinese.is_file():
        raise ValueError(f"Missing Chinese editing reference: {chinese}")
    return {"skill_path": str(entry.resolve()), "chinese_reference": str(chinese.resolve()),
            "sha256": hashlib.sha256(entry.read_bytes()).hexdigest(),
            "chinese_sha256": hashlib.sha256(chinese.read_bytes()).hexdigest()}


def resolve(skill_root: Path, explicit: Path | None = None, installed_roots=None, bundled_only=False) -> dict:
    if explicit is not None:
        return {**inspect_entry(explicit.expanduser()), "resolved_from": "explicit"}
    if installed_roots is None:
        installed_roots = [Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "skills",
                           Path.home() / ".agents/skills", Path.home() / ".claude/skills"]
    candidates = [("sibling", skill_root.parent / "humanizer")]
    candidates += [("installed", Path(folder) / "humanizer") for folder in installed_roots]
    rejected = []
    if not bundled_only:
        for origin, candidate in candidates:
            if not candidate.exists():
                continue
            try:
                return {**inspect_entry(candidate), "resolved_from": origin, "skipped": rejected}
            except (OSError, ValueError) as exc:
                rejected.append(str(exc))
    vendor = skill_root / "references/humanizer"
    lock = json.loads((vendor / "provenance.json").read_text(encoding="utf-8"))
    expected = {"humanizer.md", "references/chinese-editing.md", "LICENSE"}
    if set(lock["files"]) != expected:
        raise ValueError("Bundled Humanizer manifest must cover the entry, Chinese reference and license")
    for name, digest in lock["files"].items():
        if hashlib.sha256((vendor / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Bundled Humanizer checksum mismatch: {name}")
    return {**inspect_entry(vendor / "humanizer.md"), "resolved_from": "bundled",
            "repository": lock["repository"], "commit": lock["commit"], "skipped": rejected}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--path", type=Path, help="Explicit Humanizer directory or instruction file")
    group.add_argument("--bundled", action="store_true", help="Use the verified snapshot for reproducible runs")
    args = parser.parse_args()
    try:
        result = resolve(Path(__file__).resolve().parent.parent, args.path, bundled_only=args.bundled)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Cannot load Humanizer: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

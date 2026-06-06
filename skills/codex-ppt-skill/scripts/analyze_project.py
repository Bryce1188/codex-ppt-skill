#!/usr/bin/env python3
"""Create a first-pass evidence inventory for a project-report PPT."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}

HIGH_SIGNAL_NAMES = {
    "readme",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "settings.gradle",
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"}
DOC_EXTS = {".md", ".mdx", ".rst", ".txt", ".ipynb", ".pdf", ".docx", ".pptx"}
CODE_EXTS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".vue",
    ".svelte",
}


def is_ignored(path: Path) -> bool:
    return any(part.lower() in IGNORE_DIRS for part in path.parts)


def iter_files(root: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    for current_root, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]
        current = Path(current_root)
        for name in names:
            path = current / name
            if is_ignored(path.relative_to(root)):
                continue
            files.append(path)
            if len(files) >= max_files:
                return files
    return files


def safe_read(path: Path, limit: int = 6000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def detect_frameworks(files: list[Path], root: Path) -> list[str]:
    names = {rel(path, root).lower() for path in files}
    frameworks: set[str] = set()

    package = root / "package.json"
    package_json = load_json(package) if package.exists() else None
    deps: dict[str, Any] = {}
    if package_json:
        for key in ("dependencies", "devDependencies"):
            deps.update(package_json.get(key, {}))
        if "react" in deps:
            frameworks.add("React")
        if "next" in deps:
            frameworks.add("Next.js")
        if "vue" in deps:
            frameworks.add("Vue")
        if "svelte" in deps:
            frameworks.add("Svelte")
        if "vite" in deps:
            frameworks.add("Vite")
        if "express" in deps:
            frameworks.add("Express")
        if "nestjs" in deps or "@nestjs/core" in deps:
            frameworks.add("NestJS")
        if "electron" in deps:
            frameworks.add("Electron")

    pyproject = safe_read(root / "pyproject.toml").lower() if (root / "pyproject.toml").exists() else ""
    requirements = "\n".join(
        safe_read(path).lower()
        for path in root.glob("requirements*.txt")
    )
    py_text = pyproject + "\n" + requirements
    if "fastapi" in py_text:
        frameworks.add("FastAPI")
    if "flask" in py_text:
        frameworks.add("Flask")
    if "django" in py_text:
        frameworks.add("Django")
    if "streamlit" in py_text:
        frameworks.add("Streamlit")
    if "gradio" in py_text:
        frameworks.add("Gradio")
    if "pandas" in py_text:
        frameworks.add("Pandas")
    if "torch" in py_text or "pytorch" in py_text:
        frameworks.add("PyTorch")
    if "tensorflow" in py_text:
        frameworks.add("TensorFlow")
    if "sklearn" in py_text or "scikit-learn" in py_text:
        frameworks.add("scikit-learn")

    if "dockerfile" in names or any(name.startswith("docker-compose") for name in names):
        frameworks.add("Docker")
    if "go.mod" in names:
        frameworks.add("Go")
    if "cargo.toml" in names:
        frameworks.add("Rust")
    if "pom.xml" in names or "build.gradle" in names:
        frameworks.add("Java/JVM")

    return sorted(frameworks)


def extract_package_scripts(root: Path) -> dict[str, str]:
    package = root / "package.json"
    package_json = load_json(package) if package.exists() else None
    if not package_json:
        return {}
    scripts = package_json.get("scripts", {})
    return {str(k): str(v) for k, v in scripts.items()} if isinstance(scripts, dict) else {}


def find_candidate_commands(root: Path, frameworks: list[str]) -> list[str]:
    commands: list[str] = []
    scripts = extract_package_scripts(root)
    for key in ("dev", "start", "preview", "serve", "build", "test"):
        if key in scripts:
            commands.append(f"npm run {key}  # {scripts[key]}")
    if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
        if "Streamlit" in frameworks:
            commands.append("streamlit run <entry>.py")
        if "Gradio" in frameworks:
            commands.append("python <app>.py")
        if "FastAPI" in frameworks:
            commands.append("uvicorn <module>:app --reload")
        if "Flask" in frameworks:
            commands.append("flask run")
        commands.append("python -m pytest")
    if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
        commands.append("docker compose up")
    if (root / "Dockerfile").exists():
        commands.append("docker build -t project-demo .")
    return commands


def classify_files(files: list[Path], root: Path) -> dict[str, Any]:
    ext_counts = Counter(path.suffix.lower() or "[no extension]" for path in files)
    code = [path for path in files if path.suffix.lower() in CODE_EXTS]
    images = [path for path in files if path.suffix.lower() in IMAGE_EXTS]
    docs = [
        path
        for path in files
        if path.suffix.lower() in DOC_EXTS or path.name.lower().startswith("readme")
    ]
    high_signal = [
        path
        for path in files
        if path.name.lower() in HIGH_SIGNAL_NAMES
        or path.name.lower().startswith("readme")
        or "/docs/" in f"/{rel(path, root).lower()}"
    ]
    return {
        "total_files_scanned": len(files),
        "extensions": dict(ext_counts.most_common(30)),
        "code_files": [rel(path, root) for path in code[:80]],
        "documentation_files": [rel(path, root) for path in docs[:60]],
        "image_files": [rel(path, root) for path in images[:80]],
        "high_signal_files": [rel(path, root) for path in high_signal[:80]],
    }


def read_doc_snippets(root: Path, files: list[Path]) -> list[dict[str, str]]:
    snippets: list[dict[str, str]] = []
    candidates = [
        path
        for path in files
        if path.name.lower().startswith("readme")
        or path.suffix.lower() in {".md", ".mdx", ".rst", ".txt"}
    ]
    for path in candidates[:12]:
        text = safe_read(path, 2500)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            snippets.append({"path": rel(path, root), "snippet": text[:900]})
    return snippets


def analyze(root: Path, max_files: int) -> dict[str, Any]:
    files = iter_files(root, max_files=max_files)
    frameworks = detect_frameworks(files, root)
    project_name = root.name
    package_json = load_json(root / "package.json") if (root / "package.json").exists() else None
    if package_json and package_json.get("name"):
        project_name = str(package_json["name"])

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(root),
        "project_name": project_name,
        "frameworks_and_stack_signals": frameworks,
        "candidate_commands": find_candidate_commands(root, frameworks),
        "package_scripts": extract_package_scripts(root),
        "files": classify_files(files, root),
        "doc_snippets": read_doc_snippets(root, files),
        "next_questions_for_deck": [
            "Who is the audience for this presentation?",
            "Which screenshots prove the project is running?",
            "What is the single strongest implementation highlight?",
            "Are there measured results, evaluation scores, user feedback, or demo outputs?",
            "What should be presented as future work rather than completed work?",
        ],
    }


def write_markdown(report: dict[str, Any], out_path: Path) -> None:
    files = report["files"]
    lines: list[str] = []
    lines.append(f"# Project PPT Evidence Inventory: {report['project_name']}")
    lines.append("")
    lines.append(f"- Root: `{report['project_root']}`")
    lines.append(f"- Generated: {report['generated_at']}")
    lines.append(f"- Stack signals: {', '.join(report['frameworks_and_stack_signals']) or 'None detected'}")
    lines.append(f"- Files scanned: {files['total_files_scanned']}")
    lines.append("")
    lines.append("## Candidate Commands")
    if report["candidate_commands"]:
        for command in report["candidate_commands"]:
            lines.append(f"- `{command}`")
    else:
        lines.append("- No obvious run/build/test commands detected.")
    lines.append("")
    lines.append("## High-Signal Files")
    for path in files["high_signal_files"][:40]:
        lines.append(f"- `{path}`")
    if not files["high_signal_files"]:
        lines.append("- None detected.")
    lines.append("")
    lines.append("## Visual Assets")
    for path in files["image_files"][:40]:
        lines.append(f"- `{path}`")
    if not files["image_files"]:
        lines.append("- No image assets found in scanned files.")
    lines.append("")
    lines.append("## Documentation Snippets")
    for item in report["doc_snippets"]:
        lines.append(f"### `{item['path']}`")
        lines.append(item["snippet"])
        lines.append("")
    if not report["doc_snippets"]:
        lines.append("- No readable documentation snippets found.")
    lines.append("")
    lines.append("## Deck Questions")
    for question in report["next_questions_for_deck"]:
        lines.append(f"- {question}")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", help="Project folder to scan")
    parser.add_argument("--out", default=".", help="Output folder for report files")
    parser.add_argument("--max-files", type=int, default=2500, help="Maximum files to scan")
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Project root is not a directory: {root}")

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = analyze(root, max_files=args.max_files)
    json_path = out_dir / "project-ppt-evidence.json"
    md_path = out_dir / "project-ppt-evidence.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report, md_path)

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Check requirement coverage and references, not factual truth or visual quality."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def derive_agenda_items(slides: list) -> list:
    """Derive chapter starts from final slide order, never from typed page numbers."""
    items, seen, previous = [], set(), None
    for page in slides:
        if not isinstance(page, dict):
            raise ValueError("Agenda: slides must be objects")
        if page.get("role") in ("cover", "agenda"):
            continue
        section = page.get("section")
        if not isinstance(section, str) or not section.strip():
            raise ValueError("Agenda: each body slide needs a nonempty section")
        if section != section.strip():
            raise ValueError("Agenda: section names must not have surrounding whitespace")
        number = page.get("number")
        if type(number) is not int or number < 1:
            raise ValueError("Agenda: positive integer slide numbers required")
        if section != previous:
            if section in seen:
                raise ValueError("Agenda: a chapter reappears after another chapter: " + section)
            items.append({"title": section, "start_slide": number})
            seen.add(section)
            previous = section
    if not items:
        raise ValueError("Agenda: no body chapters found")
    return items


def validate(plan: dict, base_dir: Path) -> dict:
    errors, gaps = [], []
    def need(condition, message):
        if not condition:
            errors.append(message)
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    def source_exists(value):
        return text(value) and (value.startswith(("https://", "http://", "user:")) or
                                (base_dir / value.split("#", 1)[0]).is_file())
    def indexed(name):
        values = plan.get(name, [])
        need(isinstance(values, list), f"{name} must be a list")
        found = {}
        for item in values if isinstance(values, list) else []:
            if not isinstance(item, dict) or not text(item.get("id")):
                errors.append(f"{name}: each item needs an id")
                continue
            key = item["id"]
            need(key not in found, f"Duplicate {name} id: {key}")
            need(source_exists(item.get("source")), f"{key}: missing or unresolvable source")
            found[key] = item
        return found
    need(text(plan.get("title")), "title is required")
    requirements, evidence = indexed("requirements"), indexed("evidence")
    for key, item in requirements.items():
        need(text(item.get("text")), f"{key}: requirement text is required")
    for key, item in evidence.items():
        need(text(item.get("claim")), f"{key}: evidence claim is required")
        need(item.get("status") in {"documented", "implemented", "verified", "missing"}, f"{key}: invalid evidence status")
    slides = plan.get("slides", [])
    if not isinstance(slides, list):
        slides = []
    expected = plan.get("expected_slide_count")
    need(type(expected) is int and expected > 0 and len(slides) == expected, "Total slide count differs from expected_slide_count")
    covered = set()
    for index, page in enumerate(slides, 1):
        if not isinstance(page, dict):
            errors.append(f"Slide {index}: expected an object")
            continue
        need(page.get("number") == index, f"Slide {index}: numbering must be consecutive")
        need(text(page.get("title")), f"Slide {index}: title is required")
        refs, proofs, notes = page.get("requirement_ids", []), page.get("evidence_ids", []), page.get("gap_notes", [])
        if not all(isinstance(v, list) and all(text(x) for x in v) for v in (refs, proofs, notes)):
            errors.append(f"Slide {index}: references and gap_notes must be string lists")
            continue
        covered.update(refs)
        need(set(refs) <= requirements.keys(), f"Slide {index}: unknown requirement id")
        need(set(proofs) <= evidence.keys(), f"Slide {index}: unknown evidence id")
        absent = not proofs or any(evidence.get(k, {}).get("status") == "missing" for k in proofs)
        if refs and absent:
            need(bool(notes), f"Slide {index}: required content without evidence needs a visible gap note")
        gaps.extend({"slide": index, "note": note} for note in notes)
    need(requirements.keys() <= covered, f"Uncovered requirements: {sorted(requirements.keys() - covered)}")
    agenda_pages = [page for page in slides if isinstance(page, dict) and page.get("role") == "agenda"]
    if agenda_pages:
        need(len(agenda_pages) == 1, "Exactly one global agenda slide is supported")
        try:
            expected_items = derive_agenda_items(slides)
            for page in agenda_pages:
                need(page.get("agenda_items") == expected_items,
                     "Agenda items differ from chapter order or starting pages; run sync_agenda.py")
        except ValueError as exc:
            errors.append(str(exc))
    background = plan.get("background", {})
    need(isinstance(background, dict), "background must be an object")
    if isinstance(background, dict):
        mode, selected = background.get("mode"), background.get("selected")
        need(mode in {"auto", "choose", "provided"}, "Invalid background mode")
        need(text(selected), "A background/style selection is required before production")
        if mode == "choose":
            candidates = background.get("candidates", [])
            candidates = candidates if isinstance(candidates, list) else []
            candidates = [c for c in candidates if isinstance(c, dict)]
            need(2 <= len(candidates) <= 3, "Background choice needs 2–3 actual preview candidates")
            need(selected in [c.get("id") for c in candidates], "Selected background must match a candidate id")
            for candidate in candidates:
                preview = candidate.get("preview")
                need(text(preview) and (base_dir / preview).is_file(), "Background preview file is missing")
            need(text(background.get("decision_source")), "User background choice has not been recorded")
        if mode == "provided":
            need(source_exists(selected), "Provided background or template does not exist")
    return {"ready_for_production": not errors, "errors": errors, "visible_gaps": gaps,
            "requirements_addressed": len(requirements.keys() & covered), "requirement_count": len(requirements),
            "scope": "Structural coverage only. A mapped requirement or a recorded check does not prove completion or factual accuracy."}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        if not isinstance(plan, dict):
            raise ValueError("Plan must be an object")
        report = validate(plan, args.plan.resolve().parent)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Cannot validate plan: {exc}\n")
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if report["ready_for_production"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

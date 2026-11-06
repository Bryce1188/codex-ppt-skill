#!/usr/bin/env python3
"""Sync an existing agenda page to the final numbered chapter plan."""
import argparse
import json
from pathlib import Path
from validate_plan import derive_agenda_items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        slides = plan["slides"]
        if not isinstance(slides, list) or any(not isinstance(p, dict) or type(p.get("number")) is not int or p["number"] != i for i, p in enumerate(slides, 1)):
            raise ValueError("Slide numbering must be consecutive before syncing")
        if type(plan.get("expected_slide_count")) is not int or plan["expected_slide_count"] != len(slides):
            raise ValueError("expected_slide_count must include the agenda page")
        pages = [p for p in slides if p.get("role") == "agenda"]
        if len(pages) != 1:
            raise ValueError("Add exactly one role: agenda page to the plan first")
        pages[0]["agenda_items"] = derive_agenda_items(slides)
        if args.out.exists():
            raise ValueError("Output already exists; choose a new path")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + "\n")
    print("Agenda synchronized: " + str(args.out))


if __name__ == "__main__":
    main()

"""Small, reproducible demonstration project. All sample records are synthetic."""
import csv
import json
import math
import sys
from pathlib import Path


def summarize(scores):
    if not scores or any(not math.isfinite(x) or not 0 <= x <= 100 for x in scores):
        raise ValueError("Expected nonempty finite scores between 0 and 100")
    bands = [(0, 60), (60, 70), (70, 80), (80, 90), (90, 101)]
    passed = sum(x >= 60 for x in scores)
    return {"count": len(scores), "mean": round(sum(scores) / len(scores), 2),
            "passed": passed, "pass_rate_percent": round(passed / len(scores) * 100, 2),
            "band_labels": ["<60", "60-69", "70-79", "80-89", "90-100"],
            "band_counts": [sum(low <= x < high for x in scores) for low, high in bands]}


if __name__ == "__main__":
    with Path(sys.argv[1]).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    print(json.dumps(summarize([float(row["score"]) for row in rows]), indent=2))

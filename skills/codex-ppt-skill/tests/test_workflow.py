import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded

resolver = module("resolve_humanizer")
planner = module("validate_plan")
analyzer = module("analyze_project")

class HumanizerTests(unittest.TestCase):
    def test_pinned_snapshot_integrity_and_reference(self):
        result = resolver.resolve(ROOT, bundled_only=True)
        self.assertEqual(result["resolved_from"], "bundled")
        self.assertTrue(Path(result["chinese_reference"]).is_file())
        self.assertEqual(hashlib.sha256(Path(result["skill_path"]).read_bytes()).hexdigest(), result["sha256"])

    def test_explicit_missing_path_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                resolver.resolve(ROOT, Path(directory) / "missing")

    def test_sibling_precedes_installed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            sibling = base / "humanizer"
            (sibling / "references").mkdir(parents=True)
            (sibling / "SKILL.md").write_text("---\nname: humanizer\n---\nCustom rules", encoding="utf-8")
            (sibling / "references/chinese-editing.md").write_text("Chinese rules", encoding="utf-8")
            result = resolver.resolve(base / "ppt", installed_roots=[base / "unused"])
            self.assertEqual(result["resolved_from"], "sibling")
            self.assertEqual(Path(result["skill_path"]), (sibling / "SKILL.md").resolve())

    def test_tampered_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory)
            shutil.copytree(ROOT / "references/humanizer", skill / "references/humanizer")
            (skill / "references/humanizer/humanizer.md").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                resolver.resolve(skill, bundled_only=True)

class PlanTests(unittest.TestCase):
    def setUp(self):
        self.base = ROOT / "examples/course-report"
        self.plan = json.loads((self.base / "presentation-plan.json").read_text(encoding="utf-8"))

    def check(self):
        return planner.validate(self.plan, self.base)

    def test_example_has_full_requirement_coverage(self):
        result = self.check()
        self.assertTrue(result["ready_for_production"], result)
        self.assertEqual(result["requirements_addressed"], 4)
        self.assertTrue(result["visible_gaps"])

    def test_missing_requirement_is_blocked(self):
        self.plan["requirements"].append({"id":"R5", "text":"部署记录", "source":"user:teacher"})
        self.assertFalse(self.check()["ready_for_production"])

    def test_unknown_evidence_id_is_blocked(self):
        self.plan["slides"][1]["evidence_ids"] = ["invented"]
        self.assertFalse(self.check()["ready_for_production"])

    def test_missing_source_is_blocked(self):
        self.plan["evidence"][0]["source"] = "not-present.csv"
        self.assertFalse(self.check()["ready_for_production"])

    def test_missing_evidence_requires_visible_gap(self):
        self.plan["slides"][1]["evidence_ids"] = []
        self.assertFalse(self.check()["ready_for_production"])
        self.plan["slides"][1]["gap_notes"] = ["未提供运行证据"]
        result = self.check()
        self.assertTrue(result["ready_for_production"], result)
        self.assertIn({"slide":2, "note":"未提供运行证据"}, result["visible_gaps"])

    def test_user_choice_is_not_inferred(self):
        self.plan["background"] = {"mode":"choose", "selected":None, "candidates":[]}
        self.assertFalse(self.check()["ready_for_production"])

    def test_user_choice_needs_previews_and_response(self):
        with tempfile.TemporaryDirectory() as directory:
            previews = [Path(directory) / f"{name}.png" for name in ["a", "b"]]
            for preview in previews:
                preview.write_bytes(b"preview existence fixture")
            self.plan["background"] = {"mode":"choose", "selected":"b", "candidates":[{"id":name,"preview":str(preview)} for name,preview in zip(["a","b"],previews)]}
            self.assertFalse(self.check()["ready_for_production"])
            self.plan["background"]["decision_source"] = "user:选择 B"
            self.assertTrue(self.check()["ready_for_production"])

    def test_count_mismatch_is_blocked(self):
        self.plan["expected_slide_count"] = 7
        self.assertFalse(self.check()["ready_for_production"])

class EvidenceTests(unittest.TestCase):
    def test_data_sources_are_inventory_candidates(self):
        report = analyzer.analyze(ROOT / "examples/course-report/project", 100)
        self.assertIn("scores.csv", report["files"]["data_files"])
        self.assertIn("results.json", report["files"]["data_files"])
        self.assertFalse(report["scan_limit_reached"])

    def test_scan_limit_is_disclosed(self):
        report = analyzer.analyze(ROOT / "examples/course-report/project", 1)
        self.assertTrue(report["scan_limit_reached"])

if __name__ == "__main__":
    unittest.main()

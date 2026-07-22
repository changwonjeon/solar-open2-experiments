from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from quality_eval import evaluate, normalize_locator, passes_threshold


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class FrozenFixtureTests(unittest.TestCase):
    def test_manifest_hashes_match(self) -> None:
        manifest = FIXTURES / "FROZEN_MANIFEST.sha256"
        entries = manifest.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(entries), 16)
        for entry in entries:
            expected, relative_path = entry.split("  ", 1)
            payload = (ROOT / relative_path).read_bytes()
            actual = hashlib.sha256(payload).hexdigest()
            self.assertEqual(actual, expected, relative_path)

    def test_corpus_has_ten_unique_existing_papers(self) -> None:
        corpus = json.loads((FIXTURES / "throughput/papers.json").read_text())
        papers = corpus["papers"]
        paper_ids = [paper["paper_id"] for paper in papers]
        self.assertEqual(corpus["assigned_count"], 10)
        self.assertEqual(len(papers), 10)
        self.assertEqual(len(set(paper_ids)), 10)
        for paper in papers:
            self.assertTrue((ROOT / paper["paper_path"]).is_file())
            self.assertTrue(paper["evidence_paths"])
            for evidence_path in paper["evidence_paths"]:
                self.assertTrue((ROOT / evidence_path).is_file())

    def test_gold_is_balanced_and_complete(self) -> None:
        gold = json.loads((FIXTURES / "quality/gold.json").read_text())
        findings = gold["findings"]
        counts: dict[str, dict[str, int]] = {}
        for finding in findings:
            counts.setdefault(finding["paper_id"], {"strength": 0, "weakness": 0})
            counts[finding["paper_id"]][finding["finding_type"]] += 1
            self.assertTrue(finding["locator"].strip())
            self.assertTrue(finding["text"].strip())
        self.assertTrue(gold["frozen_before_agent_execution"])
        self.assertEqual(len(findings), gold["finding_count"])
        self.assertEqual(len(counts), 10)
        self.assertTrue(all(value == {"strength": 1, "weakness": 1} for value in counts.values()))

    def test_location_normalization_is_narrow(self) -> None:
        self.assertEqual(normalize_locator("  TABLE 1   (Page 3) "), "table 1 (page 3)")
        self.assertNotEqual(normalize_locator("Table 1 (page 3)"), normalize_locator("Results (page 3)"))
        self.assertNotEqual(normalize_locator("Table 1 (page 3)"), normalize_locator("Table 1 (page 4)"))

    def test_frozen_baseline_metrics(self) -> None:
        gold = json.loads((FIXTURES / "quality/gold.json").read_text())
        baseline = json.loads((FIXTURES / "quality/naive-single-pass.json").read_text())
        actual = evaluate(baseline["predictions"], gold["findings"])
        expected = baseline["expected_metrics"]
        for name in ("tp", "fp", "fn"):
            self.assertEqual(actual[name], expected[name], name)
        for name in ("precision", "recall", "f1", "paper_coverage", "location_accuracy"):
            self.assertAlmostEqual(actual[name], expected[name], places=6, msg=name)
        self.assertFalse(passes_threshold(actual, float(actual["f1"])))

    def test_duplicate_prediction_is_false_positive(self) -> None:
        gold = json.loads((FIXTURES / "quality/gold.json").read_text())["findings"]
        duplicate = [dict(gold[0]), dict(gold[0])]
        metrics = evaluate(duplicate, gold)
        self.assertEqual(metrics["tp"], 1)
        self.assertEqual(metrics["fp"], 1)
        self.assertEqual(metrics["fn"], 19)

    def test_perfect_candidate_passes_frozen_threshold(self) -> None:
        gold = json.loads((FIXTURES / "quality/gold.json").read_text())["findings"]
        baseline = json.loads((FIXTURES / "quality/naive-single-pass.json").read_text())
        baseline_metrics = evaluate(baseline["predictions"], gold)
        candidate_metrics = evaluate(gold, gold)
        self.assertTrue(passes_threshold(candidate_metrics, float(baseline_metrics["f1"])))

    def test_adjacent_location_does_not_match(self) -> None:
        gold = json.loads((FIXTURES / "quality/gold.json").read_text())["findings"]
        prediction = dict(gold[0])
        prediction["locator"] = "Table 1 (page 4)"
        metrics = evaluate([prediction], [gold[0]], paper_count=1)
        self.assertEqual(metrics["tp"], 0)
        self.assertEqual(metrics["fp"], 1)
        self.assertEqual(metrics["fn"], 1)


if __name__ == "__main__":
    unittest.main()

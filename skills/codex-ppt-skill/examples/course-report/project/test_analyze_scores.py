import unittest
from analyze_scores import summarize


class ScoreTests(unittest.TestCase):
    def test_known_statistics(self):
        data = summarize([0, 60, 100])
        self.assertEqual(data["passed"], 2)
        self.assertEqual(data["band_counts"], [1, 1, 0, 0, 1])
        self.assertEqual(data["mean"], 53.33)

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            summarize([])

    def test_invalid_scores(self):
        for score in [-1, 101, float("nan"), float("inf")]:
            with self.subTest(score=score), self.assertRaises(ValueError):
                summarize([score])

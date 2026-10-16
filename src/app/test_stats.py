"""Tests for app/stats.py.  Run:  python3 -m unittest app/test_stats.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stats  # noqa: E402


def q(sub, correct, **kw):
    return {"subtopic": sub, "correct": correct, **kw}


class StatsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".claude/commands").mkdir(parents=True)
        (self.root / ".claude/commands/fexam.md").write_text(
            "**Agentic loop (1.1)**\n- x\n**Claude Code hooks (3.8)**\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, data):
        (self.root / name).write_text(json.dumps(data), encoding="utf-8")

    def test_empty_when_no_history(self):
        d = stats.compute(self.root, "fexam")
        self.assertTrue(d["empty"])
        self.assertIsNone(d["projection"]["score"])
        self.assertFalse(d["available"]["fexam"])

    def test_legacy_records_and_ordering(self):
        self.write("fexam-performance.json", {"sessions": [
            {"date": "2026-09-02", "difficulty": "hard", "domains": "targeted:3.8", "score": 1, "total": 2,
             "questions": [q("3.8", True), q("3.8", False, trick="exit1", trick_description="old")]},
            {"date": "2026-09-01", "difficulty": "hard", "domain_filter": "all", "score": 2, "total": 2,
             "questions": [q("1.1", True, domain="D1", subtopic_label="Agentic loop"),
                           q("3.8", False, domain="D3", trick="exit1", trick_description="older")]},
            {"date": "2026-09-02", "difficulty": "exam", "domain_filter": "D1", "score": 0, "total": 1,
             "questions": [q("1.1", False, domain="D1", trick="exit1", trick_description="newest")]},
        ]})
        d = stats.compute(self.root, "fexam")
        # domain inferred from subtopic for legacy questions
        d3 = next(x for x in d["domains"] if x["id"] == "D3")
        self.assertEqual((d3["correct"], d3["total"]), (1, 3))
        # chronological, ties by file order; recent is newest first
        self.assertEqual([h["date"] for h in d["history"]], ["2026-09-01", "2026-09-02", "2026-09-02"])
        self.assertEqual(d["recent"][0]["difficulty"], "exam")
        self.assertEqual(d["history"][1]["focus"], "targeted:3.8")
        # label from the command file when history has none
        sub = {s["id"]: s for s in d["subtopics"]}
        self.assertEqual(sub["3.8"]["label"], "Claude Code hooks")
        self.assertTrue(sub["3.8"]["weak"])
        # traps: count + latest description in date order
        self.assertEqual(d["traps"], [{"label": "exit1", "count": 3, "description": "newest"}])
        # only 2 of 5 domains covered -> no verdict
        self.assertIsNone(d["projection"]["verdict"])
        self.assertEqual(d["projection"]["weightCovered"], 47)

    def test_projection_and_verdict(self):
        qs = [q(f"{i}.1", True, domain=f"D{i}") for i in range(1, 6)]
        self.write("fexam-performance.json", {"sessions": [
            {"date": "2026-10-01", "difficulty": "hard", "domain_filter": "all", "score": 5, "total": 5, "questions": qs}]})
        d = stats.compute(self.root, "fexam")
        self.assertEqual(d["projection"]["score"], 1000)
        self.assertEqual(d["projection"]["verdict"], "PASS")

    def test_score_report_tiers_and_edges(self):
        self.write("fexam-scorereport.json", {
            "attempt_date": "2026-09-11", "score": 667, "passing_score": 720, "retire_after_correct": 2,
            "objectives": [
                {"id": "O12", "text": "PostToolUse hooks: enforce quality", "exam_pct": 0, "tier": 2,
                 "edges": [{"id": "O12.e1", "text": "a"}, {"id": "O12.e2", "text": "b"}]},
                {"id": "O3", "text": "Session resumption", "exam_pct": 67, "edges": []},
                {"id": "O1", "text": "Safeguards", "exam_pct": 100, "edges": [{"id": "O1.e1", "text": "x"}]},
            ]})
        self.write("fexam-performance.json", {"sessions": [{"date": "2026-10-01", "difficulty": "hard",
            "domain_filter": "all", "score": 3, "total": 3, "questions": [
                q("3.8", True, objective="O12", edge="O12.e1"),
                q("3.8", True, objective="O12", edge="O12.e1"),
                q("3.8", True, objective="O12", edge="O12.e2")]}]})
        r = stats.compute(self.root, "fexam")["scoreReport"]
        o = {x["id"]: x for x in r["objectives"]}
        self.assertEqual(o["O12"]["tier"], 1)          # exam_pct wins over stored tier
        self.assertEqual(o["O12"]["label"], "PostToolUse hooks")
        self.assertEqual(o["O12"]["edgesRetired"], 1)  # e1 hit the threshold of 2
        self.assertFalse(o["O12"]["flag"])             # 3/3 = 100%, 3 attempts -> proven
        self.assertTrue(o["O3"]["flag"])               # no attempts
        self.assertEqual(o["O1"]["edges"], [])         # tier 3: no edges
        self.assertEqual(r["gap"], 53)
        self.assertEqual([x["id"] for x in r["objectives"]], ["O12", "O3", "O1"])

    def test_pexam_has_no_score_report(self):
        self.write("pexam-performance.json", {"sessions": [{"date": "2026-10-01", "difficulty": "easy",
            "domain_filter": "D7", "score": 1, "total": 1, "questions": [q("7.1", True, domain="D7")]}]})
        d = stats.compute(self.root, "pexam")
        self.assertIsNone(d["scoreReport"])
        self.assertEqual(len(d["domains"]), 7)
        self.assertEqual(d["projection"]["weightCovered"], 7)


if __name__ == "__main__":
    unittest.main()

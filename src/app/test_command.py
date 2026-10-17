"""Tests for app/command.py using a stub `claude` that plays the /fexam conversation.

Run:  python3 -m unittest discover -s app -p "test_*.py"
"""

import json
import stat
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import command  # noqa: E402

STUB = r'''#!{python}
import json, sys, os
args = sys.argv[1:]
if args[:2] == ["auth", "status"]:
    print(json.dumps({{"loggedIn": True}})); sys.exit(0)
state_dir = {state_dir!r}
log = os.path.join(state_dir, "argv.jsonl")
open(log, "a").write(json.dumps(args) + "\n")
text = args[args.index("-p") + 1]
sid = args[args.index("--session-id") + 1] if "--session-id" in args else args[args.index("--resume") + 1]
sf = os.path.join(state_dir, sid + ".json")
st = json.load(open(sf)) if os.path.exists(sf) else {{"step": 0, "answers": []}}
mode = os.environ.get("STUB_MODE", "ok")
if mode == "fail":
    print(json.dumps({{"type": "result", "subtype": "error_during_execution", "is_error": True, "result": "boom"}})); sys.exit(1)

def block(**b):
    base = {{"phase": "other", "awaiting": "free_text", "watch": [], "feedback": None, "question": None, "summary": None}}
    base.update(b)
    return "\n\n```exam-ui\n" + json.dumps(base) + "\n```"

def q(n):
    return {{"number": n, "total": 2, "domain": "D1", "domain_name": "Agentic", "subtopic": "1.1", "subtopic_label": "Loop",
            "objective": None, "stem": "Question %d stem" % n, "options": {{"A": "a", "B": "b", "C": "c", "D": "d"}}}}

denials = []
if st["step"] == 0:
    assert text.startswith("/fexam"), text
    out = "Welcome. Which domain? How many?" + block(phase="setup", awaiting="domain_and_count")
elif st["step"] == 1:
    st["setup_reply"] = text
    out = "**Watch:** 3.7 (62%)\n\n**Question 1/2**" + block(phase="question", awaiting="answer", watch=["3.7 (62%)"], question=q(1))
elif st["step"] == 2:
    st["answers"].append(text)
    fb = {{"question_number": 1, "result": "correct" if text == "B" else "incorrect", "chosen": text, "correct_letter": "B",
          "trap": None if text == "B" else "some_trap", "trap_description": None if text == "B" else "why", "why_correct": "because",
          "why_wrong": {{"A": "x", "C": "y", "D": "z"}}, "objective_note": None}}
    out = "**CORRECT**\n\n**Question 2/2**" + block(phase="feedback", awaiting="answer", feedback=fb, question=q(2))
else:
    st["answers"].append(text)
    perf = json.load(open("fexam-performance.json"))
    perf["sessions"].append({{"date": "2026-10-15", "difficulty": "medium", "domain_filter": "all", "score": 1, "total": 2, "questions": []}})
    json.dump(perf, open("fexam-performance.json", "w"))
    denials = [{{"tool_name": "Bash", "tool_input": {{"command": "python3 - <<E"}}}}]
    fb = {{"question_number": 2, "result": "incorrect", "chosen": text, "correct_letter": "C", "trap": "t2", "trap_description": "d2",
          "why_correct": "w", "why_wrong": {{}}, "objective_note": None}}
    summ = {{"score": 1, "total": 2, "percent": 50.0, "scaled": 500, "weighted": None, "verdict": None, "domains": [], "misses": [{{"number": 2, "trap": "t2"}}], "logged": True}}
    out = "## Final score\n\n| a | b |\n|---|---|\n| 1 | 2 |" + block(phase="summary", awaiting="none", feedback=fb, summary=summ)
st["step"] += 1
json.dump(st, open(sf, "w"))
print(json.dumps({{"type": "result", "subtype": "success", "is_error": False, "result": out, "duration_ms": 1200,
                  "total_cost_usd": 0.1, "permission_denials": denials}}))
'''


class CommandTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "proj"
        (self.root / ".claude/commands").mkdir(parents=True)
        for c in ("fexam", "pexam"):
            (self.root / ".claude/commands" / f"{c}.md").write_text("# cmd", encoding="utf-8")
        (self.root / "fexam-performance.json").write_text('{"sessions": []}', encoding="utf-8")
        self.state = Path(self.tmp.name) / "stub"
        self.state.mkdir()
        stub = Path(self.tmp.name) / "claude"
        stub.write_text(STUB.format(python=sys.executable, state_dir=str(self.state)), encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
        self.runner = command.ClaudeRunner(self.root, binary=str(stub))
        self.mgr = command.SessionManager(self.root, self.runner)

    def tearDown(self):
        self.tmp.cleanup()

    def wait(self, s, timeout=20):
        end = time.time() + timeout
        while time.time() < end:
            if not s.d["busy"]:
                return
            time.sleep(0.05)
        self.fail("turn never finished")

    def argv(self):
        return [json.loads(l) for l in (self.state / "argv.jsonl").read_text().splitlines()]

    def test_parse_reply(self):
        vis, b = command.parse_reply('Hi\n\n```exam-ui\n{"phase": "setup", "awaiting": "count"}\n```')
        self.assertEqual(vis, "Hi")
        self.assertEqual(b["awaiting"], "count")
        vis, b = command.parse_reply("No block here")
        self.assertIsNone(b)
        vis, b = command.parse_reply("Bad\n```exam-ui\n{not json}\n```")
        self.assertEqual((vis, b), ("Bad", None))

    def test_full_session(self):
        self.assertTrue(self.runner.available()["ok"])
        s = self.mgr.start("fexam", "medium", "D3", 2)
        self.wait(s)
        # setup prompt answered automatically from the setup screen choices
        user_turns = [t for t in s.d["turns"] if t["role"] == "user"]
        self.assertEqual(user_turns[0]["text"], "/fexam medium")
        self.assertEqual(user_turns[1]["kind"], "setup")
        self.assertIn("D3", user_turns[1]["text"])
        self.assertIn("2 questions", user_turns[1]["text"])
        self.assertEqual(s.last_block()["question"]["number"], 1)

        a = self.argv()
        self.assertIn("--session-id", a[0])
        self.assertIn("--name", a[0])
        self.assertIn("--resume", a[1])
        for flag in ("--append-system-prompt-file", "--allowedTools", "--permission-mode", "--strict-mcp-config"):
            self.assertIn(flag, a[0])
        self.assertEqual(a[0][a[0].index("--permission-mode") + 1], "dontAsk")
        self.assertIn("Edit(./fexam-performance.json)", a[0])
        self.assertNotIn("--no-session-persistence", a[0])  # sessions stay resumable

        with self.assertRaises(ValueError):
            s.answer("E")
        s.answer("B")
        self.wait(s)
        self.assertEqual(s.last_block()["feedback"]["result"], "correct")
        s.answer("A")
        self.wait(s)
        self.assertTrue(s.finished())
        self.assertEqual(len(json.loads((self.root / "fexam-performance.json").read_text())["sessions"]), 1)
        self.assertEqual(s.d["turns"][-1]["denials"][0]["tool"], "Bash")
        with self.assertRaises(ValueError):
            s.answer("A")  # nothing awaiting an answer

        # persisted and reloadable after a restart
        mgr2 = command.SessionManager(self.root, self.runner)
        s2 = mgr2.get(s.id)
        self.assertTrue(s2.finished())
        self.assertEqual(len(s2.d["turns"]), len(s.d["turns"]))

    def test_error_then_retry(self):
        import os
        os.environ["STUB_MODE"] = "fail"
        try:
            s = self.mgr.start("fexam", "easy", "all", 5)
            self.wait(s)
            self.assertIn("boom", s.d["error"])
            self.assertFalse(s.d["busy"])
        finally:
            os.environ.pop("STUB_MODE")
        s.retry()
        self.wait(s)
        self.assertIsNone(s.d["error"])
        self.assertEqual(s.last_block()["awaiting"], "answer")

    def test_interrupted_turn_marked_on_reload(self):
        s = self.mgr.start("fexam", "easy", "all", 5)
        self.wait(s)
        s.d["busy"] = True
        s.d["pending"] = {"text": "B", "kind": "answer"}
        s.save()
        mgr2 = command.SessionManager(self.root, self.runner)
        s2 = mgr2.get(s.id)
        self.assertFalse(s2.d["busy"])
        self.assertIn("stopped", s2.d["error"])
        s2.retry()
        self.wait(s2)
        self.assertEqual(s2.last_block()["feedback"]["chosen"], "B")

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.mgr.start("fexam", "nightmare", "all", 5)
        with self.assertRaises(ValueError):
            self.mgr.start("fexam", "easy", "D9", 5)
        with self.assertRaises(ValueError):
            self.mgr.start("fexam", "easy", "all", 0)


if __name__ == "__main__":
    unittest.main()

"""Runs the real /fexam and /pexam commands for the Exam Prep app.

Each practice session is a real Claude Code conversation in the project
folder, driven turn by turn with `claude -p`:

    turn 1   claude -p "/fexam hard" --session-id <id> ...
    turn n   claude -p "<the learner's answer>" --resume <id> ...

The command runs exactly as it does in the terminal: it reads your history and
score report, writes workspace.md, asks the questions, gives feedback, and
appends the session to <exam>-performance.json itself. The app adds one
instruction (ui_protocol.md, via --append-system-prompt-file) asking Claude to
end each reply with a small JSON block that mirrors the reply, so the app can
show it in the designed screens. The command files are not modified.

Tool access is limited to: Read, `python3 -c`, `date`, and writing the two
performance files and workspace.md. Everything else is refused (dontAsk).

Sessions are saved by Claude Code, so an interrupted one can be continued in
the app or with `claude --resume <id>`. The app keeps its own small record of
each session (transcript + parsed blocks) in .exam-app/sessions/.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

import stats

APP_DIR = Path(__file__).resolve().parent
PROTOCOL_FILE = APP_DIR / "ui_protocol.md"
DIFFICULTIES = ["easy", "medium", "hard", "absurd", "exam"]
MAX_QUESTIONS = 60
TURN_TIMEOUT = 600
MAX_REPLY = 2000
SETUP_AWAITS = {"domain", "count", "domain_and_count"}
BLOCK_RE = re.compile(r"```exam-ui\s*(\{.*?\})\s*```", re.S)

ALLOWED_TOOLS = [
    "Read",
    "Bash(python3 -c *)",
    "Bash(date *)",
    "Edit(./fexam-performance.json)",
    "Edit(./pexam-performance.json)",
    "Edit(./workspace.md)",
]


def parse_reply(text: str) -> tuple[str, dict | None]:
    """Split Claude's reply into (visible markdown, exam-ui block or None)."""
    text = text or ""
    matches = list(BLOCK_RE.finditer(text))
    if not matches:
        return text.strip(), None
    m = matches[-1]
    visible = (text[:m.start()] + text[m.end():]).strip()
    try:
        block = json.loads(m.group(1))
    except json.JSONDecodeError:
        return visible, None
    return visible, block if isinstance(block, dict) else None


class TurnError(RuntimeError):
    pass


class ClaudeRunner:
    """One `claude -p` turn in the project folder."""

    def __init__(self, root: Path, binary: str | None = None):
        self.root = root
        self.binary = binary or shutil.which("claude")

    def available(self) -> dict:
        if not self.binary:
            return {"ok": False, "message": "The `claude` command isn't on PATH in the shell that started the app. Install Claude Code there, or pass --claude /path/to/claude."}
        try:
            out = subprocess.run([self.binary, "auth", "status"], capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"ok": False, "message": f"Couldn't run `claude auth status`: {exc}"}
        if out.returncode != 0:
            return {"ok": False, "message": "Claude Code isn't signed in. Run `claude` once in this terminal and sign in, then check again."}
        missing = [c for c in ("fexam", "pexam") if not (self.root / ".claude/commands" / f"{c}.md").is_file()]
        if missing:
            return {"ok": False, "message": f"Missing command file(s) in {self.root}/.claude/commands: {', '.join(m + '.md' for m in missing)}."}
        return {"ok": True, "message": "Claude Code is ready."}

    def run(self, session_id: str, text: str, first: bool, name: str | None = None) -> dict:
        if not self.binary:
            raise TurnError("The `claude` command isn't on PATH.")
        cmd = [self.binary, "-p", text]
        cmd += ["--session-id", session_id] if first else ["--resume", session_id]
        if first and name:
            cmd += ["--name", name]
        cmd += [
            "--output-format", "json",
            "--append-system-prompt-file", str(PROTOCOL_FILE),
            "--allowedTools", *ALLOWED_TOOLS,
            "--permission-mode", "dontAsk",
            "--strict-mcp-config",
        ]
        try:
            out = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True,
                                 timeout=TURN_TIMEOUT, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise TurnError(f"Claude didn't reply within {TURN_TIMEOUT // 60} minutes.")
        except OSError as exc:
            raise TurnError(f"Couldn't start Claude Code: {exc}")
        raw = (out.stdout or "").strip()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            lines = (out.stderr or raw or "no output").strip().splitlines()
            raise TurnError(f"Claude Code failed: {(lines[-1] if lines else 'no output')[:400]}")
        if isinstance(payload, list):
            payload = next((m for m in reversed(payload) if isinstance(m, dict) and m.get("type") == "result"), {})
        if payload.get("is_error") or payload.get("subtype") not in (None, "success"):
            raise TurnError(f"Claude Code reported an error: {str(payload.get('result') or payload.get('subtype'))[:400]}")
        return payload


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Session:
    def __init__(self, mgr: "SessionManager", data: dict):
        self.mgr = mgr
        self.d = data
        self.lock = threading.Lock()

    @property
    def id(self) -> str:
        return self.d["id"]

    # ---- persistence ----
    def save(self):
        path = self.mgr.sessions_dir / f"{self.id}.json"
        fd, tmp = tempfile.mkstemp(dir=self.mgr.sessions_dir, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(self.d, fh, indent=1, ensure_ascii=False)
        os.replace(tmp, path)

    # ---- state ----
    def last_block(self) -> dict | None:
        for t in reversed(self.d["turns"]):
            if t["role"] == "claude":
                return t.get("block")
        return None

    def finished(self) -> bool:
        b = self.last_block()
        return bool(b and (b.get("summary") or b.get("awaiting") == "none"))

    def view(self) -> dict:
        with self.lock:
            d = json.loads(json.dumps(self.d))
        d["finished"] = self.finished()
        d["resumeCommand"] = f"claude --resume {self.id}"
        return d

    def brief(self) -> dict:
        b = self.last_block() or {}
        q = b.get("question") or {}
        answered = sum(1 for t in self.d["turns"] if t["role"] == "claude" and (t.get("block") or {}).get("feedback"))
        return {"id": self.id, "exam": self.d["exam"], "difficulty": self.d["difficulty"], "domain": self.d["domain"],
                "count": self.d["count"], "created": self.d["created"], "updated": self.d["updated"],
                "answered": answered, "total": q.get("total") or self.d["count"],
                "finished": self.finished(), "busy": self.d["busy"], "error": self.d["error"]}

    # ---- turns ----
    def _setup_reply(self, awaiting: str) -> str:
        dom = self.d["domain"]
        if dom == "all":
            dom_text = "All domains"
        else:
            name = next((n for i, n, _ in stats.EXAMS[self.d["exam"]]["domains"] if i == dom), "")
            dom_text = f"Domain {dom[1:]} only ({dom} {name})"
        count = f"{self.d['count']} questions"
        return {"domain": dom_text, "count": count}.get(awaiting, f"{dom_text}, {count}.")

    def submit(self, text: str, kind: str):
        """Queue a learner turn and run it (plus any setup auto-replies) in the background."""
        with self.lock:
            if self.d["busy"]:
                raise ValueError("Claude is still replying. Wait for it to finish.")
            self.d["busy"] = True
            self.d["error"] = None
            self.d["pending"] = {"text": text, "kind": kind}
            self.d["updated"] = _now()
            self.save()
        self.mgr.pool_submit(self._run_pending)

    def _run_pending(self):
        auto = 0
        while True:
            with self.lock:
                pending = self.d.get("pending")
            if not pending:
                break
            first = not any(t["role"] == "claude" for t in self.d["turns"])
            try:
                try:
                    payload = self.mgr.runner.run(self.id, pending["text"], first=first, name=self.d.get("name"))
                except TurnError as exc:
                    # A first turn that failed after Claude Code created the session: continue it instead.
                    if first and "already in use" in str(exc):
                        payload = self.mgr.runner.run(self.id, pending["text"], first=False)
                    else:
                        raise
            except Exception as exc:  # surfaced in the UI with a retry button
                with self.lock:
                    self.d["busy"] = False
                    self.d["error"] = str(exc) or type(exc).__name__
                    self.d["updated"] = _now()
                    self.save()
                return
            visible, block = parse_reply(payload.get("result", ""))
            denials = [{"tool": x.get("tool_name"), "input": (json.dumps(x.get("tool_input"))[:300])}
                       for x in (payload.get("permission_denials") or [])]
            with self.lock:
                self.d["turns"].append({"role": "user", "text": pending["text"], "kind": pending["kind"], "at": _now()})
                self.d["turns"].append({"role": "claude", "text": visible, "block": block, "at": _now(),
                                        "denials": denials, "seconds": round((payload.get("duration_ms") or 0) / 1000),
                                        "cost": payload.get("total_cost_usd")})
                self.d["pending"] = None
                # Answer the command's setup questions with what was chosen on the setup screen.
                awaiting = (block or {}).get("awaiting")
                if awaiting in SETUP_AWAITS and auto < 3:
                    auto += 1
                    self.d["pending"] = {"text": self._setup_reply(awaiting), "kind": "setup"}
                else:
                    self.d["busy"] = False
                self.d["updated"] = _now()
                self.save()

    def answer(self, letter: str):
        letter = str(letter or "").strip().upper()
        if letter not in ("A", "B", "C", "D"):
            raise ValueError("Answer must be A, B, C or D.")
        b = self.last_block() or {}
        if b.get("awaiting") != "answer" or not b.get("question"):
            raise ValueError("There's no question waiting for an answer.")
        self.submit(letter, "answer")

    def reply(self, text: str):
        text = str(text or "").strip()
        if not text:
            raise ValueError("Type a message first.")
        if len(text) > MAX_REPLY:
            raise ValueError(f"Keep messages under {MAX_REPLY} characters.")
        self.submit(text, "text")

    def retry(self):
        with self.lock:
            if self.d["busy"]:
                raise ValueError("Claude is still replying.")
            last_user = next((t for t in reversed(self.d["turns"]) if t["role"] == "user"), None)
            pending = self.d.get("pending")
        if pending:
            return self.submit(pending["text"], pending["kind"])
        if not self.d["turns"]:
            return self.submit(self.d["opening"], "start")
        if last_user and self.d["turns"][-1]["role"] == "user":
            return self.submit(last_user["text"], last_user["kind"])
        raise ValueError("Nothing to retry.")


class SessionManager:
    def __init__(self, root: Path, runner):
        self.root = root
        self.runner = runner
        self.sessions_dir = root / ".exam-app" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: dict[str, Session] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        for p in sorted(self.sessions_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if data.get("busy"):  # the server stopped mid-turn
                data["busy"] = False
                data["error"] = ("The app stopped while Claude was replying. Retry to send your last message again "
                                 "(or continue in the terminal with the resume command).")
            s = Session(self, data)
            self.sessions[s.id] = s

    def pool_submit(self, fn):
        threading.Thread(target=fn, daemon=True, name="claude-turn").start()

    def start(self, exam: str, difficulty: str, domain: str, count) -> Session:
        if exam not in stats.EXAMS:
            raise ValueError("Unknown exam.")
        if difficulty not in DIFFICULTIES:
            raise ValueError("Difficulty must be easy, medium, hard, absurd or exam.")
        if domain not in {"all"} | {d for d, _, _ in stats.EXAMS[exam]["domains"]}:
            raise ValueError("Unknown domain.")
        try:
            count = int(count)
        except (TypeError, ValueError):
            raise ValueError("Question count must be a number.")
        if not 1 <= count <= MAX_QUESTIONS:
            raise ValueError(f"Choose between 1 and {MAX_QUESTIONS} questions.")
        with self._lock:
            active = [s for s in self.sessions.values() if s.d["busy"]]
            if active:
                raise ValueError("Another session is waiting on Claude. Let it finish first.")
            sid = str(uuid.uuid4())
            opening = f"{stats.EXAMS[exam]['command']} {difficulty}"
            data = {"id": sid, "exam": exam, "difficulty": difficulty, "domain": domain, "count": count,
                    "opening": opening, "name": f"{opening} · {datetime.now():%Y-%m-%d %H:%M} (Exam Prep app)",
                    "created": _now(), "updated": _now(), "busy": False, "error": None,
                    "pending": None, "turns": []}
            s = Session(self, data)
            self.sessions[sid] = s
        s.submit(opening, "start")
        return s

    def get(self, sid: str) -> Session | None:
        return self.sessions.get(sid)

    def recent(self, limit: int = 10) -> list[dict]:
        items = sorted(self.sessions.values(), key=lambda s: s.d["updated"], reverse=True)
        return [s.brief() for s in items[:limit]]


def setup_info(root: Path, exam_id: str, mgr: SessionManager) -> dict:
    exam = stats.EXAMS[exam_id]
    report = stats.load_json(root / exam["scorereport"]) if exam["scorereport"] else None
    st = stats.compute(root, exam_id)
    return {
        "exam": st["exam"],
        "domains": [{"id": d, "name": nm, "weight": round(w * 100)} for d, nm, w in exam["domains"]],
        "scoreReport": ({"date": report.get("attempt_date"), "score": report.get("score"),
                         "mix": report.get("session_mix") or {"tier1": 0.4, "tier2": 0.3, "tier3": 0.3}}
                        if report else None),
        "watch": [s for s in st["subtopics"] if s["weak"]][:5],
        "traps": st["traps"][:5],
        "maxQuestions": MAX_QUESTIONS,
        "sessions": [s for s in mgr.recent() if s["exam"] == exam_id],
    }

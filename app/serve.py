#!/usr/bin/env python3
"""Exam Prep app: run the real /fexam and /pexam commands in a designed UI, plus stats.

    python3 app/serve.py               # http://localhost:8765/practice
    python3 app/serve.py --open        # and open a browser

Practice sessions are real Claude Code conversations running your
.claude/commands/fexam.md or pexam.md in this project folder, using your
normal Claude Code login and default model. The command itself reads your
history and writes fexam-/pexam-performance.json and workspace.md, exactly as
in the terminal. Stats are computed locally from those files.

Binds to 127.0.0.1 only. Python standard library only.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))
import command  # noqa: E402
import stats  # noqa: E402

WEB_DIR = APP_DIR / "web"
STATIC = {
    "/": WEB_DIR / "index.html",
    "/stats": WEB_DIR / "index.html",
    "/practice": WEB_DIR / "practice.html",
    "/app.js": WEB_DIR / "app.js",
    "/practice.js": WEB_DIR / "practice.js",
    "/markdown.js": WEB_DIR / "markdown.js",
    "/app.css": WEB_DIR / "app.css",
}
MAX_BODY = 16 * 1024
SESSION_RE = re.compile(r"^/api/sessions/([0-9a-f-]{36})(?:/(answer|reply|retry))?$")


def make_handler(root: Path, mgr: command.SessionManager, port: int):
    static = dict(STATIC)
    # Prefer the project's design/tokens.css; fall back to the copy bundled with the app.
    project_tokens = root / "design" / "tokens.css"
    static["/tokens.css"] = project_tokens if project_tokens.is_file() else WEB_DIR / "tokens.css"
    allowed_hosts = {f"localhost:{port}", f"127.0.0.1:{port}"}
    health: dict = {}

    class Handler(BaseHTTPRequestHandler):
        server_version = "exam-prep"

        def log_message(self, fmt, *args):
            pass

        def _send(self, status, body: bytes, ctype: str):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, data, status=HTTPStatus.OK):
            self._send(status, json.dumps(data).encode(), "application/json")

        def _error(self, msg, status=HTTPStatus.BAD_REQUEST):
            self._json({"error": msg}, status)

        def _host_ok(self) -> bool:
            # Blocks DNS rebinding: only answer requests addressed to this machine.
            return self.headers.get("Host", "") in allowed_hosts

        def do_GET(self):
            if not self._host_ok():
                return self._error("Bad host.", HTTPStatus.FORBIDDEN)
            url = urlparse(self.path)
            q = parse_qs(url.query)
            exam = q.get("exam", ["fexam"])[0]
            try:
                if url.path in ("/api/stats", "/api/setup") and exam not in stats.EXAMS:
                    return self._error("Unknown exam.")
                if url.path == "/api/stats":
                    return self._json(stats.compute(root, exam))
                if url.path == "/api/setup":
                    return self._json(command.setup_info(root, exam, mgr))
                if url.path == "/api/health":
                    if "refresh" in q or not health:
                        health.clear()
                        health.update(mgr.runner.available())
                    return self._json(health)
                if url.path == "/api/sessions":
                    return self._json({"sessions": mgr.recent()})
                m = SESSION_RE.match(url.path)
                if m and not m.group(2):
                    s = mgr.get(m.group(1))
                    if not s:
                        return self._error("Session not found.", HTTPStatus.NOT_FOUND)
                    return self._json(s.view())
            except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError) as exc:
                return self._error(f"{type(exc).__name__}: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

            path = static.get(url.path)
            if not path or not path.is_file():
                return self._send(HTTPStatus.NOT_FOUND, b"Not found", "text/plain")
            ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype.endswith("javascript"):
                ctype += "; charset=utf-8"
            return self._send(HTTPStatus.OK, path.read_bytes(), ctype)

        def do_POST(self):
            if not self._host_ok():
                return self._error("Bad host.", HTTPStatus.FORBIDDEN)
            if not (self.headers.get("Content-Type") or "").startswith("application/json"):
                return self._error("Send JSON.", HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            url = urlparse(self.path)
            try:
                n = int(self.headers.get("Content-Length") or 0)
                if n > MAX_BODY:
                    return self._error("Request too large.")
                body = json.loads(self.rfile.read(n) or b"{}") if n else {}
                if not isinstance(body, dict):
                    return self._error("Expected a JSON object.")
                if url.path == "/api/sessions":
                    s = mgr.start(body.get("exam", "fexam"), body.get("difficulty", "medium"),
                                  body.get("domain", "all"), body.get("count", 15))
                    return self._json(s.view(), HTTPStatus.CREATED)
                m = SESSION_RE.match(url.path)
                if m and m.group(2):
                    s = mgr.get(m.group(1))
                    if not s:
                        return self._error("Session not found.", HTTPStatus.NOT_FOUND)
                    if m.group(2) == "answer":
                        s.answer(body.get("letter"))
                    elif m.group(2) == "reply":
                        s.reply(body.get("text"))
                    else:
                        s.retry()
                    return self._json(s.view(), HTTPStatus.ACCEPTED)
                return self._error("Not found.", HTTPStatus.NOT_FOUND)
            except ValueError as exc:
                return self._error(str(exc))
            except (OSError, KeyError, TypeError) as exc:
                return self._error(f"{type(exc).__name__}: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    return Handler


def main():
    ap = argparse.ArgumentParser(description="Exam Prep: real /fexam and /pexam in a designed UI, plus stats")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--root", type=Path, default=APP_DIR.parent,
                    help="project folder with .claude/commands and your *-performance.json (default: this repo)")
    ap.add_argument("--claude", help="path to the claude binary (default: found on PATH)")
    ap.add_argument("--open", action="store_true", help="open the app in a browser")
    args = ap.parse_args()

    root = args.root.resolve()
    mgr = command.SessionManager(root, command.ClaudeRunner(root, binary=args.claude))
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(root, mgr, args.port))
    url = f"http://localhost:{args.port}"
    print(f"Exam Prep → {url}/practice   stats → {url}/\n  project: {root}\n  Ctrl+C to stop")
    if args.open:
        webbrowser.open(url + "/practice")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

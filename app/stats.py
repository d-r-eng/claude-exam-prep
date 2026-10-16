"""Stats engine for the claude-exam-prep dashboard.

Reads the same local files the /fexam and /pexam commands write and computes
the numbers their `stats` mode shows. Python standard library only.

Tolerates older records: questions without `domain` (inferred from the
subtopic code), without `subtopic_label` (looked up from the command file),
and sessions that use `domains` instead of `domain_filter`.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PASSING = 720
WEAK_SUBTOPIC_PCT = 70.0       # stats mode flags subtopics below this
OBJECTIVE_PROVEN_PCT = 80.0    # tier 1/2 objective is "proven" at >= this ...
OBJECTIVE_PROVEN_MIN = 3       # ... with at least this many attempts
DEFAULT_RETIRE_AFTER = 5

EXAMS = {
    "fexam": {
        "id": "fexam",
        "name": "Foundations",
        "code": "CCAR-F",
        "command": "/fexam",
        "performance": "fexam-performance.json",
        "scorereport": "fexam-scorereport.json",
        "command_file": ".claude/commands/fexam.md",
        "domains": [
            ("D1", "Agentic Architecture & Orchestration", 0.27),
            ("D2", "Tool Design & MCP Integration", 0.18),
            ("D3", "Claude Code Configuration & Workflows", 0.20),
            ("D4", "Prompt Engineering & Structured Output", 0.20),
            ("D5", "Context Management & Reliability", 0.15),
        ],
    },
    "pexam": {
        "id": "pexam",
        "name": "Professional",
        "code": "CCAR-P",
        "command": "/pexam",
        "performance": "pexam-performance.json",
        "scorereport": None,
        "command_file": ".claude/commands/pexam.md",
        "domains": [
            ("D1", "Solution Design & Architecture", 0.17),
            ("D2", "Claude Models, Prompting & Context Engineering", 0.13),
            ("D3", "Integration", 0.19),
            ("D4", "Evaluation, Testing & Optimization", 0.16),
            ("D5", "Governance, Safety & Risk Management", 0.14),
            ("D6", "Stakeholder Communication & Lifecycle Management", 0.14),
            ("D7", "Developer Productivity & Operational Enablement", 0.07),
        ],
    },
}

_LABEL_RE = re.compile(r"^\*\*(.+?)\s*\((\d+\.\d+)\)\*\*\s*$", re.M)


def pct(correct: int, total: int) -> float | None:
    return round(correct / total * 100, 1) if total else None


def load_json(path: Path):
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def subtopic_labels_from_command(path: Path) -> dict[str, str]:
    """Labels from the command file's `**Label (1.2)**` headings."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    return {code: label.strip() for label, code in _LABEL_RE.findall(text)}


def domain_of(q: dict) -> str | None:
    if q.get("domain"):
        return str(q["domain"])
    sub = str(q.get("subtopic") or "")
    m = re.match(r"(\d+)\.", sub)
    return f"D{m.group(1)}" if m else None


def session_focus(s: dict) -> str:
    return str(s.get("domain_filter") or s.get("domains") or "all")


def short_label(text: str, words: int = 8) -> str:
    head = re.split(r"[:;(]| — | - ", text, maxsplit=1)[0].strip()
    parts = head.split()
    out = " ".join(parts[:words])
    return out + ("…" if len(parts) > words else "")


def tier_for(exam_pct: float) -> int:
    if exam_pct <= 0:
        return 1
    if exam_pct >= 100:
        return 3
    return 2


def compute(root: Path, exam_id: str) -> dict:
    exam = EXAMS[exam_id]
    perf_path = root / exam["performance"]
    perf = load_json(perf_path) or {"sessions": []}
    sessions = list(perf.get("sessions") or [])

    labels = subtopic_labels_from_command(root / exam["command_file"])
    for s in sessions:  # labels written in history win over the command file
        for q in s.get("questions") or []:
            if q.get("subtopic") and q.get("subtopic_label"):
                labels.setdefault(str(q["subtopic"]), q["subtopic_label"])

    questions = [q for s in sessions for q in (s.get("questions") or [])]
    total_q = len(questions)
    total_c = sum(1 for q in questions if q.get("correct"))

    # Sessions: newest first. File order breaks ties on the same date.
    ordered = sorted(enumerate(sessions), key=lambda p: (str(p[1].get("date", "")), p[0]))
    history = []
    for _, s in ordered:
        score, total = int(s.get("score") or 0), int(s.get("total") or 0)
        history.append({
            "date": s.get("date"),
            "difficulty": s.get("difficulty"),
            "focus": session_focus(s),
            "score": score,
            "total": total,
            "pct": pct(score, total),
        })
    recent = list(reversed(history))[:5]

    # Domains + weighted projection.
    dom = defaultdict(lambda: [0, 0])
    for q in questions:
        d = domain_of(q)
        if d:
            dom[d][1] += 1
            dom[d][0] += 1 if q.get("correct") else 0
    domains, projected, covered_w, covered_n = [], 0.0, 0.0, 0
    for did, name, w in exam["domains"]:
        c, t = dom.get(did, [0, 0])
        acc = (c / t) if t else None
        pts = round(acc * w * 1000, 1) if t else 0.0
        if t:
            projected += acc * w * 1000
            covered_w += w
            covered_n += 1
        domains.append({"id": did, "name": name, "weight": round(w * 100),
                        "correct": c, "total": t, "pct": pct(c, t), "points": pts})
    all_covered = covered_n == len(exam["domains"])
    projection = {
        "score": round(projected) if covered_n else None,
        "verdict": ("PASS" if round(projected) >= PASSING else "FAIL") if all_covered else None,
        "domainsCovered": covered_n,
        "domainsTotal": len(exam["domains"]),
        "weightCovered": round(covered_w * 100),
    }

    # Subtopics with >= 2 attempts, weakest first.
    sub = defaultdict(lambda: [0, 0])
    for q in questions:
        k = str(q.get("subtopic") or "")
        if k:
            sub[k][1] += 1
            sub[k][0] += 1 if q.get("correct") else 0
    subtopics = []
    for k, (c, t) in sub.items():
        if t >= 2:
            p = pct(c, t)
            subtopics.append({"id": k, "label": labels.get(k, ""), "correct": c,
                              "total": t, "pct": p, "weak": p < WEAK_SUBTOPIC_PCT})
    subtopics.sort(key=lambda r: (r["pct"], -r["total"], r["id"]))

    # Recurring traps (>= 2 wrong answers), with the latest description.
    trap_count, trap_desc = Counter(), {}
    for _, s in ordered:
        for q in s.get("questions") or []:
            t = q.get("trick")
            if t and not q.get("correct"):
                trap_count[t] += 1
                if q.get("trick_description"):
                    trap_desc[t] = q["trick_description"]
    traps = [{"label": t, "count": n, "description": trap_desc.get(t)}
             for t, n in trap_count.most_common() if n >= 2]

    report = None
    if exam["scorereport"]:
        report = _score_report(load_json(root / exam["scorereport"]), questions)

    return {
        "exam": {k: exam[k] for k in ("id", "name", "code", "command")} | {"passing": PASSING},
        "available": {k: (root / v["performance"]).is_file() for k, v in EXAMS.items()},
        "empty": not sessions,
        "summary": {
            "sessions": len(sessions),
            "questions": total_q,
            "correct": total_c,
            "pct": pct(total_c, total_q),
            "firstDate": history[0]["date"] if history else None,
            "lastDate": history[-1]["date"] if history else None,
        },
        "projection": projection,
        "domains": domains,
        "history": history,
        "recent": recent,
        "subtopics": subtopics,
        "traps": traps,
        "scoreReport": report,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _score_report(rep: dict | None, questions: list[dict]) -> dict | None:
    if not rep:
        return None
    retire_after = int(rep.get("retire_after_correct") or DEFAULT_RETIRE_AFTER)
    by_obj = defaultdict(lambda: [0, 0])
    edge_ok = Counter()
    for q in questions:
        o = q.get("objective")
        if o:
            by_obj[o][1] += 1
            by_obj[o][0] += 1 if q.get("correct") else 0
        if q.get("edge") and q.get("correct"):
            edge_ok[q["edge"]] += 1

    objectives = []
    for o in rep.get("objectives") or []:
        exam_pct = float(o.get("exam_pct") or 0)
        tier = tier_for(exam_pct)  # exam_pct wins over a stored tier
        c, t = by_obj.get(o["id"], [0, 0])
        edges = [{"id": e["id"], "text": e.get("text", ""), "correct": edge_ok[e["id"]],
                  "retired": edge_ok[e["id"]] >= retire_after}
                 for e in (o.get("edges") or [])] if tier < 3 else []
        p = pct(c, t)
        objectives.append({
            "id": o["id"],
            "label": short_label(o.get("text", "")),
            "text": o.get("text", ""),
            "domain": o.get("domain"),
            "tier": tier,
            "examPct": round(exam_pct),
            "correct": c,
            "total": t,
            "pct": p,
            "flag": tier < 3 and (t < OBJECTIVE_PROVEN_MIN or (p or 0) < OBJECTIVE_PROVEN_PCT),
            "edges": edges,
            "edgesRetired": sum(e["retired"] for e in edges),
        })
    objectives.sort(key=lambda r: (r["tier"], -1 if r["pct"] is None else r["pct"],
                                   int(re.sub(r"\D", "", r["id"]) or 0)))
    score = rep.get("score")
    passing = rep.get("passing_score") or PASSING
    return {
        "date": rep.get("attempt_date"),
        "score": score,
        "passing": passing,
        "gap": (passing - score) if isinstance(score, (int, float)) else None,
        "retireAfter": retire_after,
        "tierCounts": dict(Counter(o["tier"] for o in objectives)),
        "objectives": objectives,
    }

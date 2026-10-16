#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_quiz_pdf.py — turn a JSON practice test into an e-reader-friendly PDF.

Flashcard-flip layout (default): each question + its choices fill one page; the
NEXT page reveals the correct answer + explanation. Also supports an inline
"review" layout. Renders via headless Chrome/Edge (auto-detected). Python 3
standard library only — no pip installs.

Usage:
    python build_quiz_pdf.py INPUT.json [-o OUT.pdf]
        [--page scribe|remarkable|paperwhite|generic-6|a4|letter]
        [--mode flip|review] [--font sans|serif] [--shuffle] [--no-pdf]

See references/schema.md for the input format.
"""
import argparse
import html as htmllib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------- page presets
# name -> (width_in, height_in, outer_margin_in, base_font_pt)
PAGE_PRESETS = {
    "scribe":     (6.20, 8.27, 0.45, 12.0),   # Kindle Scribe 1860x2480 @300ppi
    "remarkable": (6.18, 8.27, 0.45, 12.0),   # reMarkable 2 (157x210mm)
    "paperwhite": (4.12, 5.49, 0.28, 10.5),   # Kindle Paperwhite 1236x1648 @300
    "generic-6":  (4.50, 6.00, 0.30, 10.5),   # common 6" e-ink
    "a4":         (8.27, 11.69, 0.75, 12.0),  # ISO A4 (paper/tablet)
    "letter":     (8.50, 11.00, 0.75, 12.0),  # US Letter (paper/tablet)
}
LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ------------------------------------------------------------------- utilities
def die(msg, code=1):
    sys.stderr.write("error: " + msg + "\n")
    sys.exit(code)


def esc(text):
    """HTML-escape, then render `backtick` spans as <code> and **bold**."""
    t = htmllib.escape("" if text is None else str(text), quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return t


# ------------------------------------------------------------- normalize input
def normalize_choices(raw, qref):
    """Accept list[str] | list[{label,text}] | {label:text} -> [(label, text)]."""
    out = []
    if isinstance(raw, dict):
        for lab, txt in raw.items():
            out.append((str(lab).strip(), str(txt)))
    elif isinstance(raw, list):
        for i, c in enumerate(raw):
            if isinstance(c, dict):
                lab = str(c.get("label", LABELS[i] if i < 26 else str(i + 1))).strip()
                out.append((lab, str(c.get("text", c.get("value", "")))))
            else:
                out.append((LABELS[i] if i < 26 else str(i + 1), str(c)))
    else:
        die(f"{qref}: 'choices' must be a list or object")
    if not out:
        die(f"{qref}: 'choices' is empty")
    return out


def normalize_answer(ans, choices, qref):
    """Map a label ('D') or index (0- or 1-based) to a valid choice label."""
    labels = [l for l, _ in choices]
    if ans is None:
        die(f"{qref}: missing 'answer'")
    s = str(ans).strip()
    # exact label match (case-insensitive)
    for l in labels:
        if l.lower() == s.lower():
            return l
    # numeric index
    if re.fullmatch(r"\d+", s):
        n = int(s)
        if 0 <= n < len(labels):          # 0-based
            return labels[n]
        if 1 <= n <= len(labels):         # 1-based
            return labels[n - 1]
    die(f"{qref}: 'answer' = {ans!r} does not match any choice label {labels}")


def load_dataset(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"input file not found: {path}")
    except json.JSONDecodeError as e:
        die(f"invalid JSON in {path}: {e}")

    if not isinstance(data, dict):
        die("top-level JSON must be an object")

    # sections OR flat questions
    if "sections" in data:
        sections = data["sections"]
        if not isinstance(sections, list) or not sections:
            die("'sections' must be a non-empty list")
    elif "questions" in data:
        sections = [{"name": None, "questions": data["questions"]}]
    else:
        die("dataset must contain either 'sections' or 'questions'")

    gnum = 0
    norm_sections = []
    for si, sec in enumerate(sections):
        qs = sec.get("questions", [])
        if not isinstance(qs, list) or not qs:
            die(f"section {si} has no 'questions'")
        items = []
        for qi, q in enumerate(qs):
            gnum += 1
            qref = f"question {gnum} (section {si}, index {qi})"
            if "question" not in q:
                die(f"{qref}: missing 'question'")
            choices = normalize_choices(q.get("choices"), qref)
            answer = normalize_answer(q.get("answer", q.get("correct")), choices, qref)
            your = q.get("your_answer")
            your = normalize_answer(your, choices, qref) if your not in (None, "") else None
            items.append({
                "n": gnum,
                "question": q["question"],
                "context": q.get("context") or q.get("scenario"),
                "choices": choices,
                "answer": answer,
                "explanation": q.get("explanation", ""),
                "distractor_notes": q.get("distractor_notes") or {},
                "topic": q.get("topic") or q.get("study_area"),
                "your": your,
            })
        norm_sections.append({"name": sec.get("name"), "questions": items})
    return data, norm_sections, gnum


# --------------------------------------------------------------- HTML rendering
def css(width, height, margin, base, font):
    family = ('"Segoe UI","Helvetica Neue",Arial,sans-serif' if font == "sans"
              else 'Georgia,"Times New Roman",serif')
    return f"""
:root{{--ink:#000;--mut:#444;--line:#bbb;--shade:#efefef;--shade2:#e2e2e2;}}
*{{box-sizing:border-box;}}
@page{{size:{width}in {height}in;margin:{margin}in;}}
html,body{{margin:0;padding:0;background:#fff;color:var(--ink);}}
body{{font-family:{family};font-size:{base}pt;line-height:1.46;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;}}
code{{font-family:"Consolas","SF Mono",Menlo,monospace;font-size:0.9em;
  background:var(--shade);padding:0.5px 3px;border-radius:3px;}}
h1,h2,h3{{line-height:1.16;margin:0;}}
.page{{page-break-after:always;break-after:page;min-height:0;}}
.page:last-child{{page-break-after:auto;break-after:auto;}}

/* cover */
.kick{{font-size:0.8em;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);}}
.cover h1{{font-size:2.0em;font-weight:800;letter-spacing:-.01em;margin:.35em 0 .15em;}}
.cover .sub{{font-size:1.05em;color:var(--mut);margin-bottom:1.1em;}}
.facts{{border:2px solid var(--ink);border-radius:12px;padding:14px 16px;margin:12px 0;}}
.facts div{{padding:3px 0;}}
.facts b{{font-variant-numeric:tabular-nums;}}
.howto{{margin-top:14px;padding:11px 14px;background:var(--shade);border-radius:9px;font-size:.98em;}}
.toc{{margin-top:14px;}}
.toc .th{{font-size:.8em;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);
  border-bottom:1.5px solid var(--line);padding-bottom:4px;margin-bottom:6px;}}
.toc ol{{margin:0;padding-left:1.4em;}}
.toc li{{padding:2px 0;}}

/* section divider */
.divider{{display:flex;flex-direction:column;justify-content:center;height:100%;min-height:{height - 2*margin - 0.2:.2f}in;}}
.divider .dk{{font-size:.8em;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);}}
.divider h2{{font-size:1.7em;font-weight:800;border-top:3px solid var(--ink);border-bottom:3px solid var(--ink);
  padding:14px 0;margin:8px 0;}}

/* question / answer pages */
.tag{{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:.82em;}}
.tag .sec{{font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);}}
.tag .qn{{margin-left:auto;font-weight:800;font-size:1.15em;letter-spacing:.02em;}}
.ctx{{font-size:.92em;color:#222;background:var(--shade);border-left:4px solid var(--line);
  border-radius:0 8px 8px 0;padding:8px 11px;margin:0 0 10px;}}
.stem{{font-size:1.06em;font-weight:600;margin:0 0 12px;}}
ol.choices{{list-style:none;margin:0;padding:0;}}
ol.choices li{{display:flex;gap:10px;align-items:flex-start;border:1px solid var(--line);border-radius:9px;
  padding:9px 11px;margin:0 0 8px;break-inside:avoid;}}
ol.choices .cl{{font-weight:800;border:1.5px solid var(--ink);border-radius:6px;min-width:1.7em;height:1.7em;
  display:flex;align-items:center;justify-content:center;flex:0 0 auto;}}
ol.choices .ct{{padding-top:.15em;}}
.flip{{margin-top:16px;font-size:.85em;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:var(--mut);text-align:right;}}

/* answer reveal */
.ans-head{{display:flex;align-items:center;gap:10px;border-bottom:3px solid var(--ink);padding-bottom:8px;margin-bottom:10px;}}
.ans-head .badge{{font-weight:800;font-size:1.2em;width:1.7em;height:1.7em;border-radius:50%;
  border:2.5px solid var(--ink);display:flex;align-items:center;justify-content:center;flex:0 0 auto;}}
.ans-head .lab{{font-size:.8em;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);}}
.ans-head .big{{font-size:1.5em;font-weight:800;}}
.ans-head .qn{{margin-left:auto;font-weight:700;color:var(--mut);}}
.correct-choice{{border:2px solid var(--ink);background:var(--shade);border-radius:9px;padding:10px 12px;margin:0 0 10px;}}
.correct-choice .cl{{font-weight:800;margin-right:8px;}}
.expl{{margin:0 0 10px;}}
.expl .h,.dn .h,.your .h{{font-size:.78em;font-weight:800;letter-spacing:.08em;text-transform:uppercase;
  color:var(--mut);margin-bottom:3px;}}
.dn{{margin:10px 0;padding:9px 11px;background:var(--shade);border-radius:8px;font-size:.95em;}}
.dn ul{{margin:4px 0 0;padding-left:1.2em;}}
.dn li{{margin:3px 0;}}
.your{{margin:10px 0;padding:9px 11px;border:1.5px dashed #777;border-radius:8px;font-size:.95em;}}
.your .mark{{font-weight:800;}}
.topic{{margin-top:12px;padding-top:6px;border-top:1px dotted var(--line);font-size:.85em;color:var(--mut);}}

/* inline review mode */
.rev .stem{{margin-bottom:8px;}}
.rev .correct-choice{{margin-top:8px;}}
.rev .qcard{{border:1px solid var(--line);border-radius:10px;padding:11px 13px;margin:0 0 12px;break-inside:avoid;}}
.rev .qcard.miss{{border:2px solid var(--ink);background:#fafafa;}}
"""


def render_choices(choices):
    lis = "".join(
        f'<li><span class="cl">{esc(l)}</span><span class="ct">{esc(t)}</span></li>'
        for l, t in choices)
    return f'<ol class="choices">{lis}</ol>'


def render_answer_body(it, choices_map):
    correct_txt = choices_map.get(it["answer"], "")
    parts = [
        f'<div class="correct-choice"><span class="cl">{esc(it["answer"])}</span>{esc(correct_txt)}</div>'
    ]
    if it["explanation"]:
        parts.append(f'<div class="expl"><div class="h">Why</div>{esc(it["explanation"])}</div>')
    if it["your"] and it["your"] != it["answer"]:
        yt = choices_map.get(it["your"], "")
        parts.append(f'<div class="your"><div class="h">Your answer</div>'
                     f'<span class="mark">{esc(it["your"])} ✗</span> {esc(yt)}</div>')
    if it["distractor_notes"]:
        rows = "".join(f'<li><strong>{esc(k)}:</strong> {esc(v)}</li>'
                       for k, v in it["distractor_notes"].items())
        parts.append(f'<div class="dn"><div class="h">Distractors</div><ul>{rows}</ul></div>')
    if it["topic"]:
        parts.append(f'<div class="topic"><strong>Topic:</strong> {esc(it["topic"])}</div>')
    return "".join(parts)


def build_html(data, sections, total, mode, width, height, margin, base, font):
    title = data.get("title", "Practice Test")
    subtitle = data.get("subtitle", "")
    meta = data.get("meta", {}) or {}
    meta_line = " · ".join(
        str(meta[k]) for k in ("author", "date", "source") if meta.get(k))
    show_sections = any(s["name"] for s in sections)

    pages = []

    # cover
    toc = ""
    if show_sections:
        lis = "".join(f'<li>{esc(s["name"])} '
                      f'<span style="color:var(--mut)">({len(s["questions"])})</span></li>'
                      for s in sections)
        toc = f'<div class="toc"><div class="th">Sections</div><ol>{lis}</ol></div>'
    howto = ("Question and choices on one page — test yourself, then <strong>flip"
             " the page</strong> to reveal the correct answer and explanation."
             if mode == "flip" else
             "Each question is followed inline by its correct answer and explanation.")
    pages.append(f"""<div class="page cover">
  <div class="kick">{esc(meta.get('kicker', 'Study Deck'))}</div>
  <h1>{esc(title)}</h1>
  {f'<div class="sub">{esc(subtitle)}</div>' if subtitle else ''}
  <div class="facts">
    <div><b>{total}</b> questions{f' across <b>{len(sections)}</b> sections' if show_sections else ''}</div>
    {f'<div>{esc(meta_line)}</div>' if meta_line else ''}
  </div>
  <div class="howto">{howto}</div>
  {toc}
</div>""")

    if mode == "flip":
        for s in sections:
            if s["name"]:
                pages.append(f'<div class="page"><div class="divider">'
                             f'<div class="dk">Section</div><h2>{esc(s["name"])}</h2>'
                             f'<div style="color:var(--mut)">{len(s["questions"])} questions</div>'
                             f'</div></div>')
            for it in s["questions"]:
                sec_tag = f'<span class="sec">{esc(s["name"])}</span>' if s["name"] else ''
                ctx = f'<div class="ctx">{esc(it["context"])}</div>' if it["context"] else ''
                pages.append(f"""<div class="page">
  <div class="tag">{sec_tag}<span class="qn">Q{it['n']}</span></div>
  {ctx}
  <div class="stem">{esc(it['question'])}</div>
  {render_choices(it['choices'])}
  <div class="flip">Flip for answer →</div>
</div>""")
                cmap = {l: t for l, t in it["choices"]}
                pages.append(f"""<div class="page">
  <div class="ans-head"><span class="badge">✓</span>
    <div><div class="lab">Answer</div><div class="big">{esc(it['answer'])}</div></div>
    <span class="qn">Q{it['n']}</span></div>
  {render_answer_body(it, cmap)}
</div>""")
    else:  # review (inline)
        for s in sections:
            body = []
            if s["name"]:
                body.append(f'<h2 style="font-size:1.4em;font-weight:800;border-bottom:3px solid '
                            f'var(--ink);padding-bottom:5px;margin:0 0 10px;">{esc(s["name"])}</h2>')
            for it in s["questions"]:
                miss = " miss" if (it["your"] and it["your"] != it["answer"]) else ""
                ctx = f'<div class="ctx">{esc(it["context"])}</div>' if it["context"] else ''
                cmap = {l: t for l, t in it["choices"]}
                body.append(f"""<div class="qcard{miss}">
  <div class="tag"><span class="qn">Q{it['n']}</span></div>
  {ctx}
  <div class="stem">{esc(it['question'])}</div>
  {render_choices(it['choices'])}
  <div class="ans-head" style="margin-top:10px;"><span class="badge">✓</span>
    <div><div class="lab">Answer</div><div class="big">{esc(it['answer'])}</div></div></div>
  {render_answer_body(it, cmap)}
</div>""")
            pages.append(f'<div class="page rev">{"".join(body)}</div>')

    style = css(width, height, margin, base, font)
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(title)}</title><style>{style}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


# ------------------------------------------------------------ browser / render
def find_browser():
    names = ["chrome", "google-chrome", "google-chrome-stable", "chromium",
             "chromium-browser", "msedge", "microsoft-edge"]
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def render_pdf(browser, html_path, pdf_path):
    with tempfile.TemporaryDirectory() as prof:
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
               f"--user-data-dir={prof}", f"--print-to-pdf={pdf_path}", html_path]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode != 0 or not os.path.exists(pdf_path):
            sys.stderr.write(r.stderr.decode("utf-8", "replace")[-800:] + "\n")
            return False
    return True


# ---------------------------------------------------------------------- driver
def main():
    # Be robust to non-UTF-8 consoles (e.g. Windows cp1252): never crash on output.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Build an e-reader quiz PDF from JSON.")
    ap.add_argument("input", help="path to the quiz JSON dataset")
    ap.add_argument("-o", "--output", help="output PDF path (default: <input>.pdf)")
    ap.add_argument("--page", default=None, choices=list(PAGE_PRESETS),
                    help="page/device preset (default: scribe, or dataset 'page')")
    ap.add_argument("--mode", default="flip", choices=["flip", "review"],
                    help="flip = flashcard (default); review = answers inline")
    ap.add_argument("--font", default="sans", choices=["sans", "serif"])
    ap.add_argument("--shuffle", action="store_true",
                    help="shuffle questions within each section")
    ap.add_argument("--no-pdf", action="store_true",
                    help="emit HTML only (skip PDF rendering)")
    args = ap.parse_args()

    data, sections, total = load_dataset(args.input)

    if args.shuffle:
        import random
        for s in sections:
            random.shuffle(s["questions"])

    preset = args.page or data.get("page") or "scribe"
    if preset not in PAGE_PRESETS:
        die(f"unknown page preset {preset!r}; choose from {list(PAGE_PRESETS)}")
    w, h, m, base = PAGE_PRESETS[preset]

    html = build_html(data, sections, total, args.mode, w, h, m, base, args.font)

    in_path = Path(args.input)
    out_pdf = Path(args.output) if args.output else in_path.with_suffix(".pdf")
    html_path = out_pdf.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")

    print(f"parsed {total} questions "
          f"({len([s for s in sections if s['name']])} named sections) "
          f"| preset={preset} mode={args.mode}")
    print(f"wrote {html_path}")

    if args.no_pdf:
        print("--no-pdf set: HTML only. Open it and Print -> Save as PDF.")
        return

    browser = find_browser()
    if not browser:
        print("no Chrome/Edge found; wrote HTML only. Install Chrome or Edge, "
              "or open the HTML and Print -> Save as PDF.", file=sys.stderr)
        return

    ok = render_pdf(browser, str(html_path.resolve()), str(out_pdf.resolve()))
    if ok:
        size = out_pdf.stat().st_size
        print(f"wrote {out_pdf} ({size:,} bytes) via {Path(browser).name}")
    else:
        die("PDF render failed; the HTML was written. Open it and Print -> Save as PDF.")


if __name__ == "__main__":
    main()

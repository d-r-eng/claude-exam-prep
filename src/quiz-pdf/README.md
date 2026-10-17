# quiz-pdf

A shareable **Claude Code skill** that turns a JSON practice test into an
e-reader-friendly PDF study deck. Default layout is **flashcard flip**: the
question and its choices sit on one page; the **next page** reveals the correct
answer and explanation — so you can test yourself, then flip.

Deterministic and offline: a bundled Python script (standard library only) does
JSON → HTML → PDF via headless Chrome/Edge. No pip installs, no network, no
per-render LLM tokens.

## Install (share with others)

Copy this folder into a skills directory:

- **Project scope:** `<your-repo>/.claude/skills/quiz-pdf/`
- **User scope:** `~/.claude/skills/quiz-pdf/`

Then invoke it in Claude Code with `/quiz-pdf path/to/quiz.json`.

## Run the script directly

```bash
python scripts/build_quiz_pdf.py references/example.json --page scribe
# -> writes references/example.html and references/example.pdf
```

Options:

| Flag | Default | Meaning |
|---|---|---|
| `-o, --output` | `<input>.pdf` | Output PDF path. |
| `--page` | `scribe` | `scribe` · `remarkable` · `paperwhite` · `generic-6` · `a4` · `letter`. |
| `--mode` | `flip` | `flip` = flashcard; `review` = answers shown inline. |
| `--font` | `sans` | `sans` or `serif`. |
| `--shuffle` | off | Shuffle questions within each section. |
| `--no-pdf` | off | Emit HTML only (for machines without Chrome/Edge). |

If no Chrome/Edge is found, the script still writes the self-contained HTML —
open it and **Print → Save as PDF**.

## Input format

A single JSON object with a `title` and **either** `sections` or a flat
`questions` array. Each question needs `question`, `choices`, and `answer`;
`explanation`, `topic`, `context`, `distractor_notes`, and `your_answer` are
optional. See **`references/schema.md`** for the full reference and
**`references/example.json`** for a runnable sample.

## Requirements

- Python 3.8+
- Google Chrome or Microsoft Edge (for PDF rendering only; HTML works without it)

## Load onto a device

Connect by USB and drop the PDF into the device's `documents/` folder, or email it
to your Send-to-Kindle address.

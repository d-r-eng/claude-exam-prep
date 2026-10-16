---
name: quiz-pdf
description: Use when the user wants to turn a practice test / question bank into an e-reader-friendly PDF — flashcard-style study decks where the question and choices are on one page and the next page reveals the correct answer and explanation. Triggers on "flashcard PDF", "e-reader quiz", "practice test PDF", "study deck from JSON", "Kindle/reMarkable quiz PDF". Accepts a JSON dataset (preferred) or raw questions to convert first.
argument-hint: "path/to/quiz.json [--page scribe|remarkable|paperwhite|generic-6|a4|letter] [--mode flip|review]"
---

# quiz-pdf — JSON practice test → e-reader flashcard PDF

Turn a JSON dataset of questions into a print-ready, grayscale, e-reader-optimized
PDF. Default layout is **flashcard flip**: each question + its choices fill one
page; the **next page** reveals the correct answer and explanation. A deterministic
bundled script does JSON → HTML → PDF (headless Chrome/Edge). You (Claude) validate
the input and invoke the script — you do **not** generate the PDF markup yourself.

## The engine

`scripts/build_quiz_pdf.py` — Python 3 standard library only, no pip installs.

```
python scripts/build_quiz_pdf.py INPUT.json [-o OUT.pdf]
    [--page scribe|remarkable|paperwhite|generic-6|a4|letter]   # default: scribe
    [--mode flip|review]        # flip = flashcard (default); review = answers inline
    [--font sans|serif] [--shuffle] [--no-pdf]
```

It prints the question count, the written HTML path, and the final PDF path + size.

## How to run a request

1. **Get the dataset.** If the user gave a JSON path, use it. If none is provided
   and you can't find an obvious `*.json`, ask for the path. Never invent questions.

2. **If the user has raw questions (not JSON yet):** convert them to the schema in
   `references/schema.md` first (write a `.json` file), then proceed. Required
   per-question fields are `question`, `choices`, `answer`; add `explanation`,
   `topic`, `context`, `distractor_notes`, `your_answer` when available.

3. **Pick options.** Default `--page scribe` and `--mode flip` unless the user
   named a device or asked for an inline answer-key (then `--mode review`). Honor
   any `page` set inside the dataset unless the user overrides it.

4. **Invoke the script** from the skill directory (or with an absolute path to it).
   Report the output PDF path and page count back to the user.

5. **If it reports no Chrome/Edge found** (or you already know none is installed),
   re-run with `--no-pdf` to emit the HTML, and tell the user to open it and
   Print → Save as PDF on their machine. The HTML is self-contained.

## Input format (summary)

Top level: `title`, optional `subtitle` / `meta` / `page`, then **either**
`sections: [{name, questions:[…]}]` **or** a flat `questions: [...]`.

Each question: `question` (supports `` `code` `` and `**bold**`), `choices`
(list of strings → auto-labeled A/B/C…, or list of `{label,text}`, or a
`{label: text}` object), and `answer` (a choice label like `"D"`, or a 0-/1-based
index). Optional: `context`, `explanation`, `distractor_notes {label: why}`,
`topic`, `your_answer`. Full reference: `references/schema.md`. Runnable sample:
`references/example.json`.

## Page presets

`scribe` 6.2×8.27in (Kindle Scribe, default) · `remarkable` 6.18×8.27 ·
`paperwhite` 4.12×5.49 · `generic-6` 4.5×6.0 · `a4` · `letter`. All output is
grayscale, high-contrast, and uses ✓/✗ + borders (no reliance on color) so it
reads cleanly on e-ink.

## Notes

- **Flip integrity:** each reveal starts on a fresh page so the flip lines up. If a
  question's choices are unusually long and overflow one page, its answer still
  starts on the next page boundary.
- **Deterministic & offline:** no network, no LLM tokens per render — the same JSON
  always produces the same PDF.
- Load the deck onto a device by USB (drop into `documents/`) or via Send-to-Kindle.

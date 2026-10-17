# Quiz dataset JSON schema

The `quiz-pdf` engine reads a single JSON object. Only three per-question fields
are required — `question`, `choices`, `answer`. Everything else is optional and
enriches the reveal page.

## Top level

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | recommended | Shown on the cover. |
| `subtitle` | string | no | Cover subtitle. |
| `meta` | object | no | `{ "author", "date", "source", "kicker" }` — shown on the cover. |
| `page` | string | no | Default device preset (CLI `--page` overrides). See presets below. |
| `sections` | array | one of | `[{ "name", "questions": [...] }]` — grouped decks. |
| `questions` | array | one of | Flat deck (no sections). Use this **or** `sections`. |

Provide **either** `sections` or a top-level `questions` array.

## Question object

| Field | Type | Required | Notes |
|---|---|---|---|
| `question` | string | **yes** | The stem. Supports `` `code` `` and `**bold**`. |
| `choices` | see below | **yes** | The answer options. |
| `answer` | string/int | **yes** | Correct choice — a label (`"D"`) or an index. |
| `context` | string | no | Scenario/passage shown above the stem (alias: `scenario`). |
| `explanation` | string | no | Why the correct answer is right (shown on reveal). |
| `distractor_notes` | object | no | `{ "A": "why A is wrong", ... }`. |
| `topic` | string | no | Study-area tag (alias: `study_area`). |
| `your_answer` | string/int | no | Your selected choice — renders a ✗ on reveal (results review). |

### `choices` accepts three shapes

```jsonc
"choices": ["First option", "Second option", "Third"]          // auto-labeled A, B, C
"choices": [{"label": "A", "text": "First"}, {"label": "B", "text": "Second"}]
"choices": {"A": "First option", "B": "Second option"}
```

### `answer` / `your_answer` accept

- a **label** matching a choice: `"D"` (case-insensitive), or
- an **index**: `0`-based or `1`-based integer (both are tried).

## Page presets

| Preset | Size (in) | Device |
|---|---|---|
| `scribe` (default) | 6.2 × 8.27 | Kindle Scribe (1860×2480 @300ppi) |
| `remarkable` | 6.18 × 8.27 | reMarkable 2 |
| `paperwhite` | 4.12 × 5.49 | Kindle Paperwhite |
| `generic-6` | 4.5 × 6.0 | common 6" e-ink |
| `a4` | 8.27 × 11.69 | ISO A4 (paper/tablet) |
| `letter` | 8.5 × 11 | US Letter (paper/tablet) |

## Minimal example

```json
{
  "title": "Sample Quiz",
  "questions": [
    {
      "question": "What does `--print` (`-p`) do for the Claude Code CLI?",
      "choices": [
        "Prints the CLAUDE.md file",
        "Runs non-interactively: processes the prompt, prints to stdout, exits",
        "Enables verbose logging",
        "Formats the output as a PDF"
      ],
      "answer": "B",
      "explanation": "`-p`/`--print` is the documented non-interactive mode for CI/CD pipelines.",
      "topic": "Claude Code · CLI"
    }
  ]
}
```

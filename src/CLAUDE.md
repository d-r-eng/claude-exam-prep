# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## What This Project Is

This is a Claude Code exam practice project — prompt-based commands, not a software project. There is no build system, no tests to run, and no compiled artifacts.

Two commands are available:

| Command | Exam | Invocation |
|---|---|---|
| `/fexam` | Claude Certified Architect (Foundations) — 5 domains | `.claude/commands/fexam.md` |
| `/pexam` | Claude Certified Architect – Professional (CCAR-P) — 7 domains | `.claude/commands/pexam.md` |

Both commands accept a difficulty argument: `easy | medium | hard | absurd | stats`. Mode (`instruction` default, or `exam`) is a separate axis selected as its own step during session start — not part of the command argument.

## Persistent Files

| File | Purpose | Written by |
|---|---|---|
| `workspace.md` | **Pre-session planning doc** for the session about to start. Shows watch-list of weak subtopics and recurring tricks drawn from history, plus a blank notes area for the user. Overwritten at the start of each practice session. **Not a historical log.** | Command (session start) |
| `fexam-performance.json` | Foundations learning record. Appended at session end. Tracks per-question subtopic, correct/incorrect, and the cognitive trap triggered on wrong answers. Used by stats mode and the session-start watch list. | `/fexam` command (session end) |
| `pexam-performance.json` | Professional learning record. Same schema as fexam, domains D1–D7. | `/pexam` command (session end) |

## Architecture: How Each Command Works

Each command is a structured prompt with these layers:

1. **Frontmatter** — registers the command name, description, and argument hint with the Claude Code harness.
2. **Difficulty and mode rules** — defines easy / medium / hard / absurd / stats behaviour (question construction) and instruction / exam mode (feedback cadence) as two independent axes.
3. **Arithmetic rule** — instructs use of `python3 -c "print(...)"` via Bash for all calculations.
4. **Session format** — greet → confirm difficulty → select mode → select domain(s) and question count → read history and write `workspace.md` → Q&A loop → final score + session logging.
5. **Domain content tables** — the exam subject matter with subtopic codes (e.g. `1.2`, `3.6`) used for performance tracking.
6. **Question generation guidelines** — domain proportions, distractor patterns, difficulty rules.
7. **Distractor bank** — reusable wrong-answer patterns with labeled correct answers.
8. **High-Yield Heuristics** (pexam only) — consolidated if-then quick-reference and rule-of-thumb tie-breaker.
9. **Session logging** — workspace.md format and performance JSON schema.

## Exam Domain Weights

### Foundations (`/fexam`)
| Domain | Weight |
|---|---|
| Agentic Architecture & Orchestration | 27% |
| Tool Design & MCP Integration | 18% |
| Claude Code Configuration & Workflows | 20% |
| Prompt Engineering & Structured Output | 20% |
| Context Management & Reliability | 15% |

### Professional (`/pexam`)
| Domain | Weight |
|---|---|
| Solution Design & Architecture | 17% |
| Claude Models, Prompting & Context Engineering | 13% |
| Integration | 19% |
| Evaluation, Testing & Optimization | 16% |
| Governance, Safety & Risk Management | 14% |
| Stakeholder Communication & Lifecycle Management | 14% |
| Developer Productivity & Operational Enablement | 7% |

Passing score for both: 720/1000.

## Editing Guidelines

- **Adding a domain or topic:** Add a new subtopic section in the domain content area and update the exam overview table weights so they still sum to 100%.
- **Adding distractors:** Extend the distractor bank. Keep the pattern: one clearly correct answer, three plausible-but-wrong alternatives.
- **Adjusting difficulty:** Difficulty definitions are in each command's Difficulty Level section. Easy = direct recall; medium = apply a concept; hard = multi-concept tradeoff; absurd = every option superficially plausible + known exam trap distractor. Difficulty is independent of mode — see each command's Mode section for instruction (default, feedback per question) vs exam (silent, feedback at the end).
- **Question count default:** 15 questions per session (user can override during the greeting flow).
- **Subtopic codes:** Every domain section has numbered subtopics (e.g. `1.2`, `3.6`). These codes are used in `performance.json` records — do not renumber existing codes when adding new ones.

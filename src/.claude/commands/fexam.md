---
name: fexam
description: Practice for the Claude Certified Architect (Foundations) exam across all 5 domains. Tracks performance over time and surfaces weak subtopics and recurring distractor traps.
argument-hint: "easy | medium | hard | absurd | stats"
---

# Claude Certified Architect (Foundations) — Full Exam Practice

## Language

**Default language is English.** Respond in English unless the user explicitly asks to switch to another language. This rule applies to all questions, feedback, and explanations throughout the session.

---

## Exam Overview

| Domain | Topic | Weight |
|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% |
| 2 | Tool Design & MCP Integration | 18% |
| 3 | Claude Code Configuration & Workflows | 20% |
| 4 | Prompt Engineering & Structured Output | 20% |
| 5 | Context Management & Reliability | 15% |

**Passing score:** 720/1000. Format: scenario-based multiple choice, one correct answer, three plausible distractors.

**The exam rewards:**
- Deterministic solutions over probabilistic ones when stakes are high
- Proportionate fixes (don't over-engineer)
- Root cause tracing (identify WHERE in the pipeline the failure originates)
- Low-effort, high-leverage fixes as first steps

---

## Difficulty Level

The user selected difficulty: **$ARGUMENTS**

Only `easy`, `medium`, `hard`, `absurd`, or `stats` are valid. If `$ARGUMENTS` is missing or not one of those five, stop and ask: "Please specify a difficulty level: easy, medium, hard, absurd, or stats."

| Level | What it means |
|---|---|
| **easy** | Direct recall — one concept per question, distractors are clearly wrong to anyone who studied the material |
| **medium** | Scenario-based reasoning — requires applying a concept to a realistic situation, distractors are plausible but one has a clear flaw |
| **hard** | Multi-step reasoning — scenario involves two or more interacting concepts, distractors are all defensible but one is strictly correct given the full context |
| **absurd** | Maximum deception — every option is superficially plausible; at least one distractor per question is drawn directly from the distractor bank's known exam traps; requires precise rule recall, not just broad concept knowledge |
| **stats** | Performance review — no questions. Reads `fexam-performance.json` and shows subtopic accuracy, recurring tricks, and weak-area recommendations. |

Apply this level consistently to every question generated in the session.

Difficulty governs question construction only. Feedback cadence is governed by **Mode** (instruction vs. exam), a completely separate axis selected as its own step during session start — see Mode below. Any difficulty can run in either mode.

### Absurd difficulty rules (applies only when `$ARGUMENTS` is `absurd`, regardless of mode)

- **Question construction:** every option (A, B, C, D) must be defensible at first glance — no obviously wrong answers. At least one distractor per question must be drawn directly from the distractor bank's hard/absurd patterns. This is in addition to the multi-concept requirement.
- The correct answer must require knowing a specific rule precisely, not just a general principle.
- Whether feedback is shown after each answer or held until the end is decided by Mode, not by this difficulty level.

---

## Mode

Mode is a separate axis from difficulty and is **not** part of `$ARGUMENTS`. It's selected as its own step during session start (see Session Format) and defaults to `instruction` if the user doesn't specify otherwise. Every difficulty level above can run in either mode.

| Mode | What it means |
|---|---|
| **instruction** (default) | Feedback shown after every answer: correct/incorrect, why the correct answer is right, why each distractor is wrong. |
| **exam** | Exam simulation — silent scoring. No feedback after each answer; score and full breakdown shown only at the end. |

### Exam mode rules (applies only when the session's mode is `exam`)

- After the user submits each answer: respond **only** with the next question. Do not reveal whether the answer was correct or incorrect.
- Do not explain any answer until all questions are complete.
- Track answers internally throughout the session.
- At the end, show:
  1. Final score (X/Y correct)
  2. Per-question breakdown: question number, the user's answer, the correct answer, and a 2–3 sentence explanation of why the correct answer is right and what was wrong with each distractor
  3. Weak-domain summary and offer to re-drill
- If the user asks whether they got a question right mid-session, reply: "I'll reveal all results at the end — keep going!"

---

### Stats mode (applies only when `$ARGUMENTS` is `stats`)

1. Read `fexam-performance.json` from the project root using the Read tool. If it does not exist, say: "No session history yet — complete a practice session first." and stop.
2. Use `python3` via Bash for **all** calculations — never compute percentages or averages mentally (see Arithmetic section).
3. Show each of the following sections:

**Session history (most recent 5)**
Tabular: date | difficulty | mode | domains | score/total | %. Sorted newest first.

**Subtopic accuracy (≥ 2 attempts only)**
Group all `questions` entries across all sessions by `subtopic`. For each: subtopic ID and label, correct/total, %. Flag any below 70% with ⚠️. Sort ascending by accuracy so the weakest are at the top.

**Weighted domain score**
Aggregate all questions across all sessions by domain (D1–D5). Use `python3` via Bash for all calculations. Show a table with columns: Domain | Score (correct/total) | Accuracy % | Weight | Contribution (pts). For domains with no recorded attempts, show "—" in Score and Accuracy columns and 0 pts in Contribution. Compute the weighted overall as sum of (accuracy × weight × 1000) across all domains with ≥1 attempt. Show the weighted total as a 1000-pt score. If all 5 domains have ≥1 attempt, flag PASS (≥720) or FAIL (<720); otherwise note coverage (e.g., "based on 3/5 domains — 65% of exam weight").

Domain weights for the calculation:
- D1 Agentic Architecture & Orchestration: 27%
- D2 Tool Design & MCP Integration: 18%
- D3 Claude Code Configuration & Workflows: 20%
- D4 Prompt Engineering & Structured Output: 20%
- D5 Context Management & Reliability: 15%

**Recurring tricks (appeared ≥ 2 times as wrong answers)**
Scan `trick` fields across all wrong answers. List any trick label that appears ≥ 2 times: the label, count, and a one-sentence reminder of why that distractor is wrong.

4. Close with: "Want to drill your weakest area? Tell me a difficulty level and I'll focus there."

---

## Arithmetic

For **all** numerical calculations in this skill — scores, percentages, domain averages, subtopic accuracy, trick counts — use Bash to run `python3 -c "print(...)"` instead of computing mentally. Examples:

- Session percentage: `python3 -c "print(round(11/15*100, 1))"`
- Subtopic accuracy: `python3 -c "print(round(8/12*100, 1))"`
- Passing threshold (score ≥ 720 on a 1000-point scale): `python3 -c "print(round(11/15*1000))"`

Never output a computed number without running it through `python3` first.

---

## Session Format

### On Session Start

1. Greet the user in their language
2. Confirm the difficulty level from `$ARGUMENTS` (e.g., "Starting a **medium** difficulty session.")
3. Ask which mode: **"Instruction mode (feedback after every question) or exam mode (silent scoring, feedback only at the end)?"** Default to `instruction` if the user doesn't specify or gives an ambiguous answer.
   - If `exam` is selected: also say "**Exam mode active — no feedback until all questions are complete.**"
4. Ask: **"¿Quieres practicar un dominio específico o todos los dominios? / Do you want to practice a specific domain or all domains?"**
5. Ask how many questions they want (default: 15)
6. Read `fexam-performance.json` if it exists. Write `workspace.md` (see Session Logging). If any subtopics have accuracy < 70% across ≥ 2 attempts, show a brief callout before Question 1: "**Watch:** [subtopic label] ([X]%) · [subtopic label] ([X]%)" — use `python3` for all percentages.
7. Begin immediately — no teaching upfront

### Question Format

- Present ONE question at a time
- Scenario-based: describe a real production situation, then ask what to do
- Options A, B, C, D — one correct, three plausible distractors
- Wait for the user to answer before showing the next question
- Show question number and domain: e.g., **Question 3/15 — Domain 1**

### After Each Answer (instruction mode only)

Show:
1. **CORRECT ✅** or **INCORRECT ❌**
2. **Why the correct answer is right** (2–3 sentences, grounded in the concept)
3. **Why each wrong answer is wrong** — one sentence per distractor explaining the specific flaw

In **exam** mode, skip this block entirely regardless of difficulty — see Exam mode rules above.

### After All Questions

Show:
- Final score (X/Y) — compute percentage and 1000-point scale score via `python3`
- List of questions answered incorrectly, with subtopic label and the trick that was triggered
- **If `domain_filter` is `all`:** show the weighted domain score table for the current session using `python3` via Bash. Columns: Domain | Score (correct/total from this session) | Accuracy % | Weight | Contribution (pts). Use the same domain weights as stats mode (D1 27%, D2 18%, D3 20%, D4 20%, D5 15%). Compute weighted total and flag PASS (≥720) or FAIL (<720).
- Offer to re-drill weak domains
- Append session record to `fexam-performance.json` — see Session Logging

---

## Domain 1: Agentic Architecture & Orchestration (27%)

### Key concepts to test

**Agentic loop (1.1)**
- Correct termination: check `stop_reason` field — `"end_turn"` = done, `"tool_use"` = continue
- Anti-pattern 1: checking `if response.content[0].type == "text"` — wrong because model can return text AND tool_use simultaneously
- Anti-pattern 2: checking for natural language signals ("I'm done") — ambiguous and unreliable
- Anti-pattern 3: arbitrary iteration caps as primary stopping mechanism
- Tool results MUST be appended to conversation history before next turn

**Multi-agent orchestration (1.2)**
- Hub-and-spoke: coordinator at centre, subagents never communicate directly
- Critical isolation: subagents do NOT inherit coordinator's history. Everything must be explicit in their prompt.
- Narrow decomposition failure: root cause is always the coordinator's decomposition logic, NOT downstream agents
- Dynamic subagent selection: coordinator should invoke only the subagents the query requires, NOT always run the full pipeline
- Iterative refinement loop: coordinator evaluates synthesis output for coverage gaps → re-delegates to subagents with targeted follow-up queries → re-invokes synthesis until coverage is sufficient (critical for broad/multi-faceted topics)
- The exam tests tracing failures to their origin

**Subagent invocation (1.3)**
- Coordinator's `allowedTools` must include "Task" to spawn subagents
- `AgentDefinition` config: sets descriptions, system prompts, and tool restrictions per subagent type
- Parallel spawning: emit multiple Task calls in ONE coordinator response (faster)
- `fork_session`: independent branches from shared baseline
- Context passing must include structured metadata (source URLs, doc names, page numbers) for attribution
- Coordinator prompt design: specify research goals and quality criteria — NOT step-by-step procedural instructions. Goals allow subagents to adapt; procedures lock them into a fixed path.

**Workflow enforcement (1.4)**
- Prompt-based guidance = probabilistic (non-zero failure rate)
- Programmatic hooks/gates = deterministic (works every time)
- Rule: financial, security, compliance → programmatic. Style/formatting → prompt is fine.
- Multi-concern decomposition: split into discrete investigation items → investigate each in parallel with shared context → synthesise a unified resolution (don't process sequentially when concerns are independent)
- Handoff summaries must be self-contained (human agent has no transcript access)

**SDK Hooks (1.5)**
- PostToolUse: intercepts AFTER execution, BEFORE model processes result → normalise data formats
- Tool call interception: intercepts BEFORE execution → block/redirect based on business rules
- A single compliance failure → use hook, never a prompt

**Task decomposition (1.6)**
- Fixed sequential (prompt chaining): predetermined steps, reliable, cannot adapt
- Dynamic adaptive: generates subtasks from discoveries, flexible, less predictable
- Adaptive algorithm for open-ended tasks: map structure → identify high-impact areas → create prioritised plan → adapt plan as dependencies are discovered at each step
- Attention dilution: too many files in one pass → inconsistent depth. Fix: per-file passes + separate cross-file integration pass

**Session management (1.7)**
- `--resume`: use when context is still valid
- `fork_session`: use for divergent approaches from same baseline
- Fresh start + summary injection: use when files changed or context is stale
- After code modifications: inform agent of SPECIFIC file changes, not re-explore everything

---

## Domain 2: Tool Design & MCP Integration (18%)

### Key concepts to test

**Tool descriptions (2.1)**
- Descriptions are THE mechanism for tool selection (not supplementary)
- Minimal descriptions ("Retrieves customer information") cause misrouting between similar tools
- Fix for misrouting: expand descriptions. NOT few-shot examples (wrong root cause), NOT routing classifiers (over-engineered first step)
- Good description includes: purpose, input format, example queries, edge cases, explicit "use THIS vs THAT" boundaries
- System prompt keyword conflicts can override well-written descriptions

**Error handling (2.2)**
- Four error categories: Transient (retry), Validation (fix input), Business (not retryable, alternative workflow), Permission (escalate)
- MCP `isError` flag: the protocol-level mechanism for signaling tool failures back to the model (distinct from returning an error-shaped success response)
- Critical distinction: access failure (tool couldn't reach source → consider retry) vs valid empty result (source reached, no matches → do NOT retry)
- Recovery location: transient errors should be handled locally within the subagent; propagate only errors the subagent cannot resolve, and always include partial results and what was attempted
- Error metadata: `errorCategory`, `isRetryable` boolean, human-readable description

**Tool distribution (2.3)**
- Optimal: 4-5 tools per agent, scoped to role
- Replace generic tools with constrained alternatives: e.g., replace a generic `fetch_url` with a `load_document` tool that validates URLs before calling. Reduces misuse without limiting capability.
- `tool_choice` options: `"auto"` (default), `"any"` (must call a tool), `{"type": "tool", "name": "X"}` (force specific tool)
- Scoped cross-role tools: give synthesis agent a constrained verify_fact instead of routing through coordinator for 85% simple lookups

**MCP configuration (2.4)**
- Project-level: `.mcp.json` in repo → version-controlled, shared with team
- User-level: `~/.claude.json` → personal, NOT shared
- `${GITHUB_TOKEN}` syntax in `.mcp.json` keeps credentials out of version control
- Tools from ALL configured MCP servers are discovered and available simultaneously at connection time
- MCP resources: expose content catalogs (issue summaries, documentation hierarchies, database schemas) to give the agent visibility into available data without requiring exploratory tool calls
- Enhance MCP tool descriptions to explain capabilities and outputs — prevents the agent from defaulting to built-in tools (Grep, Bash) when a more capable MCP tool exists
- Use existing community servers first; build custom only for team-specific workflows

**Built-in tools (2.5)**
- Grep: searches file CONTENTS. Use to find function callers, imports, error messages
- Glob: matches file PATHS. Use to find files by extension or naming pattern
- Edit: targeted modification with unique text anchors. Fallback: Read + Write for full file
- Exploration order: Grep entry points → Read to follow imports. Do NOT read all files upfront.

---

## Domain 3: Claude Code Configuration & Workflows (20%)

### Key concepts to test

**CLAUDE.md hierarchy (3.1)**
- User-level (`~/.claude/CLAUDE.md`): only YOU, not version-controlled, NOT shared via git
- Project-level (`.claude/CLAUDE.md` or root `CLAUDE.md`): everyone, version-controlled
- Directory-level: applies when working in that specific directory only
- Exam trap: new team member not getting instructions → root cause is user-level instead of project-level config
- `/memory` command: debugging tool for inconsistent behaviour across sessions
- `@import` syntax for modular organisation; `.claude/rules/` for topic-specific rule files

**Custom commands and skills (3.2)**
- Slash commands: `.claude/commands/` (project-scoped, shared via git); `~/.claude/commands/` (personal, not shared)
- Skills: `.claude/skills/` with `SKILL.md` frontmatter (project-scoped); `~/.claude/skills/` (personal — use a different name to avoid overriding teammates' version)
- Skill frontmatter: `context: fork` (isolated sub-agent, verbose output stays contained), `allowed-tools` (restricts tools), `argument-hint` (prompts for parameters)
- Skills = on-demand, task-specific. CLAUDE.md = always-loaded, universal standards. Never mix these.

**Path-specific rules (3.3)**
- `.claude/rules/` files with YAML frontmatter `paths: ["**/*.test.tsx"]`
- Advantage over directory CLAUDE.md: glob patterns match files across the ENTIRE codebase
- Loads ONLY when editing matching files → token efficiency

**Plan mode vs direct execution (3.4)**
- Plan mode when: large-scale changes, multiple valid approaches, architectural decisions, multi-file modifications (45+ files)
- Direct execution when: well-understood single-file bug fix, clear limited scope
- Explore subagent: isolates verbose discovery from main conversation, returns summaries
- Common pattern: plan mode for investigation → direct execution for implementation

**Iterative refinement (3.5)**
- Concrete input/output examples beat prose descriptions every time (2-3 examples)
- Test-driven iteration: write tests first, share failures
- Interview pattern: have Claude ask questions before implementing
- Batch feedback when fixes interact; sequential when issues are independent

**CI/CD integration (3.6)**
- `-p` flag: non-interactive mode. Without it, CI job hangs waiting for input. THIS IS TESTED.
- `--output-format json --json-schema`: machine-parseable structured findings
- CLAUDE.md provides project context to CI: document testing standards, fixture conventions, and review criteria so CI-invoked Claude Code produces higher-quality output
- Provide existing test files in context so test generation avoids duplicating scenarios already covered by the suite
- Same session that generated code is LESS effective at reviewing it (retains reasoning context)
- Re-reviews: include prior findings, instruct to report ONLY new/unaddressed issues

---

## Domain 4: Prompt Engineering & Structured Output (20%)

### Key concepts to test

**Explicit criteria (4.1)**
- Vague: "be conservative." Specific: "Flag only when claimed behaviour contradicts actual code. Skip style preferences."
- High false positive rates in ONE category destroy trust in ALL categories
- Fix: temporarily disable high-FP categories while improving prompts for them
- Severity calibration requires actual CODE EXAMPLES, not prose descriptions

**Few-shot prompting (4.2)**
- Most effective technique for consistency — beats more instructions or confidence thresholds
- Deploy when: inconsistent formatting, inconsistent judgment on ambiguous cases, extraction misses existing information
- For extraction from varied document structures (inline citations vs bibliographies, narrative vs structured tables): add few-shot examples demonstrating correct handling to address empty/null extraction of required fields
- Construct: 2-4 examples, each showing REASONING for choice over plausible alternatives
- Enables generalisation to novel patterns, not just memorisation

**Structured output with tool_use (4.3)**
- `tool_use` with JSON schema eliminates syntax errors. Prompt-based JSON can produce malformed output.
- `tool_use` does NOT prevent: semantic errors (line items not summing to total), field placement errors, fabrication
- `tool_choice "any"`: must call a tool, chooses which (guaranteed structured output, unknown doc types)
- Schema: use optional/nullable fields to PREVENT fabrication. "unclear" enum for ambiguous cases. "other" + detail string for extensible categories.

**Validation-retry loops (4.4)**
- Retry with: original document + failed extraction + specific validation error
- Effective for: format mismatches, structural errors, misplaced values
- NOT effective for: information genuinely absent from source
- `detected_pattern` fields: track what triggered each finding, enables systematic prompt improvement
- Self-correction validation flows: extract `calculated_total` alongside `stated_total` to flag arithmetic discrepancies; add `conflict_detected` boolean for inconsistent source data

**Batch processing (4.5)**
- Batch API: 50% cost savings, up to 24-hour window, no latency SLA, does NOT support multi-turn tool calling
- `custom_id` fields correlate each batch request to its response — required for targeted failure handling and resubmission
- Handle failures: identify failed documents by `custom_id`, resubmit only those with modifications (e.g., chunk oversized documents that hit context limits)
- Refine prompts on a sample set before batch-processing large volumes to maximise first-pass success and reduce iterative resubmission cost
- Synchronous API: blocking workflows (pre-merge checks, developer waits for result)
- Batch API: latency-tolerant workflows (overnight reports, weekly audits)
- Exam trap: using batch for everything. Keep blocking workflows synchronous.

**Multi-instance review (4.6)**
- Same session reviewing its own output = less effective (retains reasoning context, less likely to question decisions)
- Independent instance without prior context catches more subtle issues
- Per-file local passes + separate cross-file integration pass = prevents attention dilution
- Verification pass: model self-reports confidence alongside each finding to enable calibrated routing — distinct from aggregate confidence thresholds
- Confidence-based routing: low-confidence findings → human review. Calibrate with labelled validation sets.

---

## Domain 5: Context Management & Reliability (15%)

### Key concepts to test

**Context preservation (5.1)**
- Progressive summarisation trap: compresses specific values ("$247.83 for order #8891") into vague summaries
- Fix: persistent "case facts" block with transactional facts. Include in every prompt. Never summarise it.
- Multi-turn API calls: every subsequent request must include the complete conversation history — omitting prior turns breaks coherence
- "Lost in the middle" effect: models process beginning and end reliably, middle may be missed. Fix: key summaries at the START, explicit section headers.
- Trim verbose tool results to relevant fields BEFORE appending to context
- Upstream agent optimisation: return structured key facts, not verbose reasoning chains

**Escalation and ambiguity (5.2)**
- Valid triggers: explicit human request (honour IMMEDIATELY, no investigation first), policy gaps, inability to make progress
- Invalid triggers: sentiment/frustration, self-reported confidence scores
- Frustration nuance: if issue is straightforward + customer is frustrated → acknowledge + offer resolution. Only escalate if customer REITERATES human preference after you offer help.
- Ambiguous customer match: ask for additional identifiers. Do NOT select based on heuristics.

**Error propagation (5.3)**
- Structured error context: failure type, what was attempted, partial results, alternative approaches
- Anti-pattern 1: silent suppression (empty result marked success) → prevents any recovery
- Anti-pattern 2: workflow termination on single failure → throws away partial results
- Access failure vs valid empty result (same as Domain 2 — reinforced across domains)
- Coverage annotations: note which findings are well-supported vs which areas have gaps

**Codebase exploration (5.4)**
- Context degradation: agent references "typical patterns" instead of specific classes → context filled with discovery output
- Mitigation: scratchpad files (write findings to file), subagent delegation, summary injection before next phase, `/compact`
- Crash recovery: each agent exports structured state to manifest file; coordinator loads manifest on resume

**Human review and confidence (5.5)**
- 97% overall accuracy can hide 40% error rate on a specific document type
- Always validate by document type AND field segment before automating
- Stratified random sampling of high-confidence extractions detects novel error patterns
- Field-level confidence calibration with labelled validation sets

**Information provenance (5.6)**
- Each finding needs: claim + source URL + document name + relevant excerpt + publication date
- Two conflicting credible sources: annotate BOTH with attribution. Do NOT arbitrarily select one.
- Temporal awareness: different dates explain different numbers (not contradictions)
- Rendering: financial data → tables, news → prose, technical findings → structured lists

---

## Question Generation Guidelines

When generating questions:

1. **Always scenario-based** — describe a real production situation (agent behaving unexpectedly, CI breaking, misrouted tool call, etc.)
2. **One clearly correct answer** — grounded in the concepts above
3. **Three plausible distractors** — use the specific wrong patterns the exam favours:
   - The probabilistic fix when a deterministic one is needed
   - The downstream component when the coordinator is the root cause
   - The over-engineered solution when a simple fix is correct
   - Conflating access failure with valid empty result
   - User-level config when project-level is needed
4. **Cover all domains proportionally** over a full session: ~4 D1, ~3 D2, ~3 D3, ~3 D4, ~2 D5 per 15 questions
5. **Match difficulty to `$ARGUMENTS`**: easy = direct recall, medium = single-concept scenarios, hard/absurd = multi-step reasoning with interacting concepts. For `absurd`: every option must be defensible and at least one distractor per question must be drawn from the bank below. Do not vary within a session. Mode (instruction/exam) is orthogonal — it changes feedback cadence only, never question construction.
6. **Validate before outputting** — before presenting each question, verify it passes all three checks:
   - **Self-contained:** every fact needed to distinguish the correct answer from the distractors is present in the scenario stem. The user must be able to reach the correct answer from what is written, without assuming anything unstated.
   - **No answer-option drift:** no answer option introduces new information that was not established in the scenario. Distractors must exploit the scenario, not add to it.
   - **Single unambiguous winner:** exactly one answer is strictly better than the others given only what is written. If two answers are defensible from the scenario as stated, rewrite the scenario to resolve the ambiguity before presenting the question.

---

## Distractor Bank (reuse these patterns)

### All difficulty levels

| Situation | Correct answer | Common distractors |
|---|---|---|
| High-stakes compliance failure | Programmatic hook/gate | Enhanced system prompt, few-shot examples, routing classifier |
| Agent terminates prematurely | Check `stop_reason` | Check content type, add iteration cap, parse natural language |
| Multi-agent coverage gap | Coordinator decomposition | Web search subagent, synthesis subagent, retrieval subagent |
| Tool misrouting | Expand tool descriptions | Add routing classifier, merge tools, add few-shot |
| New team member not getting instructions | Move to project-level CLAUDE.md | Update user-level, add to skills, use /memory |
| CI pipeline hangs | Add `-p` flag for non-interactive mode | `--timeout`, `--non-interactive`, `--batch` (flags don't exist); `CLAUDE_HEADLESS=true` (env var doesn't exist); redirect stdin from `/dev/null` (Unix workaround — doesn't address Claude Code's input model); use batch API (different use case entirely) |
| Escalation rate miscalibrated — agent escalates simple cases, handles complex ones | Add explicit escalation criteria with few-shot examples showing when to escalate vs resolve | Route by self-reported confidence score (LLM confidence poorly calibrated — agent is already confident on the hard cases it mishandles); deploy separate classifier model (over-engineered before prompt optimisation is tried); use sentiment analysis (sentiment ≠ case complexity) |
| Tool returns empty array, agent retries | Treat as valid empty result, no retry | Retry with backoff, escalate immediately, check permissions |
| Synthesis report has no attribution | Fix context passing (add structured metadata) | Fix synthesis agent prompt, fix web search agent, fix coordinator |

### Hard and absurd only

These distractors involve two or more interacting concepts, near-correct reasoning that breaks at an edge case, or distinctions the exam is known to exploit. Use them at `hard` and `absurd` difficulty (in either mode — exam mode just changes when feedback is shown). At `absurd`, every option in the question must be constructed at this level of plausibility.

| Situation | Correct answer | Hard/absurd/exam distractors and why they fail |
|---|---|---|
| Subagent produces wrong output; coordinator passed a complete transcript | Fix coordinator decomposition — transcript doesn't substitute for structured task prompt | "Give subagent access to coordinator memory" (wrong layer); "Add a PostToolUse hook to reformat output" (treats symptom not cause); "Use `fork_session` instead of Task" (unrelated to decomposition quality) |
| PostToolUse hook needed to normalise data vs. block a risky action | PostToolUse normalises; tool-call interception blocks | Swapping the two is the trap — both sound like "intercepting tool calls"; "add validation inside the tool itself" ignores that you don't always own the tool |
| Agent context fills with discovery output, starts referencing "typical patterns" | Delegate exploration to subagent or write findings to scratchpad file | "Use `/compact`" (compresses but doesn't prevent recurrence); "Increase context window" (not a solution Claude Code exposes); "Switch to fresh session" (loses all findings) |
| Blocking workflow (pre-merge check) running slowly; engineer suggests Batch API | Keep synchronous API — Batch has no latency SLA | "Batch API at 50% cost is always preferable" (ignores latency constraint); "Add `--output-format json`" (unrelated to throughput); "Use multi-turn tool calling in Batch" (Batch doesn't support it) |
| Two credible sources give conflicting figures for the same metric | Annotate both with full attribution; do not select one | "Choose the more recent publication" (temporal recency doesn't resolve credibility conflicts); "Average the two values" (fabrication); "Omit the figure and flag the gap" (silently drops valid data) |
| `tool_use` structured output returns semantically wrong total (line items don't sum) | `tool_use` prevents syntax errors only; add a post-extraction validation step | "Tighten the JSON schema" (schema can't enforce arithmetic relationships); "Switch to prompt-based JSON" (worse, not better); "Add a confidence threshold field" (doesn't catch deterministic calculation errors) |
| Customer explicitly says "I want a human" mid-session | Escalate immediately, no investigation | "Acknowledge frustration and offer resolution first" (correct for frustration; wrong when escalation is explicitly requested); "Offer one more attempt then escalate" (delay violates the rule); "Log request and finish current task" (ignores explicit trigger) |
| Agent loses specific transactional values after long session | Persist a "case facts" block and inject it at the start of every prompt | "Use progressive summarisation" (exactly the anti-pattern that loses specific values); "Increase summarisation frequency" (same failure mode faster); "Store values in tool metadata" (not accessible across turns) |
| Path-specific rule needs to apply to test files across multiple packages | Use `.claude/rules/` with `paths: ["**/*.test.tsx"]` glob | "Add a directory-level CLAUDE.md in each package" (doesn't scale, misses new packages); "Add rule to root CLAUDE.md" (loads always, wastes tokens); "Use `@import` in CLAUDE.md" (imports whole file, not path-scoped) |
| Coordinator spawns subagents sequentially; task is embarrassingly parallel | Emit all Task calls in a single coordinator response | "Use `fork_session` for parallel branches" (fork is for divergent approaches from a baseline, not standard parallelism); "Increase coordinator's `allowedTools`" (already has Task; order of emission is the issue); "Add a synchronisation hook between agents" (adds latency, wrong root cause) |
| 97% overall extraction accuracy; specific document type has 40% error rate | Validate accuracy by document type and field segment before automating | "97% overall meets the accuracy bar" (hides the segment failure); "Route low-confidence documents to human review" (confidence scores may be miscalibrated for this doc type); "Add more few-shot examples to the main prompt" (treats all doc types as one population) |
| Re-review of same output by the session that generated it finds fewer issues | Use an independent instance without prior context | "Increase review temperature for more variation" (doesn't remove reasoning context); "Add explicit review instructions to the same session" (same session still retains its original reasoning); "Use multi-instance review with shared context" (shared context defeats the purpose) |
| MCP server credential must be shared with the team without exposing secrets | Use `${ENV_VAR}` substitution in project-level `.mcp.json` | "Store token in `~/.claude.json`" (user-level, not shared); "Hardcode token in `.mcp.json`" (exposes secret in version control); "Pass token via system prompt" (not the MCP configuration layer) |
| Multi-file code review produces inconsistent depth, missed bugs, and contradictory findings across files | Split into focused per-file local analysis passes + separate cross-file integration pass | "Switch to a higher-tier model with a larger context window" (window size does not fix attention quality — dilution persists at any context size); "Run 3 independent full-PR passes and flag only consensus issues" (consensus voting suppresses intermittent bugs that only one pass catches) |
| Complex architectural change (e.g., monolith-to-microservices, 45+ files) — where to start? | Enter plan mode to explore, understand dependencies, and design before making changes | "Start with direct execution and let the implementation reveal natural service boundaries" (risks costly rework when dependencies discovered mid-implementation); "Use direct execution with comprehensive upfront instructions detailing the structure" (assumes correct structure without exploring the code) |

---

## Session Logging

### workspace.md — written at session start

`workspace.md` is a **planning document for the session about to begin** — not a historical log. Overwrite it before Question 1 using the Write tool. Its purpose is to surface known weak spots so the user can stay alert during the session.

Format:
```
# Session Plan — Foundations, [difficulty], [mode], [domain_filter], [N] questions
Date: [run `date +%Y-%m-%d` via Bash]

## Focus
Domain: [user's choice]   Questions: [N]   Difficulty: [level]   Mode: [instruction|exam]

## Watch List
[If fexam-performance.json exists and has subtopics with accuracy < 70% across ≥ 2 attempts:]
- [subtopic_id] [subtopic_label]: [correct]/[total] correct ([X]%) — watch for: [most frequent trick label for this subtopic, or "general weakness"]
[Repeat for each qualifying subtopic, sorted by accuracy ascending]

[If no qualifying history:]
No prior weak spots identified — starting fresh.

## Recurring Tricks to Avoid
[If any trick label has appeared ≥ 2 times as a wrong answer across all sessions:]
- [trick_label]: chosen [N] times — [one sentence on why this distractor is wrong]
[If none:] None recorded yet.

## Notes
[blank — user's scratchpad during the session]
```

Use `python3` via Bash for all accuracy percentages. Use the Read tool to load `fexam-performance.json` first.

---

### fexam-performance.json — appended at session end

After showing the final score, append a session record. Read the existing file with the Read tool (or initialise with `{"sessions": []}` if absent), append the new record, and write the updated JSON with the Write tool.

**Session record schema:**
```json
{
  "date": "YYYY-MM-DD",
  "difficulty": "easy|medium|hard|absurd",
  "mode": "instruction|exam",
  "domain_filter": "all|D1|D2|D3|D4|D5",
  "score": 11,
  "total": 15,
  "questions": [
    {
      "domain": "D3",
      "subtopic": "3.1",
      "subtopic_label": "CLAUDE.md hierarchy",
      "correct": true,
      "chosen": "A",
      "trick": null
    },
    {
      "domain": "D1",
      "subtopic": "1.2",
      "subtopic_label": "Multi-agent orchestration",
      "correct": false,
      "chosen": "C",
      "trick": "downstream_agent_not_coordinator"
    }
  ]
}
```

**Field rules:**
- `subtopic`: Use the section codes from the domain content tables (e.g. `"1.2"`, `"3.6"`, `"4.3"`). Every question must have one — assign it when generating the question, not after the answer.
- `trick`: When the answer was wrong, use a short snake_case label for the cognitive trap (e.g. `"probabilistic_fix_for_compliance"`, `"retrying_valid_empty_result"`, `"user_level_config_not_project"`, `"downstream_agent_not_coordinator"`, `"over_engineered_solution"`). Use `null` when correct.
- `chosen`: Always record the letter the user submitted, correct or not.
- `mode`: Record the mode selected during the session-start step (`"instruction"` or `"exam"`) — independent of `difficulty`.
- `date`: Run `date +%Y-%m-%d` via Bash — never hard-code.

Use `python3` via Bash for `score` (verify it matches the tally) and for any derived fields in stats mode.

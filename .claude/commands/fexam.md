---
name: fexam
description: Practice for the Claude Certified Architect (Foundations) exam across all 5 domains. Tracks performance over time and surfaces weak subtopics and recurring distractor traps.
argument-hint: "easy | medium | hard | absurd | exam | stats"
---

# Claude Certified Architect (Foundations) — Full Exam Practice

## Exam Overview

| Domain | Topic | Weight |
|---|---|---|
| 1 | Agentic Architecture & Orchestration | 27% |
| 2 | Tool Design & MCP Integration | 18% |
| 3 | Claude Code Configuration & Workflows | 20% |
| 4 | Prompt Engineering & Structured Output | 20% |
| 5 | Context Management & Reliability | 15% |

**Passing score:** 720/1000. Format: scenario-based multiple choice, one correct answer, three plausible distractors.

**Score-report weighting:** if `fexam-scorereport.json` exists in the project root, question selection is driven by the user's real exam results (29 test objectives, `O1`–`O29`), not by the domain weights above. See **Score-Report Weighting** below. The domain weights are still used for the weighted 1000-pt score and for filling the tier-3 share of a session.

---

## Difficulty Level

The user selected difficulty: **$ARGUMENTS**

Only `easy`, `medium`, `hard`, `absurd`, `exam`, or `stats` are valid. If `$ARGUMENTS` is missing or not one of those six, stop and ask: "Please specify a difficulty level: easy, medium, hard, absurd, exam, or stats."

| Level | What it means |
|---|---|
| **easy** | Direct recall — one concept per question, distractors are clearly wrong to anyone who studied the material |
| **medium** | Scenario-based reasoning — requires applying a concept to a realistic situation, distractors are plausible but one has a clear flaw |
| **hard** | Multi-step reasoning — scenario involves two or more interacting concepts, distractors are all defensible but one is strictly correct given the full context |
| **absurd** | Maximum deception — every option is superficially plausible; at least one distractor per question is drawn directly from the distractor bank's known exam traps; requires precise rule recall, not just broad concept knowledge |
| **exam** | Exam simulation — same question style as `hard`, but the session runs in **silent mode**: no feedback after each answer. Score and full breakdown are shown only at the end. |
| **stats** | Performance review — no questions. Reads `fexam-performance.json` and shows subtopic accuracy, recurring tricks, and weak-area recommendations. |

Apply this level consistently to every question generated in the session.

### Exam mode rules (applies only when `$ARGUMENTS` is `exam`)

- After the user submits each answer: respond **only** with the next question. Do not reveal whether the answer was correct or incorrect.
- Do not explain any answer until all questions are complete.
- Track answers internally throughout the session.
- At the end, show:
  1. Final score (X/Y correct)
  2. Per-question breakdown: question number, the user's answer, the correct answer, and a 2–3 sentence explanation of why the correct answer is right and what was wrong with each distractor
  3. Weak-domain summary and offer to re-drill
  4. The score-report view and the rest of the **After All Questions** block, including logging
- If the user asks whether they got a question right mid-session, reply: "I'll reveal all results at the end — keep going!"

### Absurd mode rules (applies only when `$ARGUMENTS` is `absurd`)

- Same feedback cadence as `hard`: show correct/incorrect after each answer, explain why, and analyse each distractor.
- **Question construction:** every option (A, B, C, D) must be defensible at first glance — no obviously wrong answers. At least one distractor per question must be drawn directly from the distractor bank's hard/absurd/exam patterns. This is in addition to the multi-concept requirement.
- The correct answer must require knowing a specific rule precisely, not just a general principle.

---

### Stats mode (applies only when `$ARGUMENTS` is `stats`)

1. Read `fexam-performance.json` from the project root using the Read tool. If it does not exist, say: "No session history yet — complete a practice session first." and stop.
2. Use `python3` via Bash for **all** calculations — never compute percentages or averages mentally (see Arithmetic section).
3. Show each of the following sections:

**Session history (most recent 5)**
Tabular: date | difficulty | domains | score/total | %. Sorted newest first.

**Subtopic accuracy (≥ 2 attempts only)**
Group all `questions` entries across all sessions by `subtopic`. For each: subtopic ID and label, correct/total, %. Flag any below 70% with ⚠️. Sort ascending by accuracy so the weakest are at the top.

**Weighted domain score**
Aggregate all questions across all sessions by domain (D1–D5). Use `python3` via Bash for all calculations. Show a table with columns: Domain | Score (correct/total) | Accuracy % | Weight | Contribution (pts). For domains with no recorded attempts, show "—" in Score and Accuracy columns and 0 pts in Contribution. Compute the weighted overall as sum of (accuracy × weight × 1000) across all domains with ≥1 attempt. Show the weighted total as a 1000-pt score. If all 5 domains have ≥1 attempt, flag PASS (≥720) or FAIL (<720); otherwise note coverage (e.g., "based on 3/5 domains — 65% of exam weight").

Use the domain weights from the Exam Overview table.

**Recurring tricks (appeared ≥ 2 times as wrong answers)**
Scan `trick` fields across all wrong answers. List any trick label that appears ≥ 2 times: the label, count, and a one-sentence reminder of why that distractor is wrong.

**Exam objectives: real exam vs practice**
Only if `fexam-scorereport.json` exists. Group all `questions` entries that carry an `objective` field by objective. Show a table sorted by tier then practice accuracy ascending: Objective ID | short label (≤ 8 words) | Tier | Exam % | Practice (correct/total) | Practice %. Show "—" for objectives with no practice attempts yet. Flag ⚠️ any tier-1 or tier-2 objective with practice accuracy < 80% or fewer than 3 attempts, since those are not yet proven fixed. Add a column **Edges retired** (retired/total, e.g. `2/6`) for tier-1/tier-2 objectives.

**Edge progress (tier 1 and 2)**
For each tier-1/tier-2 objective, list its edges: edge ID | short text | correct count toward retirement (e.g. `3/5`) | ✅ if retired. Sort edges by correct count ascending.

4. Close with: "Want to drill your weakest area? Tell me a difficulty level and I'll focus there."

---

## Arithmetic

For **all** numerical calculations — scores, percentages, domain averages, subtopic accuracy, trick counts — use Bash: `python3 -c "print(round(11/15*100, 1))"`. Never compute mentally.

---

## Session Format

### On Session Start

1. Greet the user. **Respond in English** unless they explicitly ask to switch languages.
2. Confirm the difficulty level from `$ARGUMENTS` (e.g., "Starting a **medium** difficulty session.")
   - If `exam`: also say "**Exam mode active — no feedback until all questions are complete.**"
3. Ask: **"¿Quieres practicar un dominio específico o todos los dominios? / Do you want to practice a specific domain or all domains?"**
4. Ask how many questions they want (default: 15)
5. Read `fexam-scorereport.json` if it exists and build the session's **question plan** (see Score-Report Weighting). Keep the plan internal — do not show it to the user.
6. Read `fexam-performance.json` if it exists. Write `workspace.md` (see Session Logging). If any subtopics have accuracy < 70% across ≥ 2 attempts, show a brief callout before Question 1: "**Watch:** [subtopic label] ([X]%) · [subtopic label] ([X]%)" — use `python3` for all percentages.
7. Begin immediately — no teaching upfront

### Question Format

- Present ONE question at a time
- Scenario-based: describe a real production situation, then ask what to do
- Options A, B, C, D — one correct, three plausible distractors
- Wait for the user to answer before showing the next question
- Show question number and domain: e.g., **Question 3/15 — Domain 1**

### After Each Answer (easy / medium / hard / absurd only)

Show:
1. **CORRECT ✅** or **INCORRECT ❌**
2. If incorrect: **Trap triggered: `snake_case_label`** — one sentence describing what the trap is and why it catches people. Assign this label before writing the explanation; it becomes the `trick` field in the JSON log and the `trick_description` is the same sentence written here.
3. **Why the correct answer is right** (2–3 sentences, grounded in the concept)
4. **Why each wrong answer is wrong** — one sentence per distractor explaining the specific flaw
5. If the question targeted a tier-1 or tier-2 objective, end with one line: *Exam objective [Oid] — you scored [exam_pct]% on this in the real exam.*

In **exam** mode, skip this block entirely — see Exam mode rules above.

### After All Questions

Show:
- Final score (X/Y) — compute percentage and 1000-point scale score via `python3`
- List of questions answered incorrectly, with subtopic label and the trick that was triggered
- **If `domain_filter` is `all`:** show the weighted domain score table for the current session using `python3` via Bash. Columns: Domain | Score (correct/total from this session) | Accuracy % | Weight | Contribution (pts). Use the domain weights from the Exam Overview table. Compute weighted total and flag PASS (≥720) or FAIL (<720).
- **Score-report view** (only if `fexam-scorereport.json` exists): a table in the style of the official score report, covering only objectives tested this session: Objective ID | short label | This session (correct/total, %) | Real exam %. Sort tier 1 first. Use `python3` for the percentages.
- Offer to re-drill weak domains
- Append session record to `fexam-performance.json` — see Session Logging

---

## Domain 1: Agentic Architecture & Orchestration (27%)

**Agentic loop (1.1)**
- Correct termination: check `stop_reason` field — `"end_turn"` = done, `"tool_use"` = continue
- Anti-pattern 1: checking `if response.content[0].type == "text"` — wrong because model can return text AND tool_use simultaneously
- Anti-pattern 2: checking for natural language signals ("I'm done") — ambiguous and unreliable
- Anti-pattern 3: arbitrary iteration caps as primary stopping mechanism
- Anti-pattern 4: breaking when `content == []` (empty content array) — wrong because a completed response always carries at least a text block; the array is never empty on a finished turn, so the loop spins indefinitely
- Tool results MUST be appended to conversation history before next turn
- Correct shape: append the assistant message (with its `tool_use` blocks), then ONE user message containing a `tool_result` block for EVERY `tool_use` block, each carrying the matching `tool_use_id`
- Full `stop_reason` set (exam tests the non-obvious ones):
  - `end_turn` → done, use the response
  - `tool_use` → run the tool(s), return results, loop
  - `max_tokens` → output was truncated. If the truncated response ends in an incomplete `tool_use` block, do NOT dispatch it; retry with a higher `max_tokens`. Never treat as a clean finish
  - `stop_sequence` → one of your stop sequences fired (terminal for this call)
  - `pause_turn` → a server-tool loop (web search, code execution) hit its iteration limit; send the assistant content back as-is to let it continue. NOT a completion, NOT an error
  - `refusal` → Claude declined; terminal. Handle explicitly (fallback/escalate), don't loop
  - `model_context_window_exceeded` → response filled the context window; treat as truncated
- Exam trap: a loop that only knows `end_turn`/`tool_use` will either spin or silently accept a truncated answer on the other values

**Multi-agent orchestration (1.2)**
- Hub-and-spoke: coordinator at centre, subagents never communicate directly
- Critical isolation: subagents do NOT inherit coordinator's history. Everything must be explicit in their prompt.
- Narrow decomposition failure: root cause is always the coordinator's decomposition logic, NOT downstream agents
- Dynamic subagent selection: coordinator should invoke only the subagents the query requires, NOT always run the full pipeline
- Iterative refinement loop: coordinator evaluates synthesis output for coverage gaps → re-delegates to subagents with targeted follow-up queries → re-invokes synthesis until coverage is sufficient (critical for broad/multi-faceted topics)
- The exam tests tracing failures to their origin

**Subagent invocation (1.3)**
- Coordinator's `allowedTools`/`tools` must include "Agent" (formerly "Task") to spawn subagents — without it, the coordinator silently does all work inline
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
- This subtopic = hooks in **agent applications** (Agent SDK). Hooks configured in Claude Code's `settings.json` for code-quality automation are subtopic **3.8**; the event names are the same.
- PreToolUse: BEFORE execution → block/redirect. Returns `permissionDecision`: `allow`|`deny`|`ask`|`defer` (exam trap: thinking it only accepts allow/deny)
- PostToolUse: AFTER execution, BEFORE model sees result → normalise data, write audit entries. ≠ logging inside tool implementation (framework-level; works for tools you don't own)
- UserPromptSubmit: on message submit, BEFORE any model processing → pre-processing requirements (audit entries, enforcement before model runs)
- A single compliance failure → use hook, never a prompt

**Task decomposition (1.6)**
- Fixed sequential (prompt chaining): predetermined steps, reliable, cannot adapt
- Dynamic adaptive: generates subtasks from discoveries, flexible, less predictable
- Adaptive algorithm for open-ended tasks: map structure → identify high-impact areas → create prioritised plan → adapt plan as dependencies are discovered at each step
- Attention dilution: too many files in one pass → inconsistent depth. Fix: per-file passes + separate cross-file integration pass
- Dynamic decomposition signals: the subtasks can't be listed until work starts (unknown codebase, investigation, research); an early finding changes what's worth doing next (a discovered dependency, a dead end, a new sub-question). The plan is a living list: add, drop and re-prioritise subtasks after each step
- Fixed-chain signals: the steps are known in advance, and auditability, reproducibility or pre-approval by compliance matters more than adaptivity
- Exam traps: decomposing by directory/module up front ("one subtask per folder") for an investigation whose scope is unknown; a fixed chain that runs every step "regardless of intermediate findings"; adding exhaustive logging to justify a dynamic planner in a regulated pipeline

**Session management (1.7)**
- `--resume`: use when context is still valid
- `fork_session`: use for divergent approaches from same baseline
- Fresh start + summary injection: use when files changed or context is stale
- After code modifications: inform agent of SPECIFIC file changes, not re-explore everything

## Domain 2: Tool Design & MCP Integration (18%)

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
- `"any"` guarantees A tool call, NOT which one. Only `{"type": "tool", "name": "X"}` guarantees a specific tool. With `any`/forced tool, the API prefills the assistant turn, so Claude emits no natural-language text before the `tool_use` block
- **Sequencing multi-tool workflows (prerequisite data first):**
  - Force the prerequisite on the first turn: `tool_choice: {"type": "tool", "name": "get_customer"}`, then switch back to `"auto"` for later turns. Exam trap: forcing the same tool on every turn locks the loop into calling it repeatedly
  - Make the dependency structural: the dependent tool takes the prerequisite's output as a REQUIRED parameter (e.g. `lookup_order(customer_id, …)`), so it cannot be called meaningfully without it
  - State the prerequisite in the dependent tool's description ("Requires `customer_id` from `get_customer`; call that first")
  - When the order is a business/compliance rule (verify identity before refund), enforce it programmatically (a gate that rejects `process_refund` until verification returned) — see 1.4
  - Dependent calls can't go in the same parallel batch: a response can emit several `tool_use` blocks at once only when their inputs are already known. Independent lookups → parallel; dependent → sequential turns
  - Wrong fixes: ordering the `tools` array (no effect on selection), "always call X first" in the system prompt (probabilistic), `"any"` (doesn't pick WHICH tool)
- Note, outside exam scope: the newest models (e.g. Opus 5.5) reject forced tool use (`any`/`tool`) with a 400 error. The exam still tests the `tool_choice` semantics above.

**MCP configuration (2.4)**
- MCP scope hierarchy (exam tests these distinctions):
  - **Project scope** (`.mcp.json` at repo root): version-controlled, shared with everyone on that repository, active in no other project
  - **Local scope**: per-project but PRIVATE to the engineer — not committed, not shared. Distinct from project scope even though both are per-project.
  - **User scope** (`~/.claude.json`): personal, available across ALL projects, not shared with teammates
  - **Machine scope**: every account on the host, regardless of project
  - Exam trap: confusing "local" (private/per-project) with "project" (shared/per-project)
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
- **Systematic exploration strategy** (the exam tests the strategy, not just which tool matches which target):
  1. **Glob** to map structure and shortlist candidate paths (cheap: returns paths, no contents)
  2. **Grep** to locate entry points, definitions and callers. Start with file-list output (`files_with_matches`) or counts to size the hit set, then content mode with a few context lines on the narrowed set. Scope with a path/glob/type filter
  3. **Read** only the files that matter, and only the relevant range (`offset`/`limit`) of large files
  4. Follow imports/calls outward one hop at a time, forming and testing a hypothesis at each step (incremental understanding)
  5. Record findings as you go (scratchpad file, or structured notes), and delegate broad sweeps to an Explore subagent that returns a summary, so raw output stays out of the main context (see 5.4)
- Anti-patterns: Read every file in a directory "for completeness"; `cat` whole trees through Bash; unscoped content-mode Grep across the monorepo (floods context); reading a 4,000-line file end to end to find one function; re-running the same broad search in each phase instead of reusing recorded findings
- Tracing a call path: Grep for the definition → Read it → Grep for callers of the symbol → Read only the call sites
- Unknown codebase, "where is X handled?": Grep for distinctive strings (route path, error message, config key) rather than guessing file names with Glob

## Domain 3: Claude Code Configuration & Workflows (20%)

**CLAUDE.md hierarchy (3.1)**
- User-level (`~/.claude/CLAUDE.md`): only YOU, not version-controlled, NOT shared via git
- Project-level (`.claude/CLAUDE.md` or root `CLAUDE.md`): everyone, version-controlled
- Directory-level: applies when working in that specific directory only
- Both user-level and project-level files load SIMULTANEOUSLY — neither overrides the other. Rules from both are in effect together. Exam trap: assuming the project file overrides or replaces the user-level file — a user-level preference that contradicts a project rule causes inconsistent behaviour for that user only.
- Exam trap: new team member not getting instructions → root cause is user-level instead of project-level config
- `/memory` command: debugging tool for inconsistent behaviour across sessions
- `@import` syntax for modular organisation; `.claude/rules/` for topic-specific rule files

**Custom commands and skills (3.2)**
- Slash commands: `.claude/commands/` (project-scoped, shared via git); `~/.claude/commands/` (personal, not shared)
- Skills: `.claude/skills/` with `SKILL.md` frontmatter (project-scoped); `~/.claude/skills/` (personal — use a different name to avoid overriding teammates' version)
- Skill frontmatter: `context: fork` (isolated sub-agent, verbose output stays contained), `allowed-tools` (allow ONLY the listed tools), `disallowed-tools` (block specific tools while all others remain available), `argument-hint` (prompts for parameters)
  - `allowed-tools` vs `disallowed-tools`: use `allowed-tools` for a minimum tool set (e.g., read-only skills); use `disallowed-tools` to remove destructive tools while retaining the full read set. Both can appear together.
- Skills = on-demand, task-specific. CLAUDE.md = always-loaded, universal standards. Never mix these.
- Skill folder structure: a skill is a **directory** (`skill-name/SKILL.md` as the entry point) that can contain supporting assets (`scripts/`, `references/`, etc.) co-located inside it — the skill folder is self-contained and portable
- `allowed-tools` is optional — when absent, the skill has access to all standard tools. Specify it only to restrict the skill to a minimum set.
- Script-orchestration pattern: `SKILL.md` instructs Claude to validate the input and invoke a bundled deterministic script via Bash, NOT generate the artifact itself. Enables offline, reproducible output without per-render LLM tokens. Distractor trap: using `context: fork` still has Claude generating output — it isolates conversation context but not non-determinism.
- Graceful fallback: skills must define what Claude does when a dependency (e.g., a renderer) is unavailable — emit the nearest useful intermediate artifact and instruct the user how to complete the final step manually. Silent failure and hard failure are both wrong.

**Path-specific rules (3.3)**
- `.claude/rules/` files with YAML frontmatter `paths: ["**/*.test.tsx"]`
- Advantage over directory CLAUDE.md: glob patterns match files across the ENTIRE codebase
- Rule files WITH `paths:` frontmatter: load ONLY when editing a matching file → token efficiency (conditional)
- Rule files WITHOUT `paths:` frontmatter: load at EVERY session launch (unconditional) — use for project-wide standards that must always be in effect regardless of what file is being edited. Exam trap: assuming all `.claude/rules/` files are conditional regardless of frontmatter.

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
- Batched issue descriptions: when several problems share a cause or their fixes touch the same code, list them ALL in one message (each with the failing input, actual output, expected output) so Claude designs one consolidated fix and evaluates it against the whole set. Drip-feeding interacting issues one per turn produces fixes that undo each other
- Targeted feedback: point at the specific failing case ("for input `2024-02-30` the parser returns a date; expected a validation error") — NOT "it's still wrong" or "make it more robust"
- Concrete examples over prose: 2–3 input→expected-output pairs define an ambiguous transformation better than paragraphs describing it
- Exam traps: "restart with a longer, more detailed prose spec" (still prose); "ask Claude to try again" with no new information; one issue per turn when issues interact; batching unrelated issues that should be verified independently

**CI/CD integration (3.6)**

- `-p` flag: non-interactive mode. Without it, CI job hangs waiting for input. THIS IS TESTED.
- `--output-format json --json-schema`: machine-parseable structured findings
- CLAUDE.md provides project context to CI: document testing standards, fixture conventions, and review criteria so CI-invoked Claude Code produces higher-quality output
- Provide existing test files in context so test generation avoids duplicating scenarios already covered by the suite
- Same session that generated code is LESS effective at reviewing it (retains reasoning context)
- Re-reviews: include prior findings, instruct to report ONLY new/unaddressed issues

**Enforcement vs guidance: settings permissions and hooks vs CLAUDE.md (3.7)**
- Core rule: **CLAUDE.md is context, not enforced configuration.** Claude reads it and usually follows it, but nothing stops a violation. Permission rules and hooks are enforced by Claude Code itself, whatever the model decides.
- Decision test for each line in a CLAUDE.md:
  - Must NEVER happen (read `.env`/secrets, `rm -rf`, push to main, touch prod config) → `permissions.deny` rule (or a PreToolUse hook when the condition needs logic)
  - Must ALWAYS happen after/before an action (format after edit, run tests, audit log) → hook (see 3.8)
  - Needs human confirmation each time (deploy script, `git push`) → `permissions.ask`
  - Style, conventions, architecture explanations, "prefer X over Y", domain knowledge → stays in CLAUDE.md
- Restructuring: move the hard constraint into settings and delete it from CLAUDE.md, or cut it to a one-line "why" so Claude doesn't waste attempts. Leaving it only in CLAUDE.md with "IMPORTANT"/"NEVER" in capitals is still probabilistic.
- Permission rule syntax (in `settings.json` → `"permissions": {"allow": [], "ask": [], "deny": []}`): `Bash(npm run test *)`, `Bash(git push *)`, `Read(./.env)`, `Read(./secrets/**)`, `Edit(./config/prod/**)`, `WebFetch(domain:example.com)`
- Evaluation order: **deny → ask → allow; first match wins; specificity doesn't matter.** An allow rule CANNOT carve an exception out of a matching deny rule. Hook decisions do not bypass deny/ask rules either.
- Settings scopes (highest precedence first):
  1. Managed settings (org/IT policy). Cannot be overridden: use for company-wide mandates
  2. Command line (`--settings`, `--disallowedTools`), for this session only
  3. `.claude/settings.local.json`: you, this project, gitignored
  4. `.claude/settings.json`: project, **committed, shared with the team**
  5. `~/.claude/settings.json`: you, all projects, not shared
- Team-wide enforcement → `.claude/settings.json` (committed). Org-wide, non-overridable → managed settings. Personal → user/local.
- Exam traps: "add NEVER in caps to CLAUDE.md"; "move it to `.claude/rules/` with a `paths:` glob" (still guidance, just scoped); "make it a skill" (on demand, not enforced); "put the deny in `settings.local.json`" for a team rule (not shared); "add an allow rule for the one exception" (deny wins); "user-level CLAUDE.md" (neither shared nor enforced)

**Claude Code hooks for automatic quality enforcement (3.8)**
- Purpose: make formatting, linting and tests happen after EVERY edit **independent of model instruction-following**. A CLAUDE.md line "always run prettier after editing" is probabilistic; a hook always runs.
- Configured under the `"hooks"` key in settings files. Team-shared → `.claude/settings.json` (committed). Personal → `~/.claude/settings.json` or `.claude/settings.local.json`.
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }
        ]
      }
    ]
  }
}
```
- `matcher` is matched against the tool name (`"Edit|Write"`, `"Bash"`, `"mcp__.*"`). With no matcher the hook fires on every tool call (wasteful for a formatter).
- The hook receives JSON on **stdin**: `tool_name`, `tool_input` (includes `file_path` for file tools), `tool_use_id`, `session_id`, `cwd`, `hook_event_name`.
- Exit codes: `0` = success (stderr goes to the debug log only; Claude never sees it). **`2` = blocking error: for PostToolUse, stderr is shown to Claude** so it can fix lint/test failures in its next step. Any other code (e.g. `1`) = non-blocking error: the action proceeds and Claude does not get the failure as feedback. Exam trap: using `exit 1` to "fail" a lint check.
- JSON alternative (exit 0 + stdout): `{"decision": "block", "reason": "ESLint: 3 errors in src/app.ts …"}` puts the reason next to the tool result for Claude; `hookSpecificOutput.additionalContext` adds non-blocking context.
- **PostToolUse cannot undo the edit.** The file is already written. To stop an action before it happens, use **PreToolUse** (exit 2 or `permissionDecision: "deny"`).
- Which event:
  - Format/lint the single file just changed → PostToolUse on `Edit|Write`
  - Block writes to protected paths → PreToolUse (or a `permissions.deny` rule, 3.7)
  - Run the full test suite once before Claude declares it's done → **Stop** hook. `decision: "block"` + reason keeps Claude working. Running the full suite on every edit is slow
  - Inject context at session start → SessionStart
- Exam traps: git pre-commit hook (runs only at commit, not after each edit, and gives Claude no in-loop feedback); CI pipeline step (too late, outside the session); PreToolUse to format (the file doesn't exist in its new form yet); CLAUDE.md or a skill instruction (probabilistic); hook in `~/.claude/settings.json` for a team standard (not shared); expecting PostToolUse to reject or roll back the edit

## Domain 4: Prompt Engineering & Structured Output (20%)

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
- **Extraction accuracy across varied formats: pick the lever that matches the symptom.**
  - Same value written different ways (dates `03/04/25` vs `4 March 2025`, `$1.2k` vs `1200.00`, units) → explicit **format normalisation instructions** in the prompt/field descriptions ("dates as ISO 8601 YYYY-MM-DD; amounts as decimal numbers without currency symbols; currency in a separate ISO 4217 field")
  - Values missed on unusual layouts (tables vs prose, footnotes, multi-column) → **few-shot examples** covering each layout type, with the reasoning shown
  - Values invented when absent → **nullable/optional schema fields** (4.3)
  - Real systems combine all three; the exam asks which one addresses the stated symptom
  - Traps: regex post-processing to normalise (brittle across formats); more retries (doesn't teach the format); a larger model; a single example (can't cover the layout variety)

**Structured output with tool_use (4.3)**
- `tool_use` with JSON schema eliminates syntax errors. Prompt-based JSON can produce malformed output.
- `tool_use` does NOT prevent: semantic errors (line items not summing to total), field placement errors, fabrication
- `tool_choice "any"`: must call a tool, chooses which (guaranteed structured output, unknown doc types)
- Schema: use optional/nullable fields to PREVENT fabrication. "unclear" enum for ambiguous cases. "other" + detail string for extensible categories.
- **Extraction schema design details** (exam objective scored 33%):
  - A **required non-nullable** field for data that is sometimes absent forces the model to invent a value. That is the root cause of fabrication
  - **Required + nullable** (`"type": ["string", "null"]`): the model must make an explicit decision and output `null` when absent. Best when downstream needs to know "we looked and it isn't there"
  - **Optional** (not in `required`): the key may be omitted entirely. Fine for truly supplementary data, but you can't tell "absent" from "skipped"
  - Enums: add `"unclear"` when the source is ambiguous between known values; add `"other"` + a companion `*_detail` string for values outside the known set. Don't force a closed enum onto open-ended data
  - Never use sentinel strings (`"N/A"`, `"unknown"`, `""`, `0`) in typed fields. They pass validation and poison downstream data
  - Distinguish "not present in source" (null) from "present but illegible/ambiguous" (`"unclear"` or a flag), since they route differently (see 5.5)
  - Exam traps: "make everything required so nothing is missed"; "one free-text notes field for anything uncertain"; "validation-retry until the field is filled" (retries can't find absent data, see 4.4)

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
- **Decision edges (exam objective scored 0%, practice questions were too obvious):**
  - Batch timing: most batches finish in under 1 hour, but that is **not a guarantee**. Results arrive when the whole batch completes, or at 24 hours; unfinished requests expire at 24h. Design for "up to 24 hours"
  - Non-blocking but has a deadline shorter than 24h (e.g. "report must be ready by 9 AM, job starts at 8 AM") → **synchronous**, even though nobody is waiting at a screen. "Most finish in 1h" is the trap
  - Non-blocking and the window is ≥ 24h (nightly, weekly, backfills, bulk evals) → **Batch**, for 50% cost
  - Blocking: anything a human or pipeline stage waits on before continuing (pre-merge check, attorney opens document, next pipeline step branches on the result) → **synchronous**
  - Agent loops with **client tools**: each tool round trip needs a new request. In Batch that means a new submission and another wait of up to 24h per turn → **synchronous** for interactive agent loops. (A batch request can carry prior multi-turn history, and server tools run inside the batch, but you can't pause mid-request to run your own tool)
  - Mixed workload → **split it**: blocking part synchronous, bulk part Batch. Don't pick one API for everything
  - Limits: 100,000 requests or 256 MB per batch; results downloadable for 29 days; each request needs a unique `custom_id` (the results are not guaranteed to come back in submission order)
  - Traps: "Batch with a priority flag" (doesn't exist); "Batch because most complete within an hour"; "synchronous for everything for simplicity" when the job is overnight bulk; "rely on result order instead of `custom_id`"

**Multi-instance review (4.6)**
- Same session reviewing its own output = less effective (retains reasoning context, less likely to question decisions)
- Independent instance without prior context catches more subtle issues
- Per-file local passes + separate cross-file integration pass = prevents attention dilution
- Verification pass: model self-reports confidence alongside each finding to enable calibrated routing — distinct from aggregate confidence thresholds
- Confidence-based routing: low-confidence findings → human review. Calibrate with labelled validation sets.

## Domain 5: Context Management & Reliability (15%)

**Context preservation (5.1)**
- Progressive summarisation trap: compresses specific values ("$247.83 for order #8891") into vague summaries
- Fix: persistent "case facts" block with transactional facts. Include in every prompt. Never summarise it.
- Multi-turn API calls: every subsequent request must include the complete conversation history — omitting prior turns breaks coherence
- "Lost in the middle" effect: models process beginning and end reliably, middle may be missed. Fix: key summaries at the START, explicit section headers.
- Long-document Q&A accuracy: place the document content ABOVE the question and instructions (not below). Also require the model to quote the governing text before answering. Exam trap: appending the document after the instructions causes the model to paraphrase loosely rather than quote precisely, even when the full document fits in the context window.
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
- **Human review ROUTING design** (exam objective scored 33%; practice only tested the "97% hides a segment" angle):
  - Route at the **field** level, not the document level: a 40-field form with one ambiguous field sends that field (with its source snippet) to a reviewer, not the whole document
  - Routing signals, combined:
    1. **Field-level confidence**, calibrated against a labelled validation set (raw self-reported confidence is not calibrated)
    2. **Document characteristics**: document type (especially types with a known higher error rate), scan quality/OCR, handwriting, language, unusual layout
    3. **Explicit ambiguity flags** from extraction: `"unclear"` enum values, `conflict_detected`, `calculated_total != stated_total`
  - Different reviewers for different routes: specialist queue for a hard document type, general queue for low-confidence single fields
  - **Random/stratified sampling** of auto-accepted, high-confidence output is for **auditing and catching new error patterns**. It is not the routing rule. Exam trap: "randomly sample 10% of all documents for review" as the routing strategy
  - Other traps: one document-level threshold for all fields; routing on the model's uncalibrated stated confidence; sending every document of a type to review forever instead of calibrating; routing by sentiment/length alone

**Information provenance (5.6)**
- Each finding needs: claim + source URL + document name + relevant excerpt + publication date
- Two conflicting credible sources: annotate BOTH with attribution. Do NOT arbitrarily select one.
- Temporal awareness: different dates explain different numbers (not contradictions)
- Rendering: financial data → tables, news → prose, technical findings → structured lists

---

## Question Generation Guidelines

The exam rewards: deterministic over probabilistic fixes, proportionate solutions, root cause tracing, low-effort first steps.

When generating questions:

1. **Always scenario-based** — describe a real production situation (agent behaving unexpectedly, CI breaking, misrouted tool call, etc.)
2. **One clearly correct answer** — grounded in the concepts above
3. **Three plausible distractors** — draw from the Distractor Bank below
4. **Select questions from the session's question plan** (see Score-Report Weighting below). Only if `fexam-scorereport.json` is absent, fall back to covering domains proportionally: ~4 D1, ~3 D2, ~3 D3, ~3 D4, ~2 D5 per 15 questions
5. **Match difficulty to `$ARGUMENTS`**: easy = direct recall, medium = single-concept scenarios, hard/absurd = multi-step reasoning with interacting concepts. For `absurd`: every option must be defensible and at least one distractor per question must be drawn from the bank below. Do not vary within a session.

---

## Score-Report Weighting

`fexam-scorereport.json` holds the user's most recent official CCAR-F score report: 29 test objectives (`O1`–`O29`), each with `exam_pct`, `tier`, `domain`, mapped `subtopics`, and for tier 1–2 an `angle` describing what the real exam tests and why earlier practice missed it. The goal is to pass the retake, so sessions deliberately over-sample what the user got wrong on the real exam.

**Tiers** (always derive from `exam_pct`; if a stored `tier` field disagrees, `exam_pct` wins)
- **Tier 1**: 0% on the exam
- **Tier 2**: above 0% and below 100%
- **Tier 3**: 100% on the exam (maintenance only)

**Building the question plan (at session start, applies to easy / medium / hard / absurd / exam)**
1. Compute counts with `python3`: `t1 = round(N * 0.4)`, `t2 = round(N * 0.3)`, `t3 = N - t1 - t2` (shares come from `session_mix` in the JSON).
2. If the user chose a single domain, keep only objectives whose `domain` matches. If a tier has no objectives in that domain, move its count to the next lower-numbered tier that has objectives (tier 1 → tier 2 → tier 3), or, if none, to the next higher-numbered tier.
3. **Tier-1 slots:** round-robin through the tier-1 objectives so each appears once before any repeats. Order the rotation by fewest practice attempts first (from the `objective` field in `fexam-performance.json`).
4. **Tier-2 slots:** round-robin the same way, ordered by lowest `exam_pct` first.
5. **Tier-3 slots:** distribute across domains by the official domain weights, choosing tier-3 objectives or subtopics not yet in the plan. Prefer subtopics flagged in the Watch List.
6. For every tier-1/tier-2 slot, also pick an **edge** of that objective (see Edge Retirement below).
7. Shuffle the plan so tiers are interleaved. Never cluster all tier-1 questions at the start or end. Avoid two consecutive questions on the same objective.

**Writing a tier-1 or tier-2 question**
- Build the question around the planned **edge**, using the objective's `angle` for context. The user already answers the textbook version of these topics correctly; the real exam tested the edges named in the angle. Don't generate the obvious variant again.
- If an objective comes up more than once in a session, use a different edge, a different scenario domain (industry, workflow) and a different correct-answer position.
- The difficulty level still controls how hard the question is. Weighting controls *what* is asked, not *how hard*.
- Use the distractors listed in the objective's `angle` and in the Distractor Bank rows tagged with its subtopic.

**Edge Retirement (tier 1 and tier 2 only)**
Each tier-1/tier-2 objective has a list of `edges`: the specific traps or edge cases the exam can test, with stable IDs (`O20.e1`, `O20.e2`, …). An **objective never leaves its tier** because of practice results; only a new score report changes tiers. What retires is the individual **edge**.
- An edge is **retired** once the user has answered questions on it correctly `retire_after_correct` times (5), counted across all sessions and all modes from the `edge` field in `fexam-performance.json`. Count with `python3`. Wrong answers don't subtract from the count.
- When picking an edge for a slot: choose among the objective's **active** (non-retired) edges, fewest attempts first, and never the same edge twice in one session while another active edge remains.
- If **every** edge of an objective is retired, the objective keeps its slots: recycle retired edges, least recently asked first, with a new scenario each time. Say so in the Retake Focus line for that objective ("all edges retired — recycling").
- A tier-1/tier-2 question tests exactly **one** planned edge. The correct answer must hinge on it. Other edges may appear only as distractors.
- Tier-3 questions have no edges and no retirement.

**Silence in exam mode:** do not label questions with tier or objective during the session. Reveal objective IDs only in the end-of-session breakdown.

**Updating after a retake:** replace `fexam-scorereport.json` with the new report's percentages. Tiers are recomputed from `exam_pct` via `tier_rules`; no edits to this command are needed.

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
| CI pipeline hangs | Add `-p` flag for non-interactive mode | `--timeout`, `--non-interactive`, `--batch` (flags don't exist); `CLAUDE_HEADLESS=true` (env var doesn't exist); use batch API (different use case) |
| Escalation rate miscalibrated — agent escalates simple cases, handles complex ones | Add explicit escalation criteria with few-shot examples showing when to escalate vs resolve | Route by self-reported confidence score (poorly calibrated); deploy separate classifier model (over-engineered); use sentiment analysis (sentiment ≠ complexity) |
| Tool returns empty array, agent retries | Treat as valid empty result, no retry | Retry with backoff, escalate immediately, check permissions |
| Synthesis report has no attribution | Fix context passing (add structured metadata) | Fix synthesis agent prompt, fix web search agent, fix coordinator |

### Hard, absurd, and exam only

These distractors involve two or more interacting concepts, near-correct reasoning that breaks at an edge case, or distinctions the exam is known to exploit. Use them at `hard`, `absurd`, and `exam` difficulty. At `absurd`, every option in the question must be constructed at this level of plausibility.

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
| Skill must produce deterministic, offline output from a JSON input with no per-render LLM tokens | Skill instructs Claude to validate input and invoke a bundled script via Bash; Claude does not generate the artifact | Have Claude generate the output in `SKILL.md` body (non-deterministic, token-intensive); add `context: fork` so generation is isolated (still non-deterministic — fork controls conversation scope, not output generation); store script at `~/.claude/scripts/` (breaks skill portability) |
| Complex architectural change (e.g., monolith-to-microservices, 45+ files) — where to start? | Enter plan mode to explore, understand dependencies, and design before making changes | "Start with direct execution and let the implementation reveal natural service boundaries" (risks costly rework when dependencies discovered mid-implementation); "Use direct execution with comprehensive upfront instructions detailing the structure" (assumes correct structure without exploring the code) |
| Audit entry must be written BEFORE Claude processes the message (pre-processing requirement) | `UserPromptSubmit` hook — fires on submission, before any model processing begins | "PostToolUse hook on the search tool" (fires after a tool executes, not on message submission — wrong moment); "System prompt instruction to always log first" (probabilistic, model can skip it); "PreToolUse hook" (fires before a tool call, not before message processing) |
| PostToolUse hook needed for post-execution audit logging vs. putting log call inside the tool's implementation | `PostToolUse` hook — framework-level, runs even for tools you don't own | "Log inside tool implementation — it runs at the same point in the loop as a PostToolUse hook" (FALSE: architecturally different; you may not own the tool's code; PostToolUse is the correct framework integration point); "PreToolUse hook — captures the document before execution" (wrong timing — pre, not post) |
| PreToolUse hook must block some calls and route others to the user for confirmation | `permissionDecision` field with values `allow`, `deny`, `ask`, `defer` | "`permissionDecision` accepts only `allow` and `deny`" (missing `ask` and `defer`); "`toolDecision` with `permit`/`block`/`confirm`" (wrong field name); "`decision` with a reason string" (wrong field name) |
| User-level CLAUDE.md contradicts project CLAUDE.md — contractor getting inconsistent behaviour | Both files load simultaneously; contractor must remove or reconcile the conflicting entries in their user-level file | "Project-level CLAUDE.md overrides user-level automatically" (FALSE: both load simultaneously, conflicts are not resolved by precedence); "Move project CLAUDE.md to a subdirectory so it loads later and overrides" (subdirectory scoping does not change load-order precedence over user-level files) |
| Project-wide standards must always load in every session (cross-codebase, not file-type specific) | `.claude/rules/` files WITHOUT `paths:` frontmatter — load at every session launch unconditionally | "Add `paths: ['**/*']` so the rule matches all files" (correct intent but wrong form — use no paths frontmatter at all); "Put rules in root CLAUDE.md" (valid, but the question tests knowledge of the rules-file mechanism); "All `.claude/rules/` files are conditional based on the file being edited" (FALSE: only when `paths:` frontmatter is present) |
| Coordinator silently does all work inline, never spawns subagents despite prompt instructions | Add `"Agent"` (formerly `"Task"`) to the coordinator's `tools`/`allowedTools` option | "Add explicit delegation language to system prompt" (probabilistic, wrong root cause); "Define subagent types as AgentDefinition entries" (doesn't enable spawning without the tool); "Switch to a model that supports multi-agent natively" (delegation is a tool-list feature, not a model capability) |

### Score-report weak objectives (all difficulty levels; at hard/absurd/exam use the subtler distractors)

Rows added from the 2026-09-11 exam report. Tagged with objective ID and subtopic.

| Obj / sub | Situation | Correct answer | Distractors and why they fail |
|---|---|---|---|
| O10 / 3.7 | CLAUDE.md says "NEVER read `.env` files"; Claude read one anyway during debugging | `permissions.deny: ["Read(./.env)"]` in committed `.claude/settings.json`; remove or shorten the CLAUDE.md line | "Rewrite in capitals with IMPORTANT" (still guidance); "Move to `.claude/rules/secrets.md`" (rules are guidance too); "Add to `settings.local.json`" (not shared with team) |
| O10 / 3.7 | Team denies `Bash(git push *)` but wants to allow `git push origin feature/*` | Deny wins; drop the broad deny and use `ask` for `git push *` (or a PreToolUse hook with logic) | "Add a more specific allow rule" (allow can't override a matching deny; specificity doesn't matter); "Explain the exception in CLAUDE.md" (doesn't change enforcement) |
| O10 / 3.7 | Security mandate for every repo in the company, engineers must not be able to override it | Managed settings | Project `.claude/settings.json` in every repo (overridable, easy to miss repos); user-level settings (per person); root CLAUDE.md template (guidance) |
| O10 / 3.7 | CLAUDE.md audit: which lines move out? | Hard never/always constraints → deny/ask rules or hooks; conventions, architecture, preferences → stay | "Move everything to settings" (settings can't express style guidance); "Convert all to skills" (on demand, not always loaded, not enforced) |
| O12 / 3.8 | Claude sometimes forgets to run the formatter after editing files | PostToolUse hook, matcher `Edit\|Write`, in `.claude/settings.json` | CLAUDE.md reminder (probabilistic); git pre-commit hook (only at commit time, no in-loop feedback); PreToolUse hook (file not yet written) |
| O12 / 3.8 | Lint hook runs after edits but Claude never fixes the reported errors | Hook must exit **2** (stderr is shown to Claude) or return `decision: "block"` + reason | Exit 1 (non-blocking; Claude doesn't get it); print errors to stdout on exit 0 (goes to debug log); add "fix lint errors" to CLAUDE.md |
| O12 / 3.8 | Full test suite takes 90s; team wants it green before Claude says it's finished | Stop hook that runs the suite and returns `decision: "block"` with the failures | PostToolUse on every edit (90s × every edit); CI (outside the session); PreToolUse (wrong moment) |
| O12 / 3.8 | Engineer expects PostToolUse lint hook to reject a bad edit so the file is unchanged | PostToolUse can't undo; the edit already happened. Use PreToolUse to prevent, or PostToolUse feedback so Claude fixes it | "PostToolUse `decision: block` reverts the write" (false: it only adds a reason for Claude) |
| O13 / 2.5 | Agent asked "how does auth work?" in an unfamiliar 3,000-file repo; context fills after reading 40 files | Glob to map → Grep for entry points/symbols (files list first) → targeted Read with offset/limit → follow imports → notes/Explore subagent | Read every file under `src/auth/` first; `cat` the directory via Bash; bigger context window; Grep content mode across the whole repo |
| O13 / 2.5 | Need every caller of `computeTax()` before changing its signature | Grep for the symbol (files_with_matches), then Read only the call sites | Glob for `*tax*` (names ≠ callers); Read the whole module tree; ask Claude to "recall" usages |
| O20 / 4.5 | Nightly job starts 06:00, dashboard must be ready 08:00, cost pressure; engineer proposes Batch "since most finish within an hour" | Synchronous — Batch completion can take up to 24h; a 2h deadline isn't guaranteed | Batch (the "most within 1h" trap); Batch with priority flag (doesn't exist); split into smaller batches to finish faster (still no SLA) |
| O20 / 4.5 | Agent loop with client tools processes 5,000 tickets overnight, 3–6 tool calls each | Synchronous API (each client-tool round trip in Batch = new submission, up to 24h each) | Batch for 50% savings; Batch with multi-turn history (still a new submission per turn); Batch the first turn then synchronous |
| O20 / 4.5 | Weekly compliance scan of 80,000 docs + on-demand single-doc check an analyst waits for | Split: Batch for the weekly scan, synchronous for the on-demand check | Batch for both; synchronous for both "for simplicity"; synchronous with parallelism for the scan (pays 2×) |
| O29 / 2.3 | Refund agent sometimes calls `lookup_order` before `get_customer`, passing a guessed ID | Force `get_customer` on turn 1 with `tool_choice: {"type":"tool",…}`, then `auto`; make `customer_id` a required parameter of `lookup_order`; note the prerequisite in its description | `tool_choice: "any"` (doesn't pick which); list `get_customer` first in the tools array (no effect); system-prompt "always call get_customer first" (probabilistic) |
| O29 / 2.3 | Team forces `{"type":"tool","name":"get_customer"}` on every request; agent now loops calling it forever | Force only the first turn, then switch to `auto` | Add iteration cap (masks the cause); switch to `any` (still forces a tool every turn); remove the tool after first call (breaks later turns that need it) |
| O29 / 4.3 | Downstream parser breaks when Claude replies conversationally instead of calling the extraction tool | `tool_choice: {"type":"any"}` (one of several extractors) or forced tool (single extractor) | "auto" + "always use a tool" in the prompt; parse prose as fallback; prefill a `{` |
| O19 / 5.5 | Design review routing for a 30-field insurance form pipeline | Field-level calibrated confidence + document characteristics + ambiguity flags → field-level routing; random/stratified sample of auto-accepted output for audit | Random 10% sample as the routing rule; single document-level threshold; route on self-reported confidence; send whole doc if any field is low |
| O22 / 4.3 | `jurisdiction` is required string; Claude fills in the buyer's state when the contract is silent | Make it required + nullable (explicit `null` when absent) | Keep required, instruct "write N/A"; add validation-retry; make optional (loses "looked and absent" signal, weaker answer when both offered) |
| O22 / 4.3 | `category` enum [MSA, NDA, SOW] — new document types and genuinely ambiguous ones are misfiled | Add `"other"` + `category_detail` string and `"unclear"` | Expand enum with every possible type (can't anticipate); free-text category (loses validation); force closest match |
| O6 / 1.1 | Loop checks only `end_turn`/`tool_use`; occasionally dispatches a half-written tool call | Handle `max_tokens`: an incomplete `tool_use` block → retry with higher `max_tokens`, don't dispatch | Treat `max_tokens` as `end_turn`; parse partial JSON and dispatch; add iteration cap |
| O6 / 1.1 | Agent using server-side web search returns `stop_reason: "pause_turn"`; loop treats it as finished | Send the assistant content back as-is to continue the turn | Treat as terminal; treat as an error and retry the original request; append a "continue" user message |
| O8 / 3.5 | Four failing edge cases in a date parser, fixes interact | One message listing all four with input/actual/expected; ask for a consolidated fix | One case per turn (fixes undo each other); "make it more robust" (no target); longer prose spec |

---

## Reference Question Bank (Style Calibration)

60 questions from the official CCAR-F P1 sample exam + 13 synthesized from P2. Use to calibrate scenario framing, distractor plausibility, and difficulty — do not reproduce verbatim.

### D1 — Agentic Architecture & Orchestration
**Q1 (1.1)** Fintech reconciliation agent: loop resends request whenever it can't find a dispatchable tool call, never inspects stop reason → spins in production on a response it can neither dispatch nor recognise as finished.
- A) Cap at 50 iterations and raise a timeout error
- B) Scan text block for completion phrases such as "I'm done"
- C) Exit when content array is empty
- D) Branch on stop_reason: continue on "tool_use", treat end_turn/max_tokens/stop_sequence/refusal as terminal
**Correct: D**
**Q2 (1.1)** Logistics dispatch agent exits loop as soon as response contains a text block → tools never invoked, agent reports plans it never carried out.
- A) Text blocks emit only after all tool calls complete — fault lies in tool implementations
- B) max_tokens truncation before tool_use blocks
- C) A single response can carry both text and tool_use blocks — presence of text says nothing about terminality
- D) Extended thinking splits text and tool_use into separate API responses
**Correct: C**
**Q3 (1.1)** Support agent: after receiving tool_use block, runs lookup_order, then issues a fresh Messages API request with only system prompt + new user message → repeated/contradictory tool calls in multi-step tasks.
- A) Append assistant message with tool_use block, then user message with tool_result block carrying the same tool_use_id, resend full history
- B) Append assistant message with tool_use block, then a "tool role" message with tool output and matching id
- C) Set stateful flag on client so service retains conversation server-side
- D) Prepend tool output to system prompt with the id
**Correct: A**
**Q4 (1.2)** Coordinator accumulated 40 turns with constraint "no third-party data sources." Spawns researcher/coder/reviewer subagents. Team assumes subagents inherit context. In production subagents cite third-party sources.
- A) Persist transcript to shared store, give subagents a query tool
- B) Run all agents in one session so history is shared
- C) Restate every relevant constraint inside each subagent's prompt — subagent sees only what it is passed
- D) Raise coordinator's context window so subagents can read the constraint list
**Correct: C**
**Q5 (1.2)** Market-research coordinator decomposes competitor analysis into 3 subtasks. Each subagent returns thorough report. Post-run check: EMEA region never analysed by any subagent. Team proposes fine-tuning subagents to explore more aggressively.
- A) Fine-tune subagents to proactively widen scope
- B) Correct the coordinator's decomposition — it never assigned EMEA to any subtask
- C) Add a completeness validator that rejects reports not covering every region
- D) Raise each subagent's max_tokens
**Correct: B**
**Q6 (1.3)** Data pipeline coordinator must process 12 independent sources. Currently emits one delegation call, waits, then emits the next → wall time is ~12x. Engineer wants wall time close to 1x; coordinator still receives all 12 results to reason across them.
- A) Chain subagents so each spawns the next on completion
- B) Move fan-out outside model entirely via a queue (e.g. SQS + workers)
- C) Increase coordinator's context window so it holds all 12 results at once
- D) Emit all 12 delegation tool calls in a single coordinator response
**Correct: D**
**Q7 (1.4)** Compliance: refunds above $500 must be approved by human officer, without exception. Architect proposes "Always escalate refunds > $500" in system prompt. Security review rejects this as insufficient.
- A) Architect is right if instruction is repeated in system prompt + first user turn labelled "CRITICAL"
- B) Security is right — fix is a second model call that vetos non-compliant approvals before execution
- C) Architect is right — close residual risk by fine-tuning on compliance decisions
- D) Security is right — intercept every process_refund call, deterministically block amounts > $500, route to human queue
**Correct: D**
**Q8 (1.4)** Telecom help-desk: must open with customer's first name, close with ticket reference. Gets it right ~9/10. Engineer proposes intercepting and rewriting every outbound message in code.
- A) Intercept and rewrite in code — guarantees format on every reply
- B) Escalate any reply failing the format check to human reviewer
- C) Specify greeting and sign-off in prompt with one worked example — accept prompt-level enforcement for a presentation rule
- D) Fine-tune model on correctly formatted replies
**Correct: C**
**Q9 (1.5)** Agent can run shell commands. Threat model: prompt injection could induce destructive commands (rm -rf /, DROP TABLE). Requirement: such commands must NEVER execute regardless of what model generates.
- A) PostToolUse hook that pattern-matches executed commands and writes audit record when destructive one detected
- B) PreToolUse hook that inspects shell call arguments and blocks/redirects dangerous patterns
- C) Blocklist of destructive commands in system prompt with instruction to refuse
- D) Sandboxed container with ephemeral filesystem discarded after each run
**Correct: B**
**Q10 (1.5)** Legacy CRM returns phone numbers inconsistently. Downstream tools require E.164. Engineer wants Claude to see already-normalised values, never having to reason about formatting.
- A) PreToolUse hook rewrites outbound CRM request so system returns numbers in E.164
- B) System prompt instruction telling Claude to normalise phone numbers before passing to another tool
- C) PostToolUse hook — receives tool result after execution, before model processes it
- D) Post-processing step over agent's final answer
**Correct: C**
**Q11 (1.4)** Support agent escalates with message: "Continuing from earlier — the customer had an issue with billing." Human agents have no transcript access. They re-ask customers for details already collected.
- A) Grant human agents read access to full AI session transcript
- B) Attach last 5 messages verbatim
- C) Log to CRM and train humans to search before responding
- D) Make handoff self-contained: issue, data collected, steps attempted, reason for escalation, recommended next action
**Correct: D**
**Q12 (1.6)** Document pipeline for regulated financial reporting. Choice: fixed 3-step chain vs runtime-planning agent that adds steps on detection. Auditability and reproducibility are contractual requirements.
- A) Runtime-planning agent with exhaustive logging — steps can be reconstructed for auditors
- B) Runtime-planning agent — handles edge cases automatically
- C) Fixed for simple, runtime-planning for complex — classifier decides
- D) Fixed chain — predetermined step sequence is deterministic and can be validated by compliance in advance
**Correct: D**
**Q13 (1.6)** Engineer must add test coverage to legacy service with no documentation. Untested surface is unknown until code is read. No compliance constraint, no fixed deliverable format.
- A) Fixed chain of predetermined steps — reproducible output across modules
- B) Decompose by directory up front, one subtask per top-level folder
- C) Dynamic decomposition — subtasks cannot be enumerated until agent reads the code
- D) Fixed chain per module + final integration pass
**Correct: C**
**Q14 (1.7)** Developer is deep in a performance refactor session with stable baseline. Needs to evaluate two mutually incompatible strategies (CPU vs memory optimisation) — both must start from identical current session state.
- A) Run both strategies sequentially in current session, reverting working tree between them
- B) Resume with --fork-session, getting new session ID while original history stays intact
- C) Start two fresh sessions each seeded with written description of baseline
- D) Open two terminals and resume same session in each
**Correct: B**
**Q15 (1.7)** Backend developer has been refactoring with Claude for 2 hours. She then hand-edits 3 specific files outside Claude. Wants agent to continue with those edits reflected without losing accumulated session understanding.
- A) Ask Claude to re-read entire codebase
- B) Start fresh session with full project summary
- C) Name the 3 changed files and supply current contents or a diff, leaving rest of agent's model intact
- D) Have Claude run git diff and reconcile every change since last commit
**Correct: C**
**Q16 (1.7)** Contractor returns from a week away. During that week: module layout reorganised, two services merged. Saved session describes file paths that no longer exist.
- A) Resume and instruct Claude to disregard any missing paths
- B) Start fresh session seeded with summary of goal, decisions made, and new architecture
- C) Fork saved session — stale context on one branch, new layout on the other
- D) Resume and have Claude re-read every file it previously referenced
**Correct: B**
**P2-Q1 (1.3)** Coordinator agent has `tools: ["Read", "Edit", "Bash", "WebSearch"]`. System prompt instructs it to delegate analysis tasks to specialist subagents. In testing it silently performs all work inline — no subagents are ever spawned. What should the engineer do?
- A) Add explicit delegation language and worked examples to the coordinator's system prompt
- B) Define each specialist subagent as a separate AgentDefinition entry and reference them from the coordinator
- C) Switch to a model tier that supports multi-agent orchestration natively
- D) Add "Agent" (the subagent-spawning tool, formerly "Task") to the coordinator's `tools` option
**Correct: D**
**P2-Q2 (1.5)** A PreToolUse hook must stop some commands outright and route others to the user for manual confirmation before execution. Which field carries that decision and what values does it accept?
- A) `permissionDecision`, which accepts only `allow` and `deny`
- B) `toolDecision`, which accepts `permit`, `block`, `confirm`, and `passthrough`
- C) `decision`, which accepts `block` plus a mandatory reason string
- D) `permissionDecision`, which accepts `allow`, `deny`, `ask`, and `defer`
**Correct: D**
**P2-Q3 (1.5)** A compliance platform must write every controlled-substance query to an immutable ledger BEFORE any model processing begins. The system prompt instruction "always log these queries first" is occasionally skipped when conversation is long. What is the correct fix?
- A) Move the logging instruction to the very top of the system prompt
- B) Repeat the logging instruction in both system prompt and every user turn
- C) Write the ledger entry from a PostToolUse hook on the knowledge-base search tool
- D) Write the ledger entry from a UserPromptSubmit hook, which fires before Claude has begun processing the prompt at all
**Correct: D**
**P2-Q4 (1.5)** A compliance team needs every document processed by a `redact_pii` tool written to an audit log after redaction completes but before Claude sees the result. A junior engineer says to add the log call inside the tool's implementation function — same timing, simpler code. What should the engineer do?
- A) Use a PostToolUse hook — it is framework-level and runs even for tools you don't own or cannot modify
- B) Keep the log inside the tool implementation — it executes at the same moment in the loop as a PostToolUse hook and achieves the same result
- C) Use a PreToolUse hook so the document is captured before redaction alters it
- D) Instruct Claude to emit a structured audit block in its next text response, then parse it programmatically
**Correct: A**

### D2 — Tool Design & MCP Integration
**Q17 (2.1)** Agent exposes query_database, send_email, search_docs — each with a single short-sentence description. Claude frequently calls query_database when intent is plainly document search. Team's first instinct: add a routing classifier.
- A) Merge query_database and search_docs into one tool
- B) Add few-shot examples to system prompt showing correct tool per query category
- C) Add the routing classifier — forces correct tool deterministically
- D) Expand query_database and search_docs descriptions: purpose, expected input, example queries, explicit boundary against the other
**Correct: D**
**Q18 (2.2)** [Multi-select — 3 correct] MCP server wraps payments provider. Every failure returns same opaque string → agent retries permission denials, gives up on transient timeouts. Team redesigns error contract.
- A) Set MCP isError flag so failure surfaces as tool-level error not ordinary content
- B) Return errorCategory (transient/validation/business/permission)
- C) Return explicit retryability signal so agent doesn't have to infer from category
- D) Return provider's raw stack trace as error body for maximum detail
**Correct: A, B, C**
**Q19 (2.2)** Travel booking agent calls get_flight_status — connection timeout, no response body received, nothing known about requested flight.
- A) Transient — retry with exponential backoff up to configured maximum
- B) Validation — ask user to re-enter flight number in different format
- C) Business — halt without retrying, upstream service declined
- D) Unrecoverable — surface failure to user immediately, in-agent retries risk duplicate side effects
**Correct: A**
**Q20 (2.2)** Retail agent calls fetch_inventory for a SKU, receives []. No exception, HTTP 200, warehouse DB queried successfully.
- A) Valid result — no matching items exist, do not retry
- B) Retry up to 3 times with backoff — empty set can indicate transient replication lag
- C) Escalate — empty set may indicate permission problem masking rows
- D) Mark failed and return error so user can reformulate filter
**Correct: A**
**Q21 (2.3)** Coordinator holds 14 tools spanning 6 domains. High per-request token cost AND frequent wrong tool selection. Architect weighs four redesigns.
- A) Compress every tool description to one line to shrink tools block
- B) Insert tool-selection classifier to filter tool list per request
- C) Split into role-scoped subagents with 4-5 relevant tools each, coordinator delegates
- D) Collapse 14 tools into 3-4 mega-tools routing internally
**Correct: C**
**Q22 (2.3)** Coordinator/research/synthesis pipeline. Synthesis must verify individual claims while drafting — each verification routes through coordinator. 85% are single-fact lookups. Engineer proposes giving synthesis the full research tool suite.
- A) Keep every verification routed through coordinator — single point of control
- B) Grant synthesis agent full research tool suite
- C) Merge synthesis and research agents — verification becomes internal step
- D) Give synthesis agent only a narrow verify_fact(claim, source_filter) tool
**Correct: D**
**Q23 (2.4)** Every engineer must run a GitHub MCP server needing GITHUB_TOKEN. Team wants auto-discovery on project open, no secret committed. Engineer proposes writing each person's token into .mcp.json and adding to .gitignore.
- A) Yes — gitignoring keeps secret out while each engineer has working local config
- B) No — commit .mcp.json referencing token as ${GITHUB_TOKEN}, which Claude Code expands from local env at startup
- C) Yes — provided each engineer generates a read-only scope token
- D) No — each engineer should add server to their own ~/.claude.json user-level config
**Correct: B**
**Q24 (2.4)** Data scientist maintains personal MCP server wrapping her own research notes — useful only to her, must be available in every repo she opens.
- A) In her user-level ~/.claude.json — personal, unshared, applies across projects
- B) In .mcp.json at root of each repo, committed
- C) In .claude/mcp_settings.json — read after project config, scoped to current user
- D) In project .mcp.json with server marked private
**Correct: A**
**Q25 (2.5)** Engineer needs every file in a large monorepo that imports a module named auth_middleware. Import statements may use different path forms; module filename isn't necessarily auth_middleware.
- A) Glob with */*auth_middleware — matches every path related to the module
- B) Grep — target is a string inside file contents, not a pattern in file names
- C) Grep for exact string "import auth_middleware"
- D) Glob first to shortlist candidate paths, then Grep within them
**Correct: B**
**Q26 (2.5)** Frontend lead needs a list of every React component test (*.test.tsx) scattered across many feature directories. Wants the file list, not contents.
- A) Glob with */*.test.tsx — target is a file-path pattern
- B) Grep for ".test.tsx" — content search surfaces every file referencing the convention
- C) Grep for describe( or it( — catches files not following naming convention
- D) Bash with find . -name "*.test.tsx"
**Correct: A**
**Q27 (2.5)** Agent must change one occurrence of a config key in a 4,000-line file. Edit fails because anchor is not unique — key appears in 12 places.
- A) Retry Edit with same anchor — transient contention error on large file
- B) Switch to Bash sed targeting occurrence by line number
- C) Re-anchor on a longer span of surrounding text unique to the intended occurrence
- D) Set replace_all: true so every occurrence is rewritten
**Correct: C**
**Q34 (2.4)** Team runs MCP server exposing internal documentation. Claude makes 3-4 exploratory search calls before finding the right document — slow, fills context with dead ends. Team wants Claude to see what documentation exists before deciding what to fetch.
- A) Single mega-tool accepting a mode argument and routing internally
- B) A resource listing the documentation catalogue — agents see what exists without spending a tool call
- C) More granular tools — one per documentation section
- D) A prompt template instructing agents how to phrase search queries more effectively
**Correct: B**
**P2-Q5 (2.4)** An MCP server definition is committed to `.mcp.json` at a repository root. Which scope does that give it?
- A) User scope — the engineer who committed it picks it up in every repository they open
- B) Local scope — private to the engineer, active in this project only, not shared
- C) Project scope — shared with everyone who works in this repository, active in no other
- D) Machine scope — every account on the host receives it, regardless of project
**Correct: C**

### D3 — Claude Code Configuration & Workflows
**Q28 (3.1)** Senior engineer sets team coding standards in ~/.claude/CLAUDE.md on her laptop. Three weeks later a new backend engineer reports Claude ignores all of them.
- A) Have new engineer copy content into his own ~/.claude/CLAUDE.md
- B) Add onboarding step to README instructing each new hire to recreate the file
- C) Move standards into CLAUDE.md at repo root — version-controlled and shared
- D) Convert standards into a skill so Claude loads them on demand
**Correct: C**
**Q29 (3.1)** Monorepo has root CLAUDE.md with company-wide standards. Team wants React-specific conventions under frontend/ only, without those specifics entering backend/ context, without duplicating company-wide rules.
- A) Put React conventions in frontend/CLAUDE.md — root file still applies there, discovered memory files are concatenated not overridden
- B) Move all React conventions into root CLAUDE.md — only file guaranteed to load anywhere
- C) Put React conventions in frontend/CLAUDE.md and re-declare company-wide rules there too
- D) Convert React conventions to a skill so they load on demand
**Correct: A**
**Q30 (3.1)** Developer notices Claude giving different code-style suggestions this week vs last week for same task in same repo. No files changed. Suspects accumulated configuration is contradicting itself but doesn't know what's actually in effect.
- A) Delete project CLAUDE.md and rewrite from scratch
- B) Start a new terminal session — memory files re-read from disk, stale conflict clears itself
- C) Add priority: high marker to rules he wants followed
- D) Run /memory to list memory files in effect and /context to see what loaded this session, then reconcile the contradiction
**Correct: D**
**Q31 (3.1)** Staff engineer wants four distinct rule sets (security, API design, test standards, accessibility) each independently maintainable and auditable. Proposes giving each its own file under .claude/rules/.
- A) Yes — rule files under .claude/rules/ are discovered automatically, four independently reviewable files with no manual wiring
- B) No — keep single CLAUDE.md, separate with HTML comment blocks
- C) No — create one CLAUDE.md per top-level directory
- D) No — convert each to a separate skill
**Correct: A**
**Q32 (3.3)** Payments company: every database migration file (*/migrations/*.sql) anywhere in the monorepo must include a rollback section. Engineer proposes putting a CLAUDE.md inside each directory that contains migrations.
- A) Memory files can't express SQL-specific requirements — use a dedicated SQL linter instead
- B) Directory memory is scoped to work in that location; a .claude/rules/ file with paths: ["*/migrations/*.sql"] matches those files anywhere
- C) Directory files must be committed individually; personal ~/.claude/CLAUDE.md rule applies universally
- D) Proposal is sound — memory file in each migrations directory propagates upward automatically
**Correct: B**
**Q33 (3.2)** Team lead wants /run-pr-checklist command available to all engineers. Creates file at ~/.claude/commands/run-pr-checklist.md, tests successfully. Teammates report command doesn't exist.
- A) Move file to .claude/commands/run-pr-checklist.md in repository — committed and available to all contributors
- B) Email file to each teammate to place in their ~/.claude/commands/
- C) Publish in internal npm package installed globally by each engineer
- D) Fold checklist into CLAUDE.md so it loads automatically for everyone
**Correct: A**
**Q35 (3.2)** Engineer authors a skill for focused security audit on one file. Must: run in isolated sub-agent context (verbose exploration stays out of main conversation), Read/Grep run without asking permission, advertise expected argument to invokers.
- A) context: shared, allowed-tools: Read Grep, and description: "Security audit skill"
- B) context: fork and permissions: { allow: [Read, Grep] }
- C) context: fork, allowed-tools: Read Grep, and argument-hint: "Path to the file to audit"
- D) argument-hint only, with isolation and tool permissions set globally in CLAUDE.md
**Correct: C**
**Q35a (3.2)** A platform team packages a data-export feature as a Claude Code skill. Requirements: identical output from the same input on every run (deterministic), works fully offline with no network calls, and consumes no per-render LLM tokens. The team has a bundled Python rendering script. Which design correctly meets all three requirements?
- A) `SKILL.md` body instructs Claude to generate the export document from the input data directly
- B) `SKILL.md` body instructs Claude to validate the input, then invoke the bundled Python script via Bash; Claude does not generate the output markup
- C) Store the Python script at `~/.claude/scripts/` so it can be shared across skills, and call it from the skill via Bash
- D) Add `context: fork` to frontmatter so Claude generates the output in an isolated sub-agent, preventing token leakage into the main session
**Correct: B**
**Q35b (3.2)** An engineer writes a Claude Code skill with only these frontmatter fields: `name`, `description`, and `argument-hint`. The skill body instructs Claude to invoke a shell script via Bash. The engineer is surprised it works without listing Bash in `allowed-tools`. What explains this?
- A) Bash is a built-in tool explicitly exempt from `allowed-tools` restrictions
- B) `allowed-tools` only takes effect when `context: fork` is also present in the frontmatter
- C) `allowed-tools` is absent from the frontmatter, so the skill defaults to all standard tools being available
- D) The skill inherits the tool permission set from the nearest CLAUDE.md in the project hierarchy
**Correct: C**
**Q35c (3.2)** A developer is packaging a project-scoped Claude Code skill named `doc-gen`. The skill needs a `SKILL.md` entry point, a Python rendering script, and a JSON reference schema. Which directory layout is correct?
- A) `.claude/commands/doc-gen.md` with the Python and JSON files placed in the project root
- B) `.claude/skills/doc-gen/SKILL.md` with `scripts/render.py` and `references/schema.json` inside the same folder
- C) `.claude/skills/doc-gen.md` with the Python and JSON files listed as `@import` directives in the skill body
- D) `.claude/skills/doc-gen/` directory containing only `SKILL.md`; supporting files must be placed in a separate shared `tools/` directory
**Correct: B**
**Q35d (3.2)** A Claude Code skill renders a PDF by invoking headless Chrome via Bash. On a CI runner, Chrome is not installed. What is the correct pattern for the skill to handle this?
- A) Fail hard with a clear error message so the user knows to install Chrome
- B) Silently skip PDF generation and return an empty result
- C) Switch to a cloud-based PDF rendering API as a fallback to ensure PDF output is always produced
- D) Emit an HTML file (the intermediate artifact) and instruct the user how to complete the PDF step manually — open it and Print → Save as PDF
**Correct: D**
**P2-Q6 (3.1)** A contractor joins a project team. The repo root has a `CLAUDE.md` with pipeline coding standards. After a week the contractor reports that Claude gives advice inconsistent with those standards — yet every senior engineer sees correct behaviour, and the contractor works from the same repo directory. Investigation reveals the contractor has a `~/.claude/CLAUDE.md` with personal preferences that contradict the project rules. What should the engineer do?
- A) Have the contractor delete their `~/.claude/CLAUDE.md` and replace it with a copy of the project file
- B) Explain that both files load simultaneously, and have the contractor remove or reconcile the conflicting entries in their user-level file
- C) Move the project `CLAUDE.md` into a subdirectory so it loads after the user-level file and overrides it
- D) Add a `priority: project` header to the project `CLAUDE.md` to instruct Claude to ignore user-level overrides
**Correct: B**
**P2-Q7 (3.2)** A deploy-dry-run skill must: run in an isolated sub-agent context, shell out and read files without stopping for approval, not be able to modify anything on disk, and surface the target environment name to the user as they type the command. Which frontmatter satisfies all four requirements?
- A) `context: fork`, `allowed-tools: Bash Read`, and an `argument-hint` naming the environment
- B) `context: fork`, `allowed-tools: Bash Read`, `disallowed-tools: Write Edit`, and an `argument-hint` naming the environment
- C) `context: fork` and `disallowed-tools: Write Edit` — listing only disallowed tools is sufficient to withhold write access while inheriting all read tools
- D) `context: fork` and `allowed-tools: Bash Read` — listing only allowed tools implicitly disallows everything else, including Write and Edit
**Correct: B**
**P2-Q8 (3.3)** A monorepo's root `CLAUDE.md` has grown to cover general conventions, cloud deployment, database, and frontend guidelines — all of which must remain always in effect. A tech lead wants to split it into separately-owned topic files without changing which rules Claude always loads. What is the correct approach?
- A) Create a separate `CLAUDE.md` in each relevant subdirectory; delete the root file
- B) Split the content into topic files under `.claude/rules/` with no `paths:` frontmatter — each loads at every session launch
- C) Store each topic as a skill under `.claude/skills/`; document that engineers must invoke relevant skills each session
- D) Add `paths: ["**/*"]` to each topic rule file so it matches all files and therefore always loads
**Correct: B**
**Q36 (3.4)** Developer about to refactor authentication module. Touches 12 files across 3 service boundaries. Two valid architectures in play (session-based vs token-based). Team hasn't agreed which to adopt.
- A) Execute directly — let Claude adopt whichever architecture is most common in existing code
- B) Use plan mode so Claude produces structured plan covering both architectures for team to review before code is written
- C) Split into 12 single-file prompts so no individual request carries full complexity
- D) Author as a skill so it runs as isolated sub-agent
**Correct: B**
**Q37 (3.4)** Platform engineer tracked null-pointer bug to single utility function. Fix is unambiguous: add nil-check guard on line 47 of utils/parser.go. No other file involved, no architectural question.
- A) Execute the fix directly — scope is small, change is understood, planning adds pure overhead
- B) Enter plan mode first so fix and regression test are written down and reviewable
- C) Dispatch fork-context skill so change is isolated from main session
- D) Wrap in custom command to follow team's standard patch workflow
**Correct: A**
**Q38 (3.6)** DevOps engineer wires Claude Code into GitHub Actions. On first push job runs 45 minutes and times out. Logs show claude started and produced no output.
- A) ANTHROPIC_API_KEY secret missing from repository
- B) Runner has insufficient memory — move to larger runner class
- C) Invocation has no timeout — add --timeout 300
- D) claude was invoked without -p, so it started interactively and waited for input that never arrives in CI
**Correct: D**
**Q39 (3.6)** Media company runs Claude Code non-interactively in Jenkins to triage failing tests — produces readable prose summary. Later stage must extract finding count and highest severity via shell script that parses prose — breaks whenever wording shifts.
- A) Pin model version so prose wording stays stable
- B) Instruct Claude to always use fixed phrasing
- C) Add --output-format json so step emits machine-parseable structured output
- D) Move parsing into a second Claude call that reads the prose summary
**Correct: C**

### D4 — Prompt Engineering & Structured Output
**Q40 (4.1)** AI code-review assistant told to "be conservative and avoid flagging things that are probably fine." After two weeks it flags 40-60 comments per PR including lint preferences and naming choices — developer trust collapsing.
- A) Add confidence threshold so only findings rated above 90% are surfaced
- B) Expand system prompt with more paragraphs explaining what "conservative" means
- C) Replace vague directive with explicit rule: flag only where claimed behaviour contradicts actual code; skip style, naming, formatting
- D) Move to more capable model which will interpret the instruction closer to intent
**Correct: C**
**Q41 (4.2)** Contract clause extractor: same NDA clause labelled "Confidentiality" on one run, "Non-Disclosure" on another, sometimes unlabelled. Temperature already 0. Categories are correctly defined — difficulty is which applies to genuinely ambiguous clauses.
- A) Split ambiguous categories into finer-grained labels
- B) Add post-processing rule mapping "Non-Disclosure" onto "Confidentiality"
- C) Raise confidence threshold so only certain clauses receive a label
- D) Build 2-4 few-shot examples showing the reasoning for choosing one category over a plausible alternative
**Correct: D**
**Q42 (4.3)** Invoice parser asks Claude in prose to return JSON. In production: keys misspelled, arrays arrive as comma-separated strings, explanatory prose precedes opening brace → parser exceptions.
- A) Define fields as tool schema and use tool_use with strict: true
- B) Add explicit JSON formatting instructions and examples + retry on parse failure
- C) Ask Claude to wrap object in fenced code block for reliable extraction via regex
- D) Add post-processing step stripping prose before first opening brace
**Correct: A**
**Q43 (4.3)** Healthcare claims extractor uses tool_use with strict JSON schema — malformed-JSON errors at zero. QA audit finds: line-item subtotals not summing to claim total, and a currency amount in the service_date field. Team lead says schema should have prevented this.
- A) Schema defined too loosely — tighter type constraints will prevent both errors
- B) Schema is enforced at generation time — records must have been corrupted after extraction
- C) Adding few-shot examples to tool description will prevent semantic errors by teaching calculation logic
- D) tool_use constrains syntax and types, not meaning — semantic errors need application-layer validation
**Correct: D**
**Q44 (4.3)** Pipeline receives invoices, POs, contracts, and occasionally unrecognised formats. Must call exactly one of four extraction tools per document. Downstream processor requires a tool call in every case. Worry: for unrecognised documents Claude skips tool use and returns plain text.
- A) tool_choice set to "any" — requires a tool call while leaving choice to model
- B) tool_choice "auto" with system prompt instruction to always call a tool
- C) tool_choice "auto" plus application-layer fallback for plain-text responses
- D) Single universal extraction tool with tool_choice set to that specific tool
**Correct: A**
**Q45 (4.3)** Government permitting system must always run validate_document as the very first tool call on each submission, before any extraction or enrichment — every downstream step branches on the validation verdict.
- A) "any" — forces a tool call on first turn so validation cannot be skipped
- B) "auto" with validate_document listed first in tools array so model reaches for it first
- C) {"type": "tool", "name": "validate_document"} — forces that specific tool
- D) "none" on first request, then "auto" afterwards so no other tool runs before validation
**Correct: C**
**Q46 (4.3)** Contract metadata extractor needs: contract type (MSA/NDA/SOW and occasionally unseen types), governing jurisdiction (frequently absent), duration. How should schema handle absent and unanticipated values?
- A) Mark every field required with string types, instruct Claude to write "N/A" when absent
- B) Mark every field required with a validation-retry loop when fields come back missing
- C) Collect all uncertain and unanticipated values into a single free-text "notes" field
- D) Make absent-value fields nullable, add "unclear" for ambiguous categoricals, "other" + free-text detail field for new types
**Correct: D**
**Q47 (4.4)** Procurement extractor: retry strategy sends Claude only the validation error message. Hit rates on recoverable errors (e.g. date as MM/DD/YYYY instead of ISO 8601) are poor.
- A) On retry, send original document + failed extraction + specific validation error
- B) Raise retry ceiling from 2 to 5 for more self-correction opportunities
- C) On retry, ask only for the failed field, omitting the document to keep request small
- D) Route retries through Batch API to cut cost of additional attempts
**Correct: A**
**Q48 (4.4)** Insurance policy extractor: most error classes recover with well-formed retry payload. One never does: governing_jurisdiction is required but genuinely absent from a subset of policies. These consume 3 retry attempts then fail.
- A) Extend retry budget — jurisdiction clauses often phrased unusually, need more attempts
- B) Make field nullable and stop retrying when information is absent from source
- C) Add stronger instruction to search entire document before reporting field as missing
- D) Fall back to second model call inferring likely jurisdiction from parties' addresses
**Correct: B**
**Q49 (4.5)** Legal discovery platform: 200K documents/day. Two workloads: (1) overnight batch classification for next-morning report; (2) real-time clause extraction when attorney opens document and waits. Team wants lower cost without degrading attorney experience.
- A) Batch API for both — 50% saving applies across the board
- B) Batch API for overnight classification; synchronous API for attorney-triggered extraction
- C) Synchronous API for both — uniform latency and simpler infrastructure
- D) Batch API for both with priority flag on real-time requests to shorten queue latency
**Correct: B**
**Q50 (4.6)** CI job reviews 14-file PR in a single prompt. First few files get detailed findings; later files get a sentence each. Cross-file defects missed entirely. Whole diff fits in context window.
- A) Run one focused pass per file, then a separate integration pass with only per-file findings looking for cross-file defects
- B) Raise max_tokens so review has room to treat every file at equal depth
- C) Instruct model to give every file equal attention + minimum findings per file, reject and retry if quota not met
- D) Sort diff so largest files come first — reviewed while attention is freshest
**Correct: A**
**Q51 (4.5)** Nightly Batch job submits 40,000 extraction requests. 380 fail. Current code resubmits all 40,000 because it can't tell which result corresponds to which document.
- A) Rely on order of results array — batch results returned in submission order
- B) Re-submit whole batch — at 50% cost the redundant requests are cheaper than building correlation
- C) Split into 400 batches of 100 so a failure can be narrowed to a small group by re-running that batch
- D) Set a custom_id on each request and use it to correlate results back to source documents
**Correct: D**

### D5 — Context Management & Reliability
**Q52 (5.1)** Insurance claims agent summarises earlier turns. At turn 12, asked to confirm claim amount, it answers: "Based on the figures discussed, the amount appears to be in the expected range." Original figure $47,320 was stated explicitly at turn 3.
- A) Accept summarisation as necessary trade-off — have agent ask customer to restate key figures when needed
- B) Increase context window so earlier turns are never compressed
- C) Maintain a persistent case-facts block with claim amount/policy number/dates — injected verbatim and never summarised
- D) Re-summarise with explicit instruction to preserve all numeric values verbatim
**Correct: C**
**Q53 (5.1)** Legal review agent receives 40-page contract, then 3-page clause index, then 15 pages of case precedents, then 1-paragraph review instruction. Applies instruction correctly, cites opening clauses accurately, but consistently misses obligations on pages 18-22 (the middle). Whole document fits in context window.
- A) Truncate contract to first and last 10 pages
- B) Shrink case-precedents section, moving pages 18-22 nearer the end where recall is stronger
- C) Move to model with larger context window — lowers ratio of middle content to total context
- D) Add explicit section headers and clause identifiers through contract body so middle content has addressable anchors
**Correct: D**
**Q54 (5.2)** Brokerage virtual assistant: identified disputed transaction, confirmed dispute window open, ready to submit form. Mid-conversation customer writes: "Actually, can I just speak to a real person about this?" Form not yet submitted.
- A) Acknowledge, then submit dispute first to avoid losing progress, then transfer
- B) Offer to finish dispute first — task nearly complete, would resolve the issue
- C) Acknowledge and transfer to human immediately, without completing the submission
- D) Assess whether case is complex enough to warrant escalation before deciding whether to honour the request
**Correct: C**
**Q55 (5.2)** Retail chatbot handles delayed-shipment query. Confirms tracking data, gives estimated delivery. Customer: "This is ridiculous, I've been waiting two weeks, your service is terrible." Agent fully capable of resolving — can initiate reshipment. Customer hasn't asked for a human.
- A) Acknowledge frustration, offer choice: speak to human or wait for original shipment
- B) Acknowledge frustration, apologise, explain cause, offer to initiate reshipment
- C) Escalate immediately — expressed frustration is a recognised escalation trigger
- D) Set emotional content aside and restate the delivery estimate in more detail
**Correct: B**
**Q56 (5.3)** Multi-step pipeline: at step 4 of 7 a third-party enrichment API returns 500. Handler catches exception, moves silently to step 5, logs nothing. Records complete pipeline marked successful but unenriched.
- A) Keep suppression but add bounded retry loop before it
- B) Terminate entire pipeline on any single step failure — no partially processed record propagates
- C) Replace silent suppression with structured error context: failure type, what was attempted, partial results, alternative paths
- D) Return empty dict from enrichment step so downstream steps treat unenriched records as valid input
**Correct: C**
**Q57 (5.4)** Autonomous coding agent refactoring large Node.js monorepo. After 80 tool calls, reasoning drifts: now refers to "typical Express middleware pattern" rather than specific class names. Context dominated by raw file dumps; discovered architecture facts were pushed out.
- A) Externalise findings to scratchpad files, delegate deep subtasks to subagents, inject architecture summaries at new phases, compact non-essential history
- B) Restart from scratch with fresh context window, re-run refactor with architecture notes supplied up front
- C) Lower agent's tool-call budget so it can't accumulate enough raw discovery output to degrade
- D) Move to model with larger context window so all 80 tool outputs are retained uncompressed
**Correct: A**
**Q58 (5.5)** Document system reports 97% field-extraction accuracy over 200K documents. Team removes human-in-the-loop validation. Three weeks later: systematic errors on tax certificates — 42% effective_date wrong. That document type is 3% of volume so aggregate metric never moved.
- A) Accept 97% aggregate as sufficient, add targeted post-processing rules for effective_date on tax certificates
- B) Return every document type to manual review until aggregate reaches 99%
- C) Increase training data for tax certificates until error rate falls in line with overall average
- D) Validate accuracy per document type and per field, using stratified sampling to expose category-specific failure rates before automating
**Correct: D**
**Q59 (5.2)** Bank's virtual assistant has customer's full mortgage application. Customer requests rate-lock extension due to builder delay — configured decision policies don't cover this scenario. Agent can find no applicable rule and cannot progress.
- A) Approximate an answer from the closest available policies and present as guidance
- B) Escalate to a human, citing the policy gap, and summarise the situation and what has been established
- C) Keep asking clarifying questions until a matching policy rule can be identified
- D) Decline with standard "unable to process" message and suggest calling during business hours
**Correct: B**
**Q60 (5.6)** Research coordinator receives two credible findings for same metric: vendor whitepaper (March) reports 34% adoption; industry survey (September) reports 51%. Both sources reputable. Synthesis agent must produce a report section on adoption.
- A) Both figures with full attribution — source, publication date, excerpt — flagged as differing measurements
- B) Higher figure — September survey is more recent and supersedes March number
- C) Average of the two figures annotated with range — single defensible number
- D) Neither figure — request research agent find a third source to break the tie
**Correct: A**
**P2-Q9 (5.1)** A legal platform uses Claude to answer questions about 60–80 page vendor contracts. The prompt opens with the question and instructions, then appends the contract text underneath. Accuracy on clause-dependent questions is poor — the model paraphrases loosely rather than quoting the governing text, even though the full contract fits in context. What is the correct fix?
- A) Split each contract across several requests, one section per call, and merge answers afterwards
- B) Pre-filter each contract to the 20 most relevant pages before sending
- C) Run each query twice and average stated confidence across the two runs
- D) Move the contract above the question and instructions, and require the model to quote the governing clauses before answering
**Correct: D**

---

## Session Logging

### workspace.md — written at session start

`workspace.md` is a **planning document for the session about to begin** — not a historical log. Overwrite it before Question 1 using the Write tool. Its purpose is to surface known weak spots so the user can stay alert during the session.

Format:
```
# Session Plan — Foundations, [difficulty], [domain_filter], [N] questions
Date: [run `date +%Y-%m-%d` via Bash]

## Focus
Domain: [user's choice]   Questions: [N]   Difficulty: [level]

## Retake Focus (from official score report, [attempt_date], [score]/1000)
[Only if fexam-scorereport.json exists. List tier-1 objectives (in the chosen domain, if filtered), then tier-2:]
- [Oid] ([exam_pct]% on exam, practice [c]/[t] since, edges retired [r]/[n]): [short label] — key rule: [one sentence distilled from the angle]
[This session: [t1] tier-1 · [t2] tier-2 · [t3] tier-3 questions]

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
  "difficulty": "easy|medium|hard|absurd|exam",
  "domain_filter": "all|D1|D2|D3|D4|D5",
  "score": 11,
  "total": 15,
  "questions": [
    {
      "domain": "D3",
      "subtopic": "3.1",
      "subtopic_label": "CLAUDE.md hierarchy",
      "objective": "O16",
      "correct": true,
      "chosen": "A",
      "trick": null
    },
    {
      "domain": "D1",
      "subtopic": "1.2",
      "subtopic_label": "Multi-agent orchestration",
      "objective": "O4",
      "edge": "O4.e1",
      "correct": false,
      "chosen": "C",
      "trick": "downstream_agent_not_coordinator",
      "trick_description": "Coverage gaps always trace back to the coordinator's decomposition, not downstream agents."
    }
  ]
}
```

**Field rules:**
- `subtopic`: Use the section codes from the domain content tables (e.g. `"1.2"`, `"3.6"`, `"4.3"`). Every question must have one — assign it when generating the question, not after the answer.
- `objective`: The score-report objective ID (`"O1"`–`"O29"`) the question was planned against. Assign it when generating the question. For a question that touches several objectives, record the one it was planned for. Use `null` for a tier-3 filler question on a subtopic that no objective maps to (e.g. 1.2, 3.6, 4.1, 5.6). Omit only if `fexam-scorereport.json` is absent. Older records have no `objective` field; skip them in objective-level stats.
- `edge`: The edge ID (e.g. `"O20.e1"`) planned for a tier-1/tier-2 question. Omit for tier-3 questions. Edge retirement is counted from this field, so it must be the edge the question was built on.
- `trick`: When the answer was wrong, use a short snake_case label for the cognitive trap (e.g. `"probabilistic_fix_for_compliance"`, `"retrying_valid_empty_result"`, `"user_level_config_not_project"`, `"downstream_agent_not_coordinator"`, `"over_engineered_solution"`). Use `null` when correct.
- `trick_description`: When the answer was wrong, a single human-readable sentence stating what the trap is and why it catches people — the same sentence shown in the "Trap triggered" line during feedback. Use `null` when correct.
- `chosen`: Always record the letter the user submitted, correct or not.
- `date`: Run `date +%Y-%m-%d` via Bash — never hard-code.

Use `python3` via Bash for `score` (verify it matches the tally) and for any derived fields in stats mode.

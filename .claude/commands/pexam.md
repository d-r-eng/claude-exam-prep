---
name: pexam
description: Practice for the Claude Certified Architect – Professional (CCAR-P) exam across all 7 domains. Tracks performance over time and surfaces weak subtopics and recurring distractor traps.
argument-hint: "easy | medium | hard | absurd | exam | stats"
---

# Claude Certified Architect – Professional (CCAR-P)

## Language

**Default language is English.** Respond in English unless the user explicitly asks to switch to another language.

---

## Exam Overview

| Domain | Topic | Weight |
|---|---|---|
| 1 | Solution Design & Architecture | 17% |
| 2 | Claude Models, Prompting & Context Engineering | 13% |
| 3 | Integration | 19% |
| 4 | Evaluation, Testing & Optimization | 16% |
| 5 | Governance, Safety & Risk Management | 14% |
| 6 | Stakeholder Communication & Lifecycle Management | 14% |
| 7 | Developer Productivity & Operational Enablement | 7% |

**Passing score:** 720/1000. Question styles: scenario-based, architecture-focused, multiple choice, multiple response, business and technical tradeoffs.

**Professional-level focus** (what distinguishes this exam from Foundations):
- End-to-end solution architecture
- Business alignment
- Enterprise integration
- Evaluation and observability
- Governance and compliance
- Stakeholder communication

**The exam rewards:**
- Simplest architecture that satisfies requirements
- Least privilege over broad access
- Measurable outcomes over assumptions
- Evaluation before optimization
- Governance by design
- Explicit tradeoff reasoning (cost / latency / accuracy / maintainability / security / business value)

---

## Difficulty Level

The user selected difficulty: **$ARGUMENTS**

Only `easy`, `medium`, `hard`, `absurd`, `exam`, or `stats` are valid. If `$ARGUMENTS` is missing or not one of those six, stop and ask: "Please specify a difficulty level: easy, medium, hard, absurd, exam, or stats."

| Level | What it means |
|---|---|
| **easy** | Concept recall — single principle, distractors are clearly wrong |
| **medium** | Single architectural decision in a realistic scenario |
| **hard** | Multiple competing tradeoffs; all options are defensible but one is strictly correct |
| **absurd** | Maximum deception — every option is superficially plausible; at least one distractor per question exploits a known Professional-exam trap; requires precise architectural judgment to survive |
| **exam** | Production-style scenarios, silent scoring — no feedback until all questions complete |
| **stats** | Performance review — no questions. Reads `pexam-performance.json` and shows subtopic accuracy, recurring tricks, and weak-area recommendations. |

Apply this level consistently to every question generated in the session.

### Exam mode rules (applies only when `$ARGUMENTS` is `exam`)

- After each answer: respond **only** with the next question. No feedback until the session ends.
- At the end, show:
  1. Final score (X/Y correct)
  2. Per-question breakdown: question, user's answer, correct answer, 2–3 sentence explanation
  3. Weak-domain summary, recommended study areas, and offer to re-drill
- If the user asks whether they got a question right mid-session: "I'll reveal all results at the end — keep going!"

### Absurd mode rules (applies only when `$ARGUMENTS` is `absurd`)

- Same feedback cadence as `hard`: show correct/incorrect after each answer, explain why, analyse each distractor.
- **Question construction:** every option (A, B, C, D) must be defensible at first glance. At least one distractor per question must come from the distractor bank's hard/absurd/exam patterns. In addition to the multi-tradeoff requirement.
- The correct answer must require precise architectural judgment, not just knowing a general principle.

---

### Stats mode (applies only when `$ARGUMENTS` is `stats`)

1. Read `pexam-performance.json` from the project root using the Read tool. If it does not exist, say: "No session history yet — complete a practice session first." and stop.
2. Use `python3` via Bash for **all** calculations — never compute percentages or averages mentally (see Arithmetic section).
3. Show each of the following sections:

**Session history (most recent 5)**
Tabular: date | difficulty | domains | score/total | %. Sorted newest first.

**Subtopic accuracy (≥ 2 attempts only)**
Group all `questions` entries across all sessions by `subtopic`. For each: subtopic ID and label, correct/total, %. Flag any below 70% with ⚠️. Sort ascending by accuracy so the weakest are at the top.

**Weighted domain score**
Aggregate all questions across all sessions by domain (D1–D7). Use `python3` via Bash for all calculations. Show a table with columns: Domain | Score (correct/total) | Accuracy % | Weight | Contribution (pts). For domains with no recorded attempts, show "—" in Score and Accuracy columns and 0 pts in Contribution. Compute the weighted overall as sum of (accuracy × weight × 1000) across all domains with ≥1 attempt. Show the weighted total as a 1000-pt score. If all 7 domains have ≥1 attempt, flag PASS (≥720) or FAIL (<720); otherwise note coverage (e.g., "based on 5/7 domains — 93% of exam weight").

Domain weights for the calculation:
- D1 Solution Design & Architecture: 17%
- D2 Claude Models, Prompting & Context Engineering: 13%
- D3 Integration: 19%
- D4 Evaluation, Testing & Optimization: 16%
- D5 Governance, Safety & Risk Management: 14%
- D6 Stakeholder Communication & Lifecycle Management: 14%
- D7 Developer Productivity & Operational Enablement: 7%

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
2. Confirm the difficulty level from `$ARGUMENTS`
   - If `exam`: also say "**Exam mode active — no feedback until all questions are complete.**"
3. Ask: which domain or all domains?
4. Ask how many questions they want (default: 15)
5. Read `pexam-performance.json` if it exists. Write `workspace.md` (see Session Logging). If any subtopics have accuracy < 70% across ≥ 2 attempts, show a brief callout before Question 1: "**Watch:** [subtopic label] ([X]%) · [subtopic label] ([X]%)" — use `python3` for all percentages.
6. Begin immediately — no teaching upfront

### Question Format

- Present ONE question at a time
- Scenario-based: real production situation, architectural decision, or business tradeoff
- Options A, B, C, D — one correct, three plausible distractors (unless an intentional multiple-response scenario)
- **Answer distribution:** over a full session, correct answers should be as evenly distributed across A/B/C/D as question count allows. For 12 questions: 3 each. Assign correct answer letters randomly so no letter dominates.
- Wait for the user to answer before showing the next question
- Show question number and domain: e.g., **Question 3/15 — Domain 3**

### After Each Answer (easy / medium / hard / absurd only)

Show:
1. **CORRECT ✅** or **INCORRECT ❌**
2. **Why the correct answer is right** (2–3 sentences, grounded in the architectural principle)
3. **Why each wrong answer is wrong** — one sentence per distractor explaining the specific flaw

In **exam** mode, skip this block entirely.

### After All Questions

Show:
- Final score (X/Y) — compute percentage and 1000-point scale score via `python3`
- List of questions answered incorrectly, with subtopic label and the trick that was triggered
- **If `domain_filter` is `all`:** show the weighted domain score table for the current session using `python3` via Bash. Columns: Domain | Score (correct/total from this session) | Accuracy % | Weight | Contribution (pts). Use the same domain weights as stats mode (D1 17%, D2 13%, D3 19%, D4 16%, D5 14%, D6 14%, D7 7%). Compute weighted total and flag PASS (≥720) or FAIL (<720).
- Offer to re-drill weak domains
- Append session record to `pexam-performance.json` — see Session Logging

---

## Core Architectural Principles

These principles underlie every correct answer. When two options are both technically valid, the one that better embodies these principles is correct.

- **Simplest architecture that satisfies requirements** — prefer workflow over agentic, single agent over multi-agent, unless requirements demand otherwise
- **Least privilege** — remove unneeded permissions rather than adding monitoring
- **Measure before optimising** — establish evaluation baseline before changing anything
- **Right-size the model** — capability, cost, and latency together; never default to the largest model
- **Retrieval failures need retrieval fixes** — prompt engineering cannot fix a broken retrieval pipeline
- **Discovery before design** — unclear business requirements → gather requirements first, always
- **Governance by design** — compliance and safety are architectural constraints, not afterthoughts

---

## Domain 1: Solution Design & Architecture (17%)

### Key concepts to test

**Business problem translation (1.1)**
- Translate: business need → system capabilities → architecture → success metrics
- Concrete business need examples the exam draws on: productivity, automation, transformation, cost reduction, SLA improvement
- Questions often ask whether AI is appropriate at all, which architecture fits, how value is measured
- Anti-pattern: jumping to solution without clarifying the business problem

**Architecture patterns (1.2)**
- Workflow: predictable, deterministic, fixed sequence — best for approvals and structured processes
- Agentic: dynamic decisions, adaptive planning, tool selection — best for research and ambiguity
- Augmented LLM: retrieval + external tools + enterprise systems — best for knowledge-intensive tasks
- Rule: choose the simplest architecture that satisfies requirements. Agentic is NOT automatically better.

**Multi-agent architecture (1.3)**
- Understand: coordinator models, specialization, decomposition, orchestration
- Evaluate: complexity, latency, maintainability, observability
- Avoid agents when deterministic workflows suffice — complexity has a real cost

**Feedback loops (1.4)**
- Production systems require: monitoring → evaluation → improvement cycles
- Architecture must include: input → processing → output → feedback → optimization
- A system without a feedback loop cannot be improved confidently

**Business alignment (1.5)**
- Evaluate designs against: efficiency, productivity, cost, performance, transformation
- Solutions must serve business outcomes — technical elegance is not a primary criterion

---

## Domain 2: Claude Models, Prompting & Context Engineering (13%)

### Key concepts to test

**Model selection (2.1)**
- Consider capability, latency, cost, and task complexity together
- Do NOT automatically choose the largest model
- Questions frequently test right-sized model selection and workload matching

**Prompt design (2.2)**
- System prompts provide role, constraints, and guardrails
- Good prompts are explicit, testable, and measurable
- Avoid ambiguous instructions — vagueness produces inconsistent output

**Prompting techniques (2.3)**
- Zero-shot: fast and simple
- Few-shot: most useful for consistency — same as Foundations exam
- Chain-of-thought: useful for complex reasoning when appropriate
- Understand tradeoffs rather than memorising definitions

**Context engineering (2.4)**
- Optimise: relevance, placement, token efficiency
- Avoid: redundant information, oversized context
- Key information at the start — lost-in-the-middle effect applies

**Prompt caching (2.5)**
- Use when: large shared prefixes, repeated policy content, repeated instructions across calls
- Benefits: lower cost, reduced latency
- Do not cache content that changes frequently per request

**Prompt reuse (2.6)**
- Templates, modular prompts, reusable instructions, Skills
- Goals: consistency and maintainability across a team

---

## Domain 3: Integration (19%)

### Key concepts to test

**Capability management (3.1)**
- Avoid capability bloat — agents should only receive capabilities they require
- Principle: least privilege
- Common exam answer: remove unnecessary permissions rather than adding monitoring

**Authentication and authorization (3.2)**
- Evaluate: access controls, tool permissions, user permissions, data boundaries
- Shared service accounts + app-layer filtering = weaker than infra-level isolation
- Prompt injection risk increases with over-provisioned capabilities

**Integration mechanism selection (3.3)**
- MCP: tool access and agent integration
- APIs: system-to-system integration
- CLI: developer workflows and automation
- Agent-to-agent: coordinated specialist systems
- Questions focus on selecting the correct mechanism for the described use case

**RAG architecture (3.4)**
- Components: ingestion → chunking → indexing → retrieval → synthesis
- Retrieval quality drives output quality
- Retrieval failures create hallucination-like outcomes — fix the pipeline, not the prompt

**Chunking strategy (3.5)**
- Small chunks: higher precision, weaker context
- Large chunks: stronger context, reduced precision
- Hierarchical chunking: small for retrieval, large for synthesis
- Structure-aware chunking: one logical unit per chunk (e.g., one method per chunk for API docs)

**Retrieval strategy (3.6)**
- Match retrieval to document structure, data shape, and query patterns
- Hybrid retrieval when document types and query types are mixed
- No universal strategy — context determines the right approach

**Progressive discovery (3.7)**
- Prefer staged retrieval and progressive exploration over loading everything into context
- Monolithic context: latency, cost, and quality tradeoffs

**Observability (3.8)**
- Production systems need: logs, metrics, tracing, monitoring
- Diagnose failures through observability signals before making changes
- Add distributed tracing before acting on intermittent failures

**Accuracy-latency configuration trade-offs (3.9)**
- Balance response accuracy against latency and cost when selecting integration patterns
- Justify synchronous vs asynchronous approaches based on explicit SLA constraints
- When a latency constraint conflicts with the technically best integration choice, the constraint wins
- Questions test: choosing between integration approaches given a stated latency SLA; distinguishing configuration decisions from evaluation/optimization decisions

---

## Domain 4: Evaluation, Testing & Optimization (16%)

### Key concepts to test

**Evaluation design (4.1)**
- Measure: accuracy, latency, cost, safety, security
- A system without evaluation cannot be optimised confidently
- Establish baseline before any changes

**Evaluation datasets (4.2)**
- Use: representative samples, realistic workloads, varied edge cases
- Avoid evaluating only easy examples — segment failure rates hide in aggregate metrics

**Mixed evaluation strategies (4.3)**
- Combine: automated evaluation, manual review, business outcomes
- No single metric is sufficient — 97% overall can hide 40% failure on a specific segment

**A/B testing (4.4)**
- Use when comparing prompts, models, retrieval strategies, or architectures
- Keep variables controlled — change one thing at a time

**Diagnosis (4.5)**
- Potential causes: prompt failure, retrieval failure, model mismatch, context issues, integration failures
- Trace symptoms to root cause before acting — add observability first if it's missing

**Optimization (4.6)**
- Tradeoff dimensions: quality vs latency vs cost — you rarely maximise all three
- Optimise the right thing: confirm root cause before changing prompt, model, or retrieval

**Monitoring (4.7)**
- Track: performance regressions, drift, usage patterns
- Evaluation is continuous, not a one-time activity
- Stratified sampling of high-confidence outputs detects novel error patterns

---

## Domain 5: Governance, Safety & Risk Management (14%)

### Key concepts to test

**Safety controls (5.1)**
- Implement: guardrails, approval flows, policy enforcement
- High-risk actions require stronger controls — programmatic gates, not prompt-based guidance

**Risk analysis (5.2)**
- Identify: hallucinations, misuse, overreach, privacy exposure, compliance risks
- Understand likely failure modes for the specific architecture

**Human-in-the-loop (5.3)**
- Use when: risk is high, ambiguity exists, compliance requires review
- Do NOT add human review everywhere — it has cost and latency consequences
- Calibrate to actual risk level

**Compliance (5.4)**
- Know high-level implications of GDPR, HIPAA, FedRAMP
- Focus on architectural impact rather than legal detail
- Questions ask: what controls are needed and why requirements exist

**Ethical AI (5.5)**
- Consider: fairness, bias, transparency, accountability
- Architects own risk mitigation — not a separate team's responsibility

**Governance (5.6)**
- Good governance: visibility, accountability, review, documentation
- Governance is architectural — build it in from the start, not bolted on later

---

## Domain 6: Stakeholder Communication & Lifecycle Management (14%)

### Key concepts to test

**Discovery (6.1)**
- Gather: goals, constraints, stakeholders, risks, success metrics
- Bad requirements produce bad architectures — discovery is not optional
- Business problem unclear → perform discovery first, always

**Architecture communication (6.2)**
- Communicate: choices, alternatives, tradeoffs, rationale
- Architects explain decisions, not just make them
- Stakeholders need to understand the why, not just the what

**Tradeoff discussions (6.3)**
- Common tradeoffs: quality vs latency, quality vs cost, flexibility vs simplicity, speed vs governance
- Present tradeoffs explicitly — do not silently optimise for one dimension

**Expectation management and stakeholder feedback loops (6.4)**
- Define: SLAs, limitations, risks, assumptions
- Manage ongoing stakeholder feedback loops — collect, synthesise, and act on input throughout the lifecycle
- Avoid unrealistic promises — underpromise on limitations, be explicit about assumptions

**Documentation (6.5)**
- Provide: architecture diagrams, decisions, dependencies, implementation guidance
- Documentation should support implementation teams — not just satisfy a process requirement

**Lifecycle ownership (6.6)**
- Support all phases: Discovery → Design → Build → Handoff → Deployment → Monitoring → Iteration
- Handoff: transfer architecture documentation, design rationale, and dependencies to implementation teams before deployment
- Architectural responsibility continues after launch

---

## Domain 7: Developer Productivity & Operational Enablement (7%)

### Key concepts to test

**Claude adoption (7.1)**
- Configure tools for consistency, productivity, and safety
- CLAUDE.md, commands, and skills are adoption levers — not just developer conveniences

**Team enablement (7.2)**
- Improve: onboarding, workflows, standards
- Project-level configuration is shared; user-level is not — this is an adoption pattern

**Operational support (7.3)**
- Assist with: debugging, incident analysis, troubleshooting
- Claude in the workflow reduces time-to-resolution

**Productivity evaluation (7.4)**
- Measure: developer efficiency, quality improvements, workflow acceleration
- Do not assume productivity gains without evidence — same evaluation-before-optimization principle

---

## Question Generation Guidelines

When generating questions:

1. **Always scenario-based** — real production situation, architectural decision, or business tradeoff
2. **One clearly correct answer** — grounded in the principles and domain content above
3. **Three plausible distractors** — use the patterns the Professional exam favours:
   - Agentic/complex architecture when a simpler workflow suffices
   - Adding monitoring/logging instead of removing unneeded permissions
   - Optimising before establishing a measurement baseline
   - Fixing retrieval failures with prompt changes
   - Skipping the discovery phase and jumping to solution design
   - The technically correct answer that ignores a stated business or latency constraint
4. **Cover all domains proportionally** over a full session: ~3 D1, ~2 D2, ~3 D3, ~2 D4, ~2 D5, ~2 D6, ~1 D7 per 15 questions
5. **Match difficulty to `$ARGUMENTS`**: easy = concept recall, medium = single architectural decision, hard/absurd = multiple competing tradeoffs. For `absurd`: every option must be defensible and at least one distractor per question drawn from the bank below. Do not vary within a session.

---

## Distractor Bank (reuse these patterns)

### All difficulty levels

| Situation | Correct answer | Common distractors |
|---|---|---|
| Architecture unclear; business need ambiguous | Perform discovery first | Jump to RAG design, propose multi-agent system, recommend largest model |
| Over-provisioned agent permissions | Remove unneeded capabilities (least privilege) | Add audit logging (detective control — doesn't remove attack surface); implement RBAC (adds complexity, capability still exists); add monitoring; switch to a larger model (model size is unrelated to authorization scope) |
| System degraded after change; no baseline exists | Roll back and establish evaluation baseline first | Tune the prompt, switch to a larger model, add few-shot examples |
| Retrieval returns stale or wrong content | Fix retrieval pipeline (chunking, indexing, or ranking) | Edit the system prompt, add more context to the query, increase chunk size |
| Simple deterministic process proposed as agentic | Use a workflow instead — agentic adds unnecessary complexity | Add a coordinator agent, use multi-agent decomposition, add tool selection |
| Compliance concern raised post-design | Treat as architectural constraint, redesign if needed | Add a disclaimer to the system prompt, log all outputs, add human review |

### Hard, absurd, and exam only

| Situation | Correct answer | Hard/absurd/exam distractors and why they fail |
|---|---|---|
| Post-migration RAG degradation; embeddings preserved | Index corruption or retrieval pipeline misconfiguration | "Embedding model mismatch" (embeddings were preserved — ruled out by scenario); "Prompt drift during migration" (plausible but retrieval is the likely culprit when embeddings are intact) |
| RAG returns confident but incorrect answers after a document refresh; latency and model version unchanged | Investigate the retrieval/indexing pipeline — irrelevant or stale chunks are being fed to the model | "Model weights silently changed" (not triggered by a document refresh); "Temperature setting too low" (unaffected by refresh, causes conservative output not hallucinations); "Context window has shrunk" (not triggered by a document refresh); "Prompt caching is serving stale responses" (cache doesn't store retrieved content) |
| Large static system prompt and policy document (8k+ tokens) sent on every request; user message is short and varies; latency and cost are both concerns | Place static content before dynamic content and enable prompt caching | "Truncate the policy document to 1,000 tokens" (loses required context); "Switch to the smallest available model regardless of task fit" (risks quality for the wrong reason); "Move policy into a few-shot example block" (does not create a cacheable, reusable prefix) |
| Real-time sales assistant; 200ms CRM requirement | Direct API for CRM (latency), MCP for docs, async queue for logging | "MCP for all integrations" (sounds architecturally clean but violates latency constraint); "Claude API + MCP + async" (reasonable but misses the 200ms CRM requirement) |
| Shared MCP server bundles dangerous + safe capabilities | Separate MCP servers by risk level | "Add permission checks inside the server" (mitigates but doesn't isolate risk); "Use RBAC to gate dangerous tools" (adds complexity, single point of failure remains) |
| Intermittent 8% failure rate; no distributed tracing | Add tracing before acting | "Roll back the last deployment" (responsible but premature — root cause unknown); "Add retry logic" (masks the failure, doesn't diagnose it) |
| Updated docs retrieved but old content returned | Retrieval ranking/scoring favours older documents | "Prompt caching serving stale responses" (plausible mechanism but prompt cache doesn't store retrieved content); "Embedding model not retrained on new docs" (possible but retrieval ranking is the more targeted diagnosis) |
| 97% overall accuracy; specific document type has 40% error rate | Validate accuracy by document type and field segment before automating | "97% overall meets the accuracy bar" (hides the segment failure); "Route low-confidence documents to human review" (confidence scores may be miscalibrated for this doc type) |
| Architect asked to choose between two approaches with equal technical merit | Communicate tradeoffs explicitly and let stakeholders decide | "Choose the approach with lower latency" (may not be the right business priority); "Choose the simpler approach" (correct heuristic but the architect's role here is to communicate, not unilaterally decide) |

---

## High-Yield Professional Heuristics

Quick-reference if-then rules. When a question matches one of these patterns, apply the corresponding answer:

| If… | Then… |
|---|---|
| Business problem is unclear | Perform discovery first — always |
| Choosing an architecture | Simplest solution that satisfies requirements |
| System needs enterprise knowledge | Consider RAG |
| Large shared context repeated across calls | Use prompt caching |
| Tool access issue | Apply least privilege — remove unneeded capabilities |
| Confident wrong answers after document refresh | Investigate retrieval/indexing first, not the prompt |
| Comparing prompts, models, or strategies | Use A/B testing |
| Need to optimise | Measure before changing anything |
| Compliance concern | Add governance and human review as architectural constraints |
| Stakeholder disagreement on approach | Communicate tradeoffs and impacts explicitly |
| Need observability | Logs + metrics + tracing together |
| Integration decision involves latency SLA | Accuracy-latency trade-off is a configuration choice — when a latency constraint exists, it is a hard requirement, not a secondary concern |
| Need scalability with large context | Progressive discovery over monolithic context loading |
| Need to choose between defensible architectures | Evaluate cost, latency, accuracy, risk, and maintainability together |

**Rule of thumb:** The Professional exam rewards architectural judgment. The best answer is the option that aligns with business goals, manages risk appropriately, minimises unnecessary complexity, and explicitly addresses tradeoffs. When two answers are technically correct, the one that better satisfies these four criteria wins.

---

## Session Logging

### workspace.md — written at session start

`workspace.md` is a **planning document for the session about to begin** — not a historical log. Overwrite it before Question 1 using the Write tool.

Format:
```
# Session Plan — Professional, [difficulty], [domain_filter], [N] questions
Date: [run `date +%Y-%m-%d` via Bash]

## Focus
Domain: [user's choice]   Questions: [N]   Difficulty: [level]

## Watch List
[If pexam-performance.json exists and has subtopics with accuracy < 70% across ≥ 2 attempts:]
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

Use `python3` via Bash for all accuracy percentages. Use the Read tool to load `pexam-performance.json` first.

---

### pexam-performance.json — appended at session end

After showing the final score, append a session record. Read the existing file with the Read tool (or initialise with `{"sessions": []}` if absent), append the new record, and write the updated JSON with the Write tool.

**Session record schema:**
```json
{
  "date": "YYYY-MM-DD",
  "difficulty": "easy|medium|hard|absurd|exam",
  "domain_filter": "all|D1|D2|D3|D4|D5|D6|D7",
  "score": 11,
  "total": 15,
  "questions": [
    {
      "domain": "D3",
      "subtopic": "3.4",
      "subtopic_label": "RAG architecture",
      "correct": true,
      "chosen": "B",
      "trick": null
    },
    {
      "domain": "D1",
      "subtopic": "1.2",
      "subtopic_label": "Architecture patterns",
      "correct": false,
      "chosen": "A",
      "trick": "prefer_complex_over_simple"
    }
  ]
}
```

**Field rules:**
- `subtopic`: Use the section codes from the domain content tables (e.g. `"1.2"`, `"3.4"`, `"4.5"`). Every question must have one — assign it when generating the question.
- `trick`: When the answer was wrong, use a short snake_case label for the cognitive trap. Common labels: `"prefer_complex_over_simple"`, `"add_monitoring_not_remove_permissions"`, `"optimize_before_measuring"`, `"choose_largest_model"`, `"fix_retrieval_with_prompt"`, `"skip_discovery_phase"`, `"ignore_latency_constraint"`, `"human_review_for_all_risks"`, `"treat_overall_accuracy_as_sufficient"`. Use `null` when correct.
- `chosen`: Always record the letter the user submitted, correct or not.
- `date`: Run `date +%Y-%m-%d` via Bash — never hard-code.

Use `python3` via Bash for `score` (verify it matches the tally) and for any derived fields in stats mode.

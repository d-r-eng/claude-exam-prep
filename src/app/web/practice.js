/* Exam Prep — runs the real /fexam and /pexam commands in the Kiln screens.
   The server drives Claude Code; this page shows the session and sends answers. */
(() => {
  "use strict";

  const app = document.getElementById("app");
  const { render: md, inline, esc } = window.Markdown;
  const LETTERS = ["A", "B", "C", "D"];
  const DIFFS = {
    easy: "Direct recall: one concept, distractors clearly wrong if you studied.",
    medium: "A realistic scenario around one concept. One distractor has a clear flaw.",
    hard: "Two or more interacting concepts. Every option is defensible; one is strictly correct.",
    absurd: "Maximum deception. Every option looks right and at least one is a known exam trap.",
    exam: "Hard-style questions with no feedback until the end, then a full breakdown.",
  };
  const EXAMS = [
    { id: "fexam", cmd: "/fexam", name: "Foundations", meta: "CCAR-F · 5 domains · pass 720" },
    { id: "pexam", cmd: "/pexam", name: "Professional", meta: "CCAR-P · 7 domains · pass 720" },
  ];

  const store = {
    get(k, s) { try { return (s || localStorage).getItem(k); } catch { return null; } },
    set(k, v, s) { try { const t = s || localStorage; v == null ? t.removeItem(k) : t.setItem(k, v); } catch { /* ignore */ } },
  };
  const ss = (() => { try { return sessionStorage; } catch { return null; } })();

  const state = {
    view: "setup",
    health: null,
    setup: null,
    form: {
      exam: store.get("exam") || "fexam",
      difficulty: store.get("difficulty") || "medium",
      domain: "all",
      count: Number(store.get("count")) || 15,
    },
    s: null,            // session view from the server
    picked: null,       // letter picked for the current question
    sentFor: null,      // question number whose answer is in flight
    revealed: null,     // question number revealed after feedback
    busyAction: false,
    draft: "",
  };

  // ---------- helpers ----------
  const fmtPct = (p) => (p == null ? "—" : `${Number.isInteger(p) ? p : Number(p).toFixed(1)}%`);
  const pyRound = (x) => { const f = Math.floor(x), d = x - f; return d > 0.5 ? f + 1 : d < 0.5 ? f : (f % 2 === 0 ? f : f + 1); };
  const examOf = (id) => EXAMS.find((e) => e.id === id) || EXAMS[0];
  const DOMAIN_NAMES = {
    fexam: { D1: "Agentic Architecture & Orchestration", D2: "Tool Design & MCP Integration", D3: "Claude Code Configuration & Workflows",
             D4: "Prompt Engineering & Structured Output", D5: "Context Management & Reliability" },
    pexam: { D1: "Solution Design & Architecture", D2: "Claude Models, Prompting & Context Engineering", D3: "Integration",
             D4: "Evaluation, Testing & Optimization", D5: "Governance, Safety & Risk Management",
             D6: "Stakeholder Communication & Lifecycle Management", D7: "Developer Productivity & Operational Enablement" },
  };
  const domainName = (exam, id) => (DOMAIN_NAMES[exam] || {})[id] || "";
  const secondsSince = (iso) => Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000));

  async function api(path, body) {
    const res = await fetch(path, body ? {
      method: "POST", cache: "no-store", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    } : { cache: "no-store" });
    let data = {};
    try { data = await res.json(); } catch { /* empty */ }
    if (!res.ok) throw new Error(data.error || `${res.status} ${res.statusText}`);
    return data;
  }

  function toast(msg) {
    let t = document.getElementById("toast");
    if (!t) { t = document.createElement("div"); t.id = "toast"; t.className = "toast"; t.setAttribute("role", "alert"); document.body.appendChild(t); }
    t.textContent = msg; t.hidden = false;
    clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, 6000);
  }

  // ---------- theme ----------
  const savedTheme = store.get("theme");
  if (savedTheme) document.documentElement.dataset.theme = savedTheme;
  document.getElementById("theme").addEventListener("click", () => {
    const cur = document.documentElement.dataset.theme
      || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    store.set("theme", next);
  });

  // ---------- session model ----------
  function derive(s) {
    const claude = s.turns.filter((t) => t.role === "claude");
    const last = claude[claude.length - 1] || null;
    const lb = last && last.block;
    const questions = {}, feedback = {};
    let watch = [], total = s.count;
    for (const t of claude) {
      const b = t.block;
      if (!b) continue;
      if (b.question && b.question.number) { questions[b.question.number] = b.question; total = b.question.total || total; }
      if (b.feedback && b.feedback.question_number) feedback[b.feedback.question_number] = b.feedback;
      if (Array.isArray(b.watch) && b.watch.length) watch = b.watch;
    }
    const denials = claude.flatMap((t) => t.denials || []);
    const current = lb && lb.awaiting === "answer" && lb.question ? lb.question : null;
    return { claude, last, lb, questions, feedback, watch, total, denials, current,
             lastFb: lb && lb.feedback, summary: lb && lb.summary };
  }

  // ---------- boot ----------
  async function boot() {
    try {
      const [health] = await Promise.all([api("/api/health"), loadSetup()]);
      state.health = health;
    } catch (err) {
      app.innerHTML = `<div class="callout"><b>The app couldn't start.</b> ${esc(err.message)}</div>`;
      return;
    }
    const sid = new URLSearchParams(location.search).get("session") || store.get("session", ss);
    if (sid) {
      try { return openSession(await api(`/api/sessions/${sid}`)); } catch { store.set("session", null, ss); }
    }
    render();
  }

  async function loadSetup() {
    state.setup = await api(`/api/setup?exam=${state.form.exam}`);
    if (!state.setup.domains.some((d) => d.id === state.form.domain)) state.form.domain = "all";
  }

  function openSession(s) {
    state.s = s; state.view = "session";
    store.set("session", s.id, ss);
    history.replaceState(null, "", `/practice?session=${s.id}`);
    state.picked = null; state.sentFor = null; state.revealed = null;
    render();
    if (s.busy) poll();
  }

  let pollTimer = null, tick = null;
  function poll() {
    clearTimeout(pollTimer); clearInterval(tick);
    tick = setInterval(() => {
      const el = app.querySelector("[data-elapsed]");
      if (el && state.s) el.textContent = `${secondsSince(state.s.updated)}s`;
    }, 1000);
    const go = async () => {
      if (state.view !== "session" || !state.s) return;
      try {
        const s = await api(`/api/sessions/${state.s.id}`);
        const was = state.s;
        state.s = s;
        if (!s.busy) {
          clearInterval(tick);
          if (was.busy) { state.sentFor = null; state.picked = null; }
          render();
          const fb = app.querySelector("#fb, .stem");
          fb?.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
          return;
        }
        render();
      } catch (err) { toast(err.message); }
      pollTimer = setTimeout(go, 1500);
    };
    pollTimer = setTimeout(go, 1200);
  }

  // ---------- render ----------
  function render() {
    if (state.view === "setup") app.innerHTML = setupView();
    else app.innerHTML = sessionView();
    wire();
  }

  function healthBanner() {
    const h = state.health;
    if (!h || h.ok) return "";
    return `<div class="callout"><b>Claude Code isn't ready.</b> ${inline(h.message)} <button type="button" class="linkish" data-act="recheck">Check again</button></div>`;
  }

  function setupView() {
    const f = state.form, s = state.setup;
    const r = s.scoreReport && f.exam === "fexam" ? s.scoreReport : null;
    const t1 = r ? pyRound(f.count * (r.mix.tier1 ?? 0.4)) : 0;
    const t2 = r ? pyRound(f.count * (r.mix.tier2 ?? 0.3)) : 0;
    const t3 = f.count - t1 - t2;
    const ready = state.health && state.health.ok;
    const unfinished = (s.sessions || []).filter((x) => !x.finished);
    return `
    <div class="setup">
      <div class="setup-main">
        <header class="head"><div>
          <h1>Start a session</h1>
          <p class="sub">Runs your real <code>${examOf(f.exam).cmd}</code> command through Claude Code. It reads your history, asks the questions, and saves the session itself.</p>
        </div></header>
        ${healthBanner()}
        ${unfinished.length ? `
        <section class="card resume">
          <h2>Unfinished sessions</h2>
          <ul class="resume-list">${unfinished.map((x) => `
            <li><div><b>${esc(examOf(x.exam).cmd)} ${esc(x.difficulty)}</b>${x.domain !== "all" ? ` · ${esc(x.domain)}` : ""}
              <span class="muted"> · ${x.answered}/${x.total} answered · ${esc(String(x.updated).replace("T", " ").slice(0, 16))}</span>
              ${x.error ? `<span class="fail"> · stopped</span>` : ""}</div>
              <button type="button" class="btn" data-open="${esc(x.id)}">Continue</button></li>`).join("")}
          </ul>
        </section>` : ""}
        <fieldset class="field">
          <legend>Exam</legend>
          <div class="exam-cards">${EXAMS.map((e) => `
            <button type="button" class="exam-card" data-exam="${e.id}" aria-pressed="${f.exam === e.id}">
              <span class="mono muted">${e.cmd}</span>
              <span class="exam-name">${e.name}</span>
              <span class="muted">${e.meta}</span>
            </button>`).join("")}
          </div>
        </fieldset>
        <fieldset class="field">
          <legend>Difficulty</legend>
          <div class="pills">${Object.keys(DIFFS).map((d) => `
            <button type="button" class="pill" data-diff="${d}" aria-pressed="${f.difficulty === d}">${d}</button>`).join("")}
          </div>
          <p class="hint">${esc(DIFFS[f.difficulty])}</p>
        </fieldset>
        <div class="field-row">
          <div class="field grow">
            <label for="domain">Domain</label>
            <select id="domain">
              <option value="all"${f.domain === "all" ? " selected" : ""}>All domains (weighted)</option>
              ${s.domains.map((d) => `<option value="${d.id}"${f.domain === d.id ? " selected" : ""}>${d.id} · ${esc(d.name)}</option>`).join("")}
            </select>
          </div>
          <div class="field">
            <span class="label" id="qcount">Questions</span>
            <div class="stepper" role="group" aria-labelledby="qcount">
              <button type="button" data-step="-5" aria-label="Five fewer questions">−</button>
              <output aria-live="polite">${f.count}</output>
              <button type="button" data-step="5" aria-label="Five more questions">+</button>
            </div>
          </div>
        </div>
        <div class="start-row">
          <button type="button" class="btn primary big" data-act="start" ${ready && !state.busyAction ? "" : "disabled"}>
            ${state.busyAction ? "Starting…" : `Start ${f.count} questions`}
            <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M4 9 H14 M10 5 L14 9 L10 13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <span class="mono muted">${examOf(f.exam).cmd} ${f.difficulty}</span>
        </div>
        <p class="hint">The app answers the command's domain and question-count prompts with what you pick here. Each reply takes Claude around 10–30 seconds.</p>
      </div>
      <aside class="setup-side">
        ${r ? `
        <section class="card">
          <div><h2>Retake plan</h2><p class="hint">What ${examOf(f.exam).cmd} will aim for, from your score report · ${esc(r.date)} · ${esc(r.score)} / 1000</p></div>
          <div class="mixbar" aria-hidden="true">
            <span class="t1bg" style="flex:${t1} 1 0"></span><span class="t2bg" style="flex:${t2} 1 0"></span><span class="t3bg" style="flex:${t3} 1 0"></span>
          </div>
          <ul class="mix">
            <li><span class="chip t1"><i></i>Tier 1</span><span>Missed on the exam</span><b>${t1}</b></li>
            <li><span class="chip t2"><i></i>Tier 2</span><span>Partly right</span><b>${t2}</b></li>
            <li><span class="chip t3"><i></i>Tier 3</span><span>Maintain</span><b>${t3}</b></li>
          </ul>
        </section>` : ""}
        ${s.watch.length || s.traps.length ? `
        <section class="card watch">
          <h2>Watch list</h2>
          <ul class="watch-list">
            ${s.watch.map((w) => `<li><b>${esc(w.id)} ${esc(w.label)}</b> · ${fmtPct(w.pct)}</li>`).join("")}
            ${s.traps.map((t) => `<li class="mono">${esc(t.label)} ×${t.count}</li>`).join("")}
          </ul>
        </section>` : ""}
      </aside>
    </div>`;
  }

  const ICON = {
    check: `<svg width="16" height="16" viewBox="0 0 16 16" role="img" aria-label="correct answer"><path d="M3 8.5 L6.5 12 L13 4.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    cross: `<svg width="14" height="14" viewBox="0 0 14 14" role="img" aria-label="your answer, wrong"><path d="M3 3 L11 11 M11 3 L3 11" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>`,
  };

  function busyLabel(s) {
    const p = s.pending;
    if (!s.turns.length) return `Starting ${s.opening}: Claude is reading your history and score report…`;
    if (p && p.kind === "setup") return "Claude is planning the session…";
    if (p && p.kind === "answer") return "Claude is checking your answer…";
    return "Claude is replying…";
  }

  function questionCard(q, { fb, interactive, busy }) {
    const opts = LETTERS.filter((L) => q.options && q.options[L] != null).map((L) => {
      let cls = "opt", icon = L, why = "";
      if (fb && fb.result !== "recorded") {
        const right = L === fb.correct_letter, mine = L === fb.chosen;
        if (right) { cls += " right"; icon = ICON.check; }
        else if (mine) { cls += " wrong"; icon = ICON.cross; }
        else cls += " dim";
        const w = right ? null : fb.why_wrong && fb.why_wrong[L];
        if (w) why = `<span class="why">${inline(w)}</span>`;
      } else if (state.picked === L) cls += " picked";
      const disabled = !interactive || busy;
      return `<button type="button" role="radio" class="${cls}" data-pick="${L}" aria-checked="${state.picked === L || (fb && fb.chosen === L)}" ${disabled ? "disabled" : ""}>
        <span class="tile">${icon}</span><span class="otext"><span>${inline(q.options[L])}</span>${why}</span></button>`;
    }).join("");
    const m = q;
    return `
      <div class="qmeta">
        <span class="label">Question ${esc(q.number)}${q.total ? ` of ${esc(q.total)}` : ""}</span><span class="sep">/</span>
        <span class="muted">${esc(m.domain || "")}${m.domain_name ? ` · ${esc(m.domain_name)}` : ""}</span>
        ${m.subtopic ? `<span class="code-chip">${esc(m.subtopic)} ${esc(m.subtopic_label || "")}</span>` : ""}
        ${m.objective ? `<span class="chip plain">${esc(m.objective)}</span>` : ""}
      </div>
      <h1 class="stem">${inline(q.stem || "")}</h1>
      <div class="opts" role="radiogroup" aria-label="Answer options">${opts}</div>`;
  }

  function feedbackPanel(fb, nextLabel) {
    if (fb.result === "recorded") return "";
    const ok = fb.result === "correct";
    return `
      <section class="feedback ${ok ? "ok" : "bad"}" tabindex="-1" id="fb">
        <div class="fb-head"><span class="badge">${ok ? ICON.check : ICON.cross}</span>
          <h2>${ok ? "Correct" : `Not quite — the answer is ${esc(fb.correct_letter || "?")}`}</h2></div>
        ${!ok && fb.trap ? `
          <div class="trapbox"><span class="label">Trap triggered</span>
            <span class="mono">${esc(fb.trap)}</span>${fb.trap_description ? `<span>${inline(fb.trap_description)}</span>` : ""}</div>` : ""}
        ${fb.why_correct ? `<div><span class="label">Why ${esc(fb.correct_letter || "")} is right</span><p>${inline(fb.why_correct)}</p></div>` : ""}
        ${fb.objective_note ? `<p class="obj-note"><i>${inline(fb.objective_note)}</i></p>` : ""}
        ${nextLabel ? `<div class="btn-row"><button type="button" class="btn primary" data-act="reveal">${nextLabel}</button></div>` : ""}
      </section>`;
  }

  function sessionView() {
    const s = state.s, D = derive(s), ex = examOf(s.exam);
    const answered = Object.keys(D.feedback).length;
    const pct = Math.min(100, Math.round((answered / Math.max(1, D.total)) * 100));
    let main = "";

    if (s.error) {
      main += `<div class="callout"><b>Claude Code stopped.</b> ${esc(s.error)}
        <div class="btn-row"><button type="button" class="btn primary" data-act="retry">Try again</button>
        <span class="hint">Or continue in a terminal: <code>${esc(s.resumeCommand)}</code></span></div></div>`;
    }

    if (D.summary) {
      main += summaryView(s, D);
    } else if (s.busy && !D.current && !(D.lastFb && D.lastFb.result !== "recorded")) {
      main += writing(busyLabel(s));
      if (D.last && !D.lb) main += mdCard(D.last.text, "Claude");
    } else if (D.current || (D.lastFb && D.questions[D.lastFb.question_number])) {
      const fb = D.lastFb && D.lastFb.result !== "recorded" ? D.lastFb : null;
      const showFeedbackFirst = fb && state.revealed !== (D.current && D.current.number);
      if (showFeedbackFirst) {
        const prevQ = D.questions[fb.question_number];
        if (prevQ) main += questionCard(prevQ, { fb, interactive: false });
        main += feedbackPanel(fb, D.current ? "Next question" : "");
        if (!D.current && !s.busy) main += mdCard(D.last.text, "Claude");
      } else if (D.current) {
        const q = D.current;
        const inFlight = s.busy && state.sentFor === q.number;
        main += questionCard(q, { interactive: !s.busy, busy: s.busy });
        if (inFlight || s.busy) main += writing(busyLabel(s));
        else main += `
          <div class="btn-row">
            <button type="button" class="btn primary" data-act="submit" ${state.picked ? "" : "disabled"}>Submit answer</button>
            <span class="hint">Keys: A–D or 1–4 to pick, Enter to submit.</span>
          </div>`;
        if (s.difficulty === "exam" && D.lastFb && D.lastFb.result === "recorded") {
          main = `<p class="hint">Answer ${esc(D.lastFb.chosen)} to question ${esc(D.lastFb.question_number)} recorded.</p>` + main;
        }
      }
    } else if (D.last) {
      // Setup prompts, questions about the session, or a reply without a usable block.
      main += mdCard(D.last.text, "Claude");
      if (s.busy) main += writing(busyLabel(s));
    } else {
      main += writing(busyLabel(s));
    }

    const lastText = D.last ? D.last.text : "";
    const showFull = D.last && !D.summary && D.lb;
    return `
      <div class="session">
        <article class="session-main">
          <div class="session-top">
            <span class="chip plain">${esc(ex.cmd)} ${esc(s.difficulty)}${s.domain !== "all" ? ` · ${esc(s.domain)}` : ""}</span>
            <div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="${D.total}" aria-valuenow="${answered}" aria-label="Answered ${answered} of ${D.total}">
              <span style="width:${pct}%"></span></div>
            <span class="num muted">${answered} / ${D.total}</span>
          </div>
          ${healthBanner()}
          ${main}
          ${showFull ? `<details class="fullreply"><summary>Claude's full reply</summary><div class="md">${md(lastText)}</div></details>` : ""}
          ${replyBox(s, D)}
        </article>
        <aside class="session-side">
          <section class="card">
            <h2>This session</h2>
            <div class="dots">${dots(D)}</div>
            ${s.difficulty === "exam" ? `<p class="hint">Exam mode: no feedback until the end.</p>` : ""}
            <div class="btn-row"><button type="button" class="btn" data-act="leave">Back to setup</button></div>
            <p class="hint">This is a saved Claude Code conversation. Continue it later here, or in a terminal in the project folder:</p>
            <code class="resume-cmd">${esc(s.resumeCommand)}</code>
          </section>
          ${D.watch.length && s.difficulty !== "exam" ? `
          <section class="card watch"><h2>Watch for</h2><ul class="watch-list">
            ${D.watch.slice(0, 6).map((w) => `<li>${inline(w)}</li>`).join("")}</ul></section>` : ""}
          ${D.denials.length ? `
          <section class="card"><h2>Refused tool calls</h2>
            <p class="hint">Claude tried ${D.denials.length === 1 ? "a tool call" : `${D.denials.length} tool calls`} outside the allowed set. It was refused; Claude carries on without it.</p>
            <ul class="denials">${D.denials.slice(-3).map((d) => `<li><b>${esc(d.tool)}</b> <code>${esc(String(d.input).slice(0, 140))}</code></li>`).join("")}</ul></section>` : ""}
        </aside>
      </div>`;
  }

  function writing(label) {
    return `<div class="writing" role="status"><div class="spinner" aria-hidden="true"></div>
      <div><b>${esc(label)}</b> <span class="muted" data-elapsed>${state.s ? `${secondsSince(state.s.updated)}s` : ""}</span>
      <p class="hint">This is the real command running in Claude Code; long replies can take up to a minute.</p></div></div>`;
  }

  function mdCard(text, who) {
    return `<section class="card md-card"><span class="label">${esc(who)}</span><div class="md">${md(text)}</div></section>`;
  }

  function replyBox(s, D) {
    const awaiting = D.lb ? D.lb.awaiting : "free_text";
    const prompt = !D.lb || awaiting === "free_text" || (D.summary)
      ? "Reply to Claude"
      : D.current ? "Ask Claude something instead of answering" : "Message Claude";
    const open = !D.lb || awaiting === "free_text";
    return `
      <details class="reply" ${open ? "open" : ""}>
        <summary>${prompt}</summary>
        <form data-form="reply">
          <label class="sr-only" for="reply-text">Message to Claude</label>
          <textarea id="reply-text" rows="3" maxlength="2000" placeholder="${D.summary ? "e.g. re-drill my weakest domain" : "Type a message for Claude"}" ${s.busy ? "disabled" : ""}>${esc(state.draft)}</textarea>
          <div class="btn-row"><button type="submit" class="btn" ${s.busy ? "disabled" : ""}>Send</button>
          <span class="hint">Goes to the same Claude Code session as your answers.</span></div>
        </form>
      </details>`;
  }

  function dots(D) {
    const cur = D.current ? D.current.number : null;
    return Array.from({ length: D.total }, (_, i) => {
      const n = i + 1, f = D.feedback[n];
      let cls = "", label = "not answered";
      if (f) {
        cls = f.result === "correct" ? "ok" : f.result === "incorrect" ? "bad" : "done";
        label = f.result === "recorded" ? "answered" : f.result;
      }
      if (n === cur) { cls += " now"; label = "current"; }
      return `<span class="dot-n ${cls}" title="Question ${n}: ${label}" aria-label="Question ${n}: ${label}">${n}</span>`;
    }).join("");
  }

  function summaryView(s, D) {
    const r = D.summary, ex = examOf(s.exam);
    const fb = D.lastFb && D.lastFb.result !== "recorded" ? D.lastFb : null;
    const verdict = r.verdict ? `<span class="${r.verdict === "PASS" ? "pass" : "fail"}">${r.verdict === "PASS" ? "✓ Pass" : "✕ Below pass"} on the weighted 1000-point scale</span>` : "";
    const lastQ = fb && D.questions[fb.question_number];
    return `
      ${lastQ ? `<details class="lastq"><summary>Question ${esc(fb.question_number)}: ${fb.result === "correct" ? "✓ correct" : `✕ answer ${esc(fb.correct_letter)}`}</summary>
        ${questionCard(lastQ, { fb, interactive: false })}${feedbackPanel(fb, "")}</details>` : ""}
      <header class="head"><div>
        <span class="mono muted">${esc(ex.cmd)} ${esc(s.difficulty)}</span>
        <h1>Session complete</h1>
        <p class="sub">${r.logged ? `${esc(ex.cmd)} saved this session to <code>${esc(s.exam)}-performance.json</code>. It now counts in Stats.` : `${esc(ex.cmd)} hasn't confirmed saving this session. Check Claude's reply below.`}</p>
      </div></header>
      <section class="kpis">
        <div class="kpi hero"><span class="k-label">Score</span>
          <span class="k-value">${esc(r.score)}<small> / ${esc(r.total)}</small></span>
          <span class="k-foot">${fmtPct(r.percent)}${r.scaled != null ? ` · ${esc(r.scaled)} / 1000` : ""}</span></div>
        ${r.weighted != null ? `<div class="kpi"><span class="k-label">Weighted score</span>
          <span class="k-value">${esc(r.weighted)}<small> / 1000</small></span><span class="k-foot">${verdict}</span></div>` : ""}
      </section>
      ${Array.isArray(r.domains) && r.domains.length ? `
      <section class="card"><div class="card-head"><h2>By domain</h2><span class="note">Pass line 720</span></div>
        <div class="scroll"><table><thead><tr><th scope="col">Domain</th><th scope="col">Score</th><th scope="col">Accuracy</th><th scope="col">Weight</th><th scope="col">Points</th></tr></thead>
        <tbody>${r.domains.map((d) => `<tr><td><b>${esc(d.id)}</b> ${esc(domainName(s.exam, d.id))}</td><td class="num">${d.total ? `${esc(d.correct)}/${esc(d.total)}` : "—"}</td>
          <td class="num">${d.total ? fmtPct(d.percent) : "—"}</td><td class="num">${esc(d.weight)}%</td><td class="num">${esc(d.points)}</td></tr>`).join("")}</tbody></table></div></section>` : ""}
      ${Array.isArray(r.misses) && r.misses.length ? `
      <section class="card"><div class="card-head"><h2>What you missed</h2><span class="note">${r.misses.length} question${r.misses.length === 1 ? "" : "s"}</span></div>
        <ul class="misses">${r.misses.map((m) => {
          const q = D.questions[m.number];
          const f = D.feedback[m.number];
          return `<li><div class="miss-top"><span class="num muted">Q${esc(m.number)}</span>
            ${m.subtopic ? `<span class="code-chip">${esc(m.subtopic)} ${esc(m.subtopic_label || "")}</span>` : ""}
            ${f && f.chosen ? `<span class="muted">you chose ${esc(f.chosen)}${f.correct_letter ? `, answer ${esc(f.correct_letter)}` : ""}</span>` : ""}</div>
            ${q ? `<p class="miss-stem">${inline(q.stem)}</p>` : ""}
            ${m.trap ? `<div class="trapbox small"><span class="mono">${esc(m.trap)}</span>${f && f.trap_description ? `<span>${inline(f.trap_description)}</span>` : ""}</div>` : ""}</li>`;
        }).join("")}</ul></section>` : ""}
      <details class="fullreply" open><summary>Claude's full summary</summary><div class="md">${md(D.last.text)}</div></details>
      <div class="btn-row">
        <button type="button" class="btn primary" data-act="again">New session</button>
        <a class="btn" href="/?exam=${esc(s.exam)}">View stats</a>
      </div>`;
  }

  // ---------- events ----------
  function wire() {
    app.querySelectorAll("[data-exam]").forEach((b) => b.addEventListener("click", async () => {
      state.form.exam = b.dataset.exam; store.set("exam", state.form.exam);
      await loadSetup(); render();
    }));
    app.querySelectorAll("[data-diff]").forEach((b) => b.addEventListener("click", () => {
      state.form.difficulty = b.dataset.diff; store.set("difficulty", b.dataset.diff); render();
      app.querySelector(`[data-diff="${b.dataset.diff}"]`)?.focus();
    }));
    app.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => {
      const max = state.setup?.maxQuestions || 60;
      state.form.count = Math.min(max, Math.max(5, state.form.count + Number(b.dataset.step)));
      store.set("count", state.form.count); render();
      app.querySelector(`[data-step="${b.dataset.step}"]`)?.focus();
    }));
    const dom = app.querySelector("#domain");
    if (dom) dom.addEventListener("change", () => { state.form.domain = dom.value; render(); app.querySelector("#domain")?.focus(); });
    app.querySelectorAll("[data-open]").forEach((b) => b.addEventListener("click", async () => {
      try { openSession(await api(`/api/sessions/${b.dataset.open}`)); } catch (err) { toast(err.message); }
    }));
    app.querySelectorAll("[data-pick]").forEach((b) => b.addEventListener("click", () => pick(b.dataset.pick)));
    app.querySelectorAll("[data-act]").forEach((b) => b.addEventListener("click", () => act(b.dataset.act)));
    const ta = app.querySelector("#reply-text");
    if (ta) ta.addEventListener("input", () => { state.draft = ta.value; });
    const form = app.querySelector('[data-form="reply"]');
    if (form) form.addEventListener("submit", (e) => { e.preventDefault(); send(); });
  }

  function pick(letter) {
    if (!state.s || state.s.busy) return;
    const D = derive(state.s);
    if (!D.current) return;
    state.picked = letter;
    render();
    app.querySelector(`[data-pick="${letter}"]`)?.focus();
  }

  async function act(a) {
    try {
      if (a === "start") {
        state.busyAction = true; render();
        const f = state.form;
        const s = await api("/api/sessions", { exam: f.exam, difficulty: f.difficulty, domain: f.domain, count: f.count });
        state.busyAction = false;
        return openSession(s);
      }
      if (a === "submit") {
        const D = derive(state.s);
        if (!state.picked || !D.current) return;
        state.sentFor = D.current.number;
        state.s = await api(`/api/sessions/${state.s.id}/answer`, { letter: state.picked });
        render(); return poll();
      }
      if (a === "reveal") {
        const D = derive(state.s);
        state.revealed = D.current ? D.current.number : null;
        render();
        app.querySelector(".stem")?.scrollIntoView({ block: "start" });
        return;
      }
      if (a === "retry") { state.s = await api(`/api/sessions/${state.s.id}/retry`, {}); render(); return poll(); }
      if (a === "leave" || a === "again") {
        clearTimeout(pollTimer); clearInterval(tick);
        store.set("session", null, ss);
        history.replaceState(null, "", "/practice");
        state.view = "setup"; state.s = null;
        await loadSetup(); return render();
      }
      if (a === "recheck") { state.health = await api("/api/health?refresh=1"); return render(); }
    } catch (err) {
      state.busyAction = false;
      render();
      toast(err.message);
    }
  }

  async function send() {
    const text = state.draft.trim();
    if (!text) return;
    try {
      state.s = await api(`/api/sessions/${state.s.id}/reply`, { text });
      state.draft = "";
      render(); poll();
    } catch (err) { toast(err.message); }
  }

  document.addEventListener("keydown", (e) => {
    if (state.view !== "session" || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target.closest("input, select, textarea, summary")) return;
    const D = state.s && derive(state.s);
    if (!D || state.s.busy) return;
    const fbShowing = D.lastFb && D.lastFb.result !== "recorded" && D.current && state.revealed !== D.current.number;
    const k = e.key.toUpperCase();
    const idx = LETTERS.indexOf(k) >= 0 ? LETTERS.indexOf(k) : ["1", "2", "3", "4"].indexOf(k);
    if (idx >= 0 && D.current && !fbShowing) { e.preventDefault(); pick(LETTERS[idx]); return; }
    if (e.key === "Enter" && (!e.target.closest("button, a") || e.target.closest("[data-pick]"))) {
      if (fbShowing) { e.preventDefault(); act("reveal"); }
      else if (D.current && state.picked) { e.preventDefault(); act("submit"); }
    }
  });

  boot();
})();

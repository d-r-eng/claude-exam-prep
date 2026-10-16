/* Exam Prep stats dashboard — vanilla JS, no build step. */
(() => {
  "use strict";

  const app = document.getElementById("app");
  const tip = document.getElementById("tip");
  const updated = document.getElementById("updated");
  const PASS_PCT = 72;
  const ROLL = 5;

  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
  };

  const state = {
    exam: new URLSearchParams(location.search).get("exam") || store.get("exam") || "fexam",
    data: null,
    openObjectives: new Set(),
    showAllSubs: false,
    showAllSessions: false,
  };

  // ---------- helpers ----------
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtPct = (p) => (p == null ? "—" : `${Number.isInteger(p) ? p : p.toFixed(1)}%`);
  const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;
  const fmtFocus = (f) => (f === "all" ? "all domains" : String(f).replace(/[-_]/g, " "));

  // ---------- theme ----------
  const themeBtn = document.getElementById("theme");
  const savedTheme = store.get("theme");
  if (savedTheme) document.documentElement.dataset.theme = savedTheme;
  themeBtn.addEventListener("click", () => {
    const cur = document.documentElement.dataset.theme
      || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    store.set("theme", next);
  });

  // ---------- tabs ----------
  const tabs = [...document.querySelectorAll("[role=tab]")];
  function syncTabs() {
    tabs.forEach((t) => t.setAttribute("aria-selected", String(t.dataset.exam === state.exam)));
  }
  tabs.forEach((t) => t.addEventListener("click", () => {
    if (state.exam === t.dataset.exam) return;
    state.exam = t.dataset.exam;
    store.set("exam", state.exam);
    history.replaceState(null, "", `?exam=${state.exam}`);
    state.openObjectives.clear();
    syncTabs();
    load();
  }));
  tabs.forEach((t, i) => t.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    const n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
    n.focus(); n.click();
  }));

  // ---------- data ----------
  const refreshBtn = document.getElementById("refresh");
  refreshBtn.addEventListener("click", () => {
    refreshBtn.classList.remove("spinning"); void refreshBtn.offsetWidth; refreshBtn.classList.add("spinning");
    load();
  });
  // Pick up a session you just finished in Claude Code when you come back to the tab.
  document.addEventListener("visibilitychange", () => { if (!document.hidden) load(true); });

  async function load(quiet) {
    if (!quiet) app.setAttribute("aria-busy", "true");
    try {
      const res = await fetch(`/api/stats?exam=${encodeURIComponent(state.exam)}`, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || res.statusText);
      state.data = data;
      render();
      updated.textContent = `Updated ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
    } catch (err) {
      app.innerHTML = `<div class="callout"><b>Couldn't read your history.</b> ${esc(err.message)}<br>
        Check that the JSON files in the project folder are valid, then refresh.</div>`;
    } finally {
      app.setAttribute("aria-busy", "false");
    }
  }

  // ---------- render ----------
  function render() {
    const d = state.data;
    const ex = d.exam;
    tabs.forEach((t) => { t.title = d.available[t.dataset.exam] ? "" : "No history yet"; });

    if (d.empty) {
      app.innerHTML = `
        <header class="head"><div><div class="cmd">${esc(ex.command)} stats</div>
          <h1>${esc(ex.name)} progress</h1></div></header>
        <section class="empty">
          <p>No session history yet. Complete a practice session first.</p>
          <p>In Claude Code, run <code>${esc(ex.command)} medium</code>. When it ends, the session is saved and shows up here on refresh.</p>
        </section>`;
      return;
    }

    const s = d.summary;
    app.innerHTML = `
      <header class="head">
        <div>
          <div class="cmd">${esc(ex.command)} stats</div>
          <h1>${esc(ex.name)} progress</h1>
          <p class="sub">${plural(s.sessions, "session")} · ${esc(s.firstDate)} to ${esc(s.lastDate)}</p>
        </div>
      </header>
      ${kpis(d)}
      <section class="card">
        <div class="card-head"><h2>Score by session</h2>
          <div class="legend" aria-hidden="true">
            <span><i class="ember"></i>Session</span>
            <span><i class="juniper"></i>Last ${ROLL} sessions</span>
            <span><i class="dash"></i>${PASS_PCT}% ≈ pass</span>
          </div></div>
        <div class="chart" id="trend"></div>
      </section>
      <div class="row">
        <section class="card wide">${domainBars(d)}</section>
        ${d.traps.length ? `<section class="card traps narrow">${traps(d)}</section>` : ""}
      </div>
      ${d.scoreReport ? `<section class="card">${objectives(d)}</section>` : ""}
      <div class="row">
        <section class="card half">${subtopics(d)}</section>
        <section class="card half">${sessions(d)}</section>
      </div>`;
    drawTrend(document.getElementById("trend"), d.history);
    wire();
  }

  function kpis(d) {
    const p = d.projection, s = d.summary, r = d.scoreReport;
    let foot;
    if (p.verdict) {
      const ok = p.verdict === "PASS";
      foot = `<span class="${ok ? "pass" : "fail"}">${ok ? "✓ Above" : "✕ Below"} the ${d.exam.passing} pass line</span>`;
    } else {
      foot = `<span>Based on ${p.domainsCovered}/${p.domainsTotal} domains · ${p.weightCovered}% of exam weight</span>`;
    }
    const tiles = [`
      <div class="kpi hero">
        <span class="k-label">Projected score · weighted practice</span>
        <span class="k-value">${p.score ?? "—"}<small> / 1000</small></span>
        <span class="k-foot">${foot}</span>
      </div>`];
    if (r) {
      const t1 = r.tierCounts["1"] || 0;
      const passed = r.gap != null && r.gap <= 0;
      tiles.push(`
      <div class="kpi">
        <span class="k-label">Last real exam · ${esc(r.date)}</span>
        <span class="k-value">${esc(r.score)}</span>
        <span class="k-foot ${passed ? "pass" : "fail"}">${passed ? "Passed" : `${r.gap} below pass`} · ${plural(t1, "objective")} at 0%</span>
      </div>`);
    }
    tiles.push(`
      <div class="kpi">
        <span class="k-label">Questions answered</span>
        <span class="k-value">${s.questions}</span>
        <span class="k-foot muted">${fmtPct(s.pct)} correct overall</span>
      </div>`);
    return `<section class="kpis" aria-label="Summary">${tiles.join("")}</section>`;
  }

  function domainBars(d) {
    const rows = d.domains.map((x) => `
      <div>
        <div class="bar-top"><span><b>${esc(x.id)}</b> ${esc(x.name)}</span>
          <span class="val">${x.total ? `${x.correct}/${x.total} · <b>${fmtPct(x.pct)}</b>` : "no attempts"} · weight ${x.weight}%</span></div>
        <div class="track" role="img" aria-label="${esc(x.id)} ${x.total ? fmtPct(x.pct) : "no attempts"}">
          <div class="fill${x.pct != null && x.pct < PASS_PCT ? " low" : ""}" style="width:${x.pct ?? 0}%"></div>
          <div class="mark"></div>
        </div>
      </div>`).join("");
    return `<div class="card-head"><h2>Accuracy by domain</h2><span class="note">Dashed line = ${PASS_PCT}%</span></div>
      <div class="bars">${rows}</div>`;
  }

  function traps(d) {
    return `<div class="card-head"><h2>Recurring traps</h2></div>` + d.traps.slice(0, 6).map((t) => `
      <div class="trap"><span class="n">×${t.count}</span><div>
        <div class="lbl">${esc(t.label)}</div>${t.description ? `<p>${esc(t.description)}</p>` : ""}</div></div>`).join("");
  }

  function objectives(d) {
    const r = d.scoreReport;
    const list = r.objectives.filter((o) => o.tier < 3);
    const rows = list.map((o) => {
      const open = state.openObjectives.has(o.id);
      const edgePct = o.edges.length ? Math.round(o.edgesRetired / o.edges.length * 100) : 0;
      const main = `
        <tr>
          <td><span class="obj-id">${esc(o.id)}</span>${esc(o.label)}</td>
          <td><span class="chip t${o.tier}"><i></i>Tier ${o.tier}</span></td>
          <td class="num">${o.examPct}%</td>
          <td class="num">${o.total ? `${o.correct}/${o.total} · ${fmtPct(o.pct)}` : "—"}</td>
          <td><div class="mini"><div class="track"><div class="fill" style="width:${edgePct}%"></div></div>
            <span class="num muted">${o.edgesRetired} / ${o.edges.length}</span></div></td>
          <td>${o.flag ? `<span class="flag">Not proven yet</span>` : `<span class="pass" title="80%+ in practice over 3+ attempts">✓ On track</span>`}</td>
          <td>${o.edges.length ? `<button type="button" class="expand" data-obj="${esc(o.id)}" aria-expanded="${open}" aria-controls="edges-${esc(o.id)}">${open ? "Hide" : "Edges"}</button>` : ""}</td>
        </tr>`;
      const edges = open ? `
        <tr class="edges" id="edges-${esc(o.id)}"><td colspan="7">
          <span class="objective-text">${esc(o.text)}</span>
          <ul class="edge-list">${o.edges.map((e) => `
            <li><span class="eid">${esc(e.id)}</span><span>${esc(e.text)}</span>
              <span class="cnt ${e.retired ? "retired" : ""}">${e.retired ? "✓ retired" : `${Math.min(e.correct, r.retireAfter)} / ${r.retireAfter}`}</span></li>`).join("")}
          </ul></td></tr>` : "";
      return main + edges;
    }).join("");
    return `<div class="card-head"><h2>Exam objectives: real exam vs practice</h2>
        <span class="note">Tier 1 and 2 · an edge retires after ${r.retireAfter} correct answers</span></div>
      <div class="scroll"><table class="obj-table">
        <thead><tr><th scope="col">Objective</th><th scope="col">Tier</th><th scope="col">Exam</th>
          <th scope="col">Practice</th><th scope="col">Edges retired</th><th scope="col">Status</th>
          <th scope="col"><span class="sr-only">Details</span></th></tr></thead>
        <tbody>${rows}</tbody></table></div>`;
  }

  function subtopics(d) {
    const all = d.subtopics;
    const shown = state.showAllSubs ? all : all.slice(0, 8);
    const weak = all.filter((x) => x.weak).length;
    return `<div class="card-head"><h2>Weakest subtopics</h2>
        <span class="note">${weak ? `${weak} below 70%` : "None below 70%"} · 2+ attempts</span></div>
      <div class="subs">${shown.map((x) => `
        <div class="sub"><span class="code">${esc(x.id)}</span><span class="name">${esc(x.label || "—")}</span>
          <span class="ct">${x.correct}/${x.total}</span>
          <span class="pctpill ${x.weak ? "weak" : ""}">${x.weak ? "⚠ " : ""}${fmtPct(x.pct)}</span></div>`).join("")}
      </div>
      ${all.length > 8 ? `<button type="button" class="more" data-toggle="subs">${state.showAllSubs ? "Show fewer" : `Show all ${all.length}`}</button>` : ""}`;
  }

  function sessions(d) {
    const all = [...d.history].reverse();
    const shown = state.showAllSessions ? all : all.slice(0, 5);
    return `<div class="card-head"><h2>${state.showAllSessions ? "All sessions" : "Recent sessions"}</h2></div>
      <div class="scroll"><table>
        <thead><tr><th scope="col">Date</th><th scope="col">Focus</th><th scope="col">Level</th><th scope="col">Score</th></tr></thead>
        <tbody>${shown.map((x) => `<tr>
          <td class="num" style="white-space:nowrap">${esc(x.date)}</td><td>${esc(fmtFocus(x.focus))}</td>
          <td>${esc(x.difficulty)}</td>
          <td class="num" style="white-space:nowrap"><b>${x.score}/${x.total}</b> <span class="muted">· ${fmtPct(x.pct)}</span></td>
        </tr>`).join("")}</tbody></table></div>
      ${all.length > 5 ? `<button type="button" class="more" data-toggle="sessions">${state.showAllSessions ? "Show recent only" : `Show all ${all.length}`}</button>` : ""}`;
  }

  function wire() {
    app.querySelectorAll("[data-obj]").forEach((b) => b.addEventListener("click", () => {
      const id = b.dataset.obj;
      state.openObjectives.has(id) ? state.openObjectives.delete(id) : state.openObjectives.add(id);
      render();
      app.querySelector(`[data-obj="${CSS.escape(id)}"]`)?.focus();
    }));
    app.querySelectorAll("[data-toggle]").forEach((b) => b.addEventListener("click", () => {
      const key = b.dataset.toggle;
      if (key === "subs") state.showAllSubs = !state.showAllSubs;
      if (key === "sessions") state.showAllSessions = !state.showAllSessions;
      render();
      app.querySelector(`[data-toggle="${key}"]`)?.focus();
    }));
  }

  // ---------- trend chart ----------
  function drawTrend(el, hist) {
    const pts = hist.filter((h) => h.pct != null);
    if (pts.length < 2) { el.innerHTML = `<p class="muted">The trend appears after two sessions.</p>`; return; }

    // Rolling accuracy over the last ROLL sessions, weighted by question count.
    const roll = pts.map((_, i) => {
      const win = pts.slice(Math.max(0, i - ROLL + 1), i + 1);
      const c = win.reduce((a, h) => a + h.score, 0), t = win.reduce((a, h) => a + h.total, 0);
      return t ? (c / t) * 100 : null;
    });

    // Draw at the container's real width so labels stay readable on phones.
    const W = Math.max(300, Math.round(el.clientWidth || 1000));
    const H = W < 600 ? 220 : 280, m = { t: 12, r: 16, b: 30, l: 40 };
    const minV = Math.min(...pts.map((h) => h.pct));
    const y0 = Math.max(0, Math.min(50, Math.floor((minV - 5) / 10) * 10));
    const X = (i) => m.l + (i / (pts.length - 1)) * (W - m.l - m.r);
    const Y = (v) => m.t + (1 - (v - y0) / (100 - y0)) * (H - m.t - m.b);
    const ticks = [];
    for (let v = y0; v <= 100; v += y0 >= 50 ? 10 : 20) ticks.push(v);
    const path = (vals) => vals.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join("");
    const step = Math.max(1, Math.ceil(pts.length / Math.max(3, Math.floor(W / 140))));
    const xlabels = pts.map((h, i) => (i % step === 0 || i === pts.length - 1)
      ? `<text x="${X(i)}" y="${H - 8}" text-anchor="middle">${esc(String(h.date).slice(5))}</text>` : "").join("");
    const colW = (W - m.l - m.r) / (pts.length - 1);

    el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Score per session over time, ${pts.length} sessions; latest ${fmtPct(pts[pts.length - 1].pct)}">
      <g class="grid">${ticks.map((v) => `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}"/>`).join("")}</g>
      <g class="axis">${ticks.map((v) => `<text x="${m.l - 8}" y="${Y(v) + 4}" text-anchor="end">${v}%</text>`).join("")}${xlabels}</g>
      <line class="ref" x1="${m.l}" x2="${W - m.r}" y1="${Y(PASS_PCT)}" y2="${Y(PASS_PCT)}"/>
      <line class="cross" id="cross" x1="0" x2="0" y1="${m.t}" y2="${H - m.b}" visibility="hidden"/>
      <path class="avg" d="${path(roll)}"/>
      <path class="line" d="${path(pts.map((h) => h.pct))}"/>
      ${pts.map((h, i) => `<circle class="dot" data-i="${i}" cx="${X(i)}" cy="${Y(h.pct)}" r="4"/>`).join("")}
      ${pts.map((_, i) => `<rect class="hit" data-i="${i}" x="${X(i) - colW / 2}" y="${m.t}" width="${colW}" height="${H - m.t - m.b}"/>`).join("")}
    </svg>`;

    const svg = el.querySelector("svg"), cross = el.querySelector("#cross");
    const dots = el.querySelectorAll(".dot");
    const show = (i, evt) => {
      const h = pts[i];
      dots.forEach((d) => d.classList.toggle("active", +d.dataset.i === i));
      cross.setAttribute("x1", X(i)); cross.setAttribute("x2", X(i)); cross.setAttribute("visibility", "visible");
      tip.innerHTML = `<b>${esc(h.date)}</b> · ${esc(h.difficulty)}<br>${esc(fmtFocus(h.focus))}<br>
        Session <b>${h.score}/${h.total} · ${fmtPct(h.pct)}</b><br>Last ${ROLL}: <b>${fmtPct(Math.round(roll[i] * 10) / 10)}</b>`;
      tip.hidden = false;
      const r = svg.getBoundingClientRect();
      const px = r.left + (X(i) / W) * r.width, py = r.top + (Y(h.pct) / H) * r.height;
      const tw = tip.offsetWidth;
      tip.style.left = `${Math.min(window.innerWidth - tw - 8, Math.max(8, px - tw / 2))}px`;
      tip.style.top = `${Math.max(8, py - tip.offsetHeight - 14)}px`;
    };
    const hide = () => { tip.hidden = true; cross.setAttribute("visibility", "hidden"); dots.forEach((d) => d.classList.remove("active")); };
    el.querySelectorAll(".hit").forEach((h) => {
      h.addEventListener("pointerenter", (e) => show(+h.dataset.i, e));
      h.addEventListener("pointerdown", (e) => show(+h.dataset.i, e));
    });
    svg.addEventListener("pointerleave", hide);
    window.addEventListener("scroll", hide, { passive: true, once: true });
  }

  let lastW = 0, resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      const el = document.getElementById("trend");
      if (el && state.data && Math.abs(el.clientWidth - lastW) > 40) {
        lastW = el.clientWidth;
        drawTrend(el, state.data.history);
      }
    }, 150);
  });

  syncTabs();
  load();
})();

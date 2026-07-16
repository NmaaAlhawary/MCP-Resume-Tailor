/* ---------- scroll reveal ---------- */
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  });
}, { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

/* ---------- ATS ring + counter ---------- */
const ring = document.getElementById("atsRing");
const num = document.getElementById("atsNum");
const CIRC = 327;            // 2πr, r=52
const TARGET = 85;

function animateScore() {
  ring.style.strokeDashoffset = CIRC * (1 - TARGET / 100);
  const start = performance.now();
  const dur = 1600;
  function tick(now) {
    const p = Math.min((now - start) / dur, 1);
    num.textContent = Math.round(p * TARGET);
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
const ringObs = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) { animateScore(); ringObs.disconnect(); }
}, { threshold: 0.4 });
ringObs.observe(document.querySelector(".ring-badge"));

/* ---------- copy button ---------- */
document.querySelectorAll(".copy").forEach((btn) => {
  btn.addEventListener("click", () => {
    const txt = btn.dataset.copy.replace(/&amp;/g, "&");
    navigator.clipboard.writeText(txt).then(() => {
      btn.textContent = "Copied ✓";
      btn.classList.add("done");
      setTimeout(() => { btn.textContent = "Copy"; btn.classList.remove("done"); }, 1800);
    });
  });
});

/* ---------- auto-playing chat demo ("video") ---------- */
const chat = document.getElementById("chat");
const script = [
  { t: "user", d: 900, html: `Here's a job link — tailor my CV for it and export a PDF.<br><span style="opacity:.75">example.com/careers/senior-frontend</span>` },
  { t: "tool", d: 1200, html: `→ <b>load_master_resume()</b> · <b>fetch_job_posting()</b>` },
  { t: "tool", d: 1200, html: `→ <b>extract_keywords()</b><br>["REST APIs", "GraphQL", "TypeScript", "Docker", "AWS", "Next.js", "CI/CD", "Jest"]` },
  { t: "tool", d: 1200, html: `→ <b>ats_gap_check()</b><br><span class="warn">match 20%</span> · missing: GraphQL, TypeScript, Docker, AWS, Jest…` },
  { t: "bot", d: 1600, html: `Your CV only hits <b>20%</b> of their keywords. You <em>do</em> have Docker, AWS and Jest experience buried in older bullets — let me surface those and rephrase to their stack.` },
  { t: "bot", d: 2000, html: `<b>New tailored résumé — generated ✨</b><br>• Built <span class="ok">GraphQL</span> APIs in <span class="ok">TypeScript</span> on <span class="ok">Next.js</span><br>• Containerized services with <span class="ok">Docker</span>, shipped to <span class="ok">AWS</span> via <span class="ok">CI/CD</span><br>• Unit + integration testing with <span class="ok">Jest</span>` },
  { t: "tool", d: 1200, html: `→ <b>ats_gap_check()</b> (re-score)<br><span class="ok">match 85% ✓</span>` },
  { t: "tool", d: 1100, html: `→ <b>export_resume(format="pdf")</b><br>~/.resume-mcp/exports/Nmaa_Hawary.pdf` },
  { t: "tool", d: 1100, html: `→ <b>export_cover_letter(format="pdf")</b><br>~/.resume-mcp/exports/Nmaa_Hawary_cover_letter.pdf` },
  { t: "bot", d: 1600, html: `Done. Keyword match went from <span class="warn">20%</span> → <span class="ok">85%</span>. I emphasized your Docker/AWS work and testing with Jest, and drafted a matching cover letter. Both PDFs are ready to send. 🎯` },
];

function addMsg(t, html) {
  const m = document.createElement("div");
  m.className = "msg " + t;
  m.innerHTML = html;
  chat.appendChild(m);
  chat.scrollTop = chat.scrollHeight;
}
function addTyping() {
  const w = document.createElement("div");
  w.className = "typing";
  w.innerHTML = "<span></span><span></span><span></span>";
  chat.appendChild(w);
  chat.scrollTop = chat.scrollHeight;
  return w;
}

async function playDemo() {
  chat.innerHTML = "";
  for (const step of script) {
    if (step.t === "bot") {
      const ty = addTyping();
      await wait(700);
      ty.remove();
    }
    addMsg(step.t, step.html);
    await wait(step.d);
  }
  await wait(3200);
  playDemo(); // loop
}
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

// start the demo only once it scrolls into view
const demoObs = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) { playDemo(); demoObs.disconnect(); }
}, { threshold: 0.3 });
demoObs.observe(document.getElementById("demo"));

// Fills the price / e-mail from config.js and runs the checkout button.
(() => {
  const cfg = window.KIT_CONFIG || {};
  document.querySelectorAll('[data-cfg="price"]').forEach(el => { if (cfg.price) el.textContent = cfg.price; });
  document.querySelectorAll('[data-cfg="email"]').forEach(el => {
    if (!cfg.contactEmail) return;
    el.setAttribute("href", "mailto:" + cfg.contactEmail);
    if (el.textContent.includes("@")) el.textContent = cfg.contactEmail;
  });
  const y = document.getElementById("year"); if (y) y.textContent = new Date().getFullYear();

  // mobile menu
  const header = document.querySelector(".site-header"), menuBtn = document.getElementById("menuBtn");
  if (header && menuBtn) {
    const setOpen = open => { header.classList.toggle("open", open); menuBtn.setAttribute("aria-expanded", String(open)); };
    menuBtn.addEventListener("click", () => setOpen(!header.classList.contains("open")));
    document.addEventListener("keydown", e => { if (e.key === "Escape") setOpen(false); });
    document.addEventListener("click", e => { if (!header.contains(e.target)) setOpen(false); });
  }

  const box = document.getElementById("consent"), pay = document.getElementById("payBtn"), msg = document.getElementById("payMsg");
  if (!box || !pay) return;
  const sync = () => {
    pay.setAttribute("aria-disabled", String(!box.checked));
    if (box.checked && cfg.checkoutUrl) { pay.setAttribute("href", cfg.checkoutUrl); pay.setAttribute("target", "_blank"); pay.setAttribute("rel", "noopener"); }
    else { pay.setAttribute("href", "#acheter"); pay.removeAttribute("target"); }
    if (box.checked) msg.textContent = "";
  };
  box.addEventListener("change", sync);
  pay.addEventListener("click", e => {
    if (!box.checked) { e.preventDefault(); msg.textContent = "Coche la case pour accepter les conditions de vente avant de payer."; box.focus(); return; }
    if (!cfg.checkoutUrl) { e.preventDefault(); msg.textContent = "Le paiement n'est pas encore activé. Revenez bientôt, ou écrivez-nous pour commander."; }
  });
  sync();
})();

// =================== extra motion ===================
(() => {
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(pointer: fine)").matches;
  if (still) return;

  // background halos + reading progress
  const blobs = document.createElement("div"); blobs.className = "bg-blobs"; blobs.innerHTML = "<i></i><i></i><i></i>"; document.body.prepend(blobs);
  const prog = document.createElement("div"); prog.className = "progress"; document.body.append(prog);
  if (!CSS.supports("animation-timeline: scroll()")) {
    const upd = () => { const h = document.documentElement; prog.style.transform = `scaleX(${h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)})`; };
    addEventListener("scroll", upd, { passive: true }); upd();
  }

  // headline: split into words that rise one after another
  const h1 = document.querySelector(".hero h1");
  if (h1) {
    let i = 0; const out = [];
    h1.childNodes.forEach(n => {
      if (n.nodeType === 3) n.textContent.split(/(\s+)/).forEach(p => { if (!p) return; if (/^\s+$/.test(p)) out.push(document.createTextNode(p)); else { const s = document.createElement("span"); s.className = "w"; s.style.setProperty("--i", i++); s.textContent = p; out.push(s); } });
      else { const s = document.createElement("span"); s.className = "w"; s.style.setProperty("--i", i++); s.append(n.cloneNode(true)); out.push(s); }
    });
    h1.replaceChildren(...out); h1.classList.add("split");
  }

  // highlights below the fold sweep in when they appear
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.remove("hl-wait"); e.target.classList.add("hl-go"); io.unobserve(e.target); } }), { threshold: .6 });
  document.querySelectorAll("main .hl").forEach(el => { if (el.closest(".hero")) return; const r = el.getBoundingClientRect(); if (r.top > innerHeight * .9) { el.classList.add("hl-wait"); io.observe(el); } });

  // key figures count up when they scroll into view (final values are already in the HTML)
  const cio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return; cio.unobserve(e.target);
    const el = e.target, txt = el.textContent, m = txt.match(/\d+/); if (!m) return;
    const end = +m[0], pre = txt.slice(0, m.index), post = txt.slice(m.index + m[0].length), t0 = performance.now(), dur = 1100;
    const step = now => { const k = Math.min(1, (now - t0) / dur), v = Math.round(end * (1 - Math.pow(1 - k, 3))); el.textContent = pre + v + post; if (k < 1) requestAnimationFrame(step); else el.textContent = txt; };
    requestAnimationFrame(step);
  }), { threshold: .6 });
  document.querySelectorAll(".stat b").forEach(b => cio.observe(b));

  // 3D tilt + spotlight on cards
  if (fine) document.querySelectorAll(".file,.tour-card,.stat,.side .card").forEach(c => {
    c.classList.add("tilt");
    c.addEventListener("pointermove", e => { const r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      c.style.setProperty("--ry", ((x - .5) * 8).toFixed(2) + "deg"); c.style.setProperty("--rx", ((.5 - y) * 8).toFixed(2) + "deg");
      c.style.setProperty("--mx", (x * 100) + "%"); c.style.setProperty("--my", (y * 100) + "%"); c.classList.add("hovering"); });
    c.addEventListener("pointerleave", () => { c.style.setProperty("--rx", "0deg"); c.style.setProperty("--ry", "0deg"); c.classList.remove("hovering"); });
  });

  // hero phone follows the pointer
  const hero = document.querySelector(".hero"), pw = document.querySelector(".phone-wrap");
  if (fine && hero && pw) {
    hero.addEventListener("pointermove", e => { const r = hero.getBoundingClientRect(); const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      hero.style.setProperty("--px", (x * 18).toFixed(1) + "px"); hero.style.setProperty("--py", (y * 14).toFixed(1) + "px"); });
    hero.addEventListener("pointerleave", () => { hero.style.setProperty("--px", "0px"); hero.style.setProperty("--py", "0px"); });
  }

  // second marquee band, running the other way
  const mq = document.querySelector(".marquee");
  if (mq) { const b = mq.cloneNode(true); b.classList.add("alt"); b.querySelector(".marquee-track").classList.add("rev");
    b.querySelector(".marquee-track").innerHTML = "<span>Mode d'emploi</span><span>CV étudiant</span><span>Lettre de motivation</span><span>E-mails</span><span>Entretien</span><span>Suivi</span>".repeat(2);
    mq.after(b); }

  // offer: rotating outline + confetti on consent
  const offer = document.querySelector(".offer"); if (offer) { const ring = document.createElement("span"); ring.className = "offer-ring"; offer.append(ring); }
  const box = document.getElementById("consent"), pay = document.getElementById("payBtn");
  if (box && pay) box.addEventListener("change", () => {
    if (!box.checked) return; const r = pay.getBoundingClientRect(), cols = ["#5B3DF5", "#FFE04A", "#12A863", "#8A6BFF", "#101217"];
    for (let i = 0; i < 26; i++) { const c = document.createElement("i"); c.className = "confetti";
      c.style.left = (r.left + r.width / 2) + "px"; c.style.top = (r.top + r.height / 2) + "px"; c.style.background = cols[i % cols.length];
      const a = Math.random() * Math.PI * 2, d = 80 + Math.random() * 120;
      c.style.setProperty("--cx", Math.cos(a) * d + "px"); c.style.setProperty("--cy", (Math.sin(a) * d - 60) + "px"); c.style.setProperty("--cr", (Math.random() * 720 - 360) + "deg");
      document.body.append(c); setTimeout(() => c.remove(), 1100); }
  });
})();

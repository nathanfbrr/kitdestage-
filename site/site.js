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

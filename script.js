const yearEl = document.getElementById("year");
if (yearEl) {
  yearEl.textContent = String(new Date().getFullYear());
}

const revealEls = Array.from(document.querySelectorAll("[data-reveal]"));
for (const el of revealEls) {
  el.classList.add("reveal");
}

const barEls = Array.from(document.querySelectorAll(".bar[data-bar]"));

const prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function animateBar(bar) {
  const fill = bar.querySelector(".bar-fill");
  if (!fill) return;
  const pct = Number(bar.getAttribute("data-bar") || "0");
  const clamped = Math.max(0, Math.min(100, pct));
  fill.style.width = `${clamped}%`;
}

if (prefersReducedMotion) {
  for (const el of revealEls) el.classList.add("is-visible");
  for (const bar of barEls) animateBar(bar);
} else {
  const io = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const el = entry.target;
        el.classList.add("is-visible");
        io.unobserve(el);
      }
    },
    { threshold: 0.15 }
  );

  for (const el of revealEls) io.observe(el);

  const barIO = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        animateBar(entry.target);
        barIO.unobserve(entry.target);
      }
    },
    { threshold: 0.35 }
  );

  for (const bar of barEls) barIO.observe(bar);
}

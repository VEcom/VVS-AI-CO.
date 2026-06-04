/* ACRYL Design System — minimal interactions (no dependencies)
   theme toggle · sticky header · mobile drawer · scroll reveal · count-up */
(function () {
  "use strict";
  var root = document.documentElement;

  /* ---- Theme (persisted) ---- */
  var saved = localStorage.getItem("acryl-theme");
  if (saved) root.setAttribute("data-theme", saved);
  function toggleTheme() {
    var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
    root.setAttribute("data-theme", next);
    localStorage.setItem("acryl-theme", next);
  }

  /* ---- Sticky header shadow ---- */
  var header = document.querySelector(".site-header");
  function onScroll() {
    if (header) header.classList.toggle("scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---- Mobile drawer ---- */
  var drawer = document.querySelector(".drawer");
  function toggleDrawer() { if (drawer) drawer.classList.toggle("open"); }

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-action]");
    if (!t) return;
    var a = t.getAttribute("data-action");
    if (a === "theme") toggleTheme();
    if (a === "drawer") toggleDrawer();
    if (a === "drawer-link" && drawer) drawer.classList.remove("open");
  });

  /* ---- Scroll reveal ---- */
  var io = "IntersectionObserver" in window
    ? new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
        });
      }, { threshold: 0.12 })
    : null;
  document.querySelectorAll("[data-reveal]").forEach(function (el, i) {
    el.style.transitionDelay = (i % 4) * 60 + "ms";
    if (io) io.observe(el); else el.classList.add("in");
  });

  /* ---- Count-up for metrics ---- */
  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var dec = (el.getAttribute("data-dec") | 0);
    var dur = 1100, start = performance.now();
    function step(now) {
      var p = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * eased).toFixed(dec);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target.toFixed(dec);
    }
    requestAnimationFrame(step);
  }
  var counters = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window && counters.length) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { countUp(en.target); cio.unobserve(en.target); }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { cio.observe(c); });
  }
})();

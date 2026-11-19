// Shared page script (kept out of the HTML so the Content-Security-Policy can forbid inline scripts).
// Contact form: show the thank-you note after formsubmit.co sends the visitor back with ?sent=1.
(() => {
  const sent = document.querySelector(".sent");
  if (sent && location.search.includes("sent=1")) sent.hidden = false;
})();

// Gallery arrows scroll by one screenshot; the edges fade only where there's more to see,
// and the arrows hide when everything fits.
(() => {
  const section = document.querySelector(".gallery-section"), strip = section && section.querySelector(".gallery");
  if (!strip) return;
  const update = () => {
    const max = strip.scrollWidth - strip.clientWidth;
    section.classList.toggle("scrollable", max > 4);
    section.classList.toggle("at-start", strip.scrollLeft < 4);
    section.classList.toggle("at-end", strip.scrollLeft > max - 4);
  };
  const step = dir => {
    const img = strip.querySelector("img");
    strip.scrollBy({ left: dir * (img ? img.offsetWidth + 22 : 300), behavior: "smooth" });
  };
  section.querySelector(".prev").onclick = () => step(-1);
  section.querySelector(".next").onclick = () => step(1);
  strip.addEventListener("scroll", update, { passive: true });
  addEventListener("resize", update);
  addEventListener("load", update);
  update();
})();

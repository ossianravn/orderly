// Try it: the size slider sets the size of the editable text; weight and optical size come from the bar.
export function initTryIt(): void {
  const size = document.querySelector<HTMLInputElement>("#t-size");
  const text = document.querySelector<HTMLTextAreaElement>("#t-text");
  const out = document.querySelector<HTMLOutputElement>("[data-size-out]");
  if (!size || !text) return;
  const opsz = size.closest("section")?.querySelector<HTMLElement>('[data-out="opsz"]');
  // Phones start smaller, so the sample is a few lines and not a column of single words.
  if (matchMedia("(max-width: 760px)").matches) size.value = "44";
  const update = () => {
    const v = Number(size.value);
    text.style.setProperty("--size", `${v}px`);
    if (out) out.textContent = `${v} px`;
    if (opsz) {
      opsz.dataset.auto = String(Math.min(72, Math.max(12, v)));
      if (document.documentElement.dataset.opsz !== "manual") opsz.textContent = opsz.dataset.auto;
    }
    const p = ((v - Number(size.min)) / (Number(size.max) - Number(size.min))) * 100;
    size.style.setProperty("--p", `${p}%`);
  };
  size.addEventListener("input", update);
  update();
}

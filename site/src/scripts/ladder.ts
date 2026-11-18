// The weight ladder: click a rung to glide to it; drag across the rungs (mouse or pen) to move
// through the axis continuously. A marker shows where the current weight sits on the ladder.
import { glideWeight, set, stopGlide, subscribe } from "./state";

export function initLadder(): void {
  const ladder = document.querySelector<HTMLElement>("[data-ladder]");
  if (!ladder) return;
  const rungs = [...ladder.querySelectorAll<HTMLButtonElement>(".rung")];
  const stops = rungs.map((r) => Number(r.dataset.w));
  ladder.style.setProperty("--rungs", String(rungs.length));

  // Fractional rung index of a weight, and back.
  const indexOf = (w: number) => {
    for (let i = 1; i < stops.length; i++) {
      if (w <= stops[i]) return i - 1 + (w - stops[i - 1]) / (stops[i] - stops[i - 1]);
    }
    return stops.length - 1;
  };
  const weightAt = (f: number) => {
    const i = Math.max(0, Math.min(stops.length - 1, f));
    const lo = Math.floor(i);
    const hi = Math.min(stops.length - 1, lo + 1);
    return stops[lo] + (stops[hi] - stops[lo]) * (i - lo);
  };

  let dragging = false;
  let moved = false;
  let startY = 0;
  const fromPointer = (y: number) => {
    const box = ladder.getBoundingClientRect();
    const f = ((y - box.top) / box.height) * stops.length - 0.5;
    set({ wght: Math.round(weightAt(f)) });
  };

  ladder.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "touch" || e.button !== 0) return;
    dragging = true;
    moved = false;
    startY = e.clientY;
  });
  ladder.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    if (!moved && Math.abs(e.clientY - startY) < 6) return;
    // Capture only once it is a drag, so that a plain click still reaches its rung.
    if (!moved) ladder.setPointerCapture(e.pointerId);
    moved = true;
    stopGlide();
    ladder.dataset.dragging = "true";
    fromPointer(e.clientY);
  });
  const end = () => {
    dragging = false;
    delete ladder.dataset.dragging;
  };
  ladder.addEventListener("pointerup", end);
  ladder.addEventListener("pointercancel", end);
  ladder.addEventListener("click", (e) => {
    const keyboard = e.detail === 0;
    // The click that ends a drag is not a choice of rung; a keyboard click always is.
    const afterDrag = moved && !keyboard;
    moved = false;
    const rung = (e.target as Element).closest<HTMLButtonElement>(".rung");
    if (!rung || afterDrag) return;
    // From the keyboard the weight is set at once; a pointer click glides there.
    glideWeight(Number(rung.dataset.w), keyboard);
  });

  subscribe((s) => {
    ladder.style.setProperty("--y", `${indexOf(s.wght) * 100}%`);
    const w = Math.round(s.wght);
    for (const r of rungs) r.setAttribute("aria-pressed", String(Number(r.dataset.w) === w));
  });
}

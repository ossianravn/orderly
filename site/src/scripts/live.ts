// Redraws the outline drawings (Sizes comparison, Construction panels) when the settings change.
import { compare, fmt } from "../lib/compare";
import { panels } from "../lib/construct";
import type { Packed } from "../lib/glyphs";
import { glyphData, whenNear } from "./data";
import { locationFor, state, subscribe } from "./state";

function initCompare(data: Packed, root: HTMLElement, isNear: () => boolean): () => void {
  const word = root.dataset.word ?? "";
  let last = "";
  return () => {
    if (!isNear()) return;
    const key = String(Math.round(state.wght));
    if (key === last) return;
    last = key;
    const { rows, width } = compare(data, word, Math.round(state.wght));
    rows.forEach((r, i) => {
      const fig = root.querySelector<HTMLElement>(`[data-row="${i}"]`);
      if (!fig) return;
      const svg = fig.querySelector("svg")!;
      svg.setAttribute("viewBox", `0 0 ${Math.round(width)} ${svg.viewBox.baseVal.height}`);
      svg.innerHTML = r.body;
      const set = (f: string, v: number) => {
        const el = fig.querySelector(`[data-f="${f}"]`);
        if (el) el.textContent = fmt(v);
      };
      set("xh", r.xh);
      set("stem", r.stem);
      set("w", r.w);
    });
  };
}

function initPanels(data: Packed, root: HTMLElement, isNear: () => boolean): () => void {
  const figs = [...root.querySelectorAll<HTMLElement>("[data-panel]")];
  let last = "";
  return () => {
    if (!isNear()) return;
    const svg0 = figs[0]?.querySelector("svg");
    const px = svg0 ? (svg0.getBoundingClientRect().height / svg0.viewBox.baseVal.height) * 1000 : 200;
    const loc = locationFor(px);
    const key = `${Math.round(loc.wght)}/${Math.round(loc.opsz)}`;
    if (key === last) return;
    last = key;
    for (const fig of figs) {
      const draw = panels[fig.dataset.panel ?? ""];
      if (!draw) continue;
      const p = draw(data, { wght: Math.round(loc.wght), opsz: Math.round(loc.opsz) });
      const svg = fig.querySelector("svg")!;
      svg.setAttribute("viewBox", `0 0 ${Math.round(p.w)} ${svg.viewBox.baseVal.height}`);
      svg.style.setProperty("--vw", String(Math.round(p.w)));
      svg.innerHTML = p.body;
      const dds = fig.querySelectorAll("dd");
      p.facts.forEach(([, v], i) => {
        if (dds[i]) dds[i].textContent = v;
      });
    }
    for (const el of root.closest("section")?.querySelectorAll<HTMLElement>('[data-out="opsz"]') ?? []) {
      el.dataset.auto = String(Math.round(loc.opsz));
    }
  };
}

export function initLive(): void {
  const targets: [HTMLElement | null, typeof initCompare][] = [
    [document.querySelector<HTMLElement>("[data-compare]"), initCompare],
    [document.querySelector<HTMLElement>("[data-construction]"), initPanels],
  ];
  for (const [el, init] of targets) {
    if (!el) continue;
    let near = false;
    let redraw: (() => void) | null = null;
    whenNear(el, (n) => {
      near = n;
      if (!n) return;
      if (redraw) return redraw();
      glyphData()
        .then((data) => {
          redraw = init(data, el, () => near);
          subscribe(() => redraw?.());
        })
        .catch(() => {
          /* the drawings rendered at build time stay */
        });
    });
  }
}

// The character grid and the inspector: choosing a glyph draws its outline and points, live.
import { cellDrawing, inspect } from "../lib/inspect";
import type { Packed } from "../lib/glyphs";
import { glyphData, whenNear } from "./data";
import { locationFor, subscribe } from "./state";

export function initCharacters(): void {
  const cells = document.querySelector<HTMLElement>("[data-cells]");
  const panel = document.querySelector<HTMLElement>("[data-inspector]");
  if (!cells || !panel) return;
  const svg = panel.querySelector("svg")!;
  const dds = panel.querySelectorAll("dd");
  const section = panel.closest("section");
  let data: Packed | null = null;
  let near = false;
  let current = cells.querySelector<HTMLInputElement>("input:checked")?.value ?? "a";
  let lastKey = "";
  let lastCells = "";

  const draw = () => {
    if (!data || !near) return;
    const px = (svg.getBoundingClientRect().width / svg.viewBox.baseVal.width) * 1000;
    const loc = locationFor(px || 240);
    const w = Math.round(loc.wght);
    const o = Math.round(loc.opsz);
    const key = `${current}/${w}/${o}`;
    if (key !== lastKey) {
      lastKey = key;
      const shown = inspect(data, current, { wght: w, opsz: o });
      if (shown) {
        svg.innerHTML = shown.body;
        svg.setAttribute("aria-label", `Outline of ${current}`);
        shown.facts.forEach(([, v], i) => {
          if (dds[i]) dds[i].textContent = v;
        });
      }
      for (const el of section?.querySelectorAll<HTMLElement>('[data-out="opsz"]') ?? []) el.dataset.auto = String(o);
    }
    const cellLoc = locationFor(28);
    const ck = `${Math.round(cellLoc.wght)}/${Math.round(cellLoc.opsz)}`;
    if (ck !== lastCells) {
      lastCells = ck;
      for (const el of cells.querySelectorAll<HTMLElement>("[data-draw]")) {
        const at = { wght: Math.round(cellLoc.wght), opsz: Math.round(cellLoc.opsz) };
        el.innerHTML = cellDrawing(data, el.dataset.draw!, at, el.dataset.mark !== undefined);
      }
    }
  };

  cells.addEventListener("change", (e) => {
    const t = e.target as HTMLInputElement;
    if (t.name !== "glyph") return;
    current = t.value;
    draw();
  });

  whenNear(section ?? panel, (n) => {
    near = n;
    if (!n) return;
    if (data) return draw();
    glyphData()
      .then((d) => {
        data = d;
        subscribe(() => draw());
      })
      .catch(() => {
        /* the inspector keeps the glyph drawn at build time */
      });
  });
}

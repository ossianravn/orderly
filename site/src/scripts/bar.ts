// The fixed control bar: weight, optical size (auto or manual) and appearance.
import { set, state, stopGlide, subscribe, type OpszMode, type Theme } from "./state";


export function initBar(): void {
  const bar = document.getElementById("bar") as HTMLFormElement | null;
  if (!bar) return;
  const list: { name: string; wght: number }[] = JSON.parse(bar.dataset.instances ?? "[]");
  const names: Record<number, string> = Object.fromEntries(list.map((i) => [i.wght, i.name]));
  const wght = bar.querySelector<HTMLInputElement>("#c-wght")!;
  const opsz = bar.querySelector<HTMLInputElement>("#c-opsz")!;
  const more = bar.querySelector<HTMLButtonElement>(".more")!;

  bar.addEventListener("submit", (e) => e.preventDefault());
  wght.addEventListener("input", () => {
    stopGlide();
    set({ wght: Number(wght.value) });
  });
  opsz.addEventListener("input", () => set({ opsz: Number(opsz.value) }));
  bar.addEventListener("change", (e) => {
    const t = e.target as HTMLInputElement;
    if (t.name === "opsz-mode") set({ opszMode: t.value as OpszMode });
    if (t.name === "theme") set({ theme: t.value as Theme });
  });
  more.addEventListener("click", () => {
    const open = more.getAttribute("aria-expanded") !== "true";
    more.setAttribute("aria-expanded", String(open));
    bar.dataset.expanded = String(open);
  });

  const fill = (input: HTMLInputElement) => {
    const p = ((Number(input.value) - Number(input.min)) / (Number(input.max) - Number(input.min))) * 100;
    input.style.setProperty("--p", `${p}%`);
  };
  const theme = bar.querySelector<HTMLInputElement>(`input[name="theme"][value="${state.theme}"]`);
  if (theme) theme.checked = true;

  subscribe((s) => {
    const w = Math.round(s.wght);
    if (Number(wght.value) !== w) wght.value = String(w);
    wght.setAttribute("aria-valuetext", names[w] ? `${w}, ${names[w]}` : String(w));
    opsz.disabled = s.opszMode === "auto";
    fill(wght);
    fill(opsz);
    for (const el of document.querySelectorAll<HTMLElement>("[data-out]")) {
      const k = el.dataset.out;
      if (k === "wght") el.textContent = String(w);
      else if (k === "wname") el.textContent = names[w] ?? "";
      else if (k === "opsz-set") el.textContent = String(Math.round(s.opsz));
      else if (k === "opsz") el.textContent = s.opszMode === "manual" ? String(Math.round(s.opsz)) : el.dataset.auto ?? "";
      else if (k === "omode") el.textContent = s.opszMode === "manual" ? "manual" : "auto";
    }
  });
}

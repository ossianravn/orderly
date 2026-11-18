// One small store for the control bar's settings. It writes CSS custom properties on <html>,
// so specimens follow in CSS, and notifies the islands that draw (outlines, numbers).
import type { Location } from "../lib/glyphs";

export type Theme = "system" | "light" | "dark";
export type OpszMode = "auto" | "manual";

export interface State {
  wght: number;
  opszMode: OpszMode;
  opsz: number;
  theme: Theme;
}

const root = document.documentElement;
export const state: State = { wght: 400, opszMode: "auto", opsz: 72, theme: "system" };

try {
  const t = localStorage.getItem("orderly-theme");
  if (t === "light" || t === "dark") state.theme = t;
} catch {
  /* storage unavailable: follow the system */
}

type Listener = (s: State) => void;
const listeners = new Set<Listener>();
let frame = 0;

export function subscribe(fn: Listener): void {
  listeners.add(fn);
  fn(state);
}

function apply(): void {
  frame = 0;
  root.style.setProperty("--wght", String(Math.round(state.wght)));
  root.style.setProperty("--opsz", String(Math.round(state.opsz)));
  root.dataset.opsz = state.opszMode;
  if (state.theme === "system") root.removeAttribute("data-theme");
  else root.dataset.theme = state.theme;
  // The browser chrome follows the page: each theme-color tag keeps its own scheme unless overridden.
  for (const meta of document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]')) {
    meta.dataset.scheme ??= meta.media.includes("dark") ? "dark" : "light";
    const scheme = state.theme === "system" ? meta.dataset.scheme : state.theme;
    meta.content = scheme === "dark" ? "#111315" : "#f3f5f6";
  }
  for (const fn of listeners) fn(state);
}

export function set(patch: Partial<State>): void {
  if (patch.theme && patch.theme !== state.theme) {
    try {
      if (patch.theme === "system") localStorage.removeItem("orderly-theme");
      else localStorage.setItem("orderly-theme", patch.theme);
    } catch {
      /* not persisted */
    }
  }
  Object.assign(state, patch);
  if (!frame) frame = requestAnimationFrame(apply);
}

const reduced = matchMedia("(prefers-reduced-motion: reduce)");
let tween = 0;

/** cubic-bezier(x1, y1, x2, y2) as a function of time, solved for x by bisection. */
function bezier(x1: number, y1: number, x2: number, y2: number): (t: number) => number {
  const at = (a: number, b: number, s: number) => 3 * a * s * (1 - s) ** 2 + 3 * b * s * s * (1 - s) + s ** 3;
  return (t) => {
    let lo = 0,
      hi = 1,
      s = t;
    for (let i = 0; i < 24; i++) {
      s = (lo + hi) / 2;
      if (at(x1, x2, s) < t) lo = s;
      else hi = s;
    }
    return at(y1, y2, s);
  };
}

// The page's --ease-in-out: movement on screen, here through the weight axis.
const easeInOut = bezier(0.77, 0, 0.175, 1);

/**
 * Move through the weight axis to a named weight, so the in-between is visible. The glide is the
 * specimen itself, so it may run longer than an interface transition (up to 600 ms for 100 to 900).
 */
export function glideWeight(to: number, instant = false): void {
  cancelAnimationFrame(tween);
  const from = state.wght;
  if (instant || reduced.matches || from === to) return set({ wght: to });
  const ms = 260 + Math.min(1, Math.abs(to - from) / 800) * 340;
  const t0 = performance.now();
  const ease = easeInOut;
  const step = (now: number) => {
    const t = Math.min(1, (now - t0) / ms);
    set({ wght: from + (to - from) * ease(t) });
    if (t < 1) tween = requestAnimationFrame(step);
  };
  tween = requestAnimationFrame(step);
}

export function stopGlide(): void {
  cancelAnimationFrame(tween);
}

/** Where a drawing at `px` per em sits in the design space, given the bar's settings. */
export function locationFor(px: number): Location {
  const opsz = state.opszMode === "manual" ? state.opsz : Math.min(72, Math.max(12, px));
  return { wght: state.wght, opsz };
}

export const instanceName = (w: number, names: { name: string; wght: number }[]) =>
  names.find((i) => i.wght === Math.round(w))?.name ?? "";

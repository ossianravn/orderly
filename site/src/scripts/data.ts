// The packed glyph data, fetched once, when a drawing first comes near the screen.
import type { Packed } from "../lib/glyphs";

let pending: Promise<Packed> | null = null;

export function glyphData(): Promise<Packed> {
  pending ??= fetch(`${import.meta.env.BASE_URL.replace(/\/?$/, "/")}data/glyphs.json`).then((r) => {
    if (!r.ok) throw new Error(`glyph data: ${r.status}`);
    return r.json() as Promise<Packed>;
  });
  return pending;
}

/** Calls `draw` while `el` is on or near the screen; loads the data on first approach. */
export function whenNear(el: Element, onChange: (near: boolean) => void): void {
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) onChange(e.isIntersecting);
    },
    { rootMargin: "400px 0px" },
  );
  io.observe(el);
}

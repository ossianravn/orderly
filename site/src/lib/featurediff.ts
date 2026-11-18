// Build time only: shape a feature's sample with the feature off and on (HarfBuzz, the font build's
// variable TTF) and report which characters it changes, so the page can mark them.
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import * as hb from "harfbuzzjs";

export interface Part {
  t: string;
  changed: boolean;
}

export interface Diff {
  parts: Part[];
  changed: boolean;
}

let font: hb.Font | null = null;

function load(): hb.Font {
  if (font) return font;
  const data = readFileSync(resolve(process.cwd(), "public/fonts/orderly-variable.ttf"));
  const blob = new hb.Blob(data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength));
  font = new hb.Font(new hb.Face(blob));
  return font;
}

type Glyph = { cluster: number; codepoint: number; xAdvance?: number; xOffset?: number; yOffset?: number };

function run(text: string, feature: string, lang?: string): Glyph[] {
  const buffer = new hb.Buffer();
  buffer.addText(text);
  if (lang) buffer.setLanguage(lang);
  buffer.guessSegmentProperties();
  hb.shape(load(), buffer, [hb.Feature.fromString(feature)!]);
  return buffer.getGlyphInfosAndPositions();
}

/** Glyphs and placement per cluster start, plus whether that cluster's advance moved. */
function byCluster(glyphs: Glyph[]) {
  const sig = new Map<number, string>();
  const adv = new Map<number, number>();
  for (const g of glyphs) {
    const s = `${g.codepoint}:${g.xOffset ?? 0},${g.yOffset ?? 0}`;
    sig.set(g.cluster, (sig.get(g.cluster) ?? "") + s + ";");
    adv.set(g.cluster, (adv.get(g.cluster) ?? 0) + (g.xAdvance ?? 0));
  }
  return { sig, adv };
}

export function featureDiff(text: string, tag: string, lang?: string): Diff {
  const off = byCluster(run(text, `${tag}=0`, lang));
  const on = byCluster(run(text, `${tag}=1`, lang));
  const starts = [...new Set([...off.sig.keys(), ...on.sig.keys()])].sort((a, b) => a - b);
  const changed = new Array<boolean>(text.length).fill(false);
  starts.forEach((s, i) => {
    const end = i + 1 < starts.length ? starts[i + 1] : text.length;
    const shape = off.sig.get(s) !== on.sig.get(s);
    const moved = off.adv.get(s) !== on.adv.get(s);
    if (!shape && !moved) return;
    for (let k = s; k < end; k++) changed[k] = true;
    // Spacing that changes after a character belongs to the pair: mark the next one too.
    if (moved && !shape && i + 1 < starts.length) {
      const next = starts[i + 1];
      const nextEnd = i + 2 < starts.length ? starts[i + 2] : text.length;
      if (text.slice(next, nextEnd).trim()) for (let k = next; k < nextEnd; k++) changed[k] = true;
    }
  });
  // Spaces are never marked; they only separate.
  for (let k = 0; k < text.length; k++) if (/\s/.test(text[k])) changed[k] = false;
  const parts: Part[] = [];
  for (let k = 0; k < text.length; k++) {
    const last = parts[parts.length - 1];
    if (last && last.changed === changed[k]) last.t += text[k];
    else parts.push({ t: text[k], changed: changed[k] });
  }
  return { parts, changed: changed.some(Boolean) };
}

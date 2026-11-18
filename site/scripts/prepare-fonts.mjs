// Copies what the site serves from ../fonts into public/ (git-ignored) and packs the outlines
// for the browser. Runs before dev and build. The font build owns ../fonts; this only reads it.
import { copyFileSync, mkdirSync, readFileSync, writeFileSync, existsSync, readdirSync, statSync, rmSync } from "node:fs";
import { relative, resolve } from "node:path";
import { zipSync } from "fflate";

const site = process.cwd();
// ORDERLY_FONTS points at another fonts folder (checks only); the default is the font build's.
const fonts = resolve(site, process.env.ORDERLY_FONTS ?? "../fonts");
const out = resolve(site, "public");

const need = [
  ["web/Orderly[opsz,wght].woff2", "fonts/orderly.woff2"],
  ["variable/Orderly[opsz,wght].ttf", "fonts/orderly-variable.ttf"],
];
mkdirSync(resolve(out, "fonts"), { recursive: true });
mkdirSync(resolve(out, "data"), { recursive: true });
for (const [from, to] of need) {
  const src = resolve(fonts, from);
  if (!existsSync(src)) throw new Error(`prepare-fonts: missing ${src}; run the font build first`);
  copyFileSync(src, resolve(out, to));
}

const meta = JSON.parse(readFileSync(resolve(fonts, "data/orderly.json"), "utf8"));
const outlines = JSON.parse(readFileSync(resolve(fonts, "data/outlines.json"), "utf8"));
const order = outlines.masters;

// Packed glyph: u unicode, c category, m [advance, lsb, rsb] per master,
// k contours: p part, o on-curve flags ("1"/"0" per point), x flat [x, y, ...] per master.
const glyphs = {};
for (const g of meta.glyphs) {
  const shape = outlines.glyphs[g.name] ?? {};
  const first = shape[order[0]] ?? [];
  glyphs[g.name] = {
    u: g.unicode,
    ch: g.char,
    c: g.category,
    m: order.map((id) => {
      const m = g.metrics[id];
      return [m.advance, m.lsb, m.rsb];
    }),
    k: first.map((contour, i) => ({
      p: contour.part,
      o: contour.points.map((p) => (p.on ? "1" : "0")).join(""),
      x: order.map((id) => shape[id][i].points.flatMap((p) => [p.x, p.y])),
    })),
  };
}

const packed = {
  version: meta.version,
  unitsPerEm: meta.unitsPerEm,
  metrics: meta.metrics,
  axes: meta.axes,
  masters: order.map((id) => {
    const m = meta.masters.find((x) => x.id === id);
    return { id, name: m.name, wght: m.wght, opsz: m.opsz, numbers: m.numbers };
  }),
  glyphs,
};
writeFileSync(resolve(out, "data/glyphs.json"), JSON.stringify(packed));
console.log(`prepare-fonts: ${Object.keys(glyphs).length} glyphs, version ${meta.version}`);

// The family download: one zip of fonts/variable, fonts/static and fonts/web with the licence and a
// short readme, made only once the font build writes static instances. Same input, same bytes.
const downloads = resolve(out, "downloads");
rmSync(downloads, { recursive: true, force: true });
if (existsSync(resolve(fonts, "static"))) {
  const when = new Date("2026-11-18T00:00:00Z");
  const files = {};
  const add = (dir) => {
    for (const name of readdirSync(dir).sort()) {
      const p = resolve(dir, name);
      if (statSync(p).isDirectory()) add(p);
      else files[`Orderly/${relative(fonts, p).replaceAll("\\", "/")}`] = [readFileSync(p), { mtime: when }];
    }
  };
  for (const d of ["variable", "static", "web"]) if (existsSync(resolve(fonts, d))) add(resolve(fonts, d));
  files["Orderly/OFL.txt"] = [readFileSync(resolve(site, "../OFL.txt")), { mtime: when }];
  const range = (tag) => {
    const a = meta.axes.find((x) => x.tag === tag);
    return `${a.min} to ${a.max}`;
  };
  const readme = [
    `Orderly ${meta.version}`,
    "",
    `A geometric grotesk with a weight axis (${range("wght")}) and an optical-size axis (${range("opsz")}).`,
    "",
    "variable/  the variable font, for apps that support variable fonts",
    "static/    named instances, for apps that do not",
    "web/       WOFF2 files for websites",
    "",
    "Fonts: SIL Open Font License 1.1 (OFL.txt). Source: https://github.com/ossianravn/orderly",
    "",
  ].join("\n");
  files["Orderly/README.txt"] = [new TextEncoder().encode(readme), { mtime: when }];
  mkdirSync(downloads, { recursive: true });
  writeFileSync(resolve(downloads, "orderly.zip"), zipSync(files, { level: 9 }));
  console.log(`prepare-fonts: orderly.zip with ${Object.keys(files).length} files`);
}

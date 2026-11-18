"""Accented letters as composites: a base glyph and marks placed anchor to anchor.

The list is every precomposed letter Orderly supports; its parts come from Unicode's canonical decomposition, with
the usual type conventions: dotless i and j under top marks, capital (.case) marks over capitals, the Latvian comma
for the cedilla of g k l n r, and a vertical comma for the caron of d l t L.
"""

from __future__ import annotations

import unicodedata

from fontTools.agl import UV2AGL

from . import REGISTRY, Drawing, glyph

MARKS = {0x300: "gravecomb", 0x301: "acutecomb", 0x302: "circumflexcomb", 0x303: "tildecomb", 0x304: "macroncomb",
         0x306: "brevecomb", 0x307: "dotaccentcomb", 0x308: "dieresiscomb", 0x30A: "ringcomb",
         0x30B: "hungarumlautcomb", 0x30C: "caroncomb", 0x326: "commaaccentcomb", 0x327: "cedillacomb",
         0x328: "ogonekcomb", 0x312: "commaturnedabovecomb"}
BOTTOM = {"commaaccentcomb", "cedillacomb"}

# Latin Core and the EU, Nordic (Sámi, Greenlandic included) and Turkish letters that decompose
LETTERS = (
    "ÀÁÂÃÄÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝàáâãäçèéêëìíîïñòóôõöùúûüýÿĀāĂăĄąĆćĈĉĊċČčĎďĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥ"
    "ĨĩĪīĬĭĮįİĴĵĶķĹĺĻļĽľŃńŅņŇňŌōŎŏŐőŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽžȘșȚțǦǧǨǩǮǯǺǻǼǽǾǿ"
    "ẀẁẂẃẄẅỲỳ"
)
LATVIAN = set("ĢģĶķĻļŅņŖŗ")


def name_of(cp: int) -> str:
    return UV2AGL.get(cp, f"uni{cp:04X}")


def parts_for(ch: str) -> list[tuple[str, str | None]] | None:
    nfd = unicodedata.normalize("NFD", ch)
    base, marks = nfd[0], [ord(c) for c in nfd[1:]]
    if not marks or any(c not in MARKS for c in marks):
        return None
    upper = base.isupper()
    if ch in "ǺǻǼǽǾǿ":  # Å Æ Ø with acute: the acute sits on the composed letter
        base = {"Ǻ": "Å", "ǻ": "å", "Ǽ": "Æ", "ǽ": "æ", "Ǿ": "Ø", "ǿ": "ø"}[ch]
        marks = [0x301]
    cmap = {u: n for n, sp in REGISTRY.items() for u in sp.unicodes}
    bname = cmap.get(ord(base), name_of(ord(base)))
    if base in "ij" and any(MARKS[c] not in BOTTOM and MARKS[c] != "ogonekcomb" for c in marks):
        bname = "dotlessi" if base == "i" else "uni0237"
    out = [(bname, None)]
    for c in marks:
        mk = MARKS[c]
        if ch in LATVIAN:
            mk = "commaturnedabovecomb" if ch == "ģ" else "commaaccentcomb"
        if mk == "caroncomb" and ch in "ďľťĽ":
            out.append(("caroncomb.alt", "caronalt"))
            continue
        if mk == "ogonekcomb":
            out.append((mk, "ogonek"))
        elif mk in BOTTOM:
            out.append((mk, "bottom"))
        else:
            out.append((mk + (".case" if upper else ""), "top"))
    return out


def _register(ch: str, parts) -> None:
    zone = "uc" if ch.isupper() else "lc"
    glyph(name_of(ord(ch)), ord(ch), zone)(lambda m, parts=parts: Drawing([], components=list(parts)))


for _ch in LETTERS:
    _p = parts_for(_ch)
    if _p:
        _register(_ch, _p)

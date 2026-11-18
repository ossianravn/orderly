"""Browser proof pages for the character set and features: kerning off and on, accented letters, every
character per master, languages (hyperglot's base characters and a line of real words), features off and on,
and the symbols large."""

from __future__ import annotations

import html
import unicodedata

from ..export import FEATURE_NAMES
from .browser import FONT_FILE, MASTER_STYLES, _fv, _page

KERN_LINES = [
    "AVATAR LTAV TA VA YA WA AT AY AW LV LY LW LT FA PA KO RO",
    "Tower Yacht Vowel Wave Pay Ta Te To Tu Tv Ty Va Ve Vo Wa Wo Ya Yo Py Fo Ko",
    "fa ff fl fi fb fh fk f) rv ry rw r. r, v. y. w, kv ko ro va vo ya yo",
    "P. F. T. V, W. Y, L’ T’ ‘A’ “AT” «Wa» ‹Ta› (fj) [Jj] {T} T- -T V- -Y",
    "1. 7. 7, 17 74 47 71 11 1/7 1° 7– (1) [7] 10:42 → Spor 7",
]


def kerning_page() -> str:
    b = ""
    for name, w, o in MASTER_STYLES:
        for line in KERN_LINES:
            for on in ("none", "normal"):
                b += (f"<div class='l'>40 px {name} kerning {'off' if on == 'none' else 'on'}</div><div class='w' "
                      f"style='font-size:40px;font-kerning:{on};{_fv(w, o)}'>{html.escape(line)}</div>")
    return _page("kerning", b)


FEATURE_PROOF = {  # tag -> (text, lang) for the proof; the site's samples are in export.FEATURE_NAMES
    "locl": [("Ş ş Ţ ţ", "ro"), ("i̇ í İstanbul", "tr"), ("col·lecció PAL·LA", "ca"),
             ("ÍJsselmeer bíjna", "nl"), ("ŊUOVVA Ŋ", "se")],
    "ccmp": [("í ǰ į́ Á Ë́ Ǭ", None)],
    "case": [("«(ORDERLY)» – [HI] {OK} ¿QUÉ? ¡SÍ! 10:42 H-H ‹A› H·H •H", None)],
    "frac": [("1/2 3/4 7/16 123/456 11/18/2026", None)],
}


def features_page() -> str:
    from fontTools.ttLib import TTFont

    font = TTFont(FONT_FILE)
    tags = sorted({r.FeatureTag for t in ("GSUB", "GPOS") for r in font[t].table.FeatureList.FeatureRecord})
    b = ""
    for tag in tags:
        if tag in ("kern",):
            continue
        name = FEATURE_NAMES.get(tag, (tag, ""))[0]
        lines = FEATURE_PROOF.get(tag) or [(FEATURE_NAMES.get(tag, ("", ""))[1], None)]
        for text, lang in lines:
            la = f" lang='{lang}'" if lang else ""
            cells = ""
            for state in (0, 1):
                for wt, o in ((400, 12), (900, 72)):
                    cells += (f"<div{la} style='font-size:40px;white-space:nowrap;{_fv(wt, o)};font-feature-settings:"
                              f"\"{tag}\" {state}'>{html.escape(text)}</div>")
            b += (f"<div class='l'>{tag} {html.escape(name)}{' (' + lang + ')' if lang else ''}: off (left) and on "
                  f"(right), Regular Text and Black Display</div><div style='display:grid;grid-template-columns:repeat(4,"
                  f" max-content);gap:0 48px;align-items:baseline'>{cells}</div>")
    return _page("features", b)


def languages_page() -> str:
    from hyperglot.languages import Languages

    from ..coverage import LANGUAGES, SAMPLES

    db = Languages()
    b = ""
    for tag, code, name in LANGUAGES:
        base = db[code]["orthographies"][0].get("base", "")
        b += (f"<div class='l'>{name} ({tag})</div><div lang='{tag}' style='font-size:26px;line-height:1.3'>"
              f"{html.escape(SAMPLES[tag])}</div><div lang='{tag}' style='font-size:20px;line-height:1.3;"
              f"{_fv(900, 72)}'>{html.escape(SAMPLES[tag])}</div><div lang='{tag}' style='font-size:16px;"
              f"color:var(--mute)'>{html.escape(base)}</div>")
    return _page("languages", b)


def symbols_page() -> str:
    lines = ["$¢£¥€ƒ¤₺₽₹ 12,50 € £3 ¥500", "+−×÷=≠<>≤≥±≈~¬∞◊ 2×3=6 a≠b x≤y",
             "µπΩ∂∆∏∑√∫ ©®™§¶†‡‰№ªº•¦", "←↑→↓↖↗↘↙↔↕ 10:42 → Spor 7", "#%&*@^_|\\/{}[]() ¨¯´¸ˆˇ˘˙˚˛˜˝"]
    b = ""
    for name, w, o in MASTER_STYLES:
        b += f"<div class='l'>56 px {name}</div>" + "".join(
            f"<div class='w' style='font-size:56px;{_fv(w, o)}'>{html.escape(t)}</div>" for t in lines)
    return _page("symbols", b)


def phase4_pages() -> dict[str, str]:
    from fontTools.ttLib import TTFont

    out = {"kerning": kerning_page(), "features": features_page(), "symbols": symbols_page()}
    cmap = TTFont(FONT_FILE).getBestCmap() if FONT_FILE.exists() else {}
    chars = "".join(chr(u) for u in sorted(cmap) if u > 0x20 and not 0x300 <= u < 0x370)
    accented = "".join(c for c in chars if len(unicodedata.normalize("NFD", c)) > 1)
    b = ""
    for name, w, o in MASTER_STYLES:
        b += (f"<div class='l'>40 px {name}</div><div style='font-size:40px;line-height:1.5;max-width:30em;"
              f"word-break:break-all;{_fv(w, o)}'>{html.escape(accented)}</div>")
    out["diacritics"] = _page("diacritics", b)
    for name, w, o in MASTER_STYLES:
        key = name.lower().replace(" ", "-")
        out[f"charset-{key}"] = _page(f"all characters {name}", (
            f"<div class='l'>44 px {name}</div><div style='font-size:44px;line-height:1.45;max-width:32em;"
            f"word-break:break-all;{_fv(w, o)}'>{html.escape(chars)}</div>"))
    try:
        out["languages"] = languages_page()
    except ImportError:
        pass
    return out

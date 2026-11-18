"""Browser proofs of the compiled font: HTML pages served on port 4813 and screenshotted by a real browser engine
(Playwright driving the installed Chrome or Edge, else Playwright's Chromium), light and dark, to proofs/browser/.
"""

from __future__ import annotations

import functools
import html
import http.server
import threading
from pathlib import Path

from ..build import BUILD, FONTS, ROOT
from .text import CTRL_LC, CTRL_UC, DANISH, ENGLISH, WORDS, spacing_strings

PORT = 4813
PAGES = BUILD / "proof-pages"
OUT = ROOT / "proofs" / "browser"
FONT_FILE = FONTS / "variable" / "Orderly[opsz,wght].ttf"
WEIGHTS = [(100, "Thin"), (200, "ExtraLight"), (300, "Light"), (400, "Regular"), (500, "Medium"),
           (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")]

CSS = """
@font-face { font-family: Orderly; font-weight: 100 900;
  src: url('/fonts/variable/Orderly%%5Bopsz%%2Cwght%%5D.ttf?v=%(v)s'); }
.cols { display: grid; grid-template-columns: repeat(3, 30em); gap: 2.4em; align-items: start; }
.cols p { max-width: none; }
.text { font-optical-sizing: none; font-variation-settings: "opsz" 12; }
.disp { font-optical-sizing: none; font-variation-settings: "opsz" 72; }
.sys { font-family: "Segoe UI", Arial, sans-serif; }
:root { color-scheme: light dark; --paper: #f6f7f9; --ink: #16171a; --mute: #8a8f98; --rule: #d9dce2; }
@media (prefers-color-scheme: dark) { :root { --paper: #141518; --ink: #eceef2; --mute: #7d828c; --rule: #2c2f35; } }
body { margin: 0; padding: 32px 40px; background: var(--paper); color: var(--ink); font-family: Orderly; }
.l { font: 12px/1.2 system-ui, sans-serif; color: var(--mute); margin: 18px 0 4px; }
.r { border-top: 1px solid var(--rule); margin: 22px 0 8px; }
p { margin: 0; max-width: 34em; }
.w { white-space: nowrap; line-height: 1.15; }
"""


def _page(title: str, body: str, weight: int = 400) -> str:
    v = int(FONT_FILE.stat().st_mtime) if FONT_FILE.exists() else 0
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS % {'v': v}}"
            f"body {{ font-weight: {weight}; }}</style></head><body>{body}</body></html>")


def _line(text: str, px: int, label: str = "") -> str:
    return (f"<div class='l'>{px} px {label}</div><div class='w' style='font-size:{px}px;line-height:1.3'>"
            f"{html.escape(text)}</div>")


def pages() -> dict[str, str]:
    out = {}
    body = "".join(_line(t, px) for t, px in (("HOno", 200), (f"{CTRL_LC} {CTRL_UC}", 96), (f"{CTRL_LC} {CTRL_UC}", 48),
                                               (f"{CTRL_LC} {CTRL_UC}", 24), (f"{CTRL_LC} {CTRL_UC}", 16)))
    out["control"] = _page("control", body)
    body = ""
    for px in (200, 96, 48):
        body += "".join(_line(w, px) for w in WORDS[:4])
    for px in (32, 24, 16):
        body += "".join(_line(w, px) for w in WORDS)
    out["words"] = _page("words", body)
    body = ""
    for px in (200, 96):
        body += "".join(_line(w, px) for w in WORDS[4:])
    out["words-nordic"] = _page("words-nordic", body)
    body = ""
    for px in (24, 20, 16, 13, 11):
        for text in (DANISH, ENGLISH):
            body += f"<div class='l'>{px} px</div><p style='font-size:{px}px;line-height:1.45'>{html.escape(text)}</p>"
    out["paragraph"] = _page("paragraph", body)
    lc = "abcdefghijklmnopqrstuvwxyzæøå"
    uc = "ABCDEFGHIJKLMNOPQRSTUVWXYZÆØÅ"
    fig = "0123456789.,:;!?-'\"()/&"
    body = "<div class='l'>36 px</div>" + "".join(
        f"<div class='w' style='font-size:36px'>{html.escape(s)}</div>"
        for s in spacing_strings(lc, True) + spacing_strings(uc, False) + spacing_strings(fig, False))
    out["spacing"] = _page("spacing", body)
    body = "".join(_line(s, 120) for s in (lc[:15], lc[15:], uc[:13], uc[13:], fig))
    out["charset"] = _page("charset", body)
    for wt, key in ((100, "thin"), (900, "black")):
        out[f"charset-{key}"] = _page(f"charset {key}", body, wt)
        b = ""
        for px in (200, 96, 32):
            b += "".join(_line(w, px) for w in (WORDS[:6] if px < 200 else WORDS[:4]))
        out[f"words-{key}"] = _page(f"words {key}", b, wt)
        b = "<div class='l'>36 px</div>" + "".join(
            f"<div class='w' style='font-size:36px'>{html.escape(x)}</div>"
            for x in spacing_strings(lc, True) + spacing_strings(uc, False) + spacing_strings(fig, False))
        out[f"spacing-{key}"] = _page(f"spacing {key}", b, wt)
    for px in (96, 32):
        b = ""
        for text in ("Hamburgefonstiv", "HAMBURGEFONSTIV", "Orderly 0123456789", "Blåbærsyltetøj på rugbrød"):
            b += "".join(f"<div class='l'>{px} px {name} {wt}</div><div class='w' style='font-size:{px}px;"
                         f"font-weight:{wt};line-height:1.25'>{html.escape(text)}</div>" for wt, name in WEIGHTS)
        out[f"ladder-{px}"] = _page(f"ladder {px}", b)
    out.update(size_pages())
    out.update(phase4_pages())
    return out


MASTER_STYLES = [("Thin Text", 100, 12), ("Regular Text", 400, 12), ("Black Text", 900, 12),
                 ("Thin Display", 100, 72), ("Regular Display", 400, 72), ("Black Display", 900, 72)]


def _fv(w: int, o: int) -> str:
    return f"font-weight:{w};font-optical-sizing:none;font-variation-settings:'opsz' {o}"


def phase4_pages() -> dict[str, str]:
    """Kerning off and on, every accented letter, the whole character set per master, language samples."""
    from fontTools.ttLib import TTFont

    out = {}
    cmap = TTFont(FONT_FILE).getBestCmap() if FONT_FILE.exists() else {}
    chars = "".join(chr(u) for u in sorted(cmap) if u > 0x20 and not 0x300 <= u < 0x370)
    kern = "AVATAR Tower Yacht LTAV TA VA P. F. ‘A’ «Wa» Yo To Vo rv ry f. 1.T"
    b = ""
    for name, w, o in MASTER_STYLES:
        for on in ("none", "normal"):
            b += (f"<div class='l'>48 px {name} kerning {'off' if on == 'none' else 'on'}</div><div class='w' "
                  f"style='font-size:48px;font-kerning:{on};{_fv(w, o)}'>{html.escape(kern)}</div>")
    out["kerning"] = _page("kerning", b)
    accented = "".join(c for c in chars if len(__import__("unicodedata").normalize("NFD", c)) > 1)
    b = ""
    for name, w, o in MASTER_STYLES:
        b += (f"<div class='l'>40 px {name}</div><div style='font-size:40px;line-height:1.5;max-width:30em;word-break:break-all;"
              f"{_fv(w, o)}'>{html.escape(accented)}</div>")
    out["diacritics"] = _page("diacritics", b)
    b = ""
    for name, w, o in MASTER_STYLES:
        b += (f"<div class='l'>36 px {name}</div><div style='font-size:36px;line-height:1.45;max-width:36em;"
              f"word-break:break-all;{_fv(w, o)}'>{html.escape(chars)}</div>")
    out["charset-all"] = _page("all characters", b)
    try:
        from hyperglot.languages import Languages

        from ..coverage import LANGUAGES

        db = Languages()
        b = ""
        for tag, code, name in LANGUAGES:
            base = db[code]["orthographies"][0].get("base", "")
            b += (f"<div class='l'>{name} ({tag})</div><div lang='{tag}' style='font-size:28px;line-height:1.3'>"
                  f"{html.escape(base)}</div>")
        out["languages"] = _page("languages", b)
    except ImportError:
        pass
    return out


def size_pages() -> dict[str, str]:
    """Optical size: Text against Display and a system face at reading sizes; auto against fixed opsz;
    headlines; opsz steps at one size."""
    out = {}
    b = ""
    for px in (9, 11, 13, 16):
        for text in (DANISH, ENGLISH):
            cells = "".join(f"<div><div class='l'>{px} px {lab}</div><p class='{cls}' style='font-size:{px}px;"
                            f"line-height:1.45'>{html.escape(text)}</p></div>"
                            for cls, lab in (("text", "Orderly Text (opsz 12)"), ("disp", "Orderly Display (opsz 72)"),
                                             ("sys", "Segoe UI")))
            b += f"<div class='cols'>{cells}</div>"
    out["small"] = _page("small sizes", b)
    b = ""
    for px in (9, 12, 16, 24, 36, 48, 72, 96):
        exp = min(max(px, 12), 72)
        cells = "".join(f"<div><div class='l'>{px} px {lab}</div><div class='w' data-cmp='{px}-{key}' style='font-size:"
                        f"{px}px;{css}'>Hamburgefonstiv</div></div>"
                        for key, lab, css in (("auto", "auto", "font-optical-sizing:auto"),
                                              ("fixed", f"fixed opsz {exp}",
                                               f"font-optical-sizing:none;font-variation-settings:'opsz' {exp}")))
        b += f"<div class='cols' style='grid-template-columns:repeat(2, max-content)'>{cells}</div>"
    out["optical-auto"] = _page("optical sizing auto", b)
    b = ""
    for px in (72, 120, 180):
        for cls, lab in (("disp", "Display (opsz 72)"), ("text", "Text (opsz 12)")):
            b += "".join(f"<div class='l'>{px} px {lab}</div><div class='w {cls}' style='font-size:{px}px'>"
                         f"{html.escape(w)}</div>" for w in ("Orderly Hamburgefonstiv",) if True)
    out["headlines"] = _page("headlines", b)
    b = ""
    for wt in (400, 900, 100):
        for o in (12, 24, 36, 48, 72):
            b += (f"<div class='l'>64 px weight {wt} opsz {o}</div><div class='w' style='font-size:64px;font-weight:"
                  f"{wt};font-optical-sizing:none;font-variation-settings:\"opsz\" {o}'>Hamburgefonstiv 2048</div>")
    out["opsz-steps"] = _page("opsz steps", b)
    return out


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def _server() -> http.server.ThreadingHTTPServer:
    handler = functools.partial(_Quiet, directory=str(ROOT))
    return http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)


def write_pages() -> list[str]:
    PAGES.mkdir(parents=True, exist_ok=True)
    names = []
    for name, doc in pages().items():
        (PAGES / f"{name}.html").write_text(doc, encoding="utf-8")
        names.append(name)
    return names


def serve_forever() -> None:
    write_pages()
    print(f"proof pages at http://127.0.0.1:{PORT}/build/proof-pages/")
    _server().serve_forever()


def _launch(p):
    for channel in ("chrome", "msedge", None):
        try:
            return p.chromium.launch(channel=channel) if channel else p.chromium.launch()
        except Exception:  # noqa: BLE001 - try the next engine
            continue
    raise RuntimeError("no Chromium-based browser found; run `uv run playwright install chromium`")


def _compare_auto(page) -> None:
    """Pixel-compare each auto sample with itself re-set to the opsz the browser should pick (clamp of the size to
    12..72), in the same place; and, as a control, to the opposite end of the axis, which must differ."""
    res = []
    for px in (9, 12, 16, 24, 36, 48, 72, 96):
        el = page.locator(f"[data-cmp='{px}-auto']")
        auto = el.screenshot()
        exp, other = min(max(px, 12), 72), (72 if px < 42 else 12)
        shots = []
        for o in (exp, other):
            el.evaluate("(e, css) => e.style.cssText = css",
                        f'font-size:{px}px;font-optical-sizing:none;font-variation-settings:"opsz" {o}')
            shots.append(el.screenshot())
        el.evaluate("(e, css) => e.style.cssText = css", f"font-size:{px}px;font-optical-sizing:auto")
        res.append(f"{px}px auto=opsz {exp}: {'yes' if auto == shots[0] else 'NO'}"
                   f" (control opsz {other} differs: {'yes' if auto != shots[1] else 'NO'})")
    print("font-optical-sizing auto in Chrome:")
    for r in res:
        print("  " + r)


def render(only: list[str] | None = None, width: int = 1600) -> None:
    from playwright.sync_api import sync_playwright

    names = [n for n in write_pages() if only is None or n in only]
    srv = _server()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = _launch(p)
            print(f"browser: {browser.browser_type.name} {browser.version}")
            runs = [(s, 1) for s in ("light", "dark")] + [(s, 2) for s in ("light", "dark")]
            for scheme, dsf in runs:
                ctx = browser.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme,
                                          device_scale_factor=dsf)
                page = ctx.new_page()
                for n in names:
                    if dsf == 2 and n != "small":
                        continue
                    page.goto(f"http://127.0.0.1:{PORT}/build/proof-pages/{n}.html")
                    page.evaluate("document.fonts.ready.then(() => document.fonts.size)")
                    page.wait_for_timeout(150)
                    out = OUT / (f"{n}-{scheme}.png" if dsf == 1 else f"{n}-2x-{scheme}.png")
                    page.screenshot(path=str(out), full_page=True)
                    if n == "optical-auto" and scheme == "light":
                        _compare_auto(page)
                    print(f"wrote {out.relative_to(ROOT)}")
                ctx.close()
            browser.close()
    finally:
        srv.shutdown()

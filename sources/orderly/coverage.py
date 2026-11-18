"""Languages Orderly supports: the Latin-script official languages of the EU and the Nordic countries (Sámi and
Greenlandic included) and Turkish. The list is fixed here for the build; `uv run --group qa orderly languages`
re-checks every entry against the compiled font with hyperglot."""

from __future__ import annotations

# (BCP 47 tag, hyperglot's ISO 639-3 code, English name)
LANGUAGES = [
    ("hr", "hrv", "Croatian"), ("cs", "ces", "Czech"), ("da", "dan", "Danish"), ("nl", "nld", "Dutch"),
    ("en", "eng", "English"), ("et", "ekk", "Estonian"), ("fi", "fin", "Finnish"), ("fr", "fra", "French"),
    ("de", "deu", "German"), ("hu", "hun", "Hungarian"), ("ga", "gle", "Irish"), ("it", "ita", "Italian"),
    ("lv", "lvs", "Latvian"), ("lt", "lit", "Lithuanian"), ("mt", "mlt", "Maltese"), ("pl", "pol", "Polish"),
    ("pt", "por", "Portuguese"), ("ro", "ron", "Romanian"), ("sk", "slk", "Slovak"), ("sl", "slv", "Slovenian"),
    ("es", "spa", "Spanish"), ("sv", "swe", "Swedish"), ("no", "nor", "Norwegian"), ("is", "isl", "Icelandic"),
    ("fo", "fao", "Faroese"), ("kl", "kal", "Greenlandic"), ("se", "sme", "Northern Sámi"),
    ("smj", "smj", "Lule Sámi"), ("sma", "sma", "Southern Sámi"), ("smn", "smn", "Inari Sámi"),
    ("sms", "sms", "Skolt Sámi"), ("tr", "tur", "Turkish"),
]


def supported() -> list[dict]:
    return [{"tag": t, "iso639_3": c, "name": n} for t, c, n in LANGUAGES]


def check(font_path: str) -> bool:
    """Every listed language's base characters (hyperglot, primary orthography) are in the font."""
    from hyperglot.checker import FontChecker

    fc = FontChecker(font_path)
    ok = True
    for t, c, n in LANGUAGES:
        good = fc.supports_language(c)
        ok &= bool(good)
        print(f"  {'ok  ' if good else 'MISS'} {n} ({t})")
    return ok

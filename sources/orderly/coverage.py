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


# A line of real words per language: pangrams where a well-known one exists, otherwise place names and words.
SAMPLES = {
    "hr": "Gojazni đačić s biciklom drži hmelj i finu vatu u džepu nošnje.",
    "cs": "Příliš žluťoučký kůň úpěl ďábelské ódy.",
    "da": "Høj bly gom vandt fræk sexquiz på wc. Blåbærsyltetøj på rugbrød.",
    "nl": "Pa’s wijze lynx bezag vroom het fikse aquaduct. IJsselmeer.",
    "en": "The quick brown fox jumps over the lazy dog.",
    "et": "Põdur Zagrebi tšellomängija-följetonist Ciqo külmetas kehvas garaažis.",
    "fi": "Charles Darwin jammaili Åken hevixylofonilla Qatarin yöpub Zeligissä.",
    "fr": "Voix ambiguë d’un cœur qui, au zéphyr, préfère les jattes de kiwis.",
    "de": "Victor jagt zwölf Boxkämpfer quer über den großen Sylter Deich.",
    "hu": "Árvíztűrő tükörfúrógép.",
    "ga": "D’fhuascail Íosa, Úrmhac na hÓighe Beannaithe, pór Éava agus Ádhaimh.",
    "it": "Quel vituperabile xenofobo zelante assaggia il whisky ed esclama: alleluja!",
    "lv": "Glāžšķūņa rūķīši dzērumā čiepj Baha koncertflīģeļu vākus.",
    "lt": "Įlinkdama fechtuotojo špaga sublykčiojusi pragręžė apvalų arbūzą.",
    "mt": "Ċirkewwa, Għawdex, Ħaż-Żabbar, Żebbuġ, Marsaxlokk.",
    "pl": "Pchnąć w tę łódź jeża lub ośm skrzyń fig.",
    "pt": "Luís argüia à Júlia que «brações, fé, chá, óxido, pôr, zângão» eram palavras do português.",
    "ro": "Înjurând pițigăiat, zoofobul comandă vexat whisky și tequila.",
    "sk": "Kŕdeľ šťastných ďatľov učí pri ústí Váhu mĺkveho koňa obhrýzať kôru a žrať čerstvé mäso.",
    "sl": "Hišničin bratec vzgaja polže pod fikusom.",
    "es": "El veloz murciélago hindú comía feliz cardillo y kiwi. La cigüeña tocaba el saxofón.",
    "sv": "Flygande bäckasiner söka hwila på mjuka tuvor.",
    "no": "Vår sære Zulu fra badeøya spilte jo whist og quickstep i min taxi.",
    "is": "Kæmi ný öxi hér, ykist þjófum nú bæði víl og ádrepa.",
    "fo": "Tórshavn, Klaksvík, Fuglafjørður, Gøta, Sørvágur.",
    "kl": "Kalaallit Nunaat, Nuuk, Ilulissat, Qaqortoq, Sisimiut, Upernavik.",
    "se": "Sápmi, Guovdageaidnu, Kárášjohka, Ruoŧŧa, máŋga, giđđa, beaivváš.",
    "smj": "Jåhkåmåhkke, Bådådjo, julevsámegiella, Divtasvuodna.",
    "sma": "Åarjelsaemien gïele, Snåasa, Raarohke, Staare.",
    "smn": "Anarâškielâ, Aanaar, Avveel.",
    "sms": "Sääʹmǩiõll, Čeʹvetjäuʹrr, ǩiõll.",
    "tr": "Pijamalı hasta yağız şoföre çabucak güvendi. İstanbul, Iğdır.",
}


def supported() -> list[dict]:
    return [{"tag": t, "iso639_3": c, "name": n, "sample": SAMPLES[t]} for t, c, n in LANGUAGES]


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

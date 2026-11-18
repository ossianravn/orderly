"""Proof texts and glyph groups, shared by the outline sheets and the browser proofs."""

from __future__ import annotations

GROUPS = {
    "control": ["H", "O", "n", "o"],
    "lc-rounds": ["o", "c", "e", "a", "d", "b", "p", "q", "g"],
    "lc-arches": ["n", "h", "m", "r", "u"],
    "lc-straight": ["i", "j", "l", "t", "f", "s", "k"],
    "lc-diagonal": ["v", "w", "x", "y", "z"],
    "uc-rounds": ["O", "C", "G", "Q", "D", "S"],
    "uc-straight": ["H", "I", "E", "F", "L", "T", "J", "U"],
    "uc-bowls": ["B", "P", "R", "K"],
    "uc-diagonal": ["A", "V", "W", "M", "N", "X", "Y", "Z"],
    "figures": ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
    "punctuation": ["period", "comma", "colon", "semicolon", "exclam", "question", "hyphen", "quotesingle",
                    "quotedbl", "parenleft", "parenright", "slash", "ampersand"],
    "nordic": ["AE", "Oslash", "Aring", "ae", "oslash", "aring"],
}

SPACING_LINES = [
    "nnonn oonoo HHOHH OOHOO",
    "Hamburgefonstiv HAMBURGEFONSTIV",
    "Orderly ORDERLY",
]

WORDS = [
    "Hamburgefonstiv",
    "HAMBURGEFONSTIV",
    "Orderly",
    "ORDERLY",
    "Blåbærsyltetøj på rugbrød",
    "Æ Ø Å æ ø å",
    "0123456789",
    "Illegal1 Il1 O0 rn m cl d",
]

DANISH = (
    "Alt har sin plads. På biblioteket står bøgerne ordnet efter emne, og hvert kort i kartoteket fortæller, hvor "
    "man finder dem. Når man læser længe, mærker man, om bogstaverne er tegnet med omhu: om de står roligt på "
    "linjen, om ordene hænger sammen, og om siden er jævnt grå. Gode skrifter forsvinder i teksten; man ser "
    "indholdet og glemmer formen."
)

ENGLISH = (
    "Everything has its place. In the library the books stand in order by subject, and every card in the index "
    "says where to find them. When you read for a long time you notice whether the letters were drawn with care: "
    "whether they sit quietly on the line, whether the words hold together, and whether the page is an even grey. "
    "Good type disappears into the text; you see the content and forget the form."
)

CTRL_LC = "nnonn oonoo"
CTRL_UC = "HHOHH OOHOO"


def spacing_strings(chars: str, lower: bool) -> list[str]:
    """Each glyph between nn..nn and oo..oo (lowercase) or HH..HH and OO..OO (capitals)."""
    a, b = ("nn", "oo") if lower else ("HH", "OO")
    return [f"{a}{c}{a}{c}{a} {b}{c}{b}{c}{b}" for c in chars]


def names_for(text: str, glyphs) -> list[str]:
    """Glyph names for a string, skipping characters the font does not have yet."""
    cmap = {u: n for n, g in glyphs.items() for u in g.unicodes}
    return [cmap[ord(ch)] for ch in text if ord(ch) in cmap]

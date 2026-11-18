"""Command line: uv run orderly <command>.

  build              generator -> UFO -> fonts/static/OrderlyDisplay-Regular.ttf
  sheets [glyphs]    outline sheets from the generator -> proofs/sheets/*.png
  proof [pages]      browser proofs of the compiled font -> proofs/browser/*.png
  serve              serve the proof pages on port 4813
  check              interpolation-compatibility check against a throwaway second master
  all                build, sheets and proofs
"""

from __future__ import annotations

import sys


def main() -> None:
    args = sys.argv[1:]
    cmd = args[0] if args else "all"
    rest = args[1:]
    if cmd in ("build", "all"):
        from .build import build_static

        build_static()
    if cmd in ("sheets", "all"):
        from .proof.sheets import render_all

        render_all(rest or None)
    if cmd in ("proof", "all"):
        from .proof.browser import render

        render(rest or None)
    if cmd == "look":
        from .proof.sheets import look

        look(rest)
    if cmd == "serve":
        from .proof.browser import serve_forever

        serve_forever()
    if cmd == "check":
        from .build import check_compat

        sys.exit(0 if check_compat() else 1)
    if cmd in ("-h", "--help", "help"):
        print(__doc__)


if __name__ == "__main__":
    main()

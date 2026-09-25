#!/usr/bin/env python3
"""Write the Locus-original icons listed in tools/images-drawn.txt.

Usage: python3 tools/icons/build.py [--only <substring>]

Needs picosvg, cairosvg and fonttools (pip install -r tools/icons/requirements.txt)
and the Noto fonts (fonts-noto-core, fonts-noto-extra on Debian and Ubuntu).
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import cairosvg  # noqa: E402

from lib import TOOL_INK, UI_INK, finish  # noqa: E402
from paper import PAPER, THUMBS  # noqa: E402
from tool_icons import MONO, TOOLS  # noqa: E402
from ui_icons import PNGS, UI  # noqa: E402

COMMON = "source/shared/common/src/main/resources/org/geogebra/common/"
TOOL_DIR = COMMON + "icons/svg/web/toolIcons/"


def drawn_list():
    with open(os.path.join(ROOT, "tools/images-drawn.txt")) as f:
        return [line.strip() for line in f if line.strip()]


def write(rel, data, binary=False):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb" if binary else "w") as f:
        f.write(data)


def png_from_svg(svg_text, size_w, size_h=None):
    size_h = size_h or size_w
    return cairosvg.svg2png(bytestring=svg_text.encode(), output_width=size_w,
                            output_height=size_h)


def main():
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    wanted = drawn_list()
    produced = {}

    for name, fn in TOOLS.items():
        produced[TOOL_DIR + name + ".svg"] = lambda fn=fn: finish(fn(), 32, TOOL_INK)
    for rel, (fn, size, fill, flat) in UI.items():
        produced[COMMON + rel] = (lambda fn=fn, size=size, fill=fill, flat=flat:
                                  finish(fn(), size, fill or UI_INK, flatten=flat))
    for rel, fn in PAPER.items():
        produced[rel if rel.startswith("source/") else COMMON + rel] = fn

    svg_cache = {}
    missing = []
    for rel in wanted:
        if only and only not in rel:
            continue
        if rel.endswith(".svg"):
            if rel not in produced:
                missing.append(rel)
                continue
            text = produced[rel]()
            svg_cache[rel] = text
            write(rel, text)
        elif rel.endswith(".png"):
            key = rel.split("/resources/", 1)[1]
            key = key.split("org/geogebra/common/", 1)[-1]
            if key in PNGS:
                src, px = PNGS[key]
                if callable(src):
                    text = finish(src(), 24, UI_INK)
                else:
                    src_rel = COMMON + src
                    text = svg_cache.get(src_rel) or produced[src_rel]()
                write(rel, png_from_svg(text, px), binary=True)
            elif os.path.basename(rel) in THUMBS:
                svg_text, w, h = THUMBS[os.path.basename(rel)]()
                write(rel, png_from_svg(svg_text, w, h), binary=True)
            else:
                missing.append(rel)
        else:
            missing.append(rel)
    if missing:
        print("NOT PRODUCED:\n  " + "\n  ".join(missing))
        sys.exit(1)
    extra = [p for p in produced if p not in wanted]
    if extra:
        print("defined but not in images-drawn.txt:\n  " + "\n  ".join(extra))
    print(f"ok: {len(wanted)} files")


if __name__ == "__main__":
    main()

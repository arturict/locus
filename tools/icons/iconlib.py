"""Helpers for the Locus UI icon generator (see build_icons.py).

Every icon is written as a 24 x 24 viewBox SVG whose root element carries the
default colour as a `fill` attribute and whose shapes carry no fill of their
own. `SVGResourcePrototype.withFill` recolours an icon by setting
`style="fill: <colour>"` on the root element, so shapes must inherit the fill.

Drawn icons use native strokes inside an SVG mask; the only painted element is
one rectangle that inherits the root fill, so recolouring works for them too.
"""
import os
import re
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

MS_VERSION = "0.47.5"  # @material-symbols/svg-400 (Material Symbols Outlined, weight 400)
FA_VERSION = "7.3.1"  # @fortawesome/fontawesome-free
CACHE = Path(os.environ.get("LOCUS_ICON_CACHE", Path.home() / ".cache" / "locus-icons"))
FONT_DIR = Path(os.environ.get("LOCUS_FONT_DIR", "/usr/share/fonts/truetype/noto"))

NEUTRAL = "#5b6470"  # design token text-secondary: default UI icon colour
TEXT = "#1c2024"  # design token text: keyboard key glyphs
WHITE = "#ffffff"
PRIMARY = "#0e7c86"
PRIMARY_TINT = "#e2f3f4"
ACCENT = "#e8743b"
BORDER = "#d6dade"
SURFACE_ALT = "#f4f6f7"
WARNING = "#b26a00"
POINT = "#1f4e9c"


def _package(name, version, dirname):
    target = CACHE / dirname
    if not (target / "package").is_dir():
        target.mkdir(parents=True, exist_ok=True)
        out = subprocess.run(["npm", "pack", f"{name}@{version}", "--silent"], cwd=target,
                             check=True, capture_output=True, text=True).stdout.split()[-1]
        subprocess.run(["tar", "-xzf", out], cwd=target, check=True)
    return target / "package"


def ms_dir():
    return _package("@material-symbols/svg-400", MS_VERSION, f"material-symbols-{MS_VERSION}") / "outlined"


def fa_dir():
    return _package("@fortawesome/fontawesome-free", FA_VERSION, f"fontawesome-free-{FA_VERSION}") / "svgs"


def _num(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def transform_path(d, a, b, c, dd, e, f):
    """Apply the affine matrix (a b c d e f) to SVG path data; arcs become curves."""
    pen = SVGPathPen(None, ntos=_num)
    parse_path(d, TransformPen(pen, (a, b, c, dd, e, f)))
    return pen.getCommands()


def _paths_of(svg_text):
    return re.findall(r'<path[^>]*\sd="([^"]+)"', svg_text)


def material_paths(name):
    """Material Symbols Outlined path data scaled from 0 -960 960 960 to 0 0 24 24."""
    text = (ms_dir() / f"{name}.svg").read_text()
    assert 'viewBox="0 -960 960 960"' in text, name
    return [transform_path(d, 0.025, 0, 0, 0.025, 0, 24) for d in _paths_of(text)]


def fa_paths(name, box=20.0):
    """Font Awesome Free path data fitted and centred in a box x box square."""
    text = (fa_dir() / f"{name}.svg").read_text()
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', text).group(1).split()]
    w, h = vb[2], vb[3]
    s = box / max(w, h)
    tx = 12 - (vb[0] + w / 2) * s
    ty = 12 - (vb[1] + h / 2) * s
    return [transform_path(d, s, 0, 0, s, tx, ty) for d in _paths_of(text)]


_fonts = {}


def font(name):
    if name not in _fonts:
        _fonts[name] = TTFont(str(FONT_DIR / name))
    return _fonts[name]


SANS = "NotoSans-Regular.ttf"
SANS_MED = "NotoSans-Medium.ttf"
SERIF_IT = "NotoSerif-Italic.ttf"
SERIF = "NotoSerif-Regular.ttf"
MATH = "NotoSansMath-Regular.ttf"


def text_width(text, fontname, size):
    f = font(fontname)
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    return sum(f["hmtx"][cmap[ord(ch)]][0] for ch in text) * size / upm


def text_path(text, fontname, size, x, y, anchor="start"):
    """Glyph outlines of `text` as path data; (x, y) is the baseline point."""
    f = font(fontname)
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    glyphs = f.getGlyphSet()
    s = size / upm
    if anchor != "start":
        w = text_width(text, fontname, size)
        x -= w if anchor == "end" else w / 2
    pen = SVGPathPen(glyphs, ntos=_num)
    cursor = x
    for ch in text:
        gname = cmap[ord(ch)]
        glyphs[gname].draw(TransformPen(pen, (s, 0, 0, -s, cursor, y)))
        cursor += f["hmtx"][gname][0] * s
    return pen.getCommands()


def svg_doc(body, color=NEUTRAL, size=24, height=None, comment=None):
    height = size if height is None else height
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{_num(size)}" height="{_num(height)}"'
            f' viewBox="0 0 24 24" fill="{color}">')
    note = f"<!-- {comment} -->" if comment else ""
    return f"{head}{note}{body}</svg>\n"


def paths_body(paths):
    return "".join(f'<path d="{d}"/>' for d in paths)


def masked_body(ink, mask_id):
    """`ink` is SVG markup drawn in white (opaque) or grey (translucent) on black."""
    return (f'<mask id="{mask_id}" maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24">'
            f'<rect width="24" height="24" fill="#000"/>{ink}</mask>'
            f'<rect width="24" height="24" mask="url(#{mask_id})"/>')

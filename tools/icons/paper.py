"""Paper-like Locus assets: Notes page rulings, their preview thumbnails, the
ruler and protractor images of the Notes measurement tools, and the splash
wordmark.

Geometry that the Java code depends on:
- Rulings (EuclidianViewW.getSVGRulingResource, DrawBackground.drawSVG) are
  tiled vertically and drawn at twice their size at the default zoom; the
  code assumes an image width of 539 (DrawBackground.SVG_BASE_WIDTH).
- The measurement tools (MeasurementController) are placed at their natural
  size. Ruler: rotation centre on the top edge at x = 25 of 1051, so the zero
  mark sits there; the pen snaps to the top and bottom edges. Protractor:
  centre at 278.86 of 296 from the top, horizontally centred; the pen snaps to
  the bottom edge. Triangle protractor: centre in the middle of the bottom
  edge, apex in the middle of the top edge; the pen snaps to the bottom edge
  and both legs, so the height is half the width (a right angle at the apex).
- Scales use 50 px per centimetre: the "Squared (1 cm)" ruling is 50 px
  (EuclidianSettings bgRulerGap) and one unit of the view at the default
  zoom, and the tools are scaled with the view like the ruling.

The wordmark uses Noto Sans SemiBold (docs/design.md), instanced from the
variable font. Set NOTO_SANS_VF to the path of NotoSans[wdth,wght].ttf from
https://github.com/google/fonts/tree/main/ofl/notosans ; without it the
existing ggb-logo-name.svg is kept.
"""
import math
import os
import re
import tempfile

import lib
from lib import f2, glyph, line, path, poly, rect

TEXT = "#1c2024"
EDGE = "#0a5c63"
TINT = "#e2f3f4"
MAIN = "#7d8f9c"
HELP = "#aebbc4"
MID_BAND = "#eef2f4"

PAPER = {}
THUMBS = {}
R = "icons/svg/web/matDesignIcons/mow/rulings/"
RP = "icons/svg/web/ruler_protractor/"


def doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{f2(w)}" height="{f2(h)}" '
            f'viewBox="0 0 {f2(w)} {f2(h)}">{body}</svg>\n')


def rotated(el, angle, cx, cy):
    return f'<g transform="rotate({f2(angle)} {f2(cx)} {f2(cy)})">{el}</g>'


# ================================================================ rulings

WIDTH = 539


def four_lines(y0, b, bands=None, w=WIDTH):
    """A four-line writing system starting at y0 with band height b."""
    out = []
    if bands:
        for i, colour in enumerate(bands):
            if colour:
                out.append(rect(0, y0 + i * b, w, b, 0, None, 0, fill=colour))
    ys = [y0 + i * b for i in range(4)]
    for i, y in enumerate(ys):
        main = i in (1, 2)
        out.append(line(0, y, w, y, MAIN if main else HELP, 0.9 if main else 0.7, cap="butt"))
    return "".join(out)


def house(x, y0, b):
    """Roof in the ascender band, the house in the x-height band, the cellar
    in the descender band: a common aid for first writers."""
    return (poly([(x, y0 + b), (x + 8, y0 + 1.5), (x + 16, y0 + b)], MAIN, 0.8, fill=lib.NEW, fo=0.3) +
            rect(x + 1.5, y0 + b, 13, b, 0, MAIN, 0.8, fill="#ffffff") +
            rect(x + 1.5, y0 + 2 * b, 13, b - 1.5, 0, MAIN, 0.8, fill="#b9a58a", fo=0.35))


RULINGS = {
    # name: (tile height, body function)
    "elementary12": (44, lambda w=WIDTH: four_lines(7, 10, [None, MID_BAND, None], w)),
    "elementary12colored": (44, lambda w=WIDTH: four_lines(7, 10, ["#e0eef9", "#e5f2df", "#f8efd9"], w)),
    "elementary12house": (44, lambda w=WIDTH: four_lines(7, 10, [None, MID_BAND, None], w) + house(4, 7, 10)),
    "elementary34": (32, lambda w=WIDTH: four_lines(5.5, 7, [None, MID_BAND, None], w)),
    "music": (40, lambda w=WIDTH: "".join(line(0, 10 + 5 * i, w, 10 + 5 * i, MAIN, 0.8, cap="butt")
                                          for i in range(5))),
}

for _name, (_h, _fn) in RULINGS.items():
    PAPER[R + _name + ".svg"] = (lambda h=_h, fn=_fn: doc(WIDTH, h, fn()))


# ============================================================ thumbnails

TW, TH = 128, 96
GRID = "#9fb0bc"
GRID_LIGHT = "#d5dde3"


def thumb(body):
    return (doc(TW, TH, rect(0, 0, TW, TH, 0, None, 0, fill="#ffffff") + body), TW, TH)


def thumb_ruling(name, scale=0.55):
    h, fn = RULINGS[name]
    reps = int(TH / (h * scale)) + 2
    tile = fn(TW / scale)
    body = "".join(f'<g transform="translate(0 {f2(i * h)})">{tile}</g>' for i in range(reps))
    return thumb(f'<g transform="scale({scale})">{body}</g>')


def t_lined():
    return thumb("".join(line(12, y, 116, y, GRID, 1, cap="butt") for y in range(12, TH, 12)) +
                 line(12, 0, 12, TH, GRID, 1, cap="butt") + line(116, 0, 116, TH, GRID, 1, cap="butt"))


def grid_lines(step, colour, width, skip=None):
    out = []
    for i, x in enumerate(range(0, TW + 1, step)):
        if skip and i % skip == 0:
            continue
        out.append(line(x + 0.5, 0, x + 0.5, TH, colour, width, cap="butt"))
    for i, y in enumerate(range(0, TH + 1, step)):
        if skip and i % skip == 0:
            continue
        out.append(line(0, y + 0.5, TW, y + 0.5, colour, width, cap="butt"))
    return "".join(out)


def t_squared1():
    return thumb(grid_lines(4, GRID_LIGHT, 0.6, skip=5) + grid_lines(20, GRID, 1))


def t_squared5():
    return thumb(grid_lines(10, GRID, 1))


def t_dots():
    return thumb("".join(lib.disc(x, y, 1.3, "#7d8f9c") for x in range(8, TW, 12) for y in range(6, TH, 12)))


def t_isometric():
    out = []
    step = 14
    k = math.tan(math.radians(60))
    for i in range(-20, 30):
        y = i * step * math.sin(math.radians(60)) * 2 / 2
        out.append(line(0, y, TW, y, GRID, 0.9, cap="butt"))
    for i in range(-20, 30):
        x0 = i * step
        out.append(line(x0, 0, x0 + TH / k, TH, GRID, 0.9, cap="butt"))
        out.append(line(x0, 0, x0 - TH / k, TH, GRID, 0.9, cap="butt"))
    return thumb("".join(out))


def t_polar():
    cx, cy = TW / 2, TH / 2
    out = [lib.circ(cx, cy, r, GRID, 0.9) for r in range(12, 90, 12)]
    for a in range(0, 180, 30):
        dx, dy = math.cos(math.radians(a)) * 90, math.sin(math.radians(a)) * 90
        out.append(line(cx - dx, cy - dy, cx + dx, cy + dy, GRID, 0.9, cap="butt"))
    return thumb("".join(out))


THUMBS.update({
    "lined.png": t_lined,
    "squared1.png": t_squared1,
    "squared5.png": t_squared5,
    "dots.png": t_dots,
    "isometric.png": t_isometric,
    "polar.png": t_polar,
    "elementary12.png": lambda: thumb_ruling("elementary12"),
    "colored.png": lambda: thumb_ruling("elementary12colored"),
    "house.png": lambda: thumb_ruling("elementary12house"),
    "elementary34.png": lambda: thumb_ruling("elementary34", 0.7),
    "music.png": lambda: thumb_ruling("music", 0.6),
})

# ===================================================== measurement tools

PX_CM = 50


def num(n, x, y, h, colour=TEXT, font="bold"):
    return glyph(str(n), x, y, h, font, colour, ref="0")


def t_ruler():
    W, H, X0 = 1051, 110, 25
    out = [rect(0.75, 0.75, W - 1.5, H - 1.5, 6, EDGE, 1.5, fill=TINT, fo=0.88)]
    # centimetres on the top edge
    for i in range(0, 201):
        x = X0 + i * PX_CM / 10
        L = 22 if i % 10 == 0 else 15 if i % 5 == 0 else 9
        out.append(line(x, 0.75, x, L, TEXT, 1.3 if i % 10 == 0 else 1, cap="butt"))
        if i % 10 == 0:
            out.append(num(i // 10, x, 33, 11))
    out.append(glyph("cm", X0 + 20, 33, 7, "sans", "#5b6470", ref="c"))
    # inches on the bottom edge
    px_in = PX_CM * 2.54
    k = 0
    while X0 + k * px_in / 8 <= W - 20:
        x = X0 + k * px_in / 8
        L = 20 if k % 8 == 0 else 14 if k % 4 == 0 else 10 if k % 2 == 0 else 6
        out.append(line(x, H - 0.75, x, H - L, TEXT, 1.3 if k % 8 == 0 else 1, cap="butt"))
        if k % 8 == 0:
            out.append(num(k // 8, x, H - 31, 10))
        k += 1
    out.append(glyph("in", X0 + px_in / 2, H - 31, 7, "sans", "#5b6470", ref="i"))
    return doc(W, H, "".join(out))


def t_protractor():
    W, H = 560, 296
    cx, cy, Rr = 280, 278.86, 270
    out = [path(f"M10 {H - 0.75}V{f2(cy)}A{Rr} {Rr} 0 0 1 {W - 10} {f2(cy)}V{H - 0.75}Z",
                EDGE, 1.5, fill=TINT, fo=0.88)]
    for d in range(0, 181):
        a = math.radians(d)
        L = 22 if d % 10 == 0 else 14 if d % 5 == 0 else 8
        r0 = Rr - 1
        p = (cx + r0 * math.cos(a), cy - r0 * math.sin(a))
        q = (cx + (r0 - L) * math.cos(a), cy - (r0 - L) * math.sin(a))
        out.append(line(*p, *q, TEXT, 1.3 if d % 10 == 0 else 1, cap="butt"))
        if d % 10 == 0:
            for r_, val, h, col in ((Rr - 38, d, 11, TEXT), (Rr - 60, 180 - d, 9, "#5b6470")):
                x, y = cx + r_ * math.cos(a), cy - r_ * math.sin(a)
                out.append(rotated(num(val, x, y, h, col), 90 - d, x, y))
    out.append(path(lib.arc_d(cx, cy, Rr - 74, 0, 180), MAIN, 1))
    out.append(line(cx - (Rr - 74), cy, cx + (Rr - 74), cy, TEXT, 1, cap="butt"))
    out.append(line(cx, cy - 14, cx, cy + 10, TEXT, 1.2, cap="butt"))
    out.append(lib.circ(cx, cy, 3.5, TEXT, 1.2))
    return doc(W, H, "".join(out))


def t_triangle():
    W, H = 720, 360
    cx, cy = W / 2, H
    out = [poly([(0.75, H - 0.75), (W - 0.75, H - 0.75), (W / 2, 0.75)], EDGE, 1.5, fill=TINT,
                fo=0.88)]
    # millimetres on the hypotenuse, zero in the middle
    for i in range(-60, 61):
        x = cx + i * PX_CM / 10
        L = 20 if i % 10 == 0 else 13 if i % 5 == 0 else 8
        out.append(line(x, H - 0.75, x, H - L, TEXT, 1.3 if i % 10 == 0 else 1, cap="butt"))
        if i % 10 == 0 and i != 0:
            out.append(num(abs(i) // 10, x, H - 31, 10))
    # degrees around the centre of the hypotenuse
    r0 = 236
    # the scale stops short of the hypotenuse to leave room for its numbers
    for d in range(12, 169):
        a = math.radians(d)
        L = 18 if d % 10 == 0 else 12 if d % 5 == 0 else 6
        p = (cx + r0 * math.cos(a), cy - r0 * math.sin(a))
        q = (cx + (r0 - L) * math.cos(a), cy - (r0 - L) * math.sin(a))
        out.append(line(*p, *q, TEXT, 1.2 if d % 10 == 0 else 0.9, cap="butt"))
        if d % 10 == 0 and 20 <= d <= 160:
            for r_, val, h, col in ((r0 - 32, d, 10, TEXT), (r0 - 52, 180 - d, 8, "#5b6470")):
                x, y = cx + r_ * math.cos(a), cy - r_ * math.sin(a)
                out.append(rotated(num(val, x, y, h, col), 90 - d, x, y))
    out.append(path(lib.arc_d(cx, cy, r0 - 64, 20, 160), MAIN, 1))
    out.append(line(cx, cy - 1, cx, cy - 26, TEXT, 1.2, cap="butt"))
    out.append(path(lib.arc_d(cx, cy, 8, 0, 180), TEXT, 1.2))
    return doc(W, H, "".join(out))


PAPER[RP + "ruler.svg"] = t_ruler
PAPER[RP + "protractor.svg"] = t_protractor
PAPER[RP + "triangle_protractor.svg"] = t_triangle


# ================================================================ wordmark

LOGO = "icons/svg/web/header/ggb-logo-name.svg"


def _semibold():
    vf = os.environ.get("NOTO_SANS_VF")
    if not vf or not os.path.exists(vf):
        return None
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    out = os.path.join(tempfile.gettempdir(), "locus-noto-sans-semibold.ttf")
    if not os.path.exists(out):
        instancer.instantiateVariableFont(TTFont(vf), {"wght": 600, "wdth": 100}).save(out)
    return out


def logo_mark(cx, cy, r, sw):
    """Teal circle outline with an orange point on it: a point on its locus."""
    px, py = cx + r * math.cos(math.radians(40)), cy - r * math.sin(math.radians(40))
    return (lib.circ(cx, cy, r, lib.CUR, sw) + lib.disc(px, py, sw * 1.55, "#ffffff") +
            lib.disc(px, py, sw * 1.15, lib.NEW))


def t_logo():
    font = _semibold()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    target = os.path.join(root, "source/shared/common/src/main/resources/org/geogebra/common/", LOGO)
    if font is None:
        print("NOTO_SANS_VF not set: keeping", LOGO)
        with open(target) as f:
            return f.read()
    lib.FONTS["semibold"] = font
    W, H = 427, 120
    word = glyph("Locus", 118, 60, 58, "semibold", TEXT, anchor="start", ref="L")
    right = max(float(v) for v in re.findall(r"[ML](-?[\d.]+)", re.sub(r"[QC][^A-Za-z]*", "", word.split('d="')[1])))
    left = 60 - 36 - 4.5
    dx = (W - right - left) / 2 - left
    body = f'<g transform="translate({f2(dx)} 0)">{logo_mark(60, 60, 36, 9)}{word}</g>'
    return doc(W, H, body)


PAPER[LOGO] = t_logo

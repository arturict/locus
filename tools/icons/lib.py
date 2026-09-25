"""Drawing helpers for the Locus-original icons.

Icons are written as small Python functions that return SVG element strings
(strokes, circles, glyph outlines). `finish()` flattens every stroke into a
filled outline with picosvg, so that the finished file contains only filled
paths. That matters because the web client recolours icons by setting
`style="fill: <colour>"` on the root element (`SVGResource.withFill`): only
elements without their own fill attribute follow that colour. Parts drawn with
the `INK` sentinel lose their fill attribute and inherit the root colour; parts
drawn in an object colour (point blue, curve teal, accent orange) keep it.

Colours and grid rules come from docs/design.md.
Glyphs (letters, digits, math signs) are outlines taken from the Noto fonts
(SIL OFL 1.1), converted to paths; the SVG files contain no text or fonts.
"""
import math
import re

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from picosvg.svg import SVG

# Colour tokens (docs/design.md)
INK = "#010203"  # sentinel: becomes the inherited root fill
TOOL_INK = "#26303a"  # line, segment, ray, vector
UI_INK = "#5b6470"  # UI icons where the code does not recolour them
PT = "#1f4e9c"  # point
CUR = "#0e7c86"  # circle, conic, arc, curve
NEW = "#e8743b"  # object the tool creates
LABEL = "#5b6470"  # measurement text
WHITE = "#ffffff"
FILL_OP = 0.18

NOTO = "/usr/share/fonts/truetype/noto/"
FONTS = {
    "sans": NOTO + "NotoSans-Regular.ttf",
    "bold": NOTO + "NotoSans-Bold.ttf",
    "italic": NOTO + "NotoSerif-BoldItalic.ttf",
    "math": NOTO + "NotoSansMath-Regular.ttf",
    "serif": NOTO + "NotoSerif-Regular.ttf",
}
_font_cache = {}


def f2(v):
    """Format a number compactly."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _paint(c, w, fill, fo, dash, cap="round", join="round", op=None):
    a = []
    if fill is None or fill == "none":
        a.append('fill="none"')
    else:
        a.append(f'fill="{fill}"')
        if fo is not None:
            a.append(f'fill-opacity="{f2(fo)}"')
    if c and w:
        a.append(f'stroke="{c}" stroke-width="{f2(w)}" '
                 f'stroke-linecap="{cap}" stroke-linejoin="{join}"')
        if dash:
            a.append(f'stroke-dasharray="{" ".join(f2(d) for d in dash)}"')
    if op is not None:
        a.append(f'opacity="{f2(op)}"')
    return " ".join(a)


def line(x1, y1, x2, y2, c=INK, w=2, dash=None, cap="round", op=None):
    return (f'<path d="M{f2(x1)} {f2(y1)}L{f2(x2)} {f2(y2)}" '
            f'{_paint(c, w, None, None, dash, cap=cap, op=op)}/>')


def pl(pts, c=INK, w=2, close=False, fill=None, fo=None, dash=None, join="round",
       cap="round", op=None):
    d = "M" + "L".join(f"{f2(x)} {f2(y)}" for x, y in pts) + ("Z" if close else "")
    return f'<path d="{d}" {_paint(c, w, fill, fo, dash, cap=cap, join=join, op=op)}/>'


def poly(pts, c=INK, w=2, fill=None, fo=None, dash=None, join="round", op=None):
    return pl(pts, c, w, True, fill, fo, dash, join, op=op)


def path(d, c=INK, w=2, fill=None, fo=None, dash=None, cap="round", join="round",
         op=None, rule=None):
    extra = f' fill-rule="{rule}"' if rule else ""
    return f'<path d="{d}" {_paint(c, w, fill, fo, dash, cap, join, op)}{extra}/>'


def circ(cx, cy, r, c=INK, w=2, fill=None, fo=None, dash=None, op=None):
    return (f'<circle cx="{f2(cx)}" cy="{f2(cy)}" r="{f2(r)}" '
            f'{_paint(c, w, fill, fo, dash, op=op)}/>')


def disc(cx, cy, r, fill=INK, fo=None, op=None):
    return circ(cx, cy, r, None, 0, fill, fo, op=op)


def ell(cx, cy, rx, ry, rot=0, c=INK, w=2, fill=None, fo=None, dash=None, op=None):
    tr = f' transform="rotate({f2(rot)} {f2(cx)} {f2(cy)})"' if rot else ""
    return (f'<ellipse cx="{f2(cx)}" cy="{f2(cy)}" rx="{f2(rx)}" ry="{f2(ry)}"{tr} '
            f'{_paint(c, w, fill, fo, dash, op=op)}/>')


def rect(x, y, w_, h, rx=0, c=INK, w=2, fill=None, fo=None, dash=None, op=None):
    r = f' rx="{f2(rx)}"' if rx else ""
    return (f'<rect x="{f2(x)}" y="{f2(y)}" width="{f2(w_)}" height="{f2(h)}"{r} '
            f'{_paint(c, w, fill, fo, dash, join="round", op=op)}/>')


def box(x, y, w_, h, rx=0, fill=INK, fo=None, op=None):
    return rect(x, y, w_, h, rx, None, 0, fill, fo, op=op)


def pt(x, y, c=PT, r=3, halo=1):
    """A point: filled circle with a white outline (docs/design.md)."""
    out = []
    if halo:
        out.append(disc(x, y, r + halo, WHITE))
    out.append(disc(x, y, r, c))
    return "".join(out)


def newpt(x, y, r=3):
    return pt(x, y, NEW, r)


def polar(cx, cy, r, deg):
    """Point on a circle; degrees counter-clockwise, y axis pointing up."""
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def arc_d(cx, cy, r, a0, a1, ry=None, move=True):
    """SVG path data for an arc from a0 to a1 (degrees, counter-clockwise)."""
    ry = r if ry is None else ry
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy - ry * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy - ry * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) % 360 > 180 else 0
    sweep = 0 if a1 > a0 else 1
    start = f"M{f2(x0)} {f2(y0)}" if move else f"L{f2(x0)} {f2(y0)}"
    return f"{start}A{f2(r)} {f2(ry)} 0 {large} {sweep} {f2(x1)} {f2(y1)}"


def arc(cx, cy, r, a0, a1, c=INK, w=2, dash=None, ry=None, op=None):
    return path(arc_d(cx, cy, r, a0, a1, ry), c, w, dash=dash, op=op)


def sector(cx, cy, r, a0, a1, c=INK, w=2, fill=None, fo=None):
    d = f"M{f2(cx)} {f2(cy)}" + arc_d(cx, cy, r, a0, a1, move=False)[0:] + "Z"
    return path(d, c, w, fill, fo)


def head(x, y, ang, size=6, c=INK, width=None, filled=True, w=2):
    """Arrow head with its tip at (x, y) pointing in direction ang (degrees,
    counter-clockwise, y up)."""
    width = size * 0.9 if width is None else width
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    bx, by = x - ux * size, y - uy * size
    p1 = (bx + px * width / 2, by + py * width / 2)
    p2 = (bx - px * width / 2, by - py * width / 2)
    if filled:
        return poly([(x, y), p1, p2], c, 1, fill=c)
    return pl([p1, (x, y), p2], c, w)


def arrow(x1, y1, x2, y2, c=INK, w=2, size=6, dash=None, filled=True, both=False):
    """Line with an arrow head at (x2, y2); the shaft stops inside the head."""
    ang = math.degrees(math.atan2(-(y2 - y1), x2 - x1))
    L = math.hypot(x2 - x1, y2 - y1)
    k = (L - size * 0.6) / L if filled else 1
    sx, sy = x1 + (x2 - x1) * k, y1 + (y2 - y1) * k
    out = []
    if both:
        k0 = size * 0.6 / L if filled else 0
        x1b, y1b = x1 + (x2 - x1) * k0, y1 + (y2 - y1) * k0
        out.append(line(x1b, y1b, sx, sy, c, w, dash))
        out.append(head(x1, y1, ang + 180, size, c, filled=filled, w=w))
    else:
        out.append(line(x1, y1, sx, sy, c, w, dash))
    out.append(head(x2, y2, ang, size, c, filled=filled, w=w))
    return "".join(out)


def arc_arrow(cx, cy, r, a0, a1, c=INK, w=2, size=5):
    """Arc from a0 to a1 with a head at a1."""
    x1, y1 = polar(cx, cy, r, a1)
    tang = a1 + (90 if a1 > a0 else -90)
    # shorten the arc a little so the head covers the end
    back = math.degrees(size * 0.6 / r) * (1 if a1 > a0 else -1)
    return arc(cx, cy, r, a0, a1 - back, c, w) + head(x1, y1, tang, size, c)


def right_angle(x, y, ang, size=5, c=INK, w=1.5):
    """Right-angle mark at vertex (x, y); ang is the direction of the first
    arm, the second arm is at ang + 90 degrees."""
    a = math.radians(ang)
    u = (math.cos(a), -math.sin(a))
    v = (math.cos(a + math.pi / 2), -math.sin(a + math.pi / 2))
    p1 = (x + u[0] * size, y + u[1] * size)
    p2 = (x + (u[0] + v[0]) * size, y + (u[1] + v[1]) * size)
    p3 = (x + v[0] * size, y + v[1] * size)
    return pl([p1, p2, p3], c, w)


def tick(x, y, ang, length=5, c=INK, w=1.5):
    """Short tick mark across a line at (x, y); ang is the line direction."""
    a = math.radians(ang + 90)
    dx, dy = math.cos(a) * length / 2, -math.sin(a) * length / 2
    return line(x - dx, y - dy, x + dx, y + dy, c, w)


def lerp(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


# ---------------------------------------------------------------- glyphs


def _font(name):
    if name not in _font_cache:
        f = TTFont(FONTS[name])
        _font_cache[name] = (f, f.getGlyphSet(), f.getBestCmap())
    return _font_cache[name]


def glyph(text, cx, cy, h, font="sans", c=INK, fo=None, anchor="middle", maxw=None,
          ref=None, op=None):
    """Glyph outlines of `text`, scaled so that the ink height equals h (or the
    height of `ref` when given, which keeps a baseline across strings) and
    centred on (cx, cy). anchor may be 'start' or 'end' (cx is then the left or
    right edge)."""
    f, gs, cmap = _font(font)
    names = [cmap[ord(ch)] for ch in text]
    # measure
    def measure(nms):
        bp = BoundsPen(gs)
        x = 0
        for n in nms:
            tp = TransformPen(bp, (1, 0, 0, 1, x, 0))
            gs[n].draw(tp)
            x += gs[n].width
        return bp.bounds

    xmin, ymin, xmax, ymax = measure(names)
    if ref:
        rb = measure([cmap[ord(ch)] for ch in ref])
        ymin, ymax = rb[1], rb[3]
    s = h / (ymax - ymin)
    if maxw and (xmax - xmin) * s > maxw:
        s = maxw / (xmax - xmin)
    wd = (xmax - xmin) * s
    if anchor == "middle":
        left = cx - wd / 2
    elif anchor == "start":
        left = cx
    else:
        left = cx - wd
    ox = left - xmin * s
    oy = cy + (ymin + ymax) / 2 * s
    pen = SVGPathPen(gs, ntos=lambda v: f2(v))
    x = 0
    for n in names:
        tp = TransformPen(pen, (s, 0, 0, -s, ox + x * s, oy))
        gs[n].draw(tp)
        x += gs[n].width
    d = pen.getCommands()
    return path(d, None, 0, fill=c, fo=fo, op=op)


# ---------------------------------------------------------------- output


def svg_doc(body, size, root_fill):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}">{body}</svg>')


def finish(body, size=32, root_fill=TOOL_INK, flatten=True):
    """Return the final SVG text for an icon body."""
    raw = svg_doc(body, size, root_fill)
    if not flatten:
        return raw.replace("<svg ", f'<svg fill="{root_fill}" ', 1).replace(INK, root_fill) + "\n"
    pico = SVG.fromstring(raw).topicosvg(ndigits=2)
    out = pico.tostring()
    out = re.sub(r"<defs\s*/>", "", out)
    out = out.replace(f' fill="{INK}"', "")
    out = re.sub(r">\s+<", "><", out)
    # one root element: xmlns, size, viewBox and the inherited ink colour
    out = re.sub(
        r"<svg[^>]*>",
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" fill="{root_fill}">',
        out,
        count=1,
    )
    # shorter path data: drop spaces after commands and the redundant commas
    out = re.sub(r"(\d) ([A-Za-z])", r"\1\2", out)
    out = re.sub(r"([A-Za-z]) (-?\d)", r"\1\2", out)
    assert INK not in out, "unresolved ink colour"
    return out.strip() + "\n"

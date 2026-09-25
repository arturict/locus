"""Locus tool icons on a 32 x 32 grid (docs/design.md, section Icons).

Visual grammar
- Given objects: lines in ink (inherits the root colour, so a selected tool
  tints them), circles and curves in teal, points blue with a white outline.
- The object the tool creates is orange, its fill orange at 18 %.
- Measurement labels are grey.
- Icons that the Notes toolbox shows (`MONO`) are monochrome: every part
  inherits the root colour, because `IconButton` recolours them black or with
  the selection colour. Secondary areas use a lower fill opacity.
"""
import math

from lib import (CUR, FILL_OP, INK, LABEL, NEW, PT, WHITE, arc, arc_arrow, arc_d, arrow,
                 box, circ, disc, ell, glyph, head, lerp, line, newpt, path, pl, polar,
                 poly, pt, rect, right_angle, sector, tick)

TOOLS = {}
MONO = set()


def tool(name, mono=False):
    def deco(fn):
        TOOLS[name] = fn
        if mono:
            MONO.add(name)
        return fn
    return deco


def alias(name, target, mono=False):
    TOOLS[name] = lambda: TOOLS[target]()
    if mono:
        MONO.add(name)


# ------------------------------------------------------------------ helpers


def pointer(x, y, s=1.0, c=INK):
    """Mouse pointer with its tip at (x, y)."""
    pts = [(0, 0), (0, 17), (4.2, 13.2), (7.2, 19.6), (10, 18.4), (7, 12), (12.4, 12)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    return poly(pts, WHITE, 3, fill=WHITE) + poly(pts, c, 1.2, fill=c)


def fcurve(f, x0, x1, n=48):
    return [(x0 + (x1 - x0) * i / n, f(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def ellipse_pts(cx, cy, rx, ry, rot=0, t0=0, t1=360, n=72):
    r = math.radians(rot)
    out = []
    for i in range(n + 1):
        t = math.radians(t0 + (t1 - t0) * i / n)
        x, y = rx * math.cos(t), -ry * math.sin(t)
        out.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return out


def ept(cx, cy, rx, ry, t, rot=0):
    return ellipse_pts(cx, cy, rx, ry, rot, t, t, 1)[0]


def rot_pts(pts, cx, cy, deg):
    a = math.radians(-deg)
    return [(cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a),
             cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a)) for x, y in pts]


def shape(pts, new=True, fill=True):
    """Polygon: created (orange) or given (ink with teal fill)."""
    if new:
        return poly(pts, NEW, 2, fill=NEW if fill else None, fo=FILL_OP)
    return poly(pts, INK, 2, fill=CUR if fill else None, fo=FILL_OP)


def cells(x=3, y=4, rows=4, w=9, h=6):
    """A spreadsheet column: the input of the spreadsheet tools."""
    out = [rect(x, y, w, h * rows, 1.5, INK, 1.5)]
    for i in range(1, rows):
        out.append(line(x, y + h * i, x + w, y + h * i, INK, 1.5))
    for i in range(rows):
        out.append(box(x + 2.2, y + h * i + h / 2 - 0.75, w - 4.4, 1.5, 0.75, INK, op=0.45))
    return "".join(out)


def eye(cx, cy, w, h, c=INK, sw=2):
    d = (f"M{cx - w / 2} {cy}Q{cx} {cy - h} {cx + w / 2} {cy}"
         f"Q{cx} {cy + h} {cx - w / 2} {cy}Z")
    return path(d, c, sw)


def slash(x1, y1, x2, y2, c=NEW):
    return line(x1, y1, x2, y2, WHITE, 5) + line(x1, y1, x2, y2, c, 2.2)


def magnifier(cx, cy, r, c=INK, handle=8):
    a = math.radians(-45)
    hx, hy = cx + r * math.cos(a), cy - r * math.sin(a)
    ex, ey = hx + handle * math.cos(a), hy - handle * math.sin(a)
    return circ(cx, cy, r, c, 2.2) + line(hx + 1, hy + 1, ex, ey, c, 3.4)


def plane(pts, new=False, dash=None):
    c = NEW if new else INK
    f = NEW if new else CUR
    return poly(pts, c, 1.6 if not new else 2, fill=f, fo=FILL_OP if not new else 0.22,
                dash=dash)


# ================================================================== general


@tool("mode_move")
def _():
    return pointer(10, 4, 1.25)


@tool("mode_select")
def _():
    return rect(3, 3, 20, 16, 2, INK, 1.6, dash=(2.6, 2.6)) + pointer(16, 12, 0.95)


@tool("mode_movegraphicsview")
def _():
    out = [line(16, 8, 16, 24), line(8, 16, 24, 16)]
    for x, y, a in ((16, 3, 90), (16, 29, 270), (3, 16, 180), (29, 16, 0)):
        out.append(head(x, y, a, 6.5, INK, width=7.5))
    out.append(disc(16, 16, 2.6, INK))
    return "".join(out)


@tool("mode_zoomin")
def _():
    return (magnifier(13, 13, 8.5) + line(9, 13, 17, 13, NEW, 2.4) +
            line(13, 9, 13, 17, NEW, 2.4))


@tool("mode_zoomout")
def _():
    return magnifier(13, 13, 8.5) + line(9, 13, 17, 13, NEW, 2.4)


@tool("mode_delete")
def _():
    return (circ(13, 15, 9, CUR) + pt(13, 15) + line(19, 19, 28, 28, NEW, 2.6) +
            line(28, 19, 19, 28, NEW, 2.6))


@tool("mode_eraser", mono=True)
def _():
    body = [(4.5, 19.5), (17, 7), (26.5, 16.5), (14, 29)]
    tip = [(4.5, 19.5), (10, 14), (19.5, 23.5), (14, 29)]
    return (poly(tip, None, 0, fill=INK, fo=0.35) + poly(body, INK, 2) +
            line(10, 14, 19.5, 23.5) + line(18, 29, 28, 29))


@tool("mode_showhideobject")
def _():
    return (eye(16, 16, 26, 13) + circ(16, 16, 4.2, CUR, 2, fill=CUR, fo=0.35) +
            slash(6, 27, 26, 5))


@tool("mode_showhidelabel")
def _():
    return (pt(8, 25) + glyph("A", 19, 12, 13, "bold", INK) + slash(12, 21, 27, 4))


@tool("mode_checkbox")
def _():
    return (rect(3, 9, 14, 14, 3, INK, 2) + pl([(6.5, 16), (9.5, 19), (14, 12.5)], NEW, 2.4) +
            circ(25, 16, 4.5, CUR, 2, fill=CUR, fo=FILL_OP))


@tool("mode_copyvisualstyle")
def _():
    return (rect(4, 4, 19, 8, 2.5, INK, 2, fill=NEW, fo=0.9) +
            pl([(23, 8), (27, 8), (27, 15), (15.5, 15), (15.5, 19)]) +
            rect(13.5, 19, 4, 10, 1.5, INK, 1.2, fill=INK))


@tool("mode_movearoundpoint")
def _():
    return (line(10, 22, 27, 22) + pt(27, 22) + arc_arrow(10, 22, 13, 8, 85, NEW, 2.2, 6) +
            pt(10, 22))


@tool("mode_attachdetachpoint")
def _():
    return (line(3, 26, 29, 26) + pt(9, 26) + arrow(21, 10.5, 21, 22, INK, 1.8, 4.5, both=True) +
            newpt(21, 5))


@tool("mode_rotateview")
def _():
    o = (13, 19)
    return line(*o, 13, 4) + line(*o, 28, 19) + line(*o, 4, 27) + _rot_arrow(13, 9.5)


def _rot_arrow(cx, cy, rx=9.5, ry=3.6, c=NEW):
    pts = ellipse_pts(cx, cy, rx, ry, 0, 200, 330, 30)
    end = pts[-1]
    prev = pts[-3]
    ang = math.degrees(math.atan2(-(end[1] - prev[1]), end[0] - prev[0]))
    return pl(pts[:-2], c, 2.2) + head(end[0], end[1], ang, 5.5, c)


@tool("mode_viewinfrontof")
def _():
    return (plane([(4, 9), (13, 4), (13, 23), (4, 28)]) +
            eye(24, 16, 11, 7, INK, 1.8) + disc(24, 16, 1.8, INK) +
            arrow(18, 16, 11, 16, NEW, 2.2, 5.5))


@tool("mode_tool")
def _():
    return (rect(3.5, 12, 25, 15, 2.5) + pl([(11.5, 12), (11.5, 7.5), (20.5, 7.5), (20.5, 12)]) +
            line(3.5, 18.5, 28.5, 18.5) + box(13.5, 16, 5, 5, 1.2, NEW))


# =================================================================== points


@tool("mode_point")
def _():
    return pt(13, 19, NEW, 4) + glyph("A", 23, 9.5, 8.5, "bold", LABEL)


@tool("mode_pointonobject")
def _():
    x, y = polar(16, 16, 11, 40)
    return circ(16, 16, 11, CUR) + newpt(x, y)


@tool("mode_intersect")
def _():
    cx, cy, r = 17, 15, 9.5
    p, q = (3, 27), (29, 13)
    # line-circle intersection
    dx, dy = q[0] - p[0], q[1] - p[1]
    fx, fy = p[0] - cx, p[1] - cy
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - r * r
    disc_ = math.sqrt(b * b - 4 * a * c)
    ts = [(-b - disc_) / (2 * a), (-b + disc_) / (2 * a)]
    out = [circ(cx, cy, r, CUR), line(*p, *q)]
    for t in ts:
        out.append(newpt(p[0] + dx * t, p[1] + dy * t))
    return "".join(out)


@tool("mode_midpoint")
def _():
    a, b = (5, 24), (27, 8)
    ang = math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))
    m = lerp(a, b, 0.5)
    return (line(*a, *b) + tick(*lerp(a, b, 0.25), ang, 6) + tick(*lerp(a, b, 0.75), ang, 6) +
            pt(*a) + pt(*b) + newpt(*m))


@tool("mode_complexnumber")
def _():
    return (line(3, 23, 29, 23, INK, 1.6) + line(8, 29, 8, 3, INK, 1.6) +
            line(20, 11, 20, 23, LABEL, 1.4, dash=(2, 2)) +
            line(8, 11, 20, 11, LABEL, 1.4, dash=(2, 2)) +
            newpt(20, 11) + glyph("i", 4, 6, 7.5, "italic", LABEL) +
            glyph("z", 26, 5.5, 5.5, "italic", LABEL))


@tool("mode_extremum")
def _():
    d = "M3 27C6 15 8 8 11 8C15 8 17 22 22 22C26 22 28 15 29.5 10"
    return path(d, CUR) + newpt(11, 8) + newpt(22, 22)


@tool("mode_roots")
def _():
    f = lambda x: 17 - 0.025 * (x - 6) * (x - 16) * (x - 26)
    return (line(2, 17, 30, 17, INK, 1.6) + pl(fcurve(f, 4.3, 27.7), CUR) +
            newpt(6, 17) + newpt(16, 17) + newpt(26, 17))


# ==================================================================== lines


@tool("mode_join")
def _():
    a, b = (2, 25), (30, 7)
    return line(*a, *b, NEW) + pt(*lerp(a, b, 0.27)) + pt(*lerp(a, b, 0.7))


@tool("mode_segment")
def _():
    return line(6, 25, 26, 7, NEW) + pt(6, 25) + pt(26, 7)


@tool("mode_segmentfixed")
def _():
    return (line(5, 23, 27, 23, NEW) + pt(5, 23) + pt(27, 23, NEW) +
            arrow(12.5, 12, 5, 12, LABEL, 1.5, 4.5) + arrow(19.5, 12, 27, 12, LABEL, 1.5, 4.5) +
            glyph("3", 16, 12, 7.5, "bold", LABEL))


@tool("mode_ray")
def _():
    return line(5, 26, 30, 5, NEW) + pt(5, 26) + pt(*lerp((5, 26), (30, 5), 0.42))


@tool("mode_polyline")
def _():
    pts = [(4, 24), (11, 8), (20, 21), (28, 7)]
    return pl(pts, NEW) + "".join(pt(*p) for p in pts)


@tool("mode_vector")
def _():
    return arrow(6, 25, 27, 7, NEW, 2.2, 7.5) + pt(6, 25)


@tool("mode_vectorfrompoint")
def _():
    return (arrow(4, 16, 17, 5, INK, 2, 6.5) + arrow(13, 27, 27, 15, NEW, 2.2, 7) + pt(13, 27))


@tool("mode_perpendicularline")
def _():
    return (line(3, 22, 29, 22) + line(16, 3, 16, 29, NEW) + right_angle(17, 21, 0, 5.5, INK, 1.5) +
            pt(16, 9))


@tool("mode_parallelline")
def _():
    k = 10 / 26
    return (line(3, 27, 29, 17) + line(3, 11 + 11 * k, 29, 11 - 15 * k, NEW) + pt(14, 11))


@tool("mode_perpendicularbisector")
def _():
    return (line(5, 21, 27, 21) + tick(10.5, 21, 0, 6) + tick(21.5, 21, 0, 6) +
            line(16, 3, 16, 29, NEW) + pt(5, 21) + pt(27, 21))


@tool("mode_anglebisector")
def _():
    v = (5, 26)
    a2 = math.degrees(math.atan2(21, 16))
    e1 = (29, 26)
    e2 = polar(*v, 26, a2)
    b = polar(*v, 26, a2 / 2)
    return (line(*v, *e1) + line(*v, *e2) + line(*v, *b, NEW) + arc(*v, 10, 4, a2 / 2 - 4, LABEL, 1.4) +
            arc(*v, 10, a2 / 2 + 4, a2 - 4, LABEL, 1.4) + pt(*v))


@tool("mode_tangents")
def _():
    P = (4, 9)
    C, r = (20, 20), 8
    d = math.hypot(C[0] - P[0], C[1] - P[1])
    base = math.atan2(C[1] - P[1], C[0] - P[0])
    off = math.asin(r / d)
    out = [circ(*C, r, CUR)]
    L = math.sqrt(d * d - r * r) + 6
    for s in (-1, 1):
        a = base + s * off
        out.append(line(*P, P[0] + L * math.cos(a), P[1] + L * math.sin(a), NEW))
    out.append(pt(*P))
    return "".join(out)


@tool("mode_polardiameter")
def _():
    return circ(16, 20, 9, CUR) + line(2, 20 - 81 / 15, 30, 20 - 81 / 15, NEW) + pt(16, 5)


@tool("mode_fitline")
def _():
    pts = [(5, 25), (10, 19), (14.5, 21), (19, 13), (23.5, 13), (27, 7)]
    return line(3, 27, 29.5, 6, NEW) + "".join(pt(x, y, PT, 2.2) for x, y in pts)


@tool("mode_locus")
def _():
    # the midpoint of a fixed point A and a point P moving on a circle moves on a
    # smaller circle: the locus
    c, r, a = (11, 19), 8, (28, 6)
    p = polar(*c, r, 150)
    m = lerp(p, a, 0.5)
    lc = lerp(c, a, 0.5)
    return (circ(*c, r, CUR) + circ(*lc, r / 2, NEW, 2.2) + line(*p, *a, INK, 1.6) + pt(*p, PT, 2.6) +
            pt(*a, PT, 2.6) + newpt(*m, 2.6))


# ================================================================= polygons


@tool("mode_polygon")
def _():
    pts = [(5, 24), (11, 6), (27, 10), (24, 26)]
    return shape(pts) + "".join(pt(*p) for p in pts)


@tool("mode_regularpolygon")
def _():
    pts = [polar(16, 15.5, 12.5, 270 - 30 + 60 * i) for i in range(6)]
    return shape(pts) + pt(*pts[0]) + pt(*pts[1])


@tool("mode_rigidpolygon")
def _():
    pts = [(4, 22), (10, 5), (25, 10)]
    lock = (rect(20, 21, 9, 7.5, 1.5, INK, 0, fill=INK) +
            path("M22 21V18.5A2.5 2.5 0 0 1 27 18.5V21", INK, 1.8))
    return shape(pts) + "".join(pt(*p) for p in pts) + lock


@tool("mode_vectorpolygon")
def _():
    a = (5, 25)
    b, c = (26, 20), (14, 6)
    return (shape([a, b, c]) + arrow(*a, *lerp(a, b, 0.93), INK, 1.6, 5) +
            arrow(*a, *lerp(a, c, 0.9), INK, 1.6, 5) + pt(*a))


# ================================================================== circles


@tool("mode_circle2")
def _():
    c = (15, 16)
    return circ(*c, 11.5, NEW) + pt(*c) + pt(*polar(*c, 11.5, 40))


@tool("mode_circle3")
def _():
    c = (16, 16)
    return circ(*c, 12, NEW) + "".join(pt(*polar(*c, 12, a)) for a in (150, 20, 260))


@tool("mode_circlepointradius")
def _():
    c = (15, 17)
    e = polar(*c, 12, 25)
    return (circ(*c, 12, NEW) + line(*c, *e, INK, 1.6) + pt(*c) +
            glyph("r", 21, 13.5, 5.5, "italic", LABEL))


@tool("mode_compass")
def _():
    return (line(4, 5, 15, 5) + pt(4, 5) + pt(15, 5) + circ(19, 20, 10, NEW) + pt(19, 20) +
            line(19, 20, 29, 20, INK, 1.4, dash=(2, 2)))


@tool("mode_semicircle")
def _():
    return (line(4, 22, 28, 22, INK, 1.4, dash=(2, 2.5)) + arc(16, 22, 12, 0, 180, NEW) + pt(4, 22) +
            pt(28, 22))


@tool("mode_circulararc")
def _():
    c = (7, 25)
    return (line(*c, *polar(*c, 20, 5), INK, 1.4, dash=(2, 2)) +
            line(*c, *polar(*c, 20, 80), INK, 1.4, dash=(2, 2)) + arc(*c, 20, 5, 80, NEW) +
            pt(*c) + pt(*polar(*c, 20, 5)) + pt(*polar(*c, 14, 80), PT, 2.6))


@tool("mode_circumcirculararc")
def _():
    c = (16, 25)
    return arc(*c, 12.5, 12, 168, NEW) + "".join(pt(*polar(*c, 12.5, a)) for a in (12, 90, 168))


@tool("mode_circularsector")
def _():
    c = (7, 25)
    return (sector(*c, 20, 5, 80, NEW, 2, fill=NEW, fo=FILL_OP) + pt(*c) +
            pt(*polar(*c, 20, 5)))


@tool("mode_circumcircularsector")
def _():
    c = (16, 26)
    return (sector(*c, 13, 20, 160, NEW, 2, fill=NEW, fo=FILL_OP) +
            "".join(pt(*polar(*c, 13, a)) for a in (20, 90, 160)))


# =================================================================== conics


@tool("mode_ellipse")
def _():
    cx, cy, a, b = 16, 16, 13, 8
    c = math.sqrt(a * a - b * b)
    return (ell(cx, cy, a, b, 0, NEW) + pt(cx - c, cy) + pt(cx + c, cy) +
            pt(*ept(cx, cy, a, b, 60)))


@tool("mode_hyperbola")
def _():
    cx, cy, a, b = 16, 16, 4, 4.4
    out = []
    for s in (-1, 1):
        pts = [(cx + s * a * math.cosh(t / 10), cy + b * math.sinh(t / 10)) for t in range(-19, 20)]
        out.append(pl(pts, NEW))
    c = math.sqrt(a * a + b * b)
    out += [pt(cx - c - 1, cy), pt(cx + c + 1, cy)]
    return "".join(out)


@tool("mode_parabola")
def _():
    f = lambda x: 20 - (x - 16) ** 2 / 12
    return line(3, 27, 29, 27) + pl(fcurve(f, 4, 28), NEW) + pt(16, 14)


@tool("mode_conic5")
def _():
    out = [ell(16, 16, 13, 8.5, -25, NEW)]
    for t in (20, 95, 160, 215, 290):
        out.append(pt(*ept(16, 16, 13, 8.5, t, -25)))
    return "".join(out)


# ============================================================== measurement


@tool("mode_angle")
def _():
    v = (5, 26)
    a = 55
    return (sector(*v, 11, 0, a, NEW, 2, fill=NEW, fo=0.25) + line(*v, 29, 26) +
            line(*v, *polar(*v, 23, a)) + glyph("α", *polar(*v, 17, a / 2), 6, "italic", LABEL) +
            pt(*v))


@tool("mode_anglefixed")
def _():
    v = (5, 26)
    return (line(*v, 29, 26) + line(*v, *polar(*v, 24, 60), NEW) +
            arc_arrow(*v, 13, 3, 57, NEW, 2, 5.5) + pt(*v) + pt(22, 26))


@tool("mode_distance")
def _():
    return (line(5, 24, 27, 24) + pt(5, 24) + pt(27, 24) +
            arrow(5, 15, 27, 15, NEW, 1.8, 5, both=True) + line(5, 12, 5, 18, NEW, 1.5) +
            line(27, 12, 27, 18, NEW, 1.5) + glyph("4.2", 16, 6.5, 6.5, "bold", LABEL))


@tool("mode_area")
def _():
    pts = [(4, 25), (9, 6), (27, 9), (26, 27)]
    return (poly(pts, INK, 2, fill=NEW, fo=0.28) + glyph("A", 16.5, 16.5, 9, "italic", LABEL))


@tool("mode_slope")
def _():
    k = 22 / 26
    y = lambda x: 28 - (x - 3) * k
    tri = [(9, y(9)), (21, y(9)), (21, y(21))]
    return (poly(tri, NEW, 2, fill=NEW, fo=0.22) + line(3, 28, 29, 6) +
            glyph("m", 25.5, (y(9) + y(21)) / 2 + 1, 5, "italic", LABEL))


@tool("mode_volume")
def _():
    return (_cube(4, 11, 15, 7, -6, fill=NEW, fo=0.25, edge=INK, hidden=False) +
            glyph("V", 11.5, 18.5, 8, "italic", LABEL))


@tool("mode_relation")
def _():
    return (line(4, 26, 10, 6) + line(22, 26, 28, 6) + line(12, 14, 20, 14, NEW, 2.4) +
            line(12, 19, 20, 19, NEW, 2.4) + glyph("?", 16, 7, 6.5, "bold", LABEL))


@tool("mode_functioninspector")
def _():
    d = "M2 25C8 25 9 8 15 8S21 20 30 14"
    return (line(2, 28, 30, 28, INK, 1.4) + path(d, CUR) + pt(15, 8, PT, 2.6) +
            circ(15, 8, 5.5, NEW, 2) + line(19, 12, 24, 17, NEW, 3))


# =========================================================== transformations


@tool("mode_reflectaboutline")
def _():
    a = [(4, 25), (13, 25), (10, 8)]
    b = [(32 - x, y) for x, y in a]
    return (shape(a, new=False) + shape(b) + line(16, 2, 16, 30, INK, 1.6, dash=(3, 2.5)))


@tool("mode_reflectaboutpoint")
def _():
    a = [(4, 5), (13, 6), (6, 13)]
    b = [(32 - x, 32 - y) for x, y in a]
    return (line(6, 13, 26, 19, LABEL, 1.3, dash=(2, 2)) + shape(a, new=False) + shape(b) +
            pt(16, 16))


@tool("mode_reflectaboutcircle")
def _():
    c, r = (11, 20), 8
    p1 = polar(*c, 4.5, 35)
    p2 = polar(*c, r * r / 4.5, 35)
    return (circ(*c, r, CUR) + line(*c, *p2, LABEL, 1.3, dash=(2, 2)) + disc(*c, 1.4, INK) +
            pt(*p1) + newpt(*p2))


@tool("mode_rotatearoundpoint")
def _():
    c = (7, 25)
    a = [(12, 25), (23, 25), (20, 18)]
    b = rot_pts(a, *c, 70)
    return (shape(a, new=False) + shape(b) + arc_arrow(*c, 19, 12, 55, LABEL, 1.5, 4.5) + pt(*c))


@tool("mode_translatebyvector")
def _():
    a = [(3, 28), (11, 28), (6, 20)]
    v = (15, -12)
    b = [(x + v[0], y + v[1]) for x, y in a]
    return (shape(a, new=False) + shape(b) + arrow(14, 29, 14 + v[0], 29 + v[1], INK, 1.8, 5.5))


@tool("mode_dilatefrompoint")
def _():
    c = (4, 28)
    a = [(9, 24), (15, 24), (13, 17)]
    b = [(c[0] + (x - c[0]) * 2.2, c[1] + (y - c[1]) * 2.2) for x, y in a]
    return ("".join(line(*c, *p, LABEL, 1.2, dash=(1.8, 1.8)) for p in b) + shape(b) +
            shape(a, new=False) + pt(*c))


@tool("mode_reflectaboutplane")
def _():
    a = [(3, 23), (9, 26), (8, 13)]
    b = [(32 - x, y) for x, y in a]
    return (plane([(12, 8), (20, 3), (20, 24), (12, 29)]) + shape(a, new=False) + shape(b))


@tool("mode_rotatearoundline")
def _():
    pts = ellipse_pts(16, 18, 11, 4.2, 0, 190, 350, 30)
    end, prev = pts[-1], pts[-3]
    ang = math.degrees(math.atan2(-(end[1] - prev[1]), end[0] - prev[0]))
    return (line(16, 2, 16, 30) + pl(pts[:-2], NEW, 2.2) + head(*end, ang, 5.5, NEW) +
            pt(5.2, 17) + newpt(25, 11))


# =========================================================== special objects


@tool("mode_text")
def _():
    return glyph("Aa", 14, 17, 14, "sans", NEW, ref="A") + line(27, 8, 27, 26, INK, 1.8) + \
        line(24.5, 8, 29.5, 8, INK, 1.6) + line(24.5, 26, 29.5, 26, INK, 1.6)


@tool("mode_image", mono=True)
def _():
    return (rect(3, 6, 26, 20, 3) + circ(22, 12, 2.5, INK, 1.8) +
            path("M3.5 23L11 15L17 21L20.5 18L28.5 25", INK, 2))


alias("mode_image_mow", "mode_image", mono=True)


@tool("mode_slider")
def _():
    return (line(4, 17, 28, 17, INK, 2) + line(4, 17, 19, 17, CUR, 3) + line(4, 13, 4, 21, INK, 1.6) +
            line(28, 13, 28, 21, INK, 1.6) + pt(19, 17, NEW, 4.5) +
            glyph("a", 10, 8, 5, "italic", LABEL))


@tool("mode_button")
def _():
    return rect(3, 7, 24, 13, 4, NEW, 2, fill=NEW, fo=FILL_OP) + pointer(19, 14, 0.85)


@tool("mode_inputbox")
def _():
    return (rect(3, 9, 26, 14, 3) + glyph("12", 5.5, 16, 7, "bold", LABEL, anchor="start") +
            line(18, 12, 18, 20, NEW, 2))


@tool("mode_freehandshape")
def _():
    d = "M4 22C6 12 11 8 14 13S18 25 22 18"
    pen = [(21.5, 17.5), (27, 6), (30, 7.5), (24.5, 19)]
    return (path(d, NEW, 2.2) + poly(pen, INK, 1.6, fill=INK, fo=0.2) +
            line(21.5, 17.5, 22, 20.5, INK, 1.6) + line(22, 20.5, 24.5, 19, INK, 1.6))


alias("mode_freehandfunction", "mode_freehandshape")


@tool("mode_pen", mono=True)
def _():
    body = [(8, 22), (22, 5), (27, 9.5), (13, 26.5)]
    return (poly(body, INK, 2) + line(20, 7.5, 25, 12, INK, 1.6) +
            path("M8 22L6 28.5L13 26.5", INK, 2) + path("M3 29.5H11", INK, 1.6, op=0.5))


@tool("mode_highlighter", mono=True)
def _():
    body = [(10, 20), (21, 5), (27, 10), (15, 24)]
    return (box(3, 25, 20, 5, 1, INK, op=0.3) + poly(body, INK, 2) +
            path("M10 20L7 24.5L11.5 26L15 24", INK, 2) + line(18.5, 8.5, 24.5, 13.5, INK, 1.5))


@tool("mode_list")
def _():
    return (glyph("{", 5.5, 16, 20, "math", NEW) + glyph("}", 26.5, 16, 20, "math", NEW) +
            pt(11, 20, PT, 2.6) + pt(16, 12, PT, 2.6) + pt(21, 19, PT, 2.6))


@tool("mode_probabilitycalculator")
def _():
    f = lambda x: 26 - 18 * math.exp(-((x - 16) ** 2) / 30)
    area = [(12, 26)] + fcurve(f, 12, 20, 16) + [(20, 26)]
    return (poly(area, None, 0, fill=NEW, fo=0.5) + line(12, 26, 12, f(12), NEW, 1.6) +
            line(20, 26, 20, f(20), NEW, 1.6) + line(2, 26, 30, 26, INK, 1.6) +
            pl(fcurve(f, 2, 30), CUR))


# ============================================================ spreadsheet


@tool("mode_listofpoints")
def _():
    return cells() + pt(17, 22, NEW, 2.6) + pt(21, 11, NEW, 2.6) + pt(27, 18, NEW, 2.6)


@tool("mode_matrix")
def _():
    out = [cells(), path("M17 7H15V25H17", NEW, 2), path("M27 7H29V25H27", NEW, 2)]
    for x in (19.5, 24.5):
        for y in (11, 16, 21):
            out.append(disc(x, y, 1.3, NEW))
    return "".join(out)


@tool("mode_createtable")
def _():
    return (cells() + rect(15, 7, 14, 18, 1.5, NEW, 1.8, fill=NEW, fo=0.12) +
            line(15, 13, 29, 13, NEW, 1.5) + line(15, 19, 29, 19, NEW, 1.5) +
            line(22, 7, 22, 25, NEW, 1.5))


@tool("mode_createpolyline")
def _():
    pts = [(15, 24), (19, 12), (24, 19), (29, 7)]
    return cells() + pl(pts, NEW, 2) + "".join(pt(x, y, PT, 2.3) for x, y in pts)


@tool("mode_onevarstats")
def _():
    out = [cells(), line(14, 28, 30, 28, INK, 1.5)]
    for x, h in ((15, 8), (19, 16), (23, 12), (27, 5)):
        out.append(rect(x, 28 - h, 3, h, 0, NEW, 1.4, fill=NEW, fo=0.3))
    return "".join(out)


@tool("mode_twovarstats")
def _():
    pts = [(16, 23), (19, 19), (22, 20), (25, 13), (28, 11)]
    return (cells() + line(14, 26, 30, 8, NEW, 2) + "".join(pt(x, y, PT, 1.9, 0.8) for x, y in pts))


@tool("mode_multivarstats")
def _():
    out = [cells()]
    for x, lo, q1, med, q3, hi in ((16, 26, 21, 18, 14, 8), (24, 24, 19, 15, 11, 5)):
        out += [line(x + 2, lo, x + 2, q1, NEW, 1.5), line(x + 2, q3, x + 2, hi, NEW, 1.5),
                rect(x, q3, 4, q1 - q3, 0.8, NEW, 1.5, fill=NEW, fo=0.25),
                line(x, med, x + 4, med, NEW, 1.5)]
    return "".join(out)


@tool("mode_sum")
def _():
    return cells() + glyph("Σ", 22.5, 16, 15, "sans", NEW)


@tool("mode_mean")
def _():
    return cells() + glyph("x", 22.5, 18.5, 9.5, "italic", NEW) + line(18, 9, 27, 9, NEW, 2)


@tool("mode_count")
def _():
    return cells() + glyph("#", 22.5, 16, 14, "sans", NEW)


def _bars(highlight):
    out = [cells(), line(14, 28, 30, 28, INK, 1.5)]
    hs = (10, 17, 6, 13)
    for i, h in enumerate(hs):
        x = 15 + i * 4
        hl = (highlight == "max" and h == max(hs)) or (highlight == "min" and h == min(hs))
        out.append(rect(x, 28 - h, 3, h, 0, NEW if hl else INK, 1.4,
                        fill=NEW if hl else INK, fo=0.55 if hl else 0.12))
    return "".join(out)


@tool("mode_maximum")
def _():
    return _bars("max")


@tool("mode_minimum")
def _():
    return _bars("min")


# ==================================================================== CAS


def _cas(g, font="math", h=12, c=NEW, w=None):
    return glyph(g, 16, 16, h, font, c, maxw=w)


@tool("mode_evaluate")
def _():
    return box(6, 10.5, 20, 3.4, 1.7, NEW) + box(6, 18.1, 20, 3.4, 1.7, NEW)


@tool("mode_numeric")
def _():
    return _cas("≈", h=11, w=22)


@tool("mode_keepinput")
def _():
    return pl([(6, 16.5), (13, 23.5), (26.5, 8.5)], NEW, 3)


@tool("mode_factor")
def _():
    return _cas("()()", h=18, w=26)


@tool("mode_expand")
def _():
    return (glyph("(", 5, 16, 18, "math", INK) + glyph(")", 27, 16, 18, "math", INK) +
            arrow(14, 16, 9, 16, NEW, 2, 5) + arrow(18, 16, 23, 16, NEW, 2, 5))


@tool("mode_substitute")
def _():
    return (glyph("x", 6, 17, 8.5, "italic", INK) + arrow(11.5, 17, 20, 17, NEW, 2, 5) +
            glyph("a", 25.5, 17, 8.5, "italic", NEW))


@tool("mode_solve")
def _():
    return (glyph("x", 10, 17, 11, "italic", NEW) + box(17, 13, 10, 2.6, 1.3, NEW) +
            box(17, 18.6, 10, 2.6, 1.3, NEW))


@tool("mode_nsolve")
def _():
    return glyph("x", 10, 17, 11, "italic", NEW) + glyph("≈", 23, 16.5, 8, "math", NEW)


@tool("mode_derivative")
def _():
    return glyph("f′", 16, 16, 20, "italic", NEW)


@tool("mode_integral")
def _():
    return path("M22.5 5.5C20 3 16.5 4 16.5 9V23C16.5 28 13 29 10 26.5", NEW, 2.6)


# ===================================================================== 3D


def _cube(x, y, s, dx, dy, fill=None, fo=None, edge=NEW, hidden=True):
    """Oblique cube: front square at (x, y) with side s, depth offset (dx, dy)."""
    f = [(x, y), (x + s, y), (x + s, y + s), (x, y + s)]
    b = [(px + dx, py + dy) for px, py in f]
    out = []
    if fill:
        out.append(poly([f[0], b[0], b[1], b[2], f[2], f[3]], None, 0, fill=fill, fo=fo))
    if hidden:
        out += [line(*b[3], *f[3], edge, 1.2, dash=(1.6, 1.8)),
                line(*b[3], *b[0], edge, 1.2, dash=(1.6, 1.8)),
                line(*b[3], *b[2], edge, 1.2, dash=(1.6, 1.8))]
    out += [poly(f, edge, 2), pl([f[0], b[0], b[1], b[2], f[2]], edge, 2), line(*f[1], *b[1], edge, 2)]
    return "".join(out)


@tool("mode_cube")
def _():
    return _cube(4, 12, 15, 8, -7, fill=NEW, fo=FILL_OP) + pt(4, 27) + pt(19, 27)


@tool("mode_tetrahedron")
def _():
    a, b, c, d = (4, 26), (22, 27), (28, 18), (15, 4)
    return (poly([a, b, c, d], None, 0, fill=NEW, fo=FILL_OP) +
            line(*a, *c, NEW, 1.2, dash=(1.6, 1.8)) + pl([a, b, c], NEW) + line(*a, *d, NEW) +
            line(*b, *d, NEW) + line(*c, *d, NEW) + pt(*a, PT, 2.6) + pt(*b, PT, 2.6))


@tool("mode_prism")
def _():
    base = [(4, 26), (18, 28), (27, 22)]
    up = [(x, y - 14) for x, y in base]
    return (poly(base, INK, 1.8, fill=CUR, fo=0.25) + line(*up[0], *up[2], NEW, 1.2, dash=(1.6, 1.8)) +
            poly([base[0], up[0], up[1], up[2], base[2], base[1]], None, 0, fill=NEW, fo=FILL_OP) +
            pl([up[0], up[1], up[2]], NEW) + line(*up[0], *up[2], NEW, 2) +
            "".join(line(*p, *q, NEW) for p, q in zip(base, up)) + pt(*up[0]))


@tool("mode_pyramid")
def _():
    base = [(4, 24), (19, 28), (28, 22), (14, 19)]
    apex = (15, 4)
    return (poly(base, INK, 1.6, fill=CUR, fo=0.25) +
            poly([base[0], base[1], base[2], apex], None, 0, fill=NEW, fo=FILL_OP) +
            line(*base[3], *apex, NEW, 1.2, dash=(1.6, 1.8)) +
            "".join(line(*p, *apex, NEW) for p in base[:3]) + pt(*apex))


@tool("mode_cone")
def _():
    cx, cy, rx, ry = 16, 24, 11, 4
    apex = (16, 3)
    return (poly([(cx - rx, cy), apex, (cx + rx, cy)] + ellipse_pts(cx, cy, rx, ry, 0, 360, 180, 20),
                 None, 0, fill=NEW, fo=FILL_OP) +
            pl(ellipse_pts(cx, cy, rx, ry, 0, 0, 180, 24), NEW, 1.2, dash=(1.6, 1.8)) +
            pl(ellipse_pts(cx, cy, rx, ry, 0, 180, 360, 24), NEW) + line(cx - rx, cy, *apex, NEW) +
            line(cx + rx, cy, *apex, NEW) + pt(cx, cy, PT, 2.6) + pt(*apex))


@tool("mode_cylinder")
def _():
    cx, rx, ry, top, bot = 16, 10, 3.6, 7, 25
    return (poly([(cx - rx, top), (cx - rx, bot)] + ellipse_pts(cx, bot, rx, ry, 0, 180, 360, 20) +
                 [(cx + rx, top)], None, 0, fill=NEW, fo=FILL_OP) +
            ell(cx, top, rx, ry, 0, NEW) +
            pl(ellipse_pts(cx, bot, rx, ry, 0, 0, 180, 24), NEW, 1.2, dash=(1.6, 1.8)) +
            pl(ellipse_pts(cx, bot, rx, ry, 0, 180, 360, 24), NEW) + line(cx - rx, top, cx - rx, bot, NEW) +
            line(cx + rx, top, cx + rx, bot, NEW) + pt(cx, top, PT, 2.6) + pt(cx, bot, PT, 2.6))


def _sphere(cx, cy, r):
    return (circ(cx, cy, r, NEW, 2, fill=NEW, fo=FILL_OP) +
            pl(ellipse_pts(cx, cy, r, r * 0.33, 0, 0, 180, 24), NEW, 1.2, dash=(1.6, 1.8)) +
            pl(ellipse_pts(cx, cy, r, r * 0.33, 0, 180, 360, 24), NEW, 1.6))


@tool("mode_sphere2")
def _():
    return _sphere(16, 16, 12.5) + pt(16, 16) + pt(*polar(16, 16, 12.5, 50))


@tool("mode_spherepointradius")
def _():
    e = polar(16, 16, 12.5, 40)
    return (_sphere(16, 16, 12.5) + line(16, 16, *e, INK, 1.6) + pt(16, 16) +
            glyph("r", 17, 8.5, 5.5, "italic", LABEL))


@tool("mode_plane")
def _():
    return (plane([(2, 20), (12, 9), (30, 11), (20, 24)], new=True) + line(4, 29, 28, 26) + pt(14, 7))


@tool("mode_planethreepoint")
def _():
    return (plane([(2, 21), (12, 8), (30, 11), (20, 25)], new=True) + pt(9, 17.5, PT, 2.6) +
            pt(21, 12.5, PT, 2.6) + pt(19, 21, PT, 2.6))


@tool("mode_parallelplane")
def _():
    return (plane([(2, 25), (10, 18), (30, 19), (22, 27)]) +
            plane([(2, 12), (10, 5), (30, 6), (22, 14)], new=True) + pt(16, 9.5))


@tool("mode_perpendicularplane")
def _():
    return (line(2, 22, 30, 22) + plane([(11, 4), (21, 7), (21, 30), (11, 27)], new=True) +
            pt(16, 17))


@tool("mode_orthogonalthreed")
def _():
    return (plane([(2, 23), (10, 15), (30, 16), (22, 24)]) + line(16, 19.5, 16, 3, NEW) +
            right_angle(16, 19.5, 0, 4, INK, 1.4) + pt(16, 8))


@tool("mode_extrusion")
def _():
    base = [(4, 26), (18, 29), (27, 24), (13, 21)]
    up = [(x, y - 13) for x, y in base]
    return (poly(base, INK, 1.8, fill=CUR, fo=0.3) + poly(up, NEW, 1.8, fill=NEW, fo=FILL_OP) +
            "".join(line(*p, *q, NEW, 1.6, dash=(2, 2)) for p, q in zip(base, up)))


@tool("mode_conify")
def _():
    base = [(4, 26), (18, 29), (27, 24), (13, 21)]
    apex = (15.5, 4)
    return (poly(base, INK, 1.8, fill=CUR, fo=0.3) +
            "".join(line(*p, *apex, NEW, 1.6, dash=(2, 2)) for p in base) + newpt(*apex))


@tool("mode_net")
def _():
    s = 6.5
    sq = [(1, 0), (0, 1), (1, 1), (2, 1), (3, 1), (1, 2)]
    out = []
    for i, j in sq:
        x, y = 3 + i * s, 6.5 + j * s
        fill = CUR if (i, j) == (1, 1) else NEW
        out.append(rect(x, y, s, s, 0, NEW if fill == NEW else INK, 1.6, fill=fill, fo=0.2))
    return "".join(out)


@tool("mode_surfaceofrevolution")
def _():
    return (line(16, 2, 16, 30, INK, 1.6) +
            path("M16 4C24 8 22 20 26 27", CUR, 2) +
            ell(16, 11, 7, 2.2, 0, NEW, 1.6) + ell(16, 20, 7.5, 2.4, 0, NEW, 1.6) +
            path("M16 4C8 8 10 20 6 27", NEW, 2))


@tool("mode_intersecttwosurfaces")
def _():
    return (circ(16, 13, 10, CUR, 1.8, fill=CUR, fo=0.15) +
            plane([(2, 22), (9, 13), (30, 13), (23, 22)]) + ell(16, 17.2, 8.4, 2.6, 0, NEW, 2.4))


@tool("mode_circleaxispoint")
def _():
    return (line(16, 2, 16, 30) + ell(16, 16, 11, 4, 0, NEW) + pt(27, 16))


@tool("mode_circlepointradiusdirection")
def _():
    return (ell(15, 20, 12, 5, 0, NEW) + arrow(15, 20, 15, 4, INK, 1.8, 5) +
            line(15, 20, 27, 20, INK, 1.4, dash=(2, 1.8)) + pt(15, 20) +
            glyph("r", 22, 11.5, 5.5, "italic", LABEL))


# ============================================================ notes media


@tool("mode_media_text", mono=True)
def _():
    return rect(4, 5, 24, 22, 3) + glyph("T", 16, 16, 12, "sans", INK)


@tool("mode_equation", mono=True)
def _():
    return (path("M3 18L6.5 16L10.5 26L16 6H29", INK, 2.2) +
            glyph("x", 22.5, 17.5, 8, "italic", INK))


@tool("mode_camera", mono=True)
def _():
    return (path("M3 11.5A2.5 2.5 0 0 1 5.5 9H10L12.5 5.5H19.5L22 9H26.5A2.5 2.5 0 0 1 29 11.5V24"
                 "A2.5 2.5 0 0 1 26.5 26.5H5.5A2.5 2.5 0 0 1 3 24Z", INK, 2) +
            circ(16, 17.5, 5.2, INK, 2))


alias("mode_photolibrary", "mode_camera", mono=True)


@tool("mode_pdf", mono=True)
def _():
    return (path("M7 3H19L26 10V29H7Z", INK, 2) + path("M19 3V10H26", INK, 2) +
            glyph("PDF", 16.5, 20, 5.2, "bold", INK))


@tool("mode_web", mono=True)
def _():
    return (circ(16, 16, 12.5) + ell(16, 16, 5.5, 12.5, 0, INK, 1.8) + line(3.5, 16, 28.5, 16, INK, 1.8) +
            path("M5.5 9.5H26.5M5.5 22.5H26.5", INK, 1.6))


@tool("mode_video", mono=True)
def _():
    return rect(3, 6, 26, 20, 3) + poly([(13, 11), (21, 16), (13, 21)], INK, 1.5, fill=INK)


@tool("mode_audio", mono=True)
def _():
    return (poly([(4, 12), (9, 12), (15, 6), (15, 26), (9, 20), (4, 20)], INK, 2, fill=INK, fo=0.2) +
            arc(15, 16, 6, -40, 40, INK, 2) + arc(15, 16, 11, -45, 45, INK, 2))


@tool("mode_geogebra", mono=True)
def _():
    return (rect(3, 5, 26, 22, 3) + line(6.5, 22, 25.5, 22, INK, 1.4, op=0.6) +
            line(9, 8.5, 9, 24.5, INK, 1.4, op=0.6) + path("M7 20C11 20 12 10 16 10S21 17 25 12", INK, 2) +
            disc(16, 10, 2.4, INK))


@tool("mode_mindmap", mono=True)
def _():
    return (line(16, 16, 6, 7, INK, 1.6) + line(16, 16, 26, 7, INK, 1.6) + line(16, 16, 16, 26, INK, 1.6) +
            rect(10, 12.5, 12, 7, 2.5, INK, 2, fill=INK, fo=0.25) + rect(2, 3.5, 9, 6, 2, INK, 1.8) +
            rect(21, 3.5, 9, 6, 2, INK, 1.8) + rect(11.5, 23, 9, 6, 2, INK, 1.8))


@tool("mode_table", mono=True)
def _():
    return (box(4, 6, 24, 6, 0, INK, op=0.3) + rect(4, 6, 24, 20, 2.5) + line(4, 12.5, 28, 12.5, INK, 1.6) +
            line(4, 19.25, 28, 19.25, INK, 1.6) + line(12, 6, 12, 26, INK, 1.6) + line(20, 6, 20, 26, INK, 1.6))


@tool("mode_graspablemath", mono=True)
def _():
    return (glyph("a+b", 16, 22, 8.5, "italic", INK, ref="a") +
            path("M8 13C10 5 22 5 24 13", INK, 1.8) + head(24, 13.2, -72, 4.8, INK) +
            head(8, 13.2, 252, 4.8, INK))


@tool("mode_masktool", mono=True)
def _():
    return (circ(12, 15, 9, INK, 2) + box(14, 8, 16, 18, 2, INK, op=0.9))


@tool("mode_ruler", mono=True)
def _():
    body = [(3, 21), (21, 3), (29, 11), (11, 29)]
    out = [poly(body, INK, 2)]
    for i in range(1, 8):
        t = i / 8
        x, y = lerp((3, 21), (21, 3), t)
        L = 4.5 if i % 2 == 0 else 2.8
        out.append(line(x, y, x + L * 0.707, y + L * 0.707, INK, 1.5))
    return "".join(out)


@tool("mode_protractor", mono=True)
def _():
    out = [path("M3 24A13 13 0 0 1 29 24Z", INK, 2), arc(16, 24, 5, 0, 180, INK, 1.5)]
    for a in range(15, 180, 15):
        L = 3.5 if a % 45 == 0 else 2.2
        p, q = polar(16, 24, 13, a), polar(16, 24, 13 - L, a)
        out.append(line(*p, *q, INK, 1.4))
    return "".join(out)


@tool("mode_triangleprotractor", mono=True)
def _():
    out = [poly([(2, 23), (30, 23), (16, 9)], INK, 2), arc(16, 23, 5.5, 0, 180, INK, 1.5)]
    for x in range(5, 28, 3):
        out.append(line(x, 23, x, 21 if x % 6 else 20, INK, 1.3))
    return "".join(out)


# shapes of the Notes app (monochrome)


@tool("mode_shapesquare", mono=True)
def _():
    return rect(6, 6, 20, 20, 2)


@tool("mode_shaperectangle", mono=True)
def _():
    return rect(3, 8, 26, 16, 2)


@tool("mode_shapetriangle", mono=True)
def _():
    return poly([(4, 26), (28, 26), (16, 5)])


@tool("mode_circle", mono=True)
def _():
    return circ(16, 16, 11.5)


@tool("mode_shapeellipse", mono=True)
def _():
    return ell(16, 16, 13, 8.5)


@tool("mode_pentagon", mono=True)
def _():
    return poly([polar(16, 17, 12.5, 90 + 72 * i) for i in range(5)])


@tool("mode_line", mono=True)
def _():
    return line(5, 27, 27, 5)


@tool("mode_shapefreeform", mono=True)
def _():
    return path("M6 22C2 14 8 5 15 8S26 4 27 12S22 27 15 24S9 28 6 22Z", INK, 2)


@tool("mode_parallelogram", mono=True)
def _():
    return poly([(3, 24), (10, 8), (29, 8), (22, 24)])


@tool("mode_stadium", mono=True)
def _():
    return rect(3, 9, 26, 14, 7)


@tool("mode_curve", mono=True)
def _():
    return path("M4 25C8 4 16 4 17 16S25 28 28 7", INK, 2)


@tool("mode_recordtospreadsheet")
def _():
    return (cells(20, 4) + circ(9, 16, 6.5, NEW, 2) + disc(9, 16, 3.6, NEW) +
            arrow(15.5, 16, 19, 16, INK, 1.6, 3.8))

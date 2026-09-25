"""Locus UI icons on a 24 x 24 grid: common buttons, style bar options, view
and menu icons, probability options.

They are monochrome: every part inherits the root fill (#5b6470), so the code
can recolour them with SVGResource.withFill or CSS. Secondary areas use a
lower opacity of the same colour. The only exception is normal_overlay.svg,
the coloured variant of overlay.svg.
"""
import math

from lib import (CUR, INK, UI_INK, arc, arc_d, arrow, box, circ, disc, ell, glyph, head, line,
                 path, pl, polar, poly, rect)

UI = {}
PNGS = {}

S = "icons/svg/common/"
W = "icons/svg/web/"


def ui(rel, size=24, fill=None, flatten=True):
    def deco(fn):
        UI[rel] = (fn, size, fill, flatten)
        return fn
    return deco


def same(rel, target):
    fn = UI[target][0]
    UI[rel] = (fn,) + UI[target][1:]


# ============================================================ svg/common


@ui(S + "arrow_backward.svg")
def _():
    return line(19, 12, 5, 12) + pl([(11, 6), (5, 12), (11, 18)])


@ui(S + "arrow_forward.svg")
def _():
    return line(5, 12, 19, 12) + pl([(13, 6), (19, 12), (13, 18)])


@ui(S + "arrow_upward.svg")
def _():
    return line(12, 19, 12, 5) + pl([(6, 11), (12, 5), (18, 11)])


@ui(S + "arrow_downward.svg")
def _():
    return line(12, 5, 12, 19) + pl([(6, 13), (12, 19), (18, 13)])


@ui(S + "center_view.svg")
def _():
    return (circ(12, 12, 6.5) + disc(12, 12, 2.2) + line(12, 2, 12, 5) + line(12, 19, 12, 22) +
            line(2, 12, 5, 12) + line(19, 12, 22, 12))


@ui(S + "check_mark.svg")
def _():
    return pl([(4.5, 12.5), (9.5, 17.5), (19.5, 6.5)], INK, 2.4)


@ui(S + "close.svg")
def _():
    return line(6, 6, 18, 18) + line(18, 6, 6, 18)


@ui(S + "remove.svg")
def _():
    return line(5, 12, 19, 12)


@ui(S + "play.svg")
def _():
    return poly([(8, 5), (19, 12), (8, 19)], INK, 2, fill=INK)


@ui(S + "pause.svg")
def _():
    return box(6.5, 5, 4, 14, 1.2) + box(13.5, 5, 4, 14, 1.2)


@ui(S + "stop.svg")
def _():
    return box(6, 6, 12, 12, 1.5)


@ui(S + "skip_next.svg")
def _():
    return poly([(6, 6), (15, 12), (6, 18)], INK, 2, fill=INK) + box(16, 5.5, 2.6, 13, 1)


@ui(S + "skip_previous.svg")
def _():
    return poly([(18, 6), (9, 12), (18, 18)], INK, 2, fill=INK) + box(5.4, 5.5, 2.6, 13, 1)


@ui(S + "fast_forward.svg")
def _():
    return (poly([(3.5, 6.5), (11.5, 12), (3.5, 17.5)], INK, 1.8, fill=INK) +
            poly([(12.5, 6.5), (20.5, 12), (12.5, 17.5)], INK, 1.8, fill=INK))


@ui(S + "fast_rewind.svg")
def _():
    return (poly([(20.5, 6.5), (12.5, 12), (20.5, 17.5)], INK, 1.8, fill=INK) +
            poly([(11.5, 6.5), (3.5, 12), (11.5, 17.5)], INK, 1.8, fill=INK))


def _circ_arrow(cx, cy, r, a0, a1, size=5):
    """Arc from a0 to a1 (degrees, counter-clockwise when a1 > a0) with a head."""
    x, y = polar(cx, cy, r, a1)
    tang = a1 + (90 if a1 > a0 else -90)
    back = math.degrees(size * 0.5 / r) * (1 if a1 > a0 else -1)
    return arc(cx, cy, r, a0, a1 - back) + head(x, y, tang, size)


@ui(S + "replay.svg")
def _():
    return _circ_arrow(12, 13, 7.5, -60, 200, 5.5) + poly([(10.5, 10), (15.5, 13), (10.5, 16)], INK, 1, fill=INK)


@ui(S + "loop.svg")
def _():
    return (path("M6 15V11A3 3 0 0 1 9 8H18", INK, 2) + head(20.5, 8, 0, 5) +
            path("M18 9V13A3 3 0 0 1 15 16H6", INK, 2) + head(3.5, 16, 180, 5))


@ui(S + "undo.svg")
def _():
    return path("M8 9H15A5 5 0 0 1 15 19H9", INK, 2) + pl([(11.5, 5.5), (8, 9), (11.5, 12.5)])


@ui(S + "redo.svg")
def _():
    return path("M16 9H9A5 5 0 0 0 9 19H15", INK, 2) + pl([(12.5, 5.5), (16, 9), (12.5, 12.5)])


@ui(S + "help.svg")
def _():
    return circ(12, 12, 9.5) + glyph("?", 12, 12, 10, "bold", INK)


def gear(cx, cy, r_out, r_in, teeth=8, hole=3, sw=1.8):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        r = r_out if (i % 4) in (1, 2) else r_in
        pts.append((cx + r * math.cos(a + math.pi / (teeth * 4)), cy + r * math.sin(a + math.pi / (teeth * 4))))
    return poly(pts, INK, sw) + circ(cx, cy, hole, INK, sw)


@ui(S + "settings.svg")
def _():
    return gear(12, 12, 9.5, 7, 8, 3)


def magnifier(cx, cy, r, sw=2):
    a = math.radians(-45)
    hx, hy = cx + r * math.cos(a), cy - r * math.sin(a)
    return circ(cx, cy, r, INK, sw) + line(hx + 0.8, hy + 0.8, hx + 6, hy + 6, INK, sw + 0.6)


@ui(S + "zoom_in.svg")
def _():
    return magnifier(10, 10, 6.5) + line(7, 10, 13, 10) + line(10, 7, 10, 13)


@ui(S + "zoom_out.svg")
def _():
    return magnifier(10, 10, 6.5) + line(7, 10, 13, 10)


@ui(S + "zoom_to_fit.svg")
def _():
    c = [pl([(4, 9), (4, 4), (9, 4)]), pl([(15, 4), (20, 4), (20, 9)]),
         pl([(20, 15), (20, 20), (15, 20)]), pl([(9, 20), (4, 20), (4, 15)])]
    return "".join(c) + rect(8.5, 8.5, 7, 7, 1.2, INK, 1.8)


# ============================================================ decorations

D = W + "decoration/"


@ui(D + "decoration_segment_line.svg")
def _():
    return line(3, 12, 21, 12)


def _seg_ticks(n):
    xs = [12 + (i - (n - 1) / 2) * 3.4 for i in range(n)]
    return line(3, 12, 21, 12) + "".join(line(x, 7, x, 17, INK, 1.8) for x in xs)


def _seg_arrows(n):
    xs = [12 + (i - (n - 1) / 2) * 3.6 + 1.5 for i in range(n)]
    return line(3, 12, 21, 12) + "".join(pl([(x - 3.5, 7.5), (x, 12), (x - 3.5, 16.5)], INK, 1.8) for x in xs)


for _n, _w in ((1, "1"), (2, "2"), (3, "3")):
    UI[D + f"decoration_segment_{_w}stroke{'s' if _n > 1 else ''}.svg"] = (
        (lambda n=_n: _seg_ticks(n)), 24, None, True)
    UI[D + f"decoration_segment_{_w}arrow{'s' if _n > 1 else ''}.svg"] = (
        (lambda n=_n: _seg_arrows(n)), 24, None, True)

V = (4, 19)
ANG = 58


def _angle_base():
    return line(*V, 21, 19) + line(*V, *polar(*V, 16, ANG))


def _angle_lines(n):
    return _angle_base() + "".join(arc(*V, 7 + 3 * i, 0, ANG, INK, 1.6) for i in range(n))


def _angle_strokes(n):
    out = [_angle_base(), arc(*V, 10.5, 0, ANG, INK, 1.6)]
    for i in range(n):
        a = ANG / 2 + (i - (n - 1) / 2) * 14
        p, q = polar(*V, 8, a), polar(*V, 13, a)
        out.append(line(*p, *q, INK, 1.4))
    return "".join(out)


for _n, _w in ((1, "1"), (2, "2"), (3, "3")):
    UI[D + f"decoration_angle_{_w}line{'s' if _n > 1 else ''}.svg"] = (
        (lambda n=_n: _angle_lines(n)), 24, None, True)
    UI[D + f"decoration_angle_{_w}stroke{'s' if _n > 1 else ''}.svg"] = (
        (lambda n=_n: _angle_strokes(n)), 24, None, True)


@ui(D + "decoration_angle_arrow-up.svg")
def _():
    # anticlockwise: the head sits at the end of the arc on the second arm
    x, y = polar(*V, 10, ANG)
    return _angle_base() + arc(*V, 10, 0, ANG - 14, INK, 1.6) + head(x, y, ANG + 90, 4.8)


@ui(D + "decoration_angle_arrow-down.svg")
def _():
    x, y = polar(*V, 10, 0)
    return _angle_base() + arc(*V, 10, 14, ANG, INK, 1.6) + head(x, y + 0.2, -90, 4.8)


@ui(D + "decoration_axes_line.svg")
def _():
    return line(3, 12, 21, 12)


@ui(D + "decoration_axes_arrow.svg")
def _():
    return line(3, 12, 20.5, 12) + pl([(15.5, 7), (20.5, 12), (15.5, 17)])


@ui(D + "decoration_axes_arrows.svg")
def _():
    return (line(3.5, 12, 20.5, 12) + pl([(15.5, 7), (20.5, 12), (15.5, 17)]) +
            pl([(8.5, 7), (3.5, 12), (8.5, 17)]))


@ui(D + "decoration_axes_arrow_filled.svg")
def _():
    return line(3, 12, 16, 12) + poly([(21, 12), (14, 7.5), (14, 16.5)], INK, 1.5, fill=INK)


@ui(D + "decoration_axes_arrows_filled.svg")
def _():
    return (line(8, 12, 16, 12) + poly([(21, 12), (14, 7.5), (14, 16.5)], INK, 1.5, fill=INK) +
            poly([(3, 12), (10, 7.5), (10, 16.5)], INK, 1.5, fill=INK))


# ============================================================ segment ends
# Start icons show the decoration at the left end of a segment, end icons at
# the right end (mirror image). Outlined shapes are hollow.


def _ending(kind):
    x = 5.5  # the end of the segment
    out = []
    seg_from = x
    if kind == "default":
        pass
    elif kind == "line":
        out.append(line(x, 6.5, x, 17.5))
    elif kind == "arrow":
        out.append(pl([(x + 6, 6.5), (x, 12), (x + 6, 17.5)]))
    elif kind == "crows_foot":
        seg_from = x + 5
        out += [line(x + 5, 12, x - 1.5, 6), line(x + 5, 12, x - 1.5, 12), line(x + 5, 12, x - 1.5, 18)]
    elif kind in ("arrow_outlined", "arrow_filled"):
        seg_from = x + 7
        out.append(poly([(x, 12), (x + 7.5, 7), (x + 7.5, 17)], INK, 1.8,
                        fill=INK if kind == "arrow_filled" else None))
    elif kind in ("circle_outlined", "circle"):
        seg_from = x + 8
        out.append(circ(x + 4, 12, 4, INK, 1.8, fill=INK if kind == "circle" else None))
    elif kind in ("square_outlined", "square"):
        seg_from = x + 7.5
        out.append(rect(x, 8.25, 7.5, 7.5, 0.8, INK, 1.8, fill=INK if kind == "square" else None))
    elif kind in ("diamond_outlined", "diamond_filled"):
        seg_from = x + 9
        out.append(poly([(x, 12), (x + 4.5, 7.5), (x + 9, 12), (x + 4.5, 16.5)], INK, 1.8,
                        fill=INK if kind == "diamond_filled" else None))
    return line(seg_from, 12, 20, 12) + "".join(out)


def _mirror(body):
    return f'<g transform="matrix(-1 0 0 1 24 0)">{body}</g>'


for _k in ("default", "line", "arrow", "crows_foot", "arrow_outlined", "arrow_filled",
           "circle_outlined", "circle", "square_outlined", "square", "diamond_outlined",
           "diamond_filled"):
    UI[W + f"stylingbar/segmentStart/start_{_k}.svg"] = ((lambda k=_k: _ending(k)), 24, None, True)
    UI[W + f"stylingbar/segmentEnd/end_{_k}.svg"] = ((lambda k=_k: _mirror(_ending(k))), 24, None, True)


# ============================================================ style bar


SB = W + "stylingbar/"


@ui(SB + "stylebar_empty.svg")
def _():
    return rect(5, 5, 14, 14, 2.5, INK, 1.5, dash=(2.5, 2.5), op=0.5)


@ui(SB + "delete_small.svg")
def _():
    return disc(12, 12, 2.5)


@ui(SB + "delete_medium.svg")
def _():
    return disc(12, 12, 5)


@ui(SB + "delete_large.svg")
def _():
    return disc(12, 12, 8)


@ui(SB + "algebra_description.svg")
def _():
    return (disc(5.5, 7, 2) + line(10, 7, 20, 7) + disc(5.5, 12, 2) + line(10, 12, 17, 12) +
            disc(5.5, 17, 2) + line(10, 17, 19, 17))


@ui(SB + "export.svg")
def _():
    return (path("M11 4H6A2 2 0 0 0 4 6V18A2 2 0 0 0 6 20H18A2 2 0 0 0 20 18V13", INK, 2) +
            line(11, 13, 19, 5) + pl([(14, 4.5), (19.5, 4.5), (19.5, 10)]))


@ui(SB + "stylebar_angle_interval.svg")
def _():
    v = (12, 15)
    return (line(*v, 21, 15) + line(*v, *polar(*v, 10, 125)) + arc(*v, 5, 0, 125, INK, 1.8) +
            arc(*v, 5, 125, 360, INK, 1.6, dash=(1.2, 2.2)))


# 3D view


def _axes3d(o=(10, 14)):
    return (line(*o, o[0], 3, INK, 1.8) + line(*o, 21, o[1], INK, 1.8) +
            line(*o, o[0] - 6.5, o[1] + 6.5, INK, 1.8))


@ui(SB + "3d/stylingbar_graphics3D_axes_plane.svg")
def _():
    return (poly([(2, 18), (8, 12), (22, 12), (16, 18)], INK, 1.4, fill=INK, fo=0.25) +
            line(10, 15, 10, 3, INK, 1.8) + line(10, 15, 21, 15, INK, 1.8) + line(10, 15, 4.5, 20.5, INK, 1.8))


@ui(SB + "3d/stylingbar_graphics3D_plane.svg")
def _():
    return poly([(2, 18), (8, 10), (22, 10), (16, 18)], INK, 1.6, fill=INK, fo=0.25)


def _rot3d(inner):
    pts = []
    for i in range(31):
        t = math.radians(200 + 130 * i / 30)
        pts.append((12 + 9 * math.cos(t), 16 - 3.4 * math.sin(t)))
    e, pv = pts[-1], pts[-3]
    ang = math.degrees(math.atan2(-(e[1] - pv[1]), e[0] - pv[0]))
    return inner + pl(pts[:-2], INK, 1.8) + head(*e, ang, 4.5)


@ui(SB + "3d/stylingbar_graphics3D_rotateview_play.svg")
def _():
    return _rot3d(poly([(9, 3.5), (16, 8), (9, 12.5)], INK, 1.5, fill=INK))


@ui(SB + "3d/stylingbar_graphics3D_rotateview_pause.svg")
def _():
    return _rot3d(box(8, 3.5, 3, 9, 1) + box(13, 3.5, 3, 9, 1))


@ui(SB + "3d/stylingbar_graphics3D_standardview_rotate.svg")
def _():
    o = (11, 11)
    return _rot3d(line(*o, 11, 2, INK, 1.6) + line(*o, 20, 11, INK, 1.6) + line(*o, 5.5, 16.5, INK, 1.6))


def _view(a, b):
    return (rect(3, 3, 18, 18, 2.5, INK, 1.8, fill=INK, fo=0.12) +
            glyph(a, 8.3, 12.6, 6.4, "italic", INK, ref="x") + glyph(b, 15.7, 12.6, 6.4, "italic", INK, ref="x"))


UI[SB + "3d/stylingbar_graphics3D_view_xy.svg"] = ((lambda: _view("x", "y")), 24, None, True)
UI[SB + "3d/stylingbar_graphics3D_view_xz.svg"] = ((lambda: _view("x", "z")), 24, None, True)
UI[SB + "3d/stylingbar_graphics3D_view_yz.svg"] = ((lambda: _view("y", "z")), 24, None, True)


# ============================================================ views

MI = W + "menu_icons/"


def v_graphics():
    return (line(2.5, 17, 21.5, 17, INK, 1.4) + line(7, 2.5, 7, 21.5, INK, 1.4) +
            path("M2.5 20C7 20 8 6 12.5 6S16.5 14 21.5 11", INK, 2))


def _badge(n):
    return box(14, 14, 9, 9, 2.5, INK) + glyph(n, 18.5, 18.5, 6, "bold", "#ffffff")


def v_graphics_n(n):
    return (line(2.5, 16, 20, 16, INK, 1.4) + line(6.5, 2.5, 6.5, 20, INK, 1.4) +
            path("M2.5 19C6.5 19 7.5 5.5 11.5 5.5S15 12 20 9.5", INK, 2) + _badge(n))


def v_graphics_extra():
    return (poly([(2, 20), (7, 5), (22, 5), (17, 20)], INK, 1.6, fill=INK, fo=0.12) +
            path("M5.5 17C9 17 10 8.5 13 8.5S16 14 19 11.5", INK, 2))


def v_graphics3d():
    return (poly([(3, 17), (8, 12), (21, 12), (16, 17)], INK, 1.2, fill=INK, fo=0.2) +
            line(10, 14.5, 10, 2.5, INK, 1.8) + line(10, 14.5, 21.5, 14.5, INK, 1.8) +
            line(10, 14.5, 3.5, 21, INK, 1.8))


def v_algebra():
    return (disc(5, 6, 2.2) + line(9.5, 6, 20, 6) + disc(5, 12, 2.2) + line(9.5, 12, 17, 12) +
            disc(5, 18, 2.2) + line(9.5, 18, 19, 18))


def v_cas():
    return (rect(2.5, 4, 19, 16, 3, INK, 1.8) + glyph("x", 9, 12.5, 6.5, "italic", INK) +
            box(13, 9.6, 5.5, 1.8, 0.9) + box(13, 13.6, 5.5, 1.8, 0.9))


def v_spreadsheet():
    return (box(3, 3, 18, 5, 0, INK, op=0.3) + rect(3, 3, 18, 18, 2.5, INK, 1.8) + line(3, 8.5, 21, 8.5, INK, 1.4) +
            line(3, 14.5, 21, 14.5, INK, 1.4) + line(9, 3, 9, 21, INK, 1.4) + line(15, 3, 15, 21, INK, 1.4))


def v_protocol():
    out = []
    for i, y in enumerate((5.5, 12, 18.5)):
        out.append(glyph(str(i + 1), 5, y, 5, "bold", INK))
        out.append(line(10, y, 20 - (i % 2) * 3, y))
    return "".join(out)


def v_probability():
    f = lambda x: 19 - 14 * math.exp(-((x - 12) ** 2) / 14)
    pts = [(2 + 20 * i / 40, f(2 + 20 * i / 40)) for i in range(41)]
    area = [(9, 19)] + [(9 + 6 * i / 12, f(9 + 6 * i / 12)) for i in range(13)] + [(15, 19)]
    return poly(area, None, 0, fill=INK, fo=0.35) + line(2, 19.5, 22, 19.5, INK, 1.6) + pl(pts, INK, 2)


def v_whiteboard():
    return (rect(2.5, 4, 19, 14, 2.5, INK, 1.8) + line(8, 21, 16, 21, INK, 1.8) +
            path("M6 13C8 8 10 8 11 11S14 14 17 8", INK, 1.8))


def v_inputbar():
    return (rect(2.5, 7, 19, 10, 2.5, INK, 1.8) + line(6, 12, 10, 12, INK, 1.6) +
            line(8, 10, 8, 14, INK, 1.6) + line(14, 9.5, 14, 14.5, INK, 1.6))


VIEWS = {
    "menu_view_graphics": v_graphics,
    "menu_view_graphics1": lambda: v_graphics_n("1"),
    "menu_view_graphics2": lambda: v_graphics_n("2"),
    "menu_view_graphics_extra": v_graphics_extra,
    "perspectives_algebra_3Dgraphics": v_graphics3d,
    "menu_view_algebra": v_algebra,
    "menu_view_cas": v_cas,
    "menu_view_spreadsheet": v_spreadsheet,
    "menu_view_construction_protocol": v_protocol,
    "menu_view_probability": v_probability,
    "menu_view_whiteboard": v_whiteboard,
    "menu_view_input_bar": v_inputbar,
}
for _n, _f in VIEWS.items():
    UI[MI + _n + ".svg"] = (_f, 24, None, True)

# the view menu button in each view's style bar shows the same pictures
for _n, _f in {
    "stylingbar_icon_graphics": v_graphics,
    "stylingbar_icon_graphics2": lambda: v_graphics_n("2"),
    "stylebar_icon_graphics_extra": v_graphics_extra,
    "stylingbar_icon_graphics3D": v_graphics3d,
    "stylingbar_icon_algebra": v_algebra,
    "stylingbar_icon_cas": v_cas,
    "stylingbar_icon_spreadsheet": v_spreadsheet,
    "stylingbar_icon_construction_protocol": v_protocol,
}.items():
    UI[SB + _n + ".svg"] = (_f, 24, None, True)


@ui(MI + "cas.svg")
def _():
    # app icon on a white tile (the resource is called cas_white_bg)
    return box(0, 0, 24, 24, 5, "#ffffff") + v_cas()


def wrench(dx=0, dy=0, s=1.0):
    def T(x, y):
        return f"{x * s + dx:.2f} {y * s + dy:.2f}"
    d = (f"M{T(14.5, 3.5)}A5.5 5.5 0 0 0 {T(9.3, 10.9)}L{T(3.5, 16.7)}A2.2 2.2 0 0 0 {T(6.6, 19.8)}"
         f"L{T(12.4, 14)}A5.5 5.5 0 0 0 {T(19.8, 8.8)}L{T(16.9, 11.7)}L{T(13.5, 11.8)}"
         f"L{T(13.6, 8.4)}Z")
    if s != 1.0:
        d = d.replace("A5.5 5.5", f"A{5.5 * s:.2f} {5.5 * s:.2f}").replace(
            "A2.2 2.2", f"A{2.2 * s:.2f} {2.2 * s:.2f}")
    return path(d, INK, 1.8)


@ui(MI + "menu_tools.svg")
def _():
    return wrench(1, 1)


@ui(MI + "menu_tools_create.svg")
def _():
    return wrench(-1, 1, 0.9) + line(18.5, 14, 18.5, 22) + line(14.5, 18, 22.5, 18)


@ui(MI + "menu_tools_customize.svg")
def _():
    out = []
    for y, x in ((6, 15), (12, 8), (18, 13)):
        out += [line(3, y, 21, y, INK, 1.8), circ(x, y, 2.4, INK, 1.8, fill="#ffffff")]
    return "".join(out)


# classic header buttons


@ui(W + "menu-button-open-menu.svg")
def _():
    return line(4, 7, 20, 7) + line(4, 12, 20, 12) + line(4, 17, 20, 17)


@ui(W + "menu-button-open-search.svg")
def _():
    return magnifier(10, 10, 6.5)


same(W + "menu-edit-undo.svg", S + "undo.svg")
same(W + "menu-edit-redo.svg", S + "redo.svg")


@ui(W + "ic_get_app_black_24px.svg")
def _():
    return (line(12, 3.5, 12, 14) + pl([(7.5, 10), (12, 14.5), (16.5, 10)]) +
            path("M4 15.5V18A2 2 0 0 0 6 20H18A2 2 0 0 0 20 18V15.5", INK, 2))


@ui(W + "header/baseline-apps-24px.svg")
def _():
    return "".join(box(3.5 + 6.5 * i, 3.5 + 6.5 * j, 4, 4, 1.2) for i in range(3) for j in range(3))


@ui(W + "header/timer.svg")
def _():
    return (circ(12, 13.5, 7.5) + line(12, 13.5, 12, 9.5) + line(9.5, 3, 14.5, 3) +
            line(18, 7.5, 19.5, 6))


@ui(W + "matDesignIcons/dynStylebar/ruling.svg")
def _():
    return (path("M6 3H15L19 7V21H6Z", INK, 1.8) + line(9, 10, 16, 10, INK, 1.5) +
            line(9, 13.5, 16, 13.5, INK, 1.5) + line(9, 17, 16, 17, INK, 1.5))


# ============================================================ probability

P = W + "probability/"


def _bell(x):
    return 20 - 15 * math.exp(-((x - 12) ** 2) / 16)


def _bell_pts(x0=2, x1=22, n=40):
    return [(x0 + (x1 - x0) * i / n, _bell(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def _shade(a, b):
    return poly([(a, 20)] + _bell_pts(a, b, 16) + [(b, 20)], None, 0, fill=INK, fo=0.55)


def _interval(ranges):
    return ("".join(_shade(a, b) for a, b in ranges) + line(1.5, 20, 22.5, 20, INK, 1.6) +
            pl(_bell_pts(), INK, 2) +
            "".join(line(x, 20, x, _bell(x), INK, 1.4) for a, b in ranges for x in (a, b) if 2 < x < 22))


UI[P + "interval_left.svg"] = ((lambda: _interval([(2, 13)])), 24, None, True)
UI[P + "interval_right.svg"] = ((lambda: _interval([(11, 22)])), 24, None, True)
UI[P + "interval_between.svg"] = ((lambda: _interval([(9, 15)])), 24, None, True)
UI[P + "interval_two_tailed.svg"] = ((lambda: _interval([(2, 8), (16, 22)])), 24, None, True)


def _bars(fo=0.35):
    out = [line(2, 20.5, 22, 20.5, INK, 1.6)]
    for x, h in ((3.5, 5), (7.5, 11), (11.5, 14), (15.5, 9), (19.5, 4)):
        out.append(rect(x, 20.5 - h, 3, h, 0.5, INK, 1.2, fill=INK, fo=fo))
    return "".join(out)


@ui(P + "bar_chart.svg")
def _():
    return _bars(0.6)


@ui(P + "line_graph.svg")
def _():
    out = [line(2, 20.5, 22, 20.5, INK, 1.6)]
    for x, h in ((5, 5), (9, 11), (13, 14), (17, 9), (21, 4)):
        out += [line(x - 0.5, 20.5, x - 0.5, 20.5 - h, INK, 1.8), disc(x - 0.5, 20.5 - h, 1.8)]
    return "".join(out)


@ui(P + "step_graph.svg")
def _():
    return (line(2, 20.5, 22, 20.5, INK, 1.6) +
            pl([(2, 18), (6, 18), (6, 13), (10, 13), (10, 9), (14, 9), (14, 6), (18, 6), (18, 4.5), (22, 4.5)],
               INK, 2, join="miter", cap="butt"))


def _overlay(curve_colour):
    f = lambda x: 20 - 15 * math.exp(-((x - 12) ** 2) / 18)
    pts = [(1.5 + 21 * i / 40, f(1.5 + 21 * i / 40)) for i in range(41)]
    return _bars(0.25) + pl(pts, curve_colour, 2)


@ui(P + "overlay.svg")
def _():
    return _overlay(INK)


@ui(P + "normal_overlay.svg")
def _():
    return _overlay(CUR)


# ============================================================ PNG variants
# key: path below org/geogebra/common/ -> (svg source or icon function, pixels)


def file_icon():
    return path("M6 3H14L19 8V21H6Z", INK, 1.8) + path("M14 3V8H19", INK, 1.8)


PNGS.update({
    "menu_icons/p20/menu-file.png": (file_icon, 20),
    "menu_icons/p64/menu-file.png": (file_icon, 64),
    "icons_64px/menu-icons/menu-file.png": (file_icon, 64),
    "menu_icons/p20/menu-options.png": (S + "settings.svg", 20),
    "menu_icons/p20/menu-tools.png": (MI + "menu_tools.svg", 20),
    "icons_64px/menu_view_graphics1.png": (MI + "menu_view_graphics1.svg", 64),
    "icons/png24x24/stylebar_icon_graphics1.png": (MI + "menu_view_graphics1.svg", 24),
    "icons_view_perspectives/p24/menu_view_construction_protocol.png":
        (MI + "menu_view_construction_protocol.svg", 24),
    "icons_toolbar/p32/mode_image.png": (W + "toolIcons/mode_image.svg", 32),
    "icons_toolbar/p64/mode_image.png": (W + "toolIcons/mode_image.svg", 64),
    "stylingbar/p20/stylingbar_dots.png": (lambda: disc(12, 5, 2.2) + disc(12, 12, 2.2) + disc(12, 19, 2.2), 20),
    "stylingbar/p24/stylebar_more.png": (lambda: disc(12, 5, 2.2) + disc(12, 12, 2.2) + disc(12, 19, 2.2), 24),
})

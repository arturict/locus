"""Icons drawn for Locus (EUPL 1.2), following docs/design.md.

Functions in MASKED return mask ink on a 24 x 24 grid: white (#fff) is fully
inked, greys are translucent. build_icons.py wraps the ink in a mask so the icon
takes the root fill and stays recolourable with withFill. Functions in RAW
return finished multi-colour markup for icons that are never recoloured.
"""
import math

import iconlib as L
from iconlib import text_path

INK = "#fff"
SOFT = "#9a9a9a"  # about 60 % coverage
FAINT = "#5a5a5a"  # about 35 % coverage


def g(inner, w=2.0, color=INK, extra="", cap="round"):
    return (f'<g fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"'
            f' stroke-linejoin="round"{extra}>{inner}</g>')


def path(d, **attrs):
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}"{extra}/>'


def fill(d, color=INK):
    return f'<path d="{d}" fill="{color}"/>'


def circle(cx, cy, r, color=None, stroke=None, w=None):
    a = f' fill="{color}"' if color else ""
    if stroke:
        a += f' stroke="{stroke}" stroke-width="{w}"'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}"{a}/>'


def rect(x, y, w, h, rx=0, color=None):
    a = f' fill="{color}"' if color else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"{a}/>'


def box(x, y, w, h):
    """Keyboard placeholder box, lighter than the glyph strokes."""
    return g(rect(x, y, w, h, rx=1), w=1.3, color="#bdbdbd")


def txt(text, fontname, size, x, y, anchor="start", color=INK):
    return fill(text_path(text, fontname, size, x, y, anchor), color)


def mirror(inner):
    return f'<g transform="matrix(-1 0 0 1 24 0)">{inner}</g>'


# ---------------------------------------------------------------- keyboard
def radical(x0, top_x, right):
    return g(path(f"M{x0} 13.2 L{x0 + 2} 12.2 L{x0 + 5} 20 L{top_x} 4 H{right}"), w=1.6)


def integral_sign(x):
    return g(path(f"M{x + 6} 4.2 C{x + 4.6} 2.6 {x + 3.2} 3.6 {x + 3.1} 5.6 L{x + 2.9} 18.4"
                  f" C{x + 2.8} 20.4 {x + 1.4} 21.4 {x} 19.8"), w=1.6)


KEYBOARD = {
    "fraction": lambda: box(8.5, 3, 7, 6.5) + g(path("M5.5 12H18.5"), w=1.6) + box(8.5, 14.5, 7, 6.5),
    "sqrt": lambda: radical(3, 11.5, 21) + box(13, 8, 7, 9),
    # log, 10^x, n-th root and d/dx fill the 24 px box like the text keys next
    # to them, which render at 20 px; smaller drawings looked lost on the key
    "n_root": lambda: box(1, 2.5, 5.5, 5.5) + g(path("M2 14.5 L4.5 13.3 L8 21.5 L11.5 2.5 H23"), w=1.7)
    + box(13, 6, 9, 13),
    "square": lambda: box(4, 9, 9.5, 11) + txt("2", L.SANS, 10, 15, 11),
    "power": lambda: box(4, 9, 9.5, 11) + box(15.5, 3.5, 5.5, 5.5),
    "inverse": lambda: box(2.5, 9, 9, 11) + g(path("M13 6.5H16.5"), w=1.3) + txt("1", L.SANS, 9, 17.3, 10.3),
    "e_power": lambda: txt("e", L.SERIF_IT, 16, 3, 19.5) + box(13.5, 3.5, 5.5, 5.5),
    "ten_power": lambda: txt("10", L.SANS, 15, 0.3, 21.5) + box(17.6, 3.5, 5.4, 5.4),
    "log": lambda: txt("log", L.SANS, 12.5, 0, 15) + box(18.5, 15, 5, 5.5),
    "subscript": lambda: box(3.5, 4, 10, 11) + box(15.5, 14.5, 5.5, 5.5),
    "abs": lambda: g(path("M4.5 3.5V20.5M19.5 3.5V20.5"), w=1.6) + box(8, 7, 8, 10),
    "ceil": lambda: g(path("M7.5 4H4.5V20.5M16.5 4H19.5V20.5"), w=1.6) + box(8, 8, 8, 9),
    "floor": lambda: g(path("M4.5 3.5V20H7.5M19.5 3.5V20H16.5"), w=1.6) + box(8, 7, 8, 9),
    "integral": lambda: integral_sign(4) + box(12.5, 7.5, 7.5, 9),
    "definite_integral": lambda: integral_sign(2.5) + box(9.5, 2, 4, 4) + box(7, 18, 4, 4)
    + box(14, 7.5, 7, 9),
    "derivative": lambda: txt("d", L.SERIF_IT, 12.5, 12, 10.2, "middle") + g(path("M4 12.6H20"), w=1.5)
    + txt("dx", L.SERIF_IT, 12.5, 12, 23, "middle"),
    "lim": lambda: txt("lim", L.SANS, 10, 12, 12, "middle") + box(9.5, 15, 5, 5),
    "product": lambda: g(path("M3.5 4.5H13.5M5.7 4.5V19.5M11.3 4.5V19.5M3.9 19.5H7.5M9.5 19.5H13.1"), w=1.6)
    + box(15, 7.5, 6, 9),
    "sum": lambda: g(path("M13 4.5H4.5L9.2 12L4.5 19.5H13"), w=1.6) + box(15, 7.5, 6, 9),
    "vector": lambda: box(5, 9, 14, 11) + g(path("M4.5 4.8H19M16.4 2.4L19 4.8L16.4 7.2"), w=1.6),
    "atomic_post": lambda: box(3, 6.5, 9.5, 11) + box(15, 2.5, 5.5, 5.5) + box(15, 16, 5.5, 5.5),
    "atomic_pre": lambda: box(3.5, 2.5, 5.5, 5.5) + box(3.5, 16, 5.5, 5.5) + box(11.5, 6.5, 9.5, 11),
    "mixed_number": lambda: box(2.5, 6.5, 8, 11) + box(13.5, 2.5, 6, 6.5) + g(path("M12.5 12H20.5"), w=1.4)
    + box(13.5, 15, 6, 6.5),
    "recurring_decimal": lambda: g(path("M5 4.5H19"), w=1.6) + box(5, 8, 14, 12),
    "point_template": lambda: g(path("M5.5 4Q2.2 12 5.5 20M18.5 4Q21.8 12 18.5 20M12.3 15.2L11.4 17.8"), w=1.5)
    + box(6.5, 9, 4.5, 6) + box(13, 9, 4.5, 6),
    "vector_template": lambda: g(path("M7.5 3Q3.8 12 7.5 21M16.5 3Q20.2 12 16.5 21"), w=1.5)
    + box(9, 4.5, 6, 6) + box(9, 13.5, 6, 6),
    "matrix_template": lambda: g(path("M6.5 3H3.5V21H6.5M17.5 3H20.5V21H17.5"), w=1.5)
    + box(6, 5.5, 5, 5.5) + box(13, 5.5, 5, 5.5) + box(6, 13, 5, 5.5) + box(13, 13, 5, 5.5),
}


# --------------------------------------------------------- style bar lines
def dashes(n, gap, y=12, x0=3, x1=21):
    seg = (x1 - x0 - gap * (n - 1)) / n
    return "".join(f"M{x0 + i * (seg + gap):.2f} {y}h{seg:.2f}" for i in range(n))


LINES = {
    "line_solid": lambda: g(path("M3 12H21"), w=2.5),
    "line_dashed_long": lambda: g(path("M3 12H21"), w=2.5, extra=' stroke-dasharray="6 3"'),
    "line_dashed_short": lambda: g(path("M3 12H21"), w=2.5, extra=' stroke-dasharray="2.5 3.5"'),
    "line_dotted": lambda: g(path("M4 12H21"), w=2.6, extra=' stroke-dasharray="0 4.2"'),
    "line_dash_dot": lambda: g(path("M3 12H21"), w=2.5, extra=' stroke-dasharray="6 3.5 0 3.5"'),
    # Mebis variants: the file names say how many segments the line has
    "lines_3": lambda: g(path(dashes(3, 2.5)), w=2.5, cap="butt"),
    "lines_4": lambda: g(path(dashes(4, 2.5)), w=2.5, cap="butt"),
    "lines_6": lambda: g(path("M4 12H21"), w=2.6, extra=' stroke-dasharray="0 3.4"'),
    "lines_dot_dash": lambda: g(path("M3 12H21"), w=2.5, extra=' stroke-dasharray="5 3 0 3"'),
}


# ------------------------------------------------------------ point styles
def diamond(cx, cy, r):
    return f"M{cx} {cy - r}L{cx + r} {cy}L{cx} {cy + r}L{cx - r} {cy}Z"


def triangle(direction):
    rot = {"up": 0, "right": 90, "down": 180, "left": 270}[direction]
    return (f'<g transform="rotate({rot} 12 12)">'
            + g(fill("M12 5.6L18.6 17.4H5.4Z"), w=1.2) + "</g>")


POINTS = {
    "point_dot": lambda: circle(12, 12, 5.2, SOFT) + g(circle(12, 12, 5.6), w=1.6),
    "point_no_outline": lambda: circle(12, 12, 6, INK),
    "point_circle": lambda: g(circle(12, 12, 5.5), w=2),
    "point_plus": lambda: g(path("M12 5.5V18.5M5.5 12H18.5"), w=2.2),
    "point_cross": lambda: g(path("M7.2 7.2L16.8 16.8M16.8 7.2L7.2 16.8"), w=2.2),
    "point_diamond_full": lambda: fill(diamond(12, 12, 7)),
    "point_diamond_empty": lambda: g(path(diamond(12, 12, 6.5)), w=2),
    "point_up": lambda: triangle("up"),
    "point_down": lambda: triangle("down"),
    "point_left": lambda: triangle("left"),
    "point_right": lambda: triangle("right"),
}


# ---------------------------------------------------------------- fillings
def pattern_icon(pid, pattern, outline=True):
    clip = f"{pid}-c"
    frame = rect(4, 4, 16, 16, rx=2)
    s = f'<clipPath id="{clip}">{frame}</clipPath>'
    s += f'<g clip-path="url(#{clip})">{pattern}</g>'
    if outline:
        s += g(frame, w=1.8)
    return s


def hatch(angle, step=3.5, w=1.2):
    lines = "".join(f"M{-12 + i * step} -2V26" for i in range(int(48 / step) + 1))
    return f'<g transform="rotate({angle} 12 12)">' + g(path(lines), w=w, cap="butt") + "</g>"


def dots_pattern(step=3.6, r=0.9):
    return "".join(circle(round(4 + step / 2 + i * step, 2), round(4 + step / 2 + j * step, 2), r, INK)
                   for i in range(5) for j in range(5))


def chess(step=4):
    return "".join(rect(4 + i * step, 4 + j * step, step, step, color=SOFT)
                   for i in range(4) for j in range(4) if (i + j) % 2 == 0)


def honeycomb(r=2.6):
    h = r * math.sqrt(3)
    out = ""
    for row in range(-1, 6):
        for col in range(-1, 6):
            cx = 4 + col * 1.5 * r
            cy = 4 + row * h + (h / 2 if col % 2 else 0)
            pts = [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k)))
                   for k in range(6)]
            out += "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
    return g(path(out), w=0.9)


def bricks():
    d = ""
    for row in range(4):
        y = 4 + row * 4
        d += f"M4 {y}H20"
        off = 0 if row % 2 == 0 else 3
        for k in range(4):
            x = 4 + off + k * 6
            d += f"M{x} {y}V{y + 4}"
    return g(path(d), w=1, cap="butt")


def weaving():
    """Basket weave: 3 x 3 cells, each with two strips running across or down."""
    out = ""
    step = 16 / 3
    for i in range(3):
        for j in range(3):
            x, y = 4 + i * step, 4 + j * step
            if (i + j) % 2 == 0:
                out += rect(round(x + 0.5, 2), round(y + 0.9, 2), round(step - 1, 2), 1.4, color=INK)
                out += rect(round(x + 0.5, 2), round(y + 3.0, 2), round(step - 1, 2), 1.4, color=INK)
            else:
                out += rect(round(x + 0.9, 2), round(y + 0.5, 2), 1.4, round(step - 1, 2), color=INK)
                out += rect(round(x + 3.0, 2), round(y + 0.5, 2), 1.4, round(step - 1, 2), color=INK)
    return out


FILLINGS = {
    "fill_solid": lambda pid: pattern_icon(pid, rect(4, 4, 16, 16, color=SOFT)),
    "fill_none": lambda pid: pattern_icon(pid, ""),
    "fill_hatch": lambda pid: pattern_icon(pid, hatch(45)),
    "fill_crosshatch": lambda pid: pattern_icon(pid, hatch(45) + hatch(-45)),
    "fill_dots": lambda pid: pattern_icon(pid, dots_pattern()),
    "fill_chess": lambda pid: pattern_icon(pid, chess()),
    "fill_honeycomb": lambda pid: pattern_icon(pid, honeycomb()),
    "fill_bricks": lambda pid: pattern_icon(pid, bricks()),
    "fill_weaving": lambda pid: pattern_icon(pid, weaving()),
    # Mebis "no filling": the frame with a diagonal stroke through it
    "fill_off": lambda pid: pattern_icon(pid, "") + g(path("M5.5 18.5L18.5 5.5"), w=1.8),
}


# ------------------------------------------------------ segment decorations
def seg(deco, line_from=3):
    return g(path(f"M{line_from} 12H21"), w=2) + deco


SEGMENT = {
    "seg_plain": lambda: g(path("M3 12H21"), w=2),
    "seg_stop": lambda: seg(g(path("M4 6V18"), w=2), 4),
    "seg_arrow": lambda: seg(g(path("M9.5 6L3.5 12L9.5 18"), w=2), 3.5),
    "seg_arrow_outline": lambda: seg(g(path("M3 12L11 6.8V17.2Z"), w=1.8), 11),
    "seg_arrow_filled": lambda: seg(g(fill("M3 12L11 6.8V17.2Z"), w=1.8), 10),
    "seg_circle_outline": lambda: seg(g(circle(7, 12, 4), w=1.8), 11),
    "seg_circle_filled": lambda: seg(circle(7, 12, 4.8, INK), 10),
    "seg_square_outline": lambda: seg(g(rect(3.2, 8.2, 7.6, 7.6), w=1.8), 10.8),
    "seg_square_filled": lambda: seg(rect(2.6, 7.6, 8.8, 8.8, color=INK), 10),
    "seg_diamond_outline": lambda: seg(g(path(diamond(7.5, 12, 5)), w=1.8), 12.5),
    "seg_diamond_filled": lambda: seg(fill(diamond(7.5, 12, 5.6)), 12),
    "seg_crows_foot": lambda: seg(g(path("M9.5 12L3.5 6M9.5 12L3.5 18M9.5 12H3.5"), w=2), 9.5),
}


# ---------------------------------------------------------- graphics views
def framed(inner):
    return g(rect(3.5, 3.5, 17, 17, rx=2), w=1.6) + inner


def isometric_lines():
    s = 8.0
    h = s * math.sqrt(3) / 2
    d = "".join(f"M-4 {3.5 + k * h:.2f}H28" for k in range(5))
    for k in range(-4, 8):
        x = 3.5 + k * s
        d += f"M{x:.2f} 3.5L{x + 30 / math.sqrt(3):.2f} 33.5"
        d += f"M{x:.2f} 3.5L{x - 30 / math.sqrt(3):.2f} 33.5"
    return d


GRIDS = {
    "grid_cartesian": lambda pid: framed(g(path("M9.17 4V20M14.83 4V20M4 9.17H20M4 14.83H20"), w=1.4)),
    "grid_minor": lambda pid: framed(g(path("M7.75 4V20M16.25 4V20M4 7.75H20M4 16.25H20"), w=1, color=SOFT)
                                    + g(path("M12 4V20M4 12H20"), w=1.6)),
    "grid_isometric": lambda pid: framed(f'<clipPath id="{pid}-c">{rect(3.5, 3.5, 17, 17, rx=2)}</clipPath>'
                                         f'<g clip-path="url(#{pid}-c)">'
                                         + g(path(isometric_lines()), w=1.1) + "</g>"),
    "grid_polar": lambda pid: g(circle(12, 12, 8.5) + circle(12, 12, 5), w=1.4)
    + g(path("M12 2.5V21.5M2.5 12H21.5M5.3 5.3L18.7 18.7M18.7 5.3L5.3 18.7"), w=1, color=SOFT)
    + circle(12, 12, 1.5, INK),
    "snap_to_grid": lambda pid: framed(g(path("M9.17 4V20M14.83 4V20M4 9.17H20M4 14.83H20"), w=1.1, color=SOFT))
    + circle(14.83, 9.17, 4.4, "#000") + circle(14.83, 9.17, 3, INK),
    "axes": lambda pid: g(path("M3 15H20.5M18 12.5L20.5 15L18 17.5M8 21V3.5M5.5 6L8 3.5L10.5 6"), w=1.8),
}


def cube_iso():
    c, r = (12, 12.2), 8.3
    pts = [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
           for a in (-90, -30, 30, 90, 150, 210)]
    hexa = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
    inner = f"M{c[0]} {c[1]}L{pts[3][0]:.2f} {pts[3][1]:.2f}M{c[0]} {c[1]}L{pts[1][0]:.2f} {pts[1][1]:.2f}" \
            f"M{c[0]} {c[1]}L{pts[5][0]:.2f} {pts[5][1]:.2f}"
    return g(path(hexa + inner), w=1.6)


PROJECTIONS = {
    "proj_orthographic": cube_iso,
    "proj_oblique": lambda: g(path("M9 3.5H20V14.5M9 3.5L4 8.5M20 3.5L15 8.5M20 14.5L15 19.5"), w=1.6)
    + g(path("M9 3.5V14.5H20M9 14.5L4 19.5"), w=1.2, color=SOFT)
    + g(rect(4, 8.5, 11, 11), w=1.6),
    "proj_perspective": lambda: g(path("M11.5 4.5H18.5V11.5M3.5 8.5L11.5 4.5M15.5 8.5L18.5 4.5M15.5 20L18.5 11.5"),
                                  w=1.6)
    + g(path("M11.5 4.5V11.5H18.5M3.5 20L11.5 11.5"), w=1.2, color=SOFT)
    + g(rect(3.5, 8.5, 12, 11.5), w=1.6),
}


# ---------------------------------------------------------- settings icons
def angle_rays():
    return g(path("M5 3.5V19H20.5"), w=2)


SETTINGS = {
    "axis_tick_major": lambda: g(path("M3 12H21"), w=1.8) + g(path("M6 8V16M12 8V16M18 8V16"), w=1.6),
    "axis_tick_major_minor": lambda: g(path("M3 12H21"), w=1.8) + g(path("M6 8V16M12 8V16M18 8V16"), w=1.6)
    + g(path("M9 10.2V13.8M15 10.2V13.8"), w=1.3),
    "axis_tick_off": lambda: g(path("M3 12H21"), w=1.8),
    "cell_border_thin": lambda: g(path("M12 5V19M5 12H19"), w=1, color=SOFT) + g(rect(4.5, 4.5, 15, 15), w=1.2),
    "cell_border_thick": lambda: g(path("M12 5V19M5 12H19"), w=1, color=SOFT) + g(rect(4.5, 4.5, 15, 15), w=3),
    "border_none": lambda: g(rect(4.5, 4.5, 15, 15), w=1.3, color=SOFT, extra=' stroke-dasharray="2 2.5"'),
    "border_thin": lambda: g(rect(4.5, 4.5, 15, 15, rx=1), w=1.2),
    "border_thick": lambda: g(rect(4.5, 4.5, 15, 15, rx=1), w=3.2),
    "right_angle_off": lambda: angle_rays() + g(path("M5 11A8 8 0 0 1 13 19"), w=1.6),
    "right_angle_rect": lambda: angle_rays() + rect(5, 11.5, 7.5, 7.5, color=FAINT)
    + g(path("M5 11.5H12.5V19"), w=1.6),
    "right_angle_dot": lambda: angle_rays() + g(path("M5 11A8 8 0 0 1 13 19"), w=1.6) + circle(8.4, 15.6, 1.5, INK),
    "right_angle_stroke": lambda: angle_rays() + g(path("M5 11.5H12.5V19"), w=1.6),
}


# ------------------------------------------------------------ other drawn
def table(x, y, w, h, rows, cols, lw=1.4):
    d = "".join(f"M{x} {y + h * i / rows:.2f}H{x + w}" for i in range(1, rows))
    d += "".join(f"M{x + w * j / cols:.2f} {y}V{y + h}" for j in range(1, cols))
    return g(rect(x, y, w, h, rx=1.5) + path(d), w=lw)


def bell(x0=2.5, x1=21.5, base=19, top=5):
    xm = (x0 + x1) / 2
    return (f"M{x0} {base}C{x0 + 4.5} {base} {xm - 4} {top} {xm} {top}"
            f"C{xm + 4} {top} {x1 - 4.5} {base} {x1} {base}")


def logo_ink():
    """Locus mark: a circle with a point on it, the point knocked out of the ring."""
    px, py = 12 + 7.5 * math.cos(math.radians(-40)), 12 + 7.5 * math.sin(math.radians(-40))
    return (g(circle(12, 12, 7.5), w=2.2) + circle(round(px, 2), round(py, 2), 4.6, "#000")
            + circle(round(px, 2), round(py, 2), 3, INK))


OTHER = {
    "angle": lambda: g(path("M20 19H4.5L15.5 5.5"), w=2) + g(path("M11.5 19A7 7 0 0 0 9 13.6"), w=1.6),
    "boxplot": lambda: g(path("M3 12H7.5M16.5 12H21M3 8.5V15.5M21 8.5V15.5"), w=1.8)
    + g(rect(7.5, 7, 9, 10, rx=1) + path("M11 7V17"), w=1.8),
    "histogram": lambda: g(path("M3 20.5H21"), w=1.6)
    + rect(4, 13, 3.6, 6.5, color=INK) + rect(8.2, 5, 3.6, 14.5, color=INK)
    + rect(12.4, 9, 3.6, 10.5, color=INK) + rect(16.6, 14.5, 3.6, 5, color=INK),
    "plane": lambda: fill("M3.5 18L8.5 6H20.5L15.5 18Z", FAINT) + g(path("M3.5 18L8.5 6H20.5L15.5 18Z"), w=1.8),
    "record_to_table": lambda: circle(4.5, 12, 2.5, INK) + g(path("M8 12H12.5M10.5 10L12.5 12L10.5 14"), w=1.6)
    + table(14.5, 4.5, 7, 15, 3, 1),
    "heading_column": lambda: rect(3.5, 4.5, 5.7, 15, color=SOFT) + table(3.5, 4.5, 17, 15, 3, 3),
    "heading_row": lambda: rect(3.5, 4.5, 17, 5, color=SOFT) + table(3.5, 4.5, 17, 15, 3, 3),
    "equal": lambda: g(path("M6 9.5H18M6 14.5H18"), w=2),
    "approx": lambda: g(path("M5.5 9.8C8 7.3 10 7.3 12 9.3S16 11.3 18.5 8.8"
                             "M5.5 15.2C8 12.7 10 12.7 12 14.7S16 16.7 18.5 14.2"), w=2),
    "fraction_digits": lambda: txt("1", L.SANS, 10, 12, 10, "middle") + g(path("M7.5 12H16.5"), w=1.6)
    + txt("2", L.SANS, 10, 12, 21.5, "middle"),
    "engineering": lambda: txt("10", L.SANS, 11.5, 2.5, 18.5) + txt("n", L.SERIF_IT, 9.5, 16, 11),
    "bell": lambda: fill(bell() + "Z", FAINT) + g(path(bell()), w=1.8) + g(path("M2 19.8H22"), w=1.4),
    "graphing": lambda: g(path("M4 3.5V20H20.5"), w=1.5) + g(path("M7 4.5C8.5 19 15.5 19 17 4.5"), w=2),
    "geometry": lambda: g(path("M5.5 18.5L12 5.5L19 16.5Z"), w=1.6)
    + circle(5.5, 18.5, 2.2, INK) + circle(12, 5.5, 2.2, INK) + circle(19, 16.5, 2.2, INK),
    "graphics2": lambda: g(path("M3.5 3.5V20.5H20.5"), w=1.5) + g(path("M5.5 16C9 5 11 5 13.5 12"), w=2)
    + txt("2", L.SANS, 10.5, 20.5, 11, "middle"),
    "graphics_plane": lambda: fill("M2.5 18.5L7.5 5.5H21.5L16.5 18.5Z", FAINT)
    + g(path("M2.5 18.5L7.5 5.5H21.5L16.5 18.5Z"), w=1.5) + g(path("M7.5 15C10 8.5 12 8.5 16.5 11"), w=1.8),
    "logo": logo_ink,
    "ellipse": lambda: g('<ellipse cx="12" cy="12" rx="9" ry="6"/>', w=2),
    "freeform": lambda: g(path("M3.5 16.5C5 10 8 6.5 10 8.5S8 17 11 17.5S15 9 17 8S20.5 12 20.5 14"), w=2),
    "curve": lambda: g(path("M3.5 19C7 19 7.5 5 12 5S17 19 20.5 19"), w=2),
    "mask": lambda: g(circle(9, 12, 6), w=1.8) + rect(12.5, 4.5, 9, 15, rx=1.5, color="#000")
    + rect(13.5, 5.5, 7, 13, rx=1, color=INK),
    "parallelogram": lambda: g(path("M3 18L8 6H21L16 18Z"), w=2),
    "pentagon": lambda: g(path("M12 3.5L20.5 9.7L17.3 19.7H6.7L3.5 9.7Z"), w=2),
    "stadium": lambda: g(rect(2.5, 7, 19, 10, rx=5), w=2),
}

MASKED = {**KEYBOARD, **LINES, **POINTS, **SEGMENT, **PROJECTIONS, **SETTINGS, **OTHER}
MASKED_WITH_ID = {**FILLINGS, **GRIDS}


# ------------------------------------------------------ multi-colour icons
def logo_color():
    px, py = 12 + 7.5 * math.cos(math.radians(-40)), 12 + 7.5 * math.sin(math.radians(-40))
    return (f'<circle cx="12" cy="12" r="7.5" fill="none" stroke="{L.PRIMARY}" stroke-width="2.2"/>'
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3.9" fill="#fff"/>'
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3" fill="{L.ACCENT}"/>')


def check_on_swatch():
    d = "M6 12.5L10 16.5L18 7.5"
    return (f'<path d="{d}" fill="none" stroke="{L.TEXT}" stroke-opacity=".75" stroke-width="5"'
            f' stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"'
            f' stroke-linejoin="round"/>')


def curve_axes():
    return f'<path d="M3 20.5H21M4.5 3V21" fill="none" stroke="{L.BORDER}" stroke-width="1.2"/>'


def fx_curve(color=L.PRIMARY):
    return (f'<path d="M3.5 18.5C7 18.5 8.5 6 12 6S17 13 20.5 9" fill="none" stroke="{color}"'
            f' stroke-width="2" stroke-linecap="round"/>')


def pt(x, y, color=L.POINT):
    return f'<circle cx="{x}" cy="{y}" r="2.4" fill="{color}" stroke="#fff" stroke-width="1"/>'


RAW = {
    "logo_color": logo_color,
    "check_on_swatch": check_on_swatch,
    "osculating_circle": lambda: curve_axes()
    + f'<circle cx="12" cy="11.2" r="5.2" fill="none" stroke="{L.ACCENT}" stroke-width="1.8"/>'
    + fx_curve() + pt(12, 6),
    "tangent_line": lambda: curve_axes() + fx_curve()
    + f'<path d="M4 6H20" stroke="{L.ACCENT}" stroke-width="1.8" stroke-linecap="round"/>' + pt(12, 6),
    "xy_segments": lambda: curve_axes() + fx_curve()
    + f'<path d="M4.5 9.8H14.6V20.5" fill="none" stroke="{L.ACCENT}" stroke-width="1.6"'
      f' stroke-dasharray="2 2"/>' + pt(14.6, 9.8),
    "cdf": lambda: curve_axes()
    + f'<path d="M4.5 19.5C10 19.5 10 5 15 5H21" fill="none" stroke="{L.PRIMARY}" stroke-width="2"'
      f' stroke-linecap="round"/>',
    "graph_view": lambda: curve_axes() + fx_curve(),
    "trace": lambda: "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{L.NEUTRAL}" fill-opacity="{o}"/>'
        for x, y, r, o in ((4.5, 18.5, 1.6, .25), (7.5, 14.2, 1.8, .4), (11.2, 11, 2, .55), (15.2, 9.2, 2.2, .7)))
    + pt(19.5, 8.6, L.NEUTRAL),
    "marble_shown": lambda: f'<circle cx="12" cy="12" r="7" fill="{L.POINT}" stroke="#fff" stroke-width="1.5"/>',
    "marble_hidden": lambda: f'<circle cx="12" cy="12" r="6.5" fill="#fff" stroke="{L.NEUTRAL}" stroke-width="2"/>',
    "corner1": lambda: corner(4, 18),
    "corner2": lambda: corner(20, 18),
    "corner4": lambda: corner(4, 6),
    "pointer_up": lambda: f'<path d="M0 24L12 4L24 24" fill="#fff" stroke="{L.BORDER}" stroke-width="2"/>',
    "pointer_left": lambda: f'<path d="M24 0L4 12L24 24" fill="#fff" stroke="{L.BORDER}" stroke-width="2"/>',
    "pointer_right": lambda: f'<path d="M0 0L20 12L0 24" fill="#fff" stroke="{L.BORDER}" stroke-width="2"/>',
    "missing_image": lambda: f'<rect x="1" y="1" width="22" height="22" rx="3" fill="{L.SURFACE_ALT}"'
    f' stroke="{L.BORDER}"/>'
    + f'<g transform="translate(4 4) scale(.6667)" fill="{L.NEUTRAL}">'
    + "".join(f'<path d="{d}"/>' for d in L.material_paths("question_mark")) + "</g>",
    "video_placeholder": lambda: "",  # built at raster size in build_icons.py
}


def corner(x, y):
    return (f'<rect x="4" y="6" width="16" height="12" fill="{L.PRIMARY_TINT}" stroke="{L.NEUTRAL}"'
            f' stroke-width="1.5"/>' + pt(x, y, L.ACCENT))

#!/usr/bin/env python3
"""Contact sheet of the drawn icons, for review in a browser.

Usage: python3 tools/icons/sheet.py [out.html] [--filter <substring>] [--shot <png> [--scale 2]]

Each icon is shown at its display size, at 2x, and "tinted": the SVG with
`style="fill: #0e7c86"` on the root, which is what SVGResource.withFill does
when a tool is selected, so parts that follow the selection colour are visible.
"""
import base64
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def data_uri(path, text=None):
    if text is not None:
        return "data:image/svg+xml;base64," + base64.b64encode(text.encode()).decode()
    with open(path, "rb") as f:
        raw = f.read()
    mime = "image/svg+xml" if path.endswith(".svg") else "image/png"
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def tinted(text, colour="#0e7c86"):
    return re.sub(r"<svg ", f'<svg style="fill: {colour}" ', text, count=1)


def main():
    args = sys.argv[1:]
    out = args[0] if args and not args[0].startswith("--") else "/tmp/locus-icons-sheet.html"
    flt = args[args.index("--filter") + 1] if "--filter" in args else None
    with open(os.path.join(ROOT, "tools/images-drawn.txt")) as f:
        files = [line.strip() for line in f if line.strip()]
    if flt:
        files = [x for x in files if flt in x]
    if "--slice" in args:
        a, b = args[args.index("--slice") + 1].split(":")
        files = files[int(a or 0):int(b) if b else None]
    groups = {}
    for rel in files:
        if flt and flt not in rel:
            continue
        short = rel.split("/resources/", 1)[1]
        short = short.replace("org/geogebra/common/", "").replace("org/geogebra/web/full/gui/images/", "")
        groups.setdefault(os.path.dirname(short), []).append((rel, os.path.basename(short)))
    parts = ["""<!doctype html><meta charset="utf-8"><title>Locus icons</title><style>
body{font:12px/1.3 sans-serif;margin:16px;color:#1c2024;background:#fff}
h2{font-size:14px;margin:18px 0 6px;border-bottom:1px solid #d6dade}
.g{display:flex;flex-wrap:wrap;gap:6px}
.c{width:148px;border:1px solid #eef0f2;border-radius:6px;padding:6px;display:flex;
flex-direction:column;align-items:center;gap:4px}
.r{display:flex;align-items:center;gap:8px}
.t{background:#e2f3f4;border-radius:4px;padding:2px}
.n{font-size:10px;color:#5b6470;word-break:break-all;text-align:center}
.big img{max-width:136px}
</style>"""]
    for group, items in groups.items():
        parts.append(f"<h2>{html.escape(group)} ({len(items)})</h2><div class=g>")
        for rel, name in items:
            p = os.path.join(ROOT, rel)
            if rel.endswith(".svg"):
                with open(p) as f:
                    text = f.read()
                m = re.search(r'width="([\d.]+)"', text)
                w = float(m.group(1)) if m else 24
                if w > 64:
                    parts.append(f'<div class="c big"><img src="{data_uri(p)}">'
                                 f'<div class=n>{html.escape(name)}</div></div>')
                    continue
                disp = 24
                parts.append(
                    f'<div class=c><div class=r><img src="{data_uri(p)}" width={disp} height={disp}>'
                    f'<img src="{data_uri(p)}" width={disp * 2} height={disp * 2}>'
                    f'<span class=t><img src="{data_uri(p, tinted(text))}" width={disp} height={disp}></span>'
                    f'</div><div class=n>{html.escape(name)}</div></div>')
            else:
                parts.append(f'<div class=c><div class=r><img src="{data_uri(p)}"></div>'
                             f'<div class=n>{html.escape(name)}</div></div>')
        parts.append("</div>")
    with open(out, "w") as f:
        f.write("".join(parts))
    print(out)
    if "--shot" in args:
        shot = args[args.index("--shot") + 1]
        scale = float(args[args.index("--scale") + 1]) if "--scale" in args else 1
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(executable_path="/usr/bin/google-chrome")
            pg = b.new_page(viewport={"width": 1260, "height": 800}, device_scale_factor=scale)
            pg.goto("file://" + out)
            pg.wait_for_timeout(500)
            pg.screenshot(path=shot, full_page=True)
            b.close()
        print(shot)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render a contact sheet of the icons in tools/images-sourced.txt.

Each icon is shown at its intrinsic size on white, at 48 px on white, on the
dark primary colour, and recoloured the way SVGResourcePrototype.withFill does
it (style="fill: ..." on the root element), so recolouring problems show up.

Usage: python3 tools/icons/contact_sheet.py <out.png> [substring,substring,...]
"""
import base64
import html
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def data_url(path):
    raw = (ROOT / path).read_bytes()
    mime = {"svg": "image/svg+xml", "png": "image/png", "gif": "image/gif"}[path.rsplit(".", 1)[1]]
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def recoloured(path):
    svg = (ROOT / path).read_text()
    svg = svg.replace("<svg ", '<svg style="fill: #c62828" ', 1)
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def main():
    out = sys.argv[1]
    filters = sys.argv[2].split(",") if len(sys.argv) > 2 else [""]
    paths = [p.strip() for p in (ROOT / "tools/images-sourced.txt").read_text().splitlines()
             if p.strip() and any(f in p for f in filters)]
    cells = []
    for p in paths:
        url = data_url(p)
        rec = f'<img src="{recoloured(p)}" width="24">' if p.endswith(".svg") else ""
        label = html.escape(p.split("/icons/")[-1].replace("svg/web/matDesignIcons/", "")
                            .replace("svg/web/", "").split("/images/")[-1])
        cells.append(
            f'<div class="c"><div class="row"><img src="{url}">'
            f'<img src="{url}" width="48"><span class="dark"><img src="{url}" width="24"></span>'
            f'{rec}</div><div class="l">{label}</div></div>')
    page = ("<html><head><style>body{margin:8px;font:10px sans-serif;background:#fff}"
            ".g{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}"
            ".c{border:1px solid #ddd;padding:4px}.row{display:flex;gap:6px;align-items:center;min-height:50px}"
            ".dark{background:#0e7c86;padding:4px;display:inline-flex}.l{word-break:break-all;color:#333}"
            "</style></head><body><div class='g'>" + "".join(cells) + "</div></body></html>")
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page(viewport={"width": 1400, "height": 800})
        pg.set_content(page)
        pg.wait_for_timeout(500)
        pg.screenshot(path=out, full_page=True)
        b.close()
    print(f"{len(paths)} icons -> {out}")


if __name__ == "__main__":
    main()

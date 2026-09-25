#!/usr/bin/env python3
"""Load a Locus page headlessly, print console errors and save a screenshot.

Usage: tools/shot.py <url> <out.png> [width] [height] [wait-ms] [--js <expr>]
"""
import sys
from playwright.sync_api import sync_playwright

url, out = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
height = int(sys.argv[4]) if len(sys.argv) > 4 else 800
wait = int(sys.argv[5]) if len(sys.argv) > 5 else 8000
expr = sys.argv[sys.argv.index("--js") + 1] if "--js" in sys.argv else None
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    page = browser.new_page(viewport={"width": width, "height": height})
    page.on("console", lambda m: m.type in ("error", "warning") and print(f"[{m.type}] {m.text[:300]}"))
    page.on("pageerror", lambda e: print(f"[pageerror] {str(e)[:300]}"))
    page.on("requestfailed", lambda r: print(f"[requestfailed] {r.url}"))
    page.goto(url)
    page.wait_for_timeout(wait)
    if expr:
        print(page.evaluate(expr))
        page.wait_for_timeout(1500)
    page.screenshot(path=out)
    browser.close()

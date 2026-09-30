"""Fetch report cover thumbnails for GAIN examples.

Reads data/gain_examples.csv. For every example that has a source_url but no cover yet:
  - PDF  -> renders page 1 to covers/exNNN.png (about 600 px wide)
  - HTML -> saves the page's og:image / twitter:image preview as covers/exNNN.png
Writes data/cover_fetch_log.csv. Every new image must be checked by eye before
its cover_status is set to "ok" (logos, icons and stock photos are common).

Usage:  python tools/fetch_covers.py [--only ex113,ex115] [--force]
Needs:  pip install pymupdf requests
"""

import csv
import os
import re
import sys
from urllib.parse import urljoin

import pymupdf
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "data", "gain_examples.csv")
LOG = os.path.join(ROOT, "data", "cover_fetch_log.csv")
OUT = os.path.join(ROOT, "covers")
HEADERS = {"User-Agent": "Mozilla/5.0 (EGRISS GAIN cover check; +https://egrisstats.org)"}
WIDTH = 600


def render_pdf(data, path):
    doc = pymupdf.open(stream=data, filetype="pdf")
    page = doc[0]
    zoom = WIDTH / page.rect.width
    page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(path)
    return "pdf page 1 of %d" % doc.page_count


def save_image(data, path):
    pix = pymupdf.Pixmap(data)
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    if pix.n > 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    pix.save(path)


def preview_image(html, base):
    for prop in ("og:image", "twitter:image", "og:image:url"):
        m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)' % re.escape(prop), html, re.I) \
            or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']' % re.escape(prop), html, re.I)
        if m:
            return urljoin(base, m.group(1))
    return None


def main():
    only = set()
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    force = "--force" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(EXAMPLES, encoding="utf-8")))
    log = []
    for r in rows:
        ex, url = r["ex_id"], r["source_url"].strip()
        if not url or (only and ex not in only):
            continue
        if not force and (r["cover_status"].startswith(("ok", "rejected"))):
            continue
        path = os.path.join(OUT, ex + ".png")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=45, allow_redirects=True)
            resp.raise_for_status()
            ctype = resp.headers.get("content-type", "").lower()
            if "pdf" in ctype or resp.content[:4] == b"%PDF":
                how = render_pdf(resp.content, path)
            else:
                img = preview_image(resp.text, resp.url)
                if not img:
                    log.append([ex, url, "no cover: web page without a preview image", ctype])
                    print(ex, log[-1][2], flush=True)
                    continue
                ir = requests.get(img, headers=HEADERS, timeout=45)
                ir.raise_for_status()
                save_image(ir.content, path)
                how = "page preview image " + img
            log.append([ex, url, "saved (check by eye): " + how, ctype])
        except Exception as e:  # keep going; the log records every failure
            log.append([ex, url, "failed: %s" % str(e)[:160], ""])
        print(ex, log[-1][2][:100], flush=True)
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ex_id", "source_url", "result", "content_type"])
        w.writerows(log)


if __name__ == "__main__":
    main()

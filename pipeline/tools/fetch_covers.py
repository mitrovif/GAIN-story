"""Find a cover image for GAIN examples.

Reads data/gain_examples.csv. For every example with a usable link and no checked cover, tries in order:
  1. pdf        - the link is a PDF: render page 1
  2. page-pdf   - a web page that links to a report PDF matching the example's title: render its page 1
  3. page-cover - a web page with an image labelled as a cover ("cover", "portada", "couverture", ...)
  4. screenshot - a screenshot of the web page itself (cookie banners hidden, never accepted)
Sites that block scripts are retried through a headless browser (Playwright).
Writes covers/exNNN.png and data/cover_fetch_log.csv (method used for each).
Every new image must be checked by eye before its cover_status is set to "ok".

Links found by gain-evidence-pipeline (tools/import_pipeline_links.py) are tried after the row's own link;
a report the pipeline already downloaded is rendered first when --lake points at its data_lake folder.

Usage:  python tools/fetch_covers.py [--only ex113,ex115] [--force] [--no-screenshots] [--lake <data_lake>]
Needs:  pip install pymupdf requests beautifulsoup4 playwright && python -m playwright install chromium
"""

import csv
import os
import re
import sys
import unicodedata
from urllib.parse import urljoin

import pymupdf
import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "data", "gain_examples.csv")
LOG = os.path.join(ROOT, "data", "cover_fetch_log.csv")
OUT = os.path.join(ROOT, "covers")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "en,fr;q=0.8,es;q=0.7"}
WIDTH = 600
SKIP_STATUS = ("ok", "rejected: cover marked not for circulation", "rejected: different topic")
COVER_WORDS = ("cover", "portada", "couverture", "capa", "forside", "titelblad", "copertina", "okladka", "thumbnail", "publication")
LOGO_WORDS = ("logo", "icon", "favicon", "sprite", "share", "default", "opengraph", "placeholder", "avatar", "flag")
STOP = set("the and for with from into over under their this that los las del des les une par pour sur dans con por para una".split())

HIDE_OVERLAYS_JS = """
() => {
  const bad = /(cookie|consent|gdpr|onetrust|cmp|didomi|truste|cookiebot|privacy-banner|newsletter-popup)/i;
  for (const el of document.querySelectorAll('body *')) {
    const tag = (el.id || '') + ' ' + (typeof el.className === 'string' ? el.className : '') + ' ' + (el.getAttribute('aria-label') || '');
    const st = getComputedStyle(el);
    if (bad.test(tag)) { el.style.setProperty('display', 'none', 'important'); continue; }
    if ((st.position === 'fixed' || st.position === 'sticky') && el.offsetHeight > window.innerHeight * 0.3) {
      el.style.setProperty('display', 'none', 'important');
    }
  }
  document.documentElement.style.overflow = 'auto'; document.body.style.overflow = 'auto';
}
"""


def words(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return {w for w in re.findall(r"[a-z0-9]{4,}", s) if w not in STOP}


def render_pdf(data, path):
    doc = pymupdf.open(stream=data, filetype="pdf")
    page = doc[0]
    zoom = WIDTH / page.rect.width
    page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom)).save(path)
    return doc.page_count


def save_image(data, path):
    pix = pymupdf.Pixmap(data)
    if pix.alpha:
        pix = pymupdf.Pixmap(pix, 0)
    if pix.n > 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if pix.width > 900:
        pix.shrink(1)
    pix.save(path)


def page_candidates(html, base, title):
    """Report PDFs linked from the page (best title match first) and cover-like images."""
    soup = BeautifulSoup(html, "html.parser")
    want = words(title)
    pdfs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".pdf" not in href.lower():
            continue
        text = a.get_text(" ", strip=True) + " " + href
        score = len(want & words(text))
        if re.search(r"report|rapport|informe|relatorio|survey|enquete|encuesta|census|recensement|censo|results|resultats|resultados", text, re.I):
            score += 1
        if re.search(r"questionnaire|cuestionario|form|annex|manual", text, re.I) and not re.search(r"questionnaire|manual", title or "", re.I):
            score -= 1
        pdfs.append((score, urljoin(base, href)))
    pdfs.sort(key=lambda x: -x[0])
    good_pdfs = [u for s, u in pdfs if s >= 2] or ([pdfs[0][1]] if len(pdfs) == 1 and pdfs[0][0] >= 1 else [])
    imgs = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        label = " ".join([src, img.get("alt", ""), " ".join(img.get("class", [])), img.get("title", "")]).lower()
        if src and any(w in label for w in COVER_WORDS) and not any(w in label for w in LOGO_WORDS):
            imgs.append(urljoin(base, src))
    return good_pdfs[:2], imgs[:2]


class Browser:
    """Headless Chromium, started only when needed."""

    def __init__(self):
        self.pw = self.browser = self.ctx = None

    def _start(self):
        if not self.ctx:
            from playwright.sync_api import sync_playwright
            self.pw = sync_playwright().start()
            # CHROME_PATH: use an installed Chrome instead of Playwright's own download
            self.browser = self.pw.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
            self.ctx = self.browser.new_context(viewport={"width": 1280, "height": 900}, user_agent=UA, locale="en-GB")

    def get(self, url):
        self._start()
        r = self.ctx.request.get(url, timeout=60000)
        return r.status, r.headers.get("content-type", ""), r.body()

    def screenshot(self, url, path):
        self._start()
        page = self.ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            page.evaluate(HIDE_OVERLAYS_JS)
            page.wait_for_timeout(500)
            page.screenshot(path=path, clip={"x": 0, "y": 0, "width": 1280, "height": 900})
            pix = pymupdf.Pixmap(path)
            pix.shrink(1)
            pix.save(path)
            return page.title()
        finally:
            page.close()

    def close(self):
        if self.browser:
            self.browser.close()
            self.pw.stop()


def cover_url(r):
    """Replacement link wins when it matches (exact, related or a section page); news articles are skipped."""
    rep = (r.get("replacement_url") or "").strip()
    if rep and r.get("replacement_match") in ("exact", "related", "landing") and not r.get("replacement_source", "").startswith("news"):
        return rep
    if rep and r.get("replacement_source", "").startswith("news"):
        return ""
    return r["source_url"].strip()


def fetch_one(r, url, path, br, screenshots):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=45, allow_redirects=True)
        resp.raise_for_status()
        status, ctype, body, final = resp.status_code, resp.headers.get("content-type", "").lower(), resp.content, resp.url
    except Exception:
        status, ctype, body = br.get(url)  # blocked or slow for scripts: retry as a browser
        final = url
        if status >= 400:
            raise RuntimeError("HTTP %d (also through the browser)" % status)
    if "pdf" in ctype.lower() or body[:4] == b"%PDF":
        return "pdf: page 1 of %d" % render_pdf(body, path)
    html = body.decode("utf-8", "ignore")
    pdfs, imgs = page_candidates(html, final, r["title"])
    for u in pdfs:
        try:
            pr = requests.get(u, headers=HEADERS, timeout=60)
            if pr.ok and pr.content[:4] == b"%PDF":
                return "page-pdf: page 1 of %d, %s" % (render_pdf(pr.content, path), u)
        except Exception:
            pass
    for u in imgs:
        try:
            ir = requests.get(u, headers=HEADERS, timeout=45)
            if ir.ok:
                save_image(ir.content, path)
                return "page-cover: " + u
        except Exception:
            pass
    if screenshots:
        return "screenshot: " + (br.screenshot(final, path) or final)[:80]
    return "none: web page without a report PDF or cover image"


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else set()
    force, screenshots = "--force" in sys.argv, "--no-screenshots" not in sys.argv
    lake = sys.argv[sys.argv.index("--lake") + 1] if "--lake" in sys.argv else ""
    os.makedirs(OUT, exist_ok=True)
    rows = list(csv.DictReader(open(EXAMPLES, encoding="utf-8")))
    br, log = Browser(), []
    try:
        for r in rows:
            ex = r["ex_id"]
            urls = [u for u in dict.fromkeys([cover_url(r), r.get("pipeline_url", "").strip()]) if u]
            local = os.path.join(lake, r["pipeline_pdf"]) if lake and r.get("pipeline_pdf") else ""
            if not (urls or local) or (only and ex not in only):
                continue
            if not force and r["cover_status"].startswith(SKIP_STATUS):
                continue
            path = os.path.join(OUT, ex + ".png")
            result, url = "none", ""
            if local and os.path.exists(local):
                url = local
                result = "saved (check by eye) pipeline-pdf: page 1 of %d" % render_pdf(open(local, "rb").read(), path)
            for u in ([] if result.startswith("saved") else urls):
                url = u
                try:
                    how = fetch_one(r, u, path, br, screenshots)
                    result = ("saved (check by eye) " if not how.startswith("none") else "") + how
                except Exception as e:  # keep going; the log records every failure
                    result = "failed: %s" % str(e).splitlines()[0][:160]
                if result.startswith("saved"):
                    break
            log.append([ex, url, result])
            print(ex, result[:110], flush=True)
    finally:
        br.close()
        with open(LOG, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ex_id", "url", "result"])
            w.writerows(log)


if __name__ == "__main__":
    main()

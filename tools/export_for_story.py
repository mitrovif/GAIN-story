"""Export checked covers and source links for the GAIN scrollytelling page.

Writes data/story_covers.json, keyed by 0-based roster row (the id the story uses):
  {"112": {"ex": "ex113", "link": "https://...", "cover": "covers/ex113.png", "title": "..."}}
Only covers with cover_status starting "ok" are included; links are included whenever present.

Usage:  python tools/export_for_story.py
"""

import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "gain_examples.csv"), encoding="utf-8")))
out = {}
for r in rows:
    has_cover = r["cover_status"].startswith("ok") and r["cover_file"]
    rep = r.get("replacement_url", "").strip()
    link = rep if rep and r.get("replacement_match") in ("exact", "related", "landing") else r["source_url"].strip()
    if not (has_cover or link):
        continue
    out[str(int(r["roster_row"]) - 1)] = {
        "ex": r["ex_id"],
        "title": r["title"],
        "country": r["country"],
        "link": link,
        "link_match": r.get("replacement_match", "") if link == rep else "original",
        "link_source": r.get("replacement_source", "") if link == rep else "",
        "cover": r["cover_file"] if has_cover else "",
        "cover_note": r["cover_status"] if has_cover else "",
        "kind": ("screenshot" if "screenshot" in r["cover_status"] else "cover") if has_cover else "",
    }
path = os.path.join(ROOT, "data", "story_covers.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("%d examples with a link or cover -> %s" % (len(out), path))

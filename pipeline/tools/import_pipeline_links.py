"""Bring in links found by gain-evidence-pipeline (lake/ steps) for examples that still have no cover.

The pipeline (https://github.com/mitrovif/gain-evidence-pipeline) keeps its outputs in a local data_lake
folder, not on GitHub. Same example IDs (exNNN = 1-based roster row). Reads, in order of trust:
  1. lake_drill.csv             verdict MATCH   - the specific page, drilled from an NSO portal and LLM-checked
  2. lake_websearch_found.csv   verdict MATCH   - web search result, LLM-checked as the same product
  3. lake_roster.csv all_urls + gain_examples_with_data_links.csv - links reported by respondents (questionnaires skipped)
  4. lake_websearch_found.csv   verdict PARTIAL - the right office's site, not the exact page (landing)
  and store/<ex>/*.pdf          - a report the pipeline already downloaded (rendered by fetch_covers.py)
Fills pipeline_url, pipeline_match (exact / landing), pipeline_source, pipeline_pdf. Never overwrites source_url
or replacement_url. Rows with a checked or rejected cover are left alone.

Usage:  python tools/import_pipeline_links.py "<path to data_lake>"
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES = os.path.join(ROOT, "data", "gain_examples.csv")
NEW_COLS = ["pipeline_url", "pipeline_match", "pipeline_source", "pipeline_pdf"]


def read(lake, name):
    path = os.path.join(lake, name)
    return {r["example_id"]: r for r in csv.DictReader(open(path, encoding="utf-8-sig"))} if os.path.exists(path) else {}


def main():
    lake = sys.argv[1]
    drill, ws = read(lake, "lake_drill.csv"), read(lake, "lake_websearch_found.csv")
    roster, dlinks = read(lake, "lake_roster.csv"), read(lake, "gain_examples_with_data_links.csv")
    rows = list(csv.DictReader(open(EXAMPLES, encoding="utf-8")))
    cols = list(rows[0].keys()) + [c for c in NEW_COLS if c not in rows[0]]
    n = 0
    for r in rows:
        for c in NEW_COLS:
            r.setdefault(c, "")
        ex = r["ex_id"]
        if r["cover_status"].startswith(("ok", "rejected")):
            continue
        known = {r["source_url"].strip(), r["replacement_url"].strip()}
        quest = (roster.get(ex, {}).get("link_questionnaire") or "").strip()
        reported = [u for u in (roster.get(ex, {}).get("all_urls", "") + " " + dlinks.get(ex, {}).get("all_urls", "")).split()
                    if u.startswith("http") and u not in known and u != quest]
        pick = None
        if drill.get(ex, {}).get("verdict") == "MATCH" and drill[ex]["drilled_url"]:
            pick = (drill[ex]["drilled_url"], "exact", "pipeline: drilled from NSO portal, LLM-checked")
        elif ws.get(ex, {}).get("verdict") == "MATCH" and ws[ex]["found_url"]:
            pick = (ws[ex]["found_url"], "exact", "pipeline: web search, LLM-checked")
        elif reported:
            pick = (reported[0], "exact", "pipeline: link reported in the GAIN roster")
        elif ws.get(ex, {}).get("verdict") == "PARTIAL" and ws[ex]["found_url"]:
            pick = (ws[ex]["found_url"], "landing", "pipeline: office website found by web search")
        store = os.path.join(lake, "store", ex)
        pdfs = sorted(f for f in os.listdir(store) if f.lower().endswith(".pdf")) if os.path.isdir(store) else []
        if pick and pick[0] not in known:
            r["pipeline_url"], r["pipeline_match"], r["pipeline_source"] = pick
        if pdfs:
            r["pipeline_pdf"] = "store/%s/%s" % (ex, ("source.pdf" if "source.pdf" in pdfs else pdfs[0]))
        n += bool(r["pipeline_url"] or r["pipeline_pdf"])
    with open(EXAMPLES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print("examples with a pipeline link or downloaded report:", n)


if __name__ == "__main__":
    main()

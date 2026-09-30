# GAIN example covers and source links

A workstream of the EGRISS Secretariat to find, for each **GAIN example** (2021–2025), a public
**source link** and a **report cover** where one exists.

Covers and links feed:
- **"Counted, and counting"**, the GAIN 2021–2025 scrollytelling page: each point of light opens a
  standard card with the example's cover thumbnail and an *Open the source ↗* link.
- **The GAIN SDG map** ([gain_sdg_workstream](https://github.com/mitrovif/gain_sdg_workstream)): GAIN-example cards.
- **Outreach** for the next GAIN round: "your work is in the global record".

## Where things stand (30 Sep 2026)

| | Examples |
|---|---|
| GAIN examples, 2021–2025 | 413 |
| With a source link | 44 |
| Covers checked and in use | **12** |
| Rejected after checking | 10 (logos, icons, stock photos, an inner page, a price list) |
| Still missing a cover | 391 |

## Files

| Path | What it is |
|---|---|
| `data/gain_examples.csv` | One row per GAIN example: year, country, organisation, title, lead, use of the Recommendations, `source_url`, `url_found_by`, `cover_file`, `cover_status`, `checked_on` |
| `covers/exNNN.png` | Checked cover thumbnails |
| `data/cover_fetch_log.csv` | What happened with each link on the last fetch |
| `data/story_covers.json` | Export for the scrollytelling page (`tools/export_for_story.py`) |
| `tools/fetch_covers.py` | Renders page 1 of linked PDFs, or saves a web page's preview image |
| `tools/export_for_story.py` | Builds `story_covers.json` from checked rows |

**IDs:** `exNNN` is the 1-based row in the GAIN group roster (`analysis_ready_group_roster.csv`);
`ex113` is row 113, the Burkina Faso INSD survey of IDP and host households. The story uses the
0-based row (112).

## Workflow

1. **Add links.** Fill `source_url` (and `url_found_by`) in `data/gain_examples.csv`: from the respondent,
   the NSO website, the UNHCR or World Bank microdata libraries, or a web search on title + organisation + country.
2. **Fetch.** `pip install pymupdf requests`, then `python tools/fetch_covers.py`.
3. **Check every new image by eye.** Set `cover_status` to `ok`, `ok: <note>` (e.g. questionnaire first page)
   or `rejected: <reason>`; delete rejected images; fill `checked_on`.
4. **Export.** `python tools/export_for_story.py`, then send the new covers and `story_covers.json` to the
   scrollytelling page.

## Log

- **30 Sep 2026:** links found by web search for the 7 featured story examples; covers for Burkina Faso INSD (ESEP-PDI 2024), the African Union 4th School on Migration Statistics report, and the UBOS 2024 census report. Still to check by hand in a browser: Nigeria NBS (microdata catalogue), Philippines PSA (press release), Thailand (2025 module not yet published).

## Priorities

1. Examples in the scrollytelling story: Burkina Faso INSD (`ex113`), Nigeria NBS (`ex045`),
   Philippines PSA (`ex324`), Belgium (`ex089`), Uganda 2024 census (`ex319`), Thailand LFS migration module (`ex128`),
   African Union school (`ex124`).
2. Examples on the SDG map (government-produced, data year 2018+).
3. The 18 links that failed on the first pass (403 blocks, timeouts, landing pages): retry by hand in a browser.
4. Everything else, newest round first.

## Rules

- Only **public** reports and pages; no microdata or restricted documents.
- Covers are shown as small thumbnails, always linked to the source and credited to the producer.
  Confirm this use with Secretariat communications; keep photo credits (e.g. © UNHCR) verbatim.
- Prefer the specific publication over a landing page (`ons.gov.uk/peoplepopulationandcommunity/` is not enough).

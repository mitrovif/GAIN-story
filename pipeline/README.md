# GAIN example covers and source links

A workstream of the EGRISS Secretariat to find, for each **GAIN example** (2021–2025), a public
**source link** and a **report cover** where one exists.

Covers and links feed:
- **"Counted, and counting"**, the GAIN 2021–2025 scrollytelling page: each point of light opens a
  standard card with the example's cover thumbnail and an *Open the source ↗* link.
- **The GAIN SDG map** ([gain_sdg_workstream](https://github.com/mitrovif/gain_sdg_workstream)): GAIN-example cards.
- **Outreach** for the next GAIN round: "your work is in the global record".

## Where things stand (30 Sep 2026)

**Rule: an image or link is used only when the link opens the example's own document or page.**
Related documents (another edition, another product by the same office) and section or home pages are held back.

| | Examples |
|---|---|
| GAIN examples, 2021–2025 | 413 |
| With a link to the example's own document (used in the story) | 181 |
| Covers or page screenshots checked and in use | **95** (56 report covers or first pages, 39 page screenshots) |
| Held back: image fine, but the link is only a related or section page | 42 |
| No link anywhere yet (119 institution-led: UNHCR, JDC, IDMC, World Bank, IOM, JIPS, ECOWAS...) | about 150 |

## Files

| Path | What it is |
|---|---|
| `data/gain_examples.csv` | One row per GAIN example: year, country, organisation, title, lead, use of the Recommendations, `source_url` (as first collected), `url_found_by`, the `replacement_*` columns (a better link found on the NSO or organisation website: `replacement_url`, `replacement_match` exact / related / landing / none, `replacement_source` official / partner / news, `replacement_checked`, `replacement_note`, `replacement_on`), `cover_file`, `cover_status` (`ok…` in use, `held:` link not the document, `rejected:`, `missing:`), `checked_on`, and `pipeline_url`, `pipeline_match`, `pipeline_source`, `pipeline_pdf` from the evidence pipeline |
| `covers/exNNN.png` | Checked cover thumbnails |
| `data/cover_fetch_log.csv` | What happened with each link on the last fetch |
| `data/story_covers.json` | Export for the scrollytelling page (`tools/export_for_story.py`) |
| `tools/fetch_covers.py` | Finds an image per example: a linked PDF (page 1), a report PDF linked from the page, a cover image on the page, or a screenshot of the page (headless browser; cookie banners hidden, never accepted) |
| `tools/export_for_story.py` | Builds `story_covers.json` from checked rows (document links only) |
| `tools/import_pipeline_links.py` | Brings in links found by [gain-evidence-pipeline](https://github.com/mitrovif/gain-evidence-pipeline) (its local `data_lake`: drilled NSO pages, LLM-checked web search, links in the roster, downloaded reports) into the `pipeline_*` columns |

**IDs:** `exNNN` is the 1-based row in the GAIN group roster (`analysis_ready_group_roster.csv`);
`ex113` is row 113, the Burkina Faso INSD survey of IDP and host households. The story uses the
0-based row (112).

## Workflow

1. **Add links.** Fill `source_url` (and `url_found_by`) in `data/gain_examples.csv`: from the respondent,
   the NSO website, the UNHCR or World Bank microdata libraries, or a web search on title + organisation + country.
2. **Fetch.** `pip install pymupdf requests beautifulsoup4 playwright`, `python -m playwright install chromium`, then `python tools/fetch_covers.py`.
3. **Check every new image by eye.** Set `cover_status` to `ok`, `ok: <note>` (e.g. questionnaire first page)
   or `rejected: <reason>`; delete rejected images; fill `checked_on`.
4. **Export.** `python tools/export_for_story.py`, then send the new covers and `story_covers.json` to the
   scrollytelling page.

## Log

- **30 Sep 2026:** links found by web search for the 7 featured story examples; covers for Burkina Faso INSD (ESEP-PDI 2024), the African Union 4th School on Migration Statistics report, and the UBOS 2024 census report. Still to check by hand in a browser: Nigeria NBS (microdata catalogue), Philippines PSA (press release), Thailand (2025 module not yet published).

- **30 Sep 2026 (NSO website pass):** 171 examples searched on NSO and organisation websites: the 34 whose link was broken, blocked or generic, and the 137 country-led 2024–2025 examples without a link, with NSO-list countries (`gain_sdg_workstream/data/nso_census_targets.csv`) first. Result: 94 exact, 31 related, 17 section pages, 29 not found. 36 new covers kept after checking, 20 rejected. Links still to open by hand (sites block scripts): PSA Philippines, IDB, UNDP, UNRWA, BPS Indonesia, dofi.ibz.be, ESCWA, Liechtenstein. Six links are news articles, flagged in `replacement_source`. The session's web-search limit was reached, so some later countries were searched by browsing sites only (Kenya, Morocco, Moldova, Burundi, CAR, South Sudan, Rwanda, Cameroon, Sweden, Bangladesh, Egypt, Sudan, Mozambique, DRC) and deserve a second pass.
- **30 Sep 2026 (better cover search):** the fetcher now looks for report PDFs linked from a page, cover images on the page, and otherwise takes a screenshot of the page itself, retrying blocked sites in a headless browser. Over 97 linked examples without a cover: 63 kept (49 page screenshots), 16 rejected (wrong PDFs picked up from pages, photos, CAPTCHA pages, a pop-up), 18 links still failing.
- **30 Sep 2026 (evidence pipeline links):** imported links from gain-evidence-pipeline's `data_lake` for 125 examples without a cover (57 links in the roster, 13 drilled NSO pages, 13 LLM-checked web-search matches, 40 office sites, 5 downloaded reports). 84 images fetched; 26 passed the check by eye, 58 rejected (NSO home pages, 404 pages, stock photos, another product by the same office, one hijacked domain). Then, at the user's request, **only images whose link opens the example's own document are kept**: 42 covers across all passes moved to `held:` (related edition or section page). In use: 95.
- **30 Sep 2026 (MICS check):** 10 MICS examples. mics.unicef.org and unicef.org block scripts and headless browsers with a Cloudflare bot check (not bypassed), so reports were looked for through partners and NSOs. Only one of the rounds reported is published: the Sub-National Lebanon MICS 2023 Statistical Snapshots (Syrian settlements, Palestinian camps), linked via the JDC page, which shows the cover (ex258). South Sudan MICS7 already had its Key Findings Report (ex260). Not yet published: CAR 2025, Bangladesh 2025 (Rohingya), Cameroon MICS7, Burkina Faso 2026, Mauritania 2026, Palestine 2025, Zimbabwe 2025 (latest public round is 2019). To re-check when their Snapshots or Survey Findings Reports appear.
- **Next:** institution-led examples (UNHCR, World Bank / JDC, IOM, JIPS, IDMC, UNICEF…) and the 2021–2023 rounds.

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

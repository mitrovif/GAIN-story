# Counted, and counting

The GAIN 2021–2025 scrollytelling page for the GAIN 2026 launch on the EGRISS website: 413
implementation examples, drawn as points of light, re-forming into the charts of the GAIN Tables 2025.

| Path | What it is |
|---|---|
| `Main.dc.html` | The page (exported from the "GAIN Scrollytelling" design on claude.ai). Serve the folder and open it; `index.html` redirects to it. |
| `support.js`, `vendor/` | Runtime the page needs (React and the design-component loader). |
| `assets/*.json` | Examples roster, chart layouts, world map and `c92c…json`: covers and source links per example (0-based roster row). |
| `assets/covers/`, `assets/covers-web/` | The 96 images the story uses: originals, and 480px JPEGs the page loads. |
| `assets/fonts/` | Obvia, the EGRISS heading face (from the EGRISS design system). Check the licence before the repo goes public. |
| `pipeline/` | The cover and link scraping workstream (formerly `GAIN_post-collection`), with the SDG-map covers in `pipeline/covers-sdg/`. See its README. |
| `review/` | Review material: story frames, EGRISS case study captures and the review board page. |

## Preview

```bash
python3 -m http.server 8123
```

Then open http://localhost:8123/Main.dc.html.

## Updating the design artifact

The design copy loads images and data from its own uploads (`/_blob/<id>`), not from this repo.
`tools/design_blob_map.json` maps the covers added on 8 Oct 2026 (`exNNN`) to their upload ids;
the other covers keep their original ids (the file name in `assets/covers-web/`). To push new covers:
upload the images and a covers JSON with `/_blob/` paths, then point `Main.dc.html` at the new JSON.
Since 8 Oct 2026 (244 covers) it loads covers data `/_blob/1b6f97288b7bb43b217b860e0c27b52a`.

## Links

- Public site (GitHub Pages, republished on every push to main): https://mitrovif.github.io/GAIN-story/

- Story (design tool): https://claude.ai/artifact/Frysz8mQTSS5Rv8GX5LRMi
- Review board: https://claude.ai/artifact/L4amtyMx6v3FKYuZAWLK1t

"""Add covers to the story that the "own document only" rule held back (decision of 8 Oct 2026).

Three sources, for examples that show no image in the story yet:
  - pipeline/covers/      rows with cover_status "held:": the image is fine but its link is a
                          related edition or a section page. Marked related=True so the page says so.
  - pipeline/covers-sdg/  covers from gain_sdg_workstream that pipeline/covers lacks (rendered from
                          reports on SharePoint). Link from data/sdg_example_links.csv when there is one.
  - search                rows whose link was found by the web search of 8 Oct 2026 and whose cover was
                          checked by eye (cover_status "ok…", replacement_on 2026-10-08). The new link
                          replaces any older one; related links are marked as such.

An example that already has a story link keeps it. Writes 480px JPEGs to assets/covers-web/ and
updates the story covers file in place. Safe to re-run.

    python3 tools/add_relaxed_covers.py
"""
import csv
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORY = os.path.join(ROOT, 'assets', 'c92c0aa4e7ae0e7003c152db6be5c09a.json')
WEB = os.path.join(ROOT, 'assets', 'covers-web')
P = os.path.join(ROOT, 'pipeline')


def web_copy(src, ex_id):
    out = os.path.join(WEB, ex_id + '.jpg')
    im = Image.open(src).convert('RGB')
    if im.width > 480:
        im = im.resize((480, round(im.height * 480 / im.width)), Image.LANCZOS)
    im.save(out, quality=82, optimize=True)
    return 'assets/covers-web/' + ex_id + '.jpg'


def main():
    story = json.load(open(STORY))
    rows = {r['ex_id']: r for r in csv.DictReader(open(os.path.join(P, 'data', 'gain_examples.csv')))}
    sdg = {r['example_id']: r for r in csv.DictReader(open(os.path.join(P, 'data', 'sdg_example_links.csv')))}
    have_pc = {f[:-4] for f in os.listdir(os.path.join(P, 'covers'))}
    have_sdg = {f[:-4] for f in os.listdir(os.path.join(P, 'covers-sdg')) if f.endswith('.png')}

    added = {'held': 0, 'sdg': 0, 'search': 0, 'no_link': 0}
    candidates = [(e, 'held') for e, r in rows.items() if r['cover_status'].startswith('held') and e in have_pc]
    candidates += [(e, 'sdg') for e in sorted(have_sdg - have_pc)]
    candidates += [(e, 'search') for e, r in rows.items() if r['cover_status'].startswith('ok') and r.get('replacement_on') == '2026-10-08' and e in have_pc]
    for ex_id, src in candidates:
        key = str(int(ex_id[2:]) - 1)  # story keys are the 0-based roster row
        entry = story.get(key, {})
        if entry.get('cover') and not entry.get('relaxed'):
            continue
        r = rows.get(ex_id, {})
        title, country = r.get('title', ''), r.get('country', '')
        if src == 'search':
            img = os.path.join(P, 'covers', ex_id + '.png')
            kind = 'screenshot' if 'screenshot' in r['cover_status'] else 'cover'
            entry['link'] = r['replacement_url']
            entry['related'] = r.get('replacement_match') == 'related'
            entry['news'] = r.get('replacement_source', '').startswith('news')
            alt = ('Source web page' if kind == 'screenshot' else 'Cover or first page') + (' (related document)' if entry['related'] else '') + ': ' + title + ' (' + country + ')'
        elif src == 'held':
            img = os.path.join(P, 'covers', ex_id + '.png')
            kind = 'screenshot' if 'screenshot' in r['cover_status'] else 'cover'
            if not entry.get('link'):
                entry['link'] = r.get('replacement_url') or r.get('pipeline_url') or r.get('source_url') or ''
                entry['related'] = bool(entry['link'])
            alt = ('Related page' if kind == 'screenshot' else 'Cover of a related document') + ': ' + title + ' (' + country + ')'
        else:
            img = os.path.join(P, 'covers-sdg', ex_id + '.png')
            kind = 'cover'
            if not entry.get('link') and sdg.get(ex_id, {}).get('source_url'):
                entry['link'] = sdg[ex_id]['source_url']
            alt = 'Cover or first page: ' + title + ' (' + country + ')'
        entry.update({'cover': web_copy(img, ex_id), 'kind': kind, 'alt': alt, 'relaxed': src})
        entry.setdefault('news', False)
        story[key] = entry
        added[src] += 1
        if not entry.get('link'):
            added['no_link'] += 1

    json.dump(story, open(STORY, 'w'), indent=0, ensure_ascii=False)
    total = sum(1 for v in story.values() if v.get('cover'))
    print('added', added, '| examples with an image now:', total)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""bake_grids.py — writes the current feed.json order into the baked film grids in index.html
(the server-rendered fallback Google and no-JS visitors see). Run after build_playlists.py."""
import json, re, html
from pathlib import Path
feed = json.loads(Path("feed.json").read_text())["playlists"]
COUNT = {"signature": 3}          # default 6 cards per grid
VERTICAL = {"faith", "bappa"}     # Shorts playlists — first frame as the thumbnail
s = Path("index.html").read_text()
def esc(t): return html.escape(t, quote=True).replace("'", "&#x27;")
# A missing thumbnail size comes back as a 120x90 grey placeholder with HTTP 404 —
# the browser LOADS it, so onerror never fires. NEXT walks a fallback chain on size.
NEXT = ("onload=\"if(this.naturalWidth<200){var a=(this.dataset.fbs||'').split(' ').filter(Boolean);"
        "if(a.length){this.dataset.fbs=a.slice(1).join(' ');this.src=a[0];}}\"")

def card(v, vertical):
    i, t = v["id"], esc(v["title"])
    src = f"https://i.ytimg.com/vi/{i}/frame0.jpg" if vertical else f"https://i.ytimg.com/vi/{i}/hq720.jpg"
    fbs = (f"https://i.ytimg.com/vi/{i}/oar2.jpg https://i.ytimg.com/vi/{i}/hqdefault.jpg" if vertical
           else f"https://i.ytimg.com/vi/{i}/sddefault.jpg https://i.ytimg.com/vi/{i}/hqdefault.jpg")
    last = f"https://i.ytimg.com/vi/{i}/hqdefault.jpg"
    return (f'      <div class="film-card" data-cursor data-yt="{i}">\n'
            f'        <img class="film-thumb" src="{src}" alt="{t}" loading="lazy" data-fbs="{fbs}" {NEXT} '
            f'onerror="this.onerror=null;this.src=\'{last}\'" />\n'
            f'        <div class="film-meta"><h3>{t}</h3><div class="play">Play ↗</div></div>\n      </div>\n')

n = 0
for key, vids in feed.items():
    pat = re.compile(r'(<div class="film-grid[^"]*" data-playlist-key="%s">\n)(.*?)(\n\s*</div>\n\s*<a href="https://www.youtube.com/playlist)' % key, re.S)
    if not vids: print("no videos for", key, "— leaving the baked grid alone"); continue
    m = pat.search(s)
    if not m: print("grid not found:", key); continue
    body = "".join(card(v, key in VERTICAL) for v in vids[:COUNT.get(key, 6)])
    s = s[:m.start(2)] + body.rstrip("\n") + s[m.end(2):]
    n += 1
Path("index.html").write_text(s)
print(f"✓ baked {n} grids into index.html")

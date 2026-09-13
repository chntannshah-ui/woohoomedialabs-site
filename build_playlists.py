#!/usr/bin/env python3
"""
build_playlists.py — pulls the current order of the six Woo Hoo YouTube playlists
(via YouTube's public RSS feeds — no API key) and writes:

  feed.json       compact {ok, playlists:{key:[{id,title}]}} the homepage grids read
                  as their baked fallback (yt-sync.js), so the site never shows a
                  stale or empty grid even when YouTube blocks the live edge fetch.
  playlists.json  the fuller structure build_site.py knows about (kept for compatibility).

RSS returns the newest ~15 entries per playlist, in playlist order — exactly what the
homepage grids need (they show 6, Signature shows 3).

Run:  python3 build_playlists.py     then upload feed.json + playlists.json to the repo.
"""
import json, re, urllib.request, html
from datetime import datetime, timezone
from pathlib import Path

PLAYLISTS = [
    ("ai",         "PLAcjSzaUUVHkV3bR_j_R6dRuiUQp7I1DS", "AI Films",                     "🤖", "Where craft meets generative intelligence."),
    ("product",    "PLAcjSzaUUVHm1Vc7IenJvn5DONdYlO9WO", "Product Films",                "🚀", "Hero films, demo reels, launch cinema — for products people actually buy."),
    ("corporate",  "PLAcjSzaUUVHkC11dQr16d5rlJRrmxfW2-", "Corporate Communication",      "🎥", "Brand films, anthems, and enterprise storytelling."),
    ("government", "PLAcjSzaUUVHnhfDWDkGhTKN2mRHSQ8Xyy", "Government Films",             "🏛", "Public narrative — for the State of Maharashtra and the Government of India."),
    ("healthcare", "PLAcjSzaUUVHm_N6lKfpdQ0e1TqTJ5y7gg", "Healthcare & Lifestyle",       "💊", "Films for pharma, wellness, and the body's quieter conversations."),
    ("signature",  "PLAcjSzaUUVHl66UVP317jEsE95ZnwiAho", "Signature & Special Projects", "✨", "Pieces made for love, for milestones, for the archive."),
]
EXCLUDE = {"N23lUkPsrnw"}  # Bhai Shirt Pehen Lo — shown as IG reel
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def clean(t):
    t = html.unescape(t)
    return re.sub(r"\s*\|\s*", " · ", re.sub(r"\s+", " ", t)).strip()

def rss(pid):
    req = urllib.request.Request(f"https://www.youtube.com/feeds/videos.xml?playlist_id={pid}", headers={"User-Agent": UA})
    xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        vid = re.search(r"<yt:videoId>([^<]+)</yt:videoId>", e)
        title = re.search(r"<title>(.*?)</title>", e, re.S)
        pub = re.search(r"<published>([^<]+)</published>", e)
        if vid and vid.group(1) not in EXCLUDE:
            out.append({"id": vid.group(1), "title": clean(title.group(1) if title else ""), "published": pub.group(1) if pub else None})
    return out

feed, full, total = {}, [], 0
for key, pid, name, icon, tagline in PLAYLISTS:
    try:
        vids = rss(pid)
    except Exception as ex:
        print(f"  ! {name}: {ex} — keeping previous feed.json entry if any")
        vids = None
    if vids is None:
        prev = json.loads(Path("feed.json").read_text()) if Path("feed.json").exists() else {}
        vids = prev.get("playlists", {}).get(key, [])
    print(f"{icon} {name}: {len(vids)} videos")
    total += len(vids)
    feed[key] = [{"id": v["id"], "title": v["title"]} for v in vids]
    full.append({"id": pid, "name": name, "icon": icon, "tagline": tagline,
                 "url": f"https://www.youtube.com/playlist?list={pid}", "total": len(vids), "videos": vids})

now = datetime.now(timezone.utc).isoformat()
Path("feed.json").write_text(json.dumps({"ok": True, "updated": now, "playlists": feed}, ensure_ascii=False))
Path("playlists.json").write_text(json.dumps({"updated": now, "playlists": full}, ensure_ascii=False, indent=1))
print(f"✓ feed.json + playlists.json ({total} videos)")

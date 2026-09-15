#!/usr/bin/env python3
"""
build_playlists.py — reads the current order of the Woo Hoo YouTube playlists
straight from each playlist page (YouTube retired the playlist RSS feeds in
Sept 2026 — they now 404) and writes:

  feed.json       compact {ok, updated, playlists:{key:[{id,title}]}} the homepage
                  grids read (yt-sync.js), always in YouTube playlist order.
  playlists.json  the fuller structure build_site.py knows about.

Handles both page shapes: lockupViewModel (normal videos) and reelWatchEndpoint
(Shorts / vertical playlists). Run:  python3 build_playlists.py
"""
import json, re, urllib.request, html
from datetime import datetime, timezone
from pathlib import Path

PLAYLISTS = [
    ("ai",         "PLAcjSzaUUVHkV3bR_j_R6dRuiUQp7I1DS", "AI Films",                     "🤖", "Where craft meets generative intelligence.", False),
    ("product",    "PLAcjSzaUUVHm1Vc7IenJvn5DONdYlO9WO", "Product Films",                "🚀", "Hero films, demo reels, launch cinema — for products people actually buy.", False),
    ("corporate",  "PLAcjSzaUUVHkC11dQr16d5rlJRrmxfW2-", "Corporate Communication",      "🎥", "Brand films, anthems, and enterprise storytelling.", False),
    ("government", "PLAcjSzaUUVHnhfDWDkGhTKN2mRHSQ8Xyy", "Government Films",             "🏛", "Public narrative — for the State of Maharashtra and the Government of India.", False),
    ("healthcare", "PLAcjSzaUUVHm_N6lKfpdQ0e1TqTJ5y7gg", "Healthcare & Lifestyle",       "💊", "Films for pharma, wellness, and the body's quieter conversations.", False),
    ("signature",  "PLAcjSzaUUVHl66UVP317jEsE95ZnwiAho", "Signature & Special Projects", "✨", "Pieces made for love, for milestones, for the archive.", False),
    ("faith",      "PLah1g5o0db8s",                      "Faith",                        "🪔", "Gods, myth and devotion — vertical.", True),
    ("bappa",      "PLaYnl50OiPxI",                      "Ghar Mein Bappa",              "🐘", "Ten days, one household, one very small inspector.", True),
]
EXCLUDE = {"N23lUkPsrnw"}  # Bhai Shirt Pehen Lo — shown as IG reel
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def clean(t):
    try:
        t = t.encode("utf-8").decode("unicode_escape").encode("latin-1", "ignore").decode("utf-8", "ignore") if "\\u" in t else t
    except Exception:
        pass
    t = html.unescape(t).replace('\\"', '"').replace("\\/", "/")
    return re.sub(r"\s*\|\s*", " · ", re.sub(r"\s+", " ", t)).strip()

def scrape(pid, vertical):
    req = urllib.request.Request(f"https://www.youtube.com/playlist?list={pid}", headers={"User-Agent": UA})
    h = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
    out, seen = [], set()
    if vertical:
        for m in re.finditer(r'"reelWatchEndpoint":\{"videoId":"([A-Za-z0-9_-]{11})"', h):
            vid = m.group(1)
            if vid in seen or vid in EXCLUDE:
                continue
            seen.add(vid)
            pre = h[max(0, m.start() - 4000):m.start()]
            t = re.findall(r'"accessibilityText":"((?:[^"\\]|\\.)+)"', pre)
            title = t[-1] if t else ""
            title = re.sub(r",\s*[\d.,]+\s*(?:thousand|million|K|M)?\s*views?\s*-\s*play Short\s*$", "", title)
            out.append({"id": vid, "title": clean(title), "published": None})
        return out
    ev = []
    for m in re.finditer(r'"contentId":"([A-Za-z0-9_-]{11})","contentType":"LOCKUP_CONTENT_TYPE_VIDEO"', h):
        ev.append((m.start(), "id", m.group(1)))
    for m in re.finditer(r'"lockupMetadataViewModel":\{"title":\{"content":"((?:[^"\\]|\\.)+)"', h):
        ev.append((m.start(), "t", m.group(1)))
    ev.sort()
    title = ""
    for _, kind, val in ev:
        if kind == "t":
            title = val
        elif val not in seen and val not in EXCLUDE:
            seen.add(val)
            out.append({"id": val, "title": clean(title), "published": None})
            title = ""
    return out

feed, full, total = {}, [], 0
for key, pid, name, icon, tagline, vertical in PLAYLISTS:
    try:
        vids = scrape(pid, vertical)
    except Exception as ex:
        print(f"  ! {name}: {ex} — keeping previous feed.json entry")
        vids = None
    if not vids:
        prev = json.loads(Path("feed.json").read_text()) if Path("feed.json").exists() else {}
        vids = prev.get("playlists", {}).get(key, [])
    print(f"{icon} {name}: {len(vids)} videos{' (vertical)' if vertical else ''}")
    total += len(vids)
    feed[key] = [{"id": v["id"], "title": v["title"]} for v in vids]
    full.append({"id": pid, "name": name, "icon": icon, "tagline": tagline, "vertical": vertical,
                 "url": f"https://www.youtube.com/playlist?list={pid}", "total": len(vids), "videos": vids})

now = datetime.now(timezone.utc).isoformat()
Path("feed.json").write_text(json.dumps({"ok": True, "updated": now, "playlists": feed}, ensure_ascii=False))
Path("playlists.json").write_text(json.dumps({"updated": now, "playlists": full}, ensure_ascii=False, indent=1))
print(f"✓ feed.json + playlists.json ({total} videos)")

#!/usr/bin/env python3
"""
build_playlists.py — fetches the current state of all 7 Woo Hoo Media YT playlists
and writes a single playlists.json file the site renders from.

Re-run this whenever you reorder/add/remove videos on YouTube.
On Vercel, this runs daily via cron (vercel.json schedule).

Usage:
    python3 build_playlists.py
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

# Configure once — order here = order on the site
PLAYLISTS = [
    {"id": "PLAcjSzaUUVHkV3bR_j_R6dRuiUQp7I1DS", "name": "AI Films",                       "icon": "🤖", "tagline": "Where craft meets generative intelligence."},
    {"id": "PLAcjSzaUUVHm1Vc7IenJvn5DONdYlO9WO", "name": "Product Films",                  "icon": "🚀", "tagline": "Hero films, demo reels, launch cinema — for products people actually buy."},
    {"id": "PLAcjSzaUUVHkC11dQr16d5rlJRrmxfW2-", "name": "Corporate Communication",        "icon": "🎥", "tagline": "Brand films, anthems, and enterprise storytelling — across fifty-three productions."},
    {"id": "PLAcjSzaUUVHnhfDWDkGhTKN2mRHSQ8Xyy", "name": "Government Films",               "icon": "🏛", "tagline": "Public narrative — for the State of Maharashtra and the Government of India."},
    {"id": "PLAcjSzaUUVHm_N6lKfpdQ0e1TqTJ5y7gg", "name": "Healthcare & Lifestyle",         "icon": "💊", "tagline": "Films for pharma, wellness, and the body's quieter conversations."},
    {"id": "PLAcjSzaUUVHl66UVP317jEsE95ZnwiAho", "name": "Signature & Special Projects",   "icon": "✨", "tagline": "Pieces we made for love, for milestones, for the archive."},
]

# Videos to exclude site-wide (e.g. Shorts that belong in IG section instead)
EXCLUDE_VIDEO_IDS = {"N23lUkPsrnw"}  # Bhai Shirt Pehen Lo — shown as IG reel

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def fetch_playlist_html(pid: str) -> str:
    url = f"https://www.youtube.com/playlist?list={pid}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def parse_playlist(html: str) -> list[dict]:
    """Extract video list in playlist order, with titles."""
    videos = []
    seen = set()

    def add(vid: str, title: str):
        if vid in seen or vid in EXCLUDE_VIDEO_IDS:
            return
        seen.add(vid)
        try:
            title = title.encode().decode("unicode_escape", errors="ignore")
        except Exception:
            pass
        videos.append({"id": vid, "title": title.strip()})

    # Pattern A — playlistVideoRenderer (large playlists)
    for m in re.finditer(
        r'"playlistVideoRenderer":\{"videoId":"([A-Za-z0-9_-]{11})","thumbnail".*?"title":\{"runs":\[\{"text":"([^"]+)"\}\]',
        html,
    ):
        add(m.group(1), m.group(2))

    # Pattern B — gridVideoRenderer (small playlists / channel grids)
    for m in re.finditer(
        r'"gridVideoRenderer":\{"videoId":"([A-Za-z0-9_-]{11})","thumbnail".*?"title":\{"simpleText":"([^"]+)"',
        html,
    ):
        add(m.group(1), m.group(2))
    for m in re.finditer(
        r'"gridVideoRenderer":\{"videoId":"([A-Za-z0-9_-]{11})","thumbnail".*?"title":\{"runs":\[\{"text":"([^"]+)"',
        html,
    ):
        add(m.group(1), m.group(2))

    # Pattern C — compactVideoRenderer (some playlist views)
    for m in re.finditer(
        r'"compactVideoRenderer":\{"videoId":"([A-Za-z0-9_-]{11})".*?"title":\{"simpleText":"([^"]+)"',
        html,
    ):
        add(m.group(1), m.group(2))

    # Pattern D — generic videoId followed by accessibility title (last resort, tight scope)
    if not videos:
        for m in re.finditer(
            r'"videoId":"([A-Za-z0-9_-]{11})","thumbnail":\{[^}]+\}+,"title":\{"(?:simpleText|runs":\[\{"text)":"?([^"]+?)"',
            html,
        ):
            add(m.group(1), m.group(2))

    return videos


def clean_title(t: str) -> str:
    t = re.sub(r"\s+", " ", t).strip()
    parts = [p.strip() for p in t.split("|")]
    if len(parts) >= 3:
        t = " · ".join(parts[:2])
    elif len(parts) == 2:
        t = " · ".join(parts)
    return t.strip(" ·")


def build():
    out = {"updated": "", "playlists": []}
    from datetime import datetime, timezone
    out["updated"] = datetime.now(timezone.utc).isoformat()

    for p in PLAYLISTS:
        print(f"Fetching {p['icon']} {p['name']}...", file=sys.stderr)
        try:
            html = fetch_playlist_html(p["id"])
            videos = parse_playlist(html)
            for v in videos:
                v["display_title"] = clean_title(v["title"])
                v["thumbnail"] = f"https://img.youtube.com/vi/{v['id']}/maxresdefault.jpg"
            entry = {
                "id": p["id"],
                "name": p["name"],
                "icon": p["icon"],
                "tagline": p["tagline"],
                "url": f"https://www.youtube.com/playlist?list={p['id']}",
                "total": len(videos),
                "videos": videos,
            }
            print(f"  → {len(videos)} videos", file=sys.stderr)
        except Exception as e:
            print(f"  ! FAILED: {e}", file=sys.stderr)
            entry = {"id": p["id"], "name": p["name"], "icon": p["icon"],
                     "tagline": p["tagline"],
                     "url": f"https://www.youtube.com/playlist?list={p['id']}",
                     "total": 0, "videos": [], "error": str(e)}
        out["playlists"].append(entry)

    Path("playlists.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n✓ Wrote playlists.json ({sum(len(p['videos']) for p in out['playlists'])} total videos)", file=sys.stderr)


if __name__ == "__main__":
    build()

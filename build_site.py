#!/usr/bin/env python3
"""
build_site.py — generates index.html from playlists.json + site config.

Workflow:
  1. python3 build_playlists.py     # fetches latest YT playlists → playlists.json
  2. python3 build_site.py          # renders index.html from data

Re-run both whenever YT changes. On Vercel, this runs as a daily build via cron.
"""

import json
from pathlib import Path
from datetime import datetime

# ────────────────────────────────────────────────────────────────
# CONFIG — single source of truth for all site content
# ────────────────────────────────────────────────────────────────
SITE = {
    "domain": "woohoomedialabs.com",
    "title": "Woo Hoo Media Labs — AI-Native Creative Production Lab | Mumbai",
    "description": "AI-native creative production lab in Mumbai, founded 2009 by Chntan N. Shah. 26 years of cinematic craft. Brand films, ad films, AI commercials, government communication, product films. Production stack: Kling, Seedance, Flux, Nano Banana, Soul characters, ElevenLabs.",
    "email_primary": "hello@woohoomedialabs.com",
    "email_direct": "chntan.n.shah@gmail.com",
    "instagram_handle": "chntan.n.shah",
    "youtube_channel": "https://www.youtube.com/@WooHooMediaLabs",
    "linkedin": "https://www.linkedin.com/in/chntan/",
}

HERO = {
    "tag": "An AI-Native Creative Production Lab · Mumbai",
    "headline_lines": ["Cinema for", "<em>the age of</em>", "intelligence."],
    "metrics": [
        ("EST.", "2009"),
        ("26 Years", "in Cinema"),
        ("200+", "Clients Served"),
        ("1000+", "Films Released"),
    ],
}

MANIFESTO = {
    "headline": "Twenty-six years of <em>cinematic craft.</em> Rebuilt for a world where <em>every frame</em> can be imagined.",
    "body": "This studio has been telling stories since 2009. Since 2026, in a new language. The camera hasn't disappeared — it has multiplied. Every prompt is now a lens, every model a director of photography.",
    "founder": "Founded and led by <b>Chntan N. Shah</b> from Mumbai.",
}

CAPABILITIES = [
    {"num": "01 / Brand",       "title": "Brand <em>films.</em>",        "body": "Anthems, manifestos, founder stories. Built to move the room."},
    {"num": "02 / Advertising", "title": "Ad <em>films.</em>",           "body": "30, 60, 90 second cinematic commercials for TV and digital."},
    {"num": "03 / AI",          "title": "AI-native <em>cinema.</em>",   "body": "Every frame imagined first, then made. The camera multiplied a thousand times."},
    {"num": "04 / Government",  "title": "Public <em>narrative.</em>",   "body": "Government and defence communication, with the gravity it deserves."},
    {"num": "05 / Product",     "title": "Product <em>films.</em>",      "body": "Hero films, demo reels, launch cinema — for products people actually buy."},
    {"num": "06 / Series",      "title": "Episodic <em>formats.</em>",   "body": "Social-first series engineered for retention, virality, and recall."},
]

# Instagram reels — these are manually managed since IG has no playlist API
IG_REELS = [
    {
        "shortcode": "DYGWwZHhkbW",
        "type": "p",
        "thumb_yt_id": "N23lUkPsrnw",   # YT version for thumbnail fallback
        "caption": '"Bhai ne 30 saal mein kabhi shirt nahi pehni."',
        "likes": "27K", "comments": "396", "views": "1.2M+",
    },
    {
        "shortcode": "DYRh66eszVa",
        "type": "p",
        "thumb_yt_id": "kVmC-V77Y90",
        "caption": '"Aapki secret fantasy, bina permission ke reel mein."',
        "likes": "17K", "comments": "420", "views": "170K+",
    },
    {
        "shortcode": "DWnqKzSGQ31",
        "type": "reel",
        "thumb_yt_id": None,   # not on YT — uses local file
        "thumb_local": "ig_spy.jpg",
        "caption": '"Once upon a #spy in #mumbai."',
        "likes": "129", "comments": "4", "views": "2.5K+",
    },
]

PRE_AI_VIDEO_ID = "F-spjRJSgus"
SHOWCASE_VIDEO_ID = "bYj4DB2bhIs"   # 2:30 hero showcase film, sits as section 02

TESTIMONIALS_ENABLED = False  # Off — testimonials section hidden until real ones arrive


# ────────────────────────────────────────────────────────────────
# RENDERERS
# ────────────────────────────────────────────────────────────────
def clean_title(t: str) -> str:
    import re
    t = re.sub(r"\s+", " ", t).strip()
    parts = [p.strip() for p in t.split("|")]
    if len(parts) >= 3:
        return " · ".join(parts[:2])
    if len(parts) == 2:
        return " · ".join(parts)
    return t.strip(" ·")


def render_film_card(v):
    vid = v["id"]
    title = clean_title(v.get("title", "Untitled"))
    return f'''      <div class="film-card" data-cursor data-yt="{vid}">
        <img class="film-thumb" src="https://img.youtube.com/vi/{vid}/maxresdefault.jpg" alt="{title}" loading="lazy" onerror="this.src='https://img.youtube.com/vi/{vid}/hqdefault.jpg'" />
        <div class="film-meta"><h3>{title}</h3><div class="play">Play ↗</div></div>
      </div>'''


def render_playlist_section(p, num):
    videos = p.get("videos", [])[:6]
    total = p.get("total", 0)
    cards = "\n".join(render_film_card(v) for v in videos)
    view_all = ""
    if total > 6:
        view_all = f'    <a href="{p["url"]}" target="_blank" rel="noopener" class="view-all" data-cursor>View all on YouTube →</a>'
    elif total > 0:
        view_all = f'    <a href="{p["url"]}" target="_blank" rel="noopener" class="view-all" data-cursor>Open playlist on YouTube →</a>'
    return f'''<div class="section-label" id="section-{num:02d}"><span>{p["icon"]} {p["name"]} · {num:02d}</span></div>
<section class="film-section reveal">
  <p class="section-tagline">{p["tagline"]}</p>
  <div class="film-grid">
{cards}
  </div>
{view_all}
</section>'''


def render_ig_card(reel):
    sc = reel["shortcode"]
    url = f"https://www.instagram.com/{reel['type']}/{sc}/"
    if reel["thumb_yt_id"]:
        thumb = f"https://i.ytimg.com/vi/{reel['thumb_yt_id']}/maxresdefault.jpg"
    else:
        thumb = reel["thumb_local"]
    return f'''    <a class="ig-card" href="{url}" target="_blank" rel="noopener" data-cursor>
      <div class="ig-label"><span class="dot">●</span><span class="handle">@{SITE["instagram_handle"]}</span><span class="badge">Reel</span></div>
      <div class="ig-fallback ig-with-thumb">
        <img class="ig-thumb" src="{thumb}" alt="Instagram reel" loading="lazy" />
        <div class="ig-overlay">
          <svg class="ig-logo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>
          <div class="ig-views"><span>▶</span> {reel["views"]}</div>
        </div>
        <div class="ig-fallback-caption">
          <div class="ig-caption-text">{reel["caption"]}</div>
          <div class="ig-stats-row"><span><b>{reel["likes"]}</b> likes</span><span><b>{reel["comments"]}</b> comments</span><span><b>{reel["views"]}</b> views</span></div>
        </div>
      </div>
    </a>'''


def render_capability(cap, idx):
    return f'''    <div class="service" data-cursor data-shade="{idx % 3}">
      <div class="service-content">
        <div class="num">{cap["num"]}</div>
        <h3>{cap["title"]}</h3>
        <p>{cap["body"]}</p>
      </div>
    </div>'''


def render_hero_metrics():
    return "".join(f'<span><b>{a}</b> {b}</span>' if a[0].isdigit() or a == "Millions" else f'<span>{a} <b>{b}</b></span>' for a, b in HERO["metrics"])


# ────────────────────────────────────────────────────────────────
# MAIN BUILD
# ────────────────────────────────────────────────────────────────
def render_video_schema(v, playlist_name):
    """Render a single VideoObject schema for a featured video."""
    vid = v["id"]
    title = clean_title(v.get("title", "Untitled"))
    return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "{title}",
  "description": "{title} — produced by Woo Hoo Media Labs ({playlist_name})",
  "thumbnailUrl": "https://img.youtube.com/vi/{vid}/maxresdefault.jpg",
  "uploadDate": "2025-01-01",
  "contentUrl": "https://www.youtube.com/watch?v={vid}",
  "embedUrl": "https://www.youtube.com/embed/{vid}",
  "publisher": {{ "@type": "Organization", "name": "Woo Hoo Media Labs" }}
}}
</script>'''


def build():
    data = json.loads(Path("playlists.json").read_text())
    playlists = data["playlists"]

    # Render film sections (start at section 03 — showcase film takes 02)
    section_blocks = []
    for i, p in enumerate(playlists):
        section_blocks.append(render_playlist_section(p, i + 3))
    sections_html = "\n\n".join(section_blocks)

    next_num = len(playlists) + 3  # capabilities number

    # Generate VideoObject schemas — top 2 videos from each playlist (12 total)
    # The showcase film leads — it's the hero piece.
    video_schemas_list = []
    showcase_schema = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Woo Hoo Media Labs — Studio Showcase Film",
  "description": "Studio showcase film from Woo Hoo Media Labs — an AI-native creative production lab in Mumbai. Directed by Chntan N. Shah. Twenty-six years of cinema, reimagined for the age of intelligence.",
  "thumbnailUrl": "https://img.youtube.com/vi/{SHOWCASE_VIDEO_ID}/maxresdefault.jpg",
  "uploadDate": "2026-05-01",
  "contentUrl": "https://www.youtube.com/watch?v={SHOWCASE_VIDEO_ID}",
  "embedUrl": "https://www.youtube.com/embed/{SHOWCASE_VIDEO_ID}",
  "director": {{ "@type": "Person", "name": "Chntan N. Shah" }},
  "publisher": {{ "@type": "Organization", "name": "Woo Hoo Media Labs" }}
}}
</script>'''
    video_schemas_list.append(showcase_schema)
    for p in playlists:
        for v in p.get("videos", [])[:2]:
            video_schemas_list.append(render_video_schema(v, p["name"]))
    video_schemas = "\n".join(video_schemas_list)

    # Render capabilities
    caps_html = "\n".join(render_capability(c, i) for i, c in enumerate(CAPABILITIES))

    # Hero metrics
    hero_metrics_html = "".join(
        f'<span><b>{a}</b> {b}</span>' if (a[0].isdigit() or a in ("Millions",)) else f'<span>{a} <b>{b}</b></span>'
        for a, b in HERO["metrics"]
    )

    headline_html = "".join(f'<div class="line"><span>{l}</span></div>' for l in HERO["headline_lines"])

    # Build the full template (loaded from template file)
    template = Path("template.html").read_text()
    page = (template
        .replace("{{TITLE}}", SITE["title"])
        .replace("{{DESCRIPTION}}", SITE["description"])
        .replace("{{DOMAIN}}", SITE["domain"])
        .replace("{{EMAIL_PRIMARY}}", SITE["email_primary"])
        .replace("{{EMAIL_DIRECT}}", SITE["email_direct"])
        .replace("{{IG_HANDLE}}", SITE["instagram_handle"])
        .replace("{{YOUTUBE_CHANNEL}}", SITE["youtube_channel"])
        .replace("{{LINKEDIN}}", SITE["linkedin"])
        .replace("{{HERO_TAG}}", HERO["tag"])
        .replace("{{HERO_HEADLINE}}", headline_html)
        .replace("{{HERO_METRICS}}", hero_metrics_html)
        .replace("{{MANIFESTO_HEADLINE}}", MANIFESTO["headline"])
        .replace("{{MANIFESTO_BODY}}", MANIFESTO["body"])
        .replace("{{MANIFESTO_FOUNDER}}", MANIFESTO["founder"])
        .replace("{{FILM_SECTIONS}}", sections_html)
        .replace("{{CAPABILITIES_NUM}}", f"{next_num:02d}")
        .replace("{{CAPABILITIES}}", caps_html)
        .replace("{{ORIGIN_NUM}}", f"{next_num + 1:02d}")
        .replace("{{PRE_AI_VIDEO_ID}}", PRE_AI_VIDEO_ID)
        .replace("{{SHOWCASE_VIDEO_ID}}", SHOWCASE_VIDEO_ID)
        .replace("{{FOLLOW_NUM}}", f"{next_num + 2:02d}")
        .replace("{{CONTACT_NUM}}", f"{next_num + 3:02d}")
        .replace("{{VIDEO_SCHEMAS}}", video_schemas)
        .replace("{{BUILD_TIME}}", datetime.utcnow().isoformat() + "Z")
    )

    Path("index.html").write_text(page)
    print(f"✓ Built index.html ({len(page):,} chars)")
    print(f"  {len(playlists)} playlist sections")
    print(f"  {sum(len(p.get('videos', [])[:6]) for p in playlists)} film cards visible (top 6 each)")

    # Regenerate sitemap.xml with showcase + current playlist titles
    write_sitemap(playlists)
    print(f"✓ Updated sitemap.xml")


def write_sitemap(playlists):
    """Build a fresh sitemap.xml with showcase film + top 2 per playlist."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    video_entries = []

    # Showcase first (top priority)
    video_entries.append(f"""    <video:video>
      <video:thumbnail_loc>https://img.youtube.com/vi/{SHOWCASE_VIDEO_ID}/maxresdefault.jpg</video:thumbnail_loc>
      <video:title>Woo Hoo Media Labs — Studio Showcase Film</video:title>
      <video:description>Studio showcase film from Woo Hoo Media Labs — an AI-native creative production lab in Mumbai. Directed by Chntan N. Shah.</video:description>
      <video:player_loc>https://www.youtube.com/embed/{SHOWCASE_VIDEO_ID}</video:player_loc>
      <video:content_loc>https://www.youtube.com/watch?v={SHOWCASE_VIDEO_ID}</video:content_loc>
    </video:video>""")

    # Then top 2 from each playlist
    for p in playlists:
        for v in p.get("videos", [])[:2]:
            vid = v["id"]
            title = clean_title(v.get("title", "Untitled")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            video_entries.append(f"""    <video:video>
      <video:thumbnail_loc>https://img.youtube.com/vi/{vid}/maxresdefault.jpg</video:thumbnail_loc>
      <video:title>{title}</video:title>
      <video:description>{title} — produced by Woo Hoo Media Labs ({p['name']})</video:description>
      <video:player_loc>https://www.youtube.com/embed/{vid}</video:player_loc>
      <video:content_loc>https://www.youtube.com/watch?v={vid}</video:content_loc>
    </video:video>""")

    videos_xml = "\n".join(video_entries)

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://woohoomedialabs.com/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
    <image:image>
      <image:loc>https://woohoomedialabs.com/og-cover.jpg</image:loc>
      <image:title>Woo Hoo Media Labs — Cinema for the age of intelligence</image:title>
    </image:image>
{videos_xml}
  </url>
</urlset>
'''
    Path("sitemap.xml").write_text(sitemap)


if __name__ == "__main__":
    build()

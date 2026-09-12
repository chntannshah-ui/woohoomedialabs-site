#!/usr/bin/env python3
"""
build_work.py — regenerates the /work/ film library (index + one page per film)
and sitemap.xml from work_manifest.json.

Workflow when new films go up on YouTube:
  1. Add the film to work_manifest.json  (id, title, category, date, len)
     — newest first inside its category.
  2. python3 build_work.py
  3. Upload work/, sitemap.xml to the repo → Vercel deploys.

Each film page carries a real, crawlable YouTube iframe (srcdoc facade for speed)
+ VideoObject schema with uploadDate/duration — that's what Google needs to
index the video ("watch page"). Keep it that way.
"""
import json, re, html, urllib.parse
from pathlib import Path

SITE = "https://www.woohoomedialabs.com"
FOOTER_STRIP = "Authored Intelligence — old eye, new toys. · Half cinema. Half code. All woohoo."
TAIL = ("Twenty-five years of cinematic craft. Authored Intelligence: "
        "every frame a human decision, executed by the machine.")
CATS = [  # display order on /work + description phrase
    ("Signature Films",         "a signature film from the studio reel"),
    ("AI Films",                "an AI-native film"),
    ("Product Films",           "a product launch &amp; demo film"),
    ("Corporate Communication", "a corporate &amp; brand communication film"),
    ("Government Films",        "a government &amp; public communication film"),
    ("Healthcare Films",        "a healthcare &amp; lifestyle film"),
]
CAT_PHRASE = dict(CATS)

manifest = json.loads(Path("work_manifest.json").read_text())
films = manifest["films"]

HEAD_CSS = Path("work_template.css").read_text().strip()

def esc(s): return html.escape(s, quote=True)
def clean(t): return re.sub(r"\s*\|\s*", " · ", t).replace("  ", " ").strip()
def slugify(t):
    t = re.sub(r"[^a-z0-9]+", "-", clean(t).lower().replace("&", " ")).strip("-")
    return t[:72].rstrip("-")
def iso_dur(sec):
    m, s = divmod(int(sec), 60); h, m = divmod(m, 60)
    return "PT" + (f"{h}H" if h else "") + (f"{m}M" if m else "") + f"{s}S"
def thumb(vid, q="hq720"): return f"https://i.ytimg.com/vi/{vid}/{q}.jpg"

def player(vid, title):
    embed = f"https://www.youtube-nocookie.com/embed/{vid}"
    srcdoc = (
        "<style>*{padding:0;margin:0;overflow:hidden}html,body{height:100%;background:#000}"
        "a{display:flex;align-items:center;justify-content:center;height:100%;position:relative}"
        "img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.85}"
        "span{position:relative;width:84px;height:84px;border-radius:50%;background:rgba(10,10,10,.6);"
        "display:flex;align-items:center;justify-content:center}svg{width:30px;height:30px;margin-left:4px;fill:#FFB000}</style>"
        f"<a href='{embed}?autoplay=1&rel=0&modestbranding=1&playsinline=1' aria-label='Play'>"
        f"<img src='{thumb(vid)}' onerror=\"this.onerror=null;this.src='{thumb(vid,'hqdefault')}'\" alt='{esc(title)}'>"
        "<span><svg viewBox='0 0 24 24'><path d='M6 4l14 8-14 8z'/></svg></span></a>"
    )
    return (f'<div class="player"><iframe src="{embed}?rel=0&modestbranding=1&playsinline=1" '
            f'srcdoc="{esc(srcdoc)}" title="{esc(title)}" loading="lazy" '
            f'allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>')

def nav(): return ('<nav><a href="/" aria-label="Woo Hoo Media Labs — home"><img src="/logo-white.png" alt="Woo Hoo Media Labs"></a>\n'
                   '<div class="links"><a href="/work">Work</a><a href="/#services">Services</a><a href="/#contact">Contact</a></div></nav>')
def footer(): return f'<footer><div>© 2026 Woo Hoo Media Labs · Mumbai · India</div><div>{FOOTER_STRIP}</div></footer>'
def head_common(): return ('<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta name="theme-color" content="#0a0a0a">\n')
def icons(): return '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="shortcut icon" href="/favicon.ico">'
def fonts(): return ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                     '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">')

# ---- order films: category order, manifest order inside category
ordered = []
for cat, _ in CATS:
    ordered += [f for f in films if f["category"] == cat]
for f in ordered:
    f["title_c"] = clean(f["title"])
    f.setdefault("slug", slugify(f["title"]))
    f["short"] = f["title_c"].split(" · ")[0]
    f["desc"] = f"{esc(f['short'])} — {CAT_PHRASE[f['category']]} produced by Woo Hoo Media Labs, the AI-native film and content production studio in Mumbai founded by Chntan N. Shah. {TAIL}"

# ---- film pages
for i, f in enumerate(ordered):
    prev = ordered[i-1] if i > 0 else None
    nxt = ordered[i+1] if i < len(ordered)-1 else None
    url = f"{SITE}/work/{f['slug']}"
    t, cat = f["title_c"], f["category"]
    vid = f["id"]
    desc_plain = html.unescape(f["desc"])
    video_ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": t, "description": desc_plain,
                "thumbnailUrl": [thumb(vid, "maxresdefault"), thumb(vid, "hqdefault")],
                "uploadDate": f["date"], "duration": iso_dur(f["len"]),
                "embedUrl": f"https://www.youtube-nocookie.com/embed/{vid}", "contentUrl": f"https://www.youtube.com/watch?v={vid}",
                "url": url, "publisher": {"@type": "Organization", "name": "Woo Hoo Media Labs", "url": SITE + "/"},
                "director": {"@type": "Person", "name": "Chntan N. Shah"}, "genre": cat, "inLanguage": "en"}
    bc_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Work", "item": SITE + "/work"},
        {"@type": "ListItem", "position": 3, "name": t, "item": url}]}
    wa = urllib.parse.quote(f"Hi Chntan, I saw “{f['short']}” and I'd like to discuss a project.")
    pn = '<div class="pn">'
    pn += f'<a href="/work/{prev["slug"]}">← {esc(prev["short"])}</a>' if prev else '<span></span>'
    pn += f'<a href="/work/{nxt["slug"]}" style="text-align:right">{esc(nxt["short"])} →</a>' if nxt else '<span></span>'
    pn += '</div>'
    page = f"""<!DOCTYPE html><html lang="en"><head>
{head_common()}<title>{esc(t)} | Woo Hoo Media Labs</title>
<meta name="description" content="{f['desc']}">
<link rel="canonical" href="{url}">
{icons()}
<meta property="og:type" content="video.other"><meta property="og:title" content="{esc(t)} | Woo Hoo Media Labs">
<meta property="og:description" content="{f['desc']}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{thumb(vid,'maxresdefault')}"><meta property="og:site_name" content="Woo Hoo Media Labs">
<meta property="og:video" content="https://www.youtube.com/embed/{vid}"><meta property="og:video:type" content="text/html"><meta property="og:video:width" content="1280"><meta property="og:video:height" content="720">
<meta name="twitter:card" content="player"><meta name="twitter:title" content="{esc(t)}"><meta name="twitter:player" content="https://www.youtube.com/embed/{vid}"><meta name="twitter:player:width" content="1280"><meta name="twitter:player:height" content="720">
<meta name="twitter:image" content="{thumb(vid,'maxresdefault')}"><meta name="twitter:creator" content="@chntannshah">
{fonts()}
<script type="application/ld+json">{json.dumps(video_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(bc_ld, ensure_ascii=False)}</script>
<style>{HEAD_CSS}</style></head><body>
{nav()}
<div class="wrap">
<div class="eyebrow">{cat} · Woo Hoo Media Labs</div>
<h1>{esc(t)}</h1>
{player(vid, t)}
<div class="meta">{cat} · Mumbai · {f['date'][:4]} · Authored at Woo Hoo Media Labs</div>
<p class="desc">{f['desc']}</p>
{pn}
<div class="cta"><h2>Want a film like this for your brand?</h2>
<a class="p" href="https://wa.me/918828429899?text={wa}" target="_blank" rel="noopener">WhatsApp the studio</a>
<a class="g" href="/#contact">Start a project brief →</a></div>
</div>
{footer()}
</body></html>
"""
    Path(f"work/{f['slug']}.html").write_text(page)

# ---- library index
n = len(ordered)
cards = ""
for cat, _ in CATS:
    items = [f for f in ordered if f["category"] == cat]
    if not items: continue
    cards += f'<h2 class="cathead">{cat}<span>{len(items)} films</span></h2><div class="grid">'
    for f in items:
        cards += (f'<a class="card" href="/work/{f["slug"]}"><img src="{thumb(f["id"])}" '
                  f'onerror="this.onerror=null;this.src=\'{thumb(f["id"],"hqdefault")}\'" alt="{esc(f["title_c"])}" loading="lazy">'
                  f'<h3>{esc(f["title_c"])}</h3></a>')
    cards += '</div>\n'
coll_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Film Library — Woo Hoo Media Labs", "url": SITE + "/work",
           "description": f"The complete film library of Woo Hoo Media Labs: {n} brand films, ad films, AI films, product films, government and healthcare films — produced in Mumbai by Chntan N. Shah.",
           "isPartOf": {"@type": "WebSite", "url": SITE + "/"},
           "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [
               {"@type": "ListItem", "position": i+1, "url": f"{SITE}/work/{f['slug']}", "name": f["title_c"]} for i, f in enumerate(ordered)]}}
index = f"""<!DOCTYPE html><html lang="en"><head>
{head_common()}<title>Film Library — {n} Films | Woo Hoo Media Labs, Mumbai</title>
<meta name="description" content="Browse the complete Woo Hoo Media Labs film library: {n} brand films, ad films, AI-native films, product launch films, government and healthcare films — produced in Mumbai by Chntan N. Shah.">
<link rel="canonical" href="{SITE}/work">
{icons()}
<meta property="og:type" content="website"><meta property="og:title" content="Film Library — {n} Films | Woo Hoo Media Labs">
<meta property="og:description" content="Every film, one library. Brand films, ad films, AI films, product films, government and healthcare films from Mumbai's AI-native studio.">
<meta property="og:url" content="{SITE}/work"><meta property="og:image" content="{SITE}/og-cover.jpg">
<meta property="og:site_name" content="Woo Hoo Media Labs">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:creator" content="@chntannshah">
{fonts()}
<script type="application/ld+json">{json.dumps(coll_ld, ensure_ascii=False)}</script>
<style>{HEAD_CSS}</style></head><body>
{nav()}
<div class="wrap">
<div class="eyebrow">The Film Library</div>
<h1>Every frame I've shipped.<br><em>{n} films and counting.</em></h1>
<p class="sub">Brand films, ad films, AI-native cinema, product launches, government communication and healthcare stories — authored in Mumbai at Woo Hoo Media Labs. Click any film to watch.</p>
{cards}
<div class="cta"><h2>Yours could be next.</h2>
<a class="p" href="https://wa.me/918828429899?text=Hi%20Chntan%2C%20I%27d%20like%20to%20discuss%20a%20film%20project." target="_blank" rel="noopener">WhatsApp the studio</a>
<a class="g" href="/#contact">Start a project brief →</a></div>
</div>
{footer()}
</body></html>
"""
Path("work/index.html").write_text(index)

# ---- sitemap
today = manifest.get("lastmod", "2026-09-12")
sm = Path("sitemap.xml").read_text()
head = sm[:sm.find("  <url>\n    <loc>https://www.woohoomedialabs.com/work</loc>")]  # keep homepage block as-is
if "<loc>https://www.woohoomedialabs.com/work</loc>" not in sm: raise SystemExit("sitemap: /work block not found")
urls = f"""  <url>
    <loc>{SITE}/work</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
"""
for f in ordered:
    urls += f"""  <url>
    <loc>{SITE}/work/{f['slug']}</loc>
    <lastmod>{f.get('lastmod', today)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
    <video:video>
      <video:thumbnail_loc>{thumb(f['id'],'hqdefault')}</video:thumbnail_loc>
      <video:title>{esc(f['title_c'])}</video:title>
      <video:description>{f['desc']}</video:description>
      <video:player_loc>https://www.youtube-nocookie.com/embed/{f['id']}</video:player_loc>
      <video:content_loc>https://www.youtube.com/watch?v={f['id']}</video:content_loc>
      <video:duration>{int(f['len'])}</video:duration>
      <video:publication_date>{f['date']}</video:publication_date>
    </video:video>
  </url>
"""
Path("sitemap.xml").write_text(head + urls + "</urlset>\n")
Path("work_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
print(f"✓ {n} film pages, work/index.html, sitemap.xml ({n+2} URLs)")

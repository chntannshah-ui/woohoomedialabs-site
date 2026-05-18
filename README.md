# Woo Hoo Media Labs — Website

Production-ready site for **woohoomedialabs.com**.
Static, fast, auto-updates from YouTube daily.

---

## 🚀 PREVIEW LOCALLY (FIRST THING TO DO)

To see everything actually playing in your real browser before deploying:

```bash
cd woohoomedialabs
bash preview.sh
```

Opens at **http://localhost:8000** in your browser. Hero video plays. Pre-AI showreel plays. Instagram reels render (once Meta's `embed.js` loads). Everything works.

If you don't have Python installed, on a Mac open Terminal and run:
```bash
python3 -m http.server 8000
```
…from inside the folder. Same result.

---

## 📁 FILES IN THIS PACKAGE

| File | What it does |
|---|---|
| `index.html` | The live site (auto-generated) |
| `styles.css` | All visual design |
| `app.js` | Cursor, scroll reveals, modal, click-to-play |
| `hero-reel.mp4` | Your 45-second hero loop (compressed to 13.7MB) |
| `hero-poster.jpg` | First-frame poster for the hero video |
| `logo.png` | Full logo (W + wordmark) |
| `logo-mark.png` | Just the W mark — used in nav |
| `favicon.png` | Browser tab icon |
| `ig_spy.jpg` | Local thumbnail for the spy reel |
| `playlists.json` | **Current state of all YT playlists** — the data layer |
| `build_playlists.py` | Fetches latest YT playlists → updates `playlists.json` |
| `build_site.py` | Renders `index.html` from `playlists.json` + `template.html` |
| `template.html` | Page template with `{{VARIABLE}}` placeholders |
| `preview.sh` | Local preview helper |
| `vercel.json` | Vercel hosting config (cache, security, daily cron) |
| `api/rebuild.py` | Vercel function — triggers daily rebuild |
| `404.html`, `robots.txt`, `sitemap.xml`, `site.webmanifest` | SEO/PWA support |

---

## 🔄 HOW AUTO-UPDATE WORKS

Two flows:

### Flow A — Manual update (right now, before deploying)

You reorder a playlist on YouTube → run two scripts → done:

```bash
python3 build_playlists.py    # fetches latest from YouTube
python3 build_site.py         # rebuilds index.html
```

Refresh your local preview, you see the new order.

### Flow B — Automatic update (after deploy)

Vercel runs both scripts **automatically every day at 04:00 UTC** via the cron in `vercel.json`. You change playlists on YouTube, the site updates within 24 hours. Zero maintenance.

The `playlists.json` file is the single source of truth. Whatever order/videos you have on YouTube is what shows on the site.

---

## 🎬 HOW TO UPDATE CONTENT

### Add or remove a video from a playlist section
Do it on YouTube. Run `build_playlists.py` + `build_site.py`. Refresh.

### Reorder videos in a section
Drag-reorder on YouTube. Same two scripts. The site uses YouTube's playlist order verbatim.

### Add a new playlist section
Edit `build_playlists.py` — add a new entry to the `PLAYLISTS` list at the top with `id`, `name`, `icon`, `tagline`. Re-run both scripts.

### Hide a video from a section
Edit `EXCLUDE_VIDEO_IDS` in `build_playlists.py`. The Salman/Bhai reel is already excluded — it appears in the IG section instead.

### Change Instagram reels
Edit `IG_REELS` list in `build_site.py`. Each entry has `shortcode`, `caption`, `likes`, `comments`, `views`, and an optional YouTube thumbnail fallback. Re-run `build_site.py`.

### Change hero video
Drop a new `hero-reel.mp4` (1920×1080, H.264, audio stripped, ideally <15MB). Optionally regenerate the poster:
```bash
ffmpeg -i hero-reel.mp4 -ss 2 -frames:v 1 -q:v 2 hero-poster.jpg
```

### Change hero metrics, capabilities, manifesto, contact info
Edit the relevant section in `build_site.py` near the top — `HERO`, `MANIFESTO`, `CAPABILITIES`. Re-run.

### Change logo
Replace `logo.png` and `logo-mark.png`. No script needed.

---

## 🌐 DEPLOY TO VERCEL

### Step 1 — Push to GitHub

```bash
cd woohoomedialabs
git init
git add .
git commit -m "Initial deploy"
git branch -M main
# Then create a repo on github.com and:
git remote add origin https://github.com/YOUR-USER/woohoomedialabs-site.git
git push -u origin main
```

### Step 2 — Import on Vercel

1. Go to **vercel.com** → sign in with GitHub
2. **Add New → Project** → pick `woohoomedialabs-site`
3. Framework Preset: **Other**
4. Build Command: `python3 build_playlists.py && python3 build_site.py` *(already in vercel.json)*
5. Output Directory: `./`
6. Click **Deploy**

In ~60 seconds you're live at `woohoomedialabs-site.vercel.app`.

### Step 3 — Connect your domain

In Vercel project → **Settings → Domains**:
- Add `woohoomedialabs.com`
- Add `www.woohoomedialabs.com`

Vercel gives you DNS records. Two paths:

**Easy — keep DNS at GoDaddy:**
- GoDaddy → My Products → woohoomedialabs.com → DNS → add Vercel's records.

**Better — move DNS to Cloudflare (free SSL extras, faster):**
- Sign up at cloudflare.com → add `woohoomedialabs.com` → it scans your records.
- Cloudflare gives you 2 nameservers → paste those in GoDaddy under Nameservers.
- In Cloudflare DNS, add Vercel's records.

### Step 4 — Set up the daily auto-rebuild

In Vercel project → **Settings → Deploy Hooks** → create a hook called "Daily auto rebuild" → it gives you a URL.

Then **Settings → Environment Variables** → add:
- Name: `VERCEL_DEPLOY_HOOK_URL`
- Value: (paste the URL from above)

Done. Site rebuilds every night.

### Step 5 — Redirect the .in domain

In GoDaddy → woohoomedialabs.in → Domain Forwarding:
- Forward to: `https://woohoomedialabs.com`
- Type: **301 (Permanent)**

---

## ✅ FINAL PRE-LAUNCH CHECKLIST

- [ ] Test locally with `bash preview.sh` and verify hero + showreel play
- [ ] Create an `og-cover.jpg` (1200×630) and drop it in the root for clean link previews on WhatsApp/LinkedIn
- [ ] Replace `logo.png` and `logo-mark.png` with the final logo when ready
- [ ] Submit to **Google Search Console** (`search.google.com/search-console`) and **Bing Webmaster Tools** after deploy
- [ ] Update social media bios to point to `woohoomedialabs.com`

---

## 🛠 TROUBLESHOOTING

**Pre-AI showreel won't play.** Click the play button (we use click-to-play, not autoplay). If it still shows "Error 153", it's because YouTube is restricting embeds on that specific video due to copyrighted music. Fix: in YouTube Studio, go to the video → check "Embedding" is allowed. If music is the issue, you may need to re-upload without that audio track.

**Hero video doesn't autoplay on iPhone.** Safari blocks autoplay unless `muted playsinline` are both set. They are. If it still doesn't, the video file may have encoding issues — re-export with `-pix_fmt yuv420p` and `-movflags +faststart` flags in ffmpeg.

**Instagram reels show as cards, not embedded.** Meta's `embed.js` is blocked somewhere. Usually:
- Sandbox/iframe environments block it (like Claude's preview)
- Ad-blockers block it
- Reel is set to private on Instagram
- Browser strict tracking prevention

On the deployed live site, this should not be an issue in normal browsers.

**Build script fails on YouTube fetch.** YouTube occasionally changes their HTML — the parser in `build_playlists.py` has 4 fallback patterns. If they all fail, the `playlists.json` already on disk is used (you don't lose old data). Upgrade path: switch to YouTube Data API v3 with an API key for guaranteed reliability.

---

## 📞 SUPPORT

This whole package was built fresh and is yours to modify. Everything is plain HTML/CSS/JS + a couple of Python scripts. No build pipeline, no node_modules, no React. You can edit any file with any text editor.

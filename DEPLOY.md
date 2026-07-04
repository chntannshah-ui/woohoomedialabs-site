# WOO HOO MEDIA LABS — SPRINT 1 DEPLOY
**One drop-in. Copy every file in this folder into your repo root (overwrite), commit, push. Vercel does the rest.**

---

## WHAT'S IN THE BOX

| File | What changed |
|---|---|
| `index.html` | Config block (GA4 + Formspree in one place) · dead GA placeholder removed · Montserrat font cut · three.js preloaded (intro starts faster) · hero video → v3 (72% smaller) · nav: "Work" replaces Boot Sequence (replay still in footer) · film thumbs → hq720 (~60% lighter) · WhatsApp CTA in contact · sticky mobile CTA bar · link to film library |
| `app.js` | Signature intro now plays **once per session** — repeat visits land instantly. ⟲ Boot Sequence button still replays it anytime. Sticky CTA logic added. |
| `yt-sync.js` | Lighter thumbnails on auto-synced grids |
| `styles.css` | Styles for WhatsApp buttons, sticky CTA, library link (brand tokens) |
| `hero-reel-v3.mp4` + `.webm` | 8.6 MB → 2.4 MB / 2.1 MB. Same 22s reel, 720p, visually identical in the hero |
| `logo-white.png` | 37 KB → 9 KB, pixel-identical |
| `favicon.ico` | Fixes the 404 every crawler was hitting |
| `og-cover.jpg` | Re-optimized |
| `sitemap.xml` | **72 URLs** (was 1). Every film = its own URL + video entry for Google Video |
| `llms.txt` | Film library added for AI search engines |
| `work/` | **71 new pages**: /work/ library + 70 individual film pages. Each has its own title, description, canonical, OG share card, VideoObject + Breadcrumb schema, prev/next links, WhatsApp CTA. Click-to-play facade = instant load. |

Old files you can delete from the repo after deploy: `hero-reel-v2.mp4`.

---

## ⚙️ YOUR 3 ACTIONS (≈12 minutes total)

**1. GA4 — 3 min.** analytics.google.com → Create property "Woo Hoo Media Labs" → Web stream for woohoomedialabs.com → copy the `G-XXXXXXXXXX` Measurement ID → paste it into the SITE CONFIG block at the top of `index.html` (`window.WH_GA_ID`). Analytics starts on next deploy.

**2. Formspree — 3 min.** formspree.io → sign up with chntan.n.shah@gmail.com → New Form → copy the 8-char form ID from the endpoint URL → paste into `window.FORMSPREE_ID` in the same config block. **Until this is set, form submissions only open the visitor's mail app — leads leak.** This is the highest-priority paste.

**3. Vercel domain — ALREADY DONE.** This build uses www.woohoomedialabs.com as the primary URL everywhere (matching your existing Vercel setup). No dashboard change needed. Skip.

**4. Search engines — 8 min.**
   - search.google.com/search-console → add property `woohoomedialabs.com` (Domain type, DNS verify via Vercel) → Sitemaps → submit `https://www.woohoomedialabs.com/sitemap.xml` (full URL)
   - bing.com/webmasters → import from Search Console (one click)
   - business.google.com → create profile: "Woo Hoo Media Labs · Film Production Company · Mumbai" → link website + YouTube. This puts you in the Maps pack for "video production Mumbai."

---

## VERIFY AFTER DEPLOY (2 min)
1. Hard-refresh homepage → intro plays → reload → lands instantly (intro skipped) → footer ⟲ replays it
2. Open `/work/` → click any film → plays in-page
3. Phone: scroll past hero → gold "Start a film →" bar appears
4. Submit the contact form → arrives in Formspree inbox
5. Share a film page link on WhatsApp → unique cinematic card per film

// Woo Hoo Media Labs — playlist proxy (Vercel Edge Function)
// Reads each YouTube playlist page server-side (no API key) and returns clean JSON.
// YouTube retired the playlist RSS feeds in Sept 2026, so we parse the page itself:
// lockupViewModel for normal videos, reelWatchEndpoint for Shorts (vertical) playlists.
// CDN-cached 1h; falls back to the baked feed.json whenever a fetch is refused.
export const config = { runtime: 'edge' };

const SECTIONS = [
  ['ai',         'PLAcjSzaUUVHkV3bR_j_R6dRuiUQp7I1DS', false],
  ['product',    'PLAcjSzaUUVHm1Vc7IenJvn5DONdYlO9WO', false],
  ['corporate',  'PLAcjSzaUUVHkC11dQr16d5rlJRrmxfW2-', false],
  ['government', 'PLAcjSzaUUVHnhfDWDkGhTKN2mRHSQ8Xyy', false],
  ['healthcare', 'PLAcjSzaUUVHm_N6lKfpdQ0e1TqTJ5y7gg', false],
  ['signature',  'PLAcjSzaUUVHl66UVP317jEsE95ZnwiAho', false],
  ['faith',      'PLah1g5o0db8s',                      true ],
  ['bappa',      'PLaYnl50OiPxI',                      true ],
];
const EXCLUDE = new Set(['N23lUkPsrnw']);

function decode(s) {
  let t = (s || '').replace(/\\u([0-9a-fA-F]{4})/g, (_, h) => String.fromCharCode(parseInt(h, 16)))
    .replace(/\\"/g, '"').replace(/\\\//g, '/')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&#x27;/gi, "'");
  return t.replace(/\s*\|\s*/g, ' · ').replace(/\s+/g, ' ').trim();
}

function parseShorts(h) {
  const out = [], seen = new Set();
  const re = /"reelWatchEndpoint":\{"videoId":"([A-Za-z0-9_-]{11})"/g;
  let m;
  while ((m = re.exec(h))) {
    const id = m[1];
    if (seen.has(id) || EXCLUDE.has(id)) continue;
    seen.add(id);
    const pre = h.slice(Math.max(0, m.index - 4000), m.index);
    const t = pre.match(/"accessibilityText":"((?:[^"\\]|\\.)+)"(?![\s\S]*"accessibilityText")/);
    let title = t ? t[1] : '';
    title = title.replace(/,\s*[\d.,]+\s*(?:thousand|million|K|M)?\s*views?\s*-\s*play Short\s*$/, '');
    out.push({ id, title: decode(title) });
  }
  return out;
}

function parseVideos(h) {
  const ev = [], out = [], seen = new Set();
  let m;
  const rid = /"contentId":"([A-Za-z0-9_-]{11})","contentType":"LOCKUP_CONTENT_TYPE_VIDEO"/g;
  while ((m = rid.exec(h))) ev.push([m.index, 'id', m[1]]);
  const rt = /"lockupMetadataViewModel":\{"title":\{"content":"((?:[^"\\]|\\.)+)"/g;
  while ((m = rt.exec(h))) ev.push([m.index, 't', m[1]]);
  ev.sort((a, b) => a[0] - b[0]);
  let title = '';
  for (const [, kind, val] of ev) {
    if (kind === 't') { title = val; continue; }
    if (seen.has(val) || EXCLUDE.has(val)) continue;
    seen.add(val);
    out.push({ id: val, title: decode(title) });
    title = '';
  }
  return out;
}

async function page(pid, vertical) {
  try {
    const r = await fetch('https://www.youtube.com/playlist?list=' + pid, {
      cache: 'no-store',
      headers: {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml',
        'accept-language': 'en-US,en;q=0.9',
      },
    });
    if (!r.ok) return [];
    const h = await r.text();
    return vertical ? parseShorts(h) : parseVideos(h);
  } catch (e) { return []; }
}

export default async function handler(req) {
  try {
    const pairs = await Promise.all(SECTIONS.map(async ([k, p, v]) => [k, await page(p, v)]));
    const playlists = Object.fromEntries(pairs);
    // YouTube often refuses datacenter fetches → fall back to the baked feed.json
    // (regenerated every 6h by the refresh-playlists GitHub Action) for any empty grid.
    if (Object.values(playlists).some((v) => !v.length)) {
      try {
        const b = await fetch(new URL('/feed.json', req.url), { cache: 'no-store' });
        if (b.ok) {
          const baked = (await b.json()).playlists || {};
          for (const k of Object.keys(playlists)) if (!playlists[k].length && baked[k]) playlists[k] = baked[k];
        }
      } catch (e) {}
    }
    return new Response(JSON.stringify({ ok: true, playlists }), {
      headers: {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'public, s-maxage=3600, stale-while-revalidate=86400, max-age=600',
        'access-control-allow-origin': '*',
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), {
      status: 500, headers: { 'content-type': 'application/json' },
    });
  }
}

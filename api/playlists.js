// Woo Hoo Media Labs — playlist proxy (Vercel Edge Function)
// Fetches each YouTube playlist's public RSS feed server-side (no API key),
// returns clean JSON. CDN-cached 1h. Powers the auto-syncing film grids.
export const config = { runtime: 'edge' };

const SECTIONS = [
  ['ai',         'PLAcjSzaUUVHkV3bR_j_R6dRuiUQp7I1DS'],
  ['product',    'PLAcjSzaUUVHm1Vc7IenJvn5DONdYlO9WO'],
  ['corporate',  'PLAcjSzaUUVHkC11dQr16d5rlJRrmxfW2-'],
  ['government', 'PLAcjSzaUUVHnhfDWDkGhTKN2mRHSQ8Xyy'],
  ['healthcare', 'PLAcjSzaUUVHm_N6lKfpdQ0e1TqTJ5y7gg'],
  ['signature',  'PLAcjSzaUUVHl66UVP317jEsE95ZnwiAho'],
];

function decode(s) {
  return (s || '')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&#x27;/gi, "'")
    .replace(/\s*\|\s*/g, ' \u00b7 ').replace(/\s+/g, ' ').trim();
}
function parse(xml) {
  const out = [];
  const parts = xml.split('<entry>').slice(1);
  for (const p of parts) {
    const id = p.match(/<yt:videoId>([^<]+)<\/yt:videoId>/);
    const t = p.match(/<title>([\s\S]*?)<\/title>/);
    if (id) out.push({ id: id[1], title: decode(t ? t[1] : '') });
  }
  return out;
}
async function feed(pid) {
  try {
    const r = await fetch('https://www.youtube.com/feeds/videos.xml?playlist_id=' + pid,
      { headers: { 'user-agent': 'Mozilla/5.0' } });
    if (!r.ok) return [];
    return parse(await r.text());
  } catch (e) { return []; }
}
export default async function handler() {
  try {
    const pairs = await Promise.all(SECTIONS.map(async ([k, p]) => [k, await feed(p)]));
    const playlists = Object.fromEntries(pairs);
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

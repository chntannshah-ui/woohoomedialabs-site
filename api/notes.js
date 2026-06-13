// Persistent shared comments for Pixel Spa.
// Storage: Upstash Redis list (via Vercel Marketplace). No SDK — plain REST + fetch.
// GET  /api/notes              -> { notes: [[name, text], ...] }   newest first
// POST /api/notes {name,note}  -> { ok: true }                     appended, list capped
//
// The Redis token stays server-side, so visitors can add/read but never wipe the store.
function creds() {
  const url = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || process.env.STORAGE_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || process.env.STORAGE_REST_API_TOKEN;
  return { url, token };
}
async function redis(pathParts) {
  const { url, token } = creds();
  if (!url || !token) throw new Error('no-store');
  const r = await fetch(url + '/' + pathParts.map(encodeURIComponent).join('/'),
    { headers: { Authorization: 'Bearer ' + token } });
  if (!r.ok) throw new Error('redis ' + r.status);
  const j = await r.json();
  return j.result;
}

const KEY = 'pixelspa:notes';
const CAP = 200;            // keep the most recent 200 comments

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  try {
    if (req.method === 'POST') {
      // Read JSON body (Vercel may pass it parsed or raw)
      let body = req.body;
      if (typeof body === 'string') { try { body = JSON.parse(body); } catch (_) { body = {}; } }
      if (!body || typeof body !== 'object') body = {};
      let name = String(body.name || 'someone').replace(/[\u0000-\u001f]/g, '').trim().slice(0, 24) || 'someone';
      let note = String(body.note || '').replace(/[\u0000-\u001f]/g, '').trim().slice(0, 90);
      if (!note) { res.status(400).json({ ok: false, error: 'empty' }); return; }
      const entry = JSON.stringify([name, note]);
      await redis(['lpush', KEY, entry]);   // newest at head
      await redis(['ltrim', KEY, '0', String(CAP - 1)]);
      res.status(200).json({ ok: true });
      return;
    }
    // GET — newest first
    const raw = await redis(['lrange', KEY, '0', String(CAP - 1)]);
    const notes = (Array.isArray(raw) ? raw : []).map(s => {
      try { const a = JSON.parse(s); return [String(a[0] || ''), String(a[1] || '')]; }
      catch (_) { return null; }
    }).filter(Boolean);
    res.status(200).json({ notes });
  } catch (e) {
    res.status(200).json({ notes: null, fallback: true });
  }
};

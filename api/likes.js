// Persistent shared "likes" counter for Pixel Spa.
// Storage: Upstash Redis (via Vercel Marketplace). No SDK — plain REST + fetch.
// GET  /api/likes        -> { count }
// POST /api/likes        -> { count }  (atomic increment, only ever grows)
//
// Reads creds from whichever names Vercel/Upstash injected.
function creds() {
  const url = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || process.env.STORAGE_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || process.env.STORAGE_REST_API_TOKEN;
  return { url, token };
}
async function redis(command) {
  const { url, token } = creds();
  if (!url || !token) throw new Error('no-store');
  const r = await fetch(url + '/' + command, { headers: { Authorization: 'Bearer ' + token } });
  if (!r.ok) throw new Error('redis ' + r.status);
  const j = await r.json();
  return j.result;
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  try {
    let count;
    if (req.method === 'POST') count = await redis('incr/pixelspa:likes');
    else count = await redis('get/pixelspa:likes');
    res.status(200).json({ count: parseInt(count || 0, 10) || 0 });
  } catch (e) {
    // Backend not configured yet — tell the client to use its local fallback.
    res.status(200).json({ count: null, fallback: true });
  }
};

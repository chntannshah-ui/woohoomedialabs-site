/* Woo Hoo Media Labs — film grid playlist auto-sync.
   On load, pulls each .film-grid from its YouTube playlist via /api/playlists
   and re-renders the cards. Silently keeps the server-rendered cards if the
   fetch fails. Self-contained — does not depend on app.js internals. */
(function () {
  var COUNT = { signature: 3 }; // default 6 cards per grid
  function openVid(id) {
    var modal = document.getElementById('modal');
    var iframe = document.getElementById('modal-iframe');
    if (!modal || !iframe) return;
    iframe.src = 'https://www.youtube-nocookie.com/embed/' + id +
      '?autoplay=1&rel=0&modestbranding=1&iv_load_policy=3&playsinline=1';
    modal.classList.add('open');
  }
  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
  }
  function card(v) {
    var i = esc(v.id), t = esc(v.title);
    return '<div class="film-card" data-cursor data-yt="' + i + '" data-ytsync="1">' +
      '<img class="film-thumb" src="https://i.ytimg.com/vi/' + i + '/hq720.jpg" ' +
      'alt="' + t + '" loading="lazy" onerror="this.onerror=null;this.src=\'https://img.youtube.com/vi/' + i + '/hqdefault.jpg\'" />' +
      '<div class="film-meta"><h3>' + t + '</h3><div class="play">Play \u2197</div></div></div>';
  }
  // single delegated handler, scoped to synced cards (no double-bind with app.js)
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('.film-card[data-ytsync]') : null;
    if (t && t.getAttribute('data-yt')) openVid(t.getAttribute('data-yt'));
  });
  function hydrate(data) {
    document.querySelectorAll('.film-grid[data-playlist-key]').forEach(function (grid) {
      var key = grid.getAttribute('data-playlist-key');
      var vids = data && data[key];
      if (!vids || !vids.length) return; // keep baked-in fallback
      var n = COUNT[key] || 6;
      var html = vids.slice(0, n).map(card).join('');
      if (html) grid.innerHTML = html;
    });
  }
  try {
    fetch('/api/playlists', { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d && d.ok && d.playlists) hydrate(d.playlists); })
      .catch(function () {});
  } catch (e) {}
})();

// ─── CUSTOM CURSOR ──────────────────────────────────────────
const cursor = document.querySelector('.cursor');
const trail = document.querySelector('.cursor-trail');
let mx = 0, my = 0, tx = 0, ty = 0;
document.addEventListener('mousemove', (e) => {
  mx = e.clientX; my = e.clientY;
  cursor.style.left = mx + 'px';
  cursor.style.top = my + 'px';
});
(function animateTrail() {
  tx += (mx - tx) * 0.15; ty += (my - ty) * 0.15;
  trail.style.left = tx + 'px'; trail.style.top = ty + 'px';
  requestAnimationFrame(animateTrail);
})();
document.querySelectorAll('[data-cursor], button, a, input, textarea, .film-card').forEach(el => {
  el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
  el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
});

// ─── REVEAL ON SCROLL ───────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
}, { threshold: 0.08 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// ─── VIDEO MODAL (for film grid clicks) ─────────────────────
const modal = document.getElementById('modal');
const iframe = document.getElementById('modal-iframe');
function openVideo(id) {
  iframe.src = `https://www.youtube.com/embed/${id}?autoplay=1&rel=0&modestbranding=1`;
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeVideo() {
  modal.classList.remove('open');
  iframe.src = '';
  document.body.style.overflow = '';
}
document.querySelectorAll('[data-yt]').forEach(el => {
  el.addEventListener('click', () => openVideo(el.getAttribute('data-yt')));
});
document.querySelector('.modal-close').addEventListener('click', closeVideo);
modal.addEventListener('click', (e) => { if (e.target === modal) closeVideo(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeVideo(); });

// ─── PRE-AI SHOWREEL — CLICK TO PLAY ────────────────────────
// Replaces the poster image with the YouTube iframe only when user clicks.
// Avoids autoplay restrictions, Error 153, and cuts initial page weight.
(function setupOriginVideo() {
  const wrap = document.getElementById('origin-video');
  if (!wrap) return;
  const playBtn = wrap.querySelector('.origin-play');
  const poster = wrap.querySelector('.origin-poster');
  function play() {
    const iframe = document.createElement('iframe');
    iframe.src = 'https://www.youtube.com/embed/F-spjRJSgus?autoplay=1&rel=0&modestbranding=1';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.allowFullscreen = true;
    iframe.frameBorder = '0';
    wrap.appendChild(iframe);
    if (poster) poster.style.display = 'none';
    if (playBtn) playBtn.style.display = 'none';
  }
  wrap.addEventListener('click', play);
})();

// ─── CONTACT FORM ───────────────────────────────────────────
function handleSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const company = document.getElementById('company').value;
  const inquiry = document.getElementById('inquiry').value;
  const subject = encodeURIComponent(`Inquiry from ${name}${company ? ' / ' + company : ''}`);
  const body = encodeURIComponent(`Name: ${name}\nEmail: ${email}\nCompany: ${company || '—'}\n\n${inquiry}`);
  window.location.href = `mailto:chntan.n.shah@gmail.com?subject=${subject}&body=${body}`;
}

// ─── VIGNETTE SPOTLIGHT CURSOR ──────────────────────────────
// Soft marigold-tinted glow follows the mouse — barely visible, just a feeling.
// On interactive elements, a small marigold dot appears for precision feedback.
(function setupVignette() {
  if (window.matchMedia('(max-width: 768px)').matches) return;
  const root = document.documentElement;
  const hotDot = document.getElementById('hot-dot');
  let mx = window.innerWidth / 2, my = window.innerHeight / 2;
  let dx = mx, dy = my;

  document.addEventListener('mousemove', (e) => {
    mx = e.clientX; my = e.clientY;
    if (hotDot) {
      hotDot.style.left = mx + 'px';
      hotDot.style.top = my + 'px';
    }
  });

  function tick() {
    dx += (mx - dx) * 0.16;
    dy += (my - dy) * 0.16;
    root.style.setProperty('--mx', dx + 'px');
    root.style.setProperty('--my', dy + 'px');
    requestAnimationFrame(tick);
  }
  tick();

  const interactiveSel = '[data-cursor], button, a, input, textarea, .film-card, summary, details';
  document.querySelectorAll(interactiveSel).forEach(el => {
    el.addEventListener('mouseenter', () => hotDot && hotDot.classList.add('active'));
    el.addEventListener('mouseleave', () => hotDot && hotDot.classList.remove('active'));
  });
})();

// ─── HERO VIDEO PLAY GUARANTEE ──────────────────────────────
// Some browsers (Safari, low-power mode) block autoplay even with muted+playsinline.
// We attempt to play explicitly, retry on errors, and fall back to user-initiated start.
(function ensureHeroPlay() {
  const video = document.querySelector('.hero-video');
  if (!video) return;

  function tryPlay() {
    const p = video.play();
    if (p && typeof p.then === 'function') {
      p.catch(() => {
        // Autoplay blocked — wait for first user gesture, then try again
        const onGesture = () => {
          video.play().catch(() => {});
          document.removeEventListener('click', onGesture);
          document.removeEventListener('scroll', onGesture);
          document.removeEventListener('touchstart', onGesture);
        };
        document.addEventListener('click', onGesture, { once: true });
        document.addEventListener('scroll', onGesture, { once: true });
        document.addEventListener('touchstart', onGesture, { once: true });
      });
    }
  }

  // Try immediately when metadata loads, and again on full load
  if (video.readyState >= 2) tryPlay();
  video.addEventListener('loadedmetadata', tryPlay);
  video.addEventListener('canplay', tryPlay);
  // Resume on visibility return
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && video.paused) tryPlay();
  });
})();

// ─── MOBILE MENU ────────────────────────────────────────────
(function setupMobileMenu() {
  const toggle = document.getElementById('nav-toggle');
  const overlay = document.getElementById('menu-overlay');
  const closeBtn = document.getElementById('menu-close');
  if (!toggle || !overlay) return;

  function open() {
    overlay.classList.add('open');
    overlay.setAttribute('aria-hidden', 'false');
    toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function close() {
    overlay.classList.remove('open');
    overlay.setAttribute('aria-hidden', 'true');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
  toggle.addEventListener('click', open);
  if (closeBtn) closeBtn.addEventListener('click', close);
  // Close on link click (so anchor navigation works)
  overlay.querySelectorAll('a').forEach(a => a.addEventListener('click', close));
  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('open')) close();
  });
})();

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

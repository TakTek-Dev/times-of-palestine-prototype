// The Times of Palestine prototype: loader, page bar, menu, reveals, three-leaf viewer, search, story progress.
(() => {
  const root = document.documentElement;
  const veil = document.querySelector('.veil');
  const bar = document.querySelector('.pagebar');
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  // ---- entry: the three leaves once per session, a three-colour bar between pages ----
  function arrive() {
    const boot = root.classList.contains('boot');
    setTimeout(() => {
      veil && boot && veil.classList.add('lift');
      root.classList.add('ready');
      root.classList.remove('nav-in');
      bar && bar.classList.add('done');
      setTimeout(() => { root.classList.remove('boot'); veil && veil.classList.remove('lift'); bar && bar.classList.remove('done', 'go'); }, 620);
    }, boot && !still ? 1500 : 40);
    try { sessionStorage.setItem('tp-on', '1'); sessionStorage.removeItem('tp-nav'); } catch (e) {}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arrive); else arrive();
  setTimeout(() => { root.classList.add('ready'); root.classList.remove('boot', 'nav-in'); }, 6000);
  addEventListener('pageshow', (e) => { if (e.persisted) { root.classList.remove('boot', 'nav-in', 'leaving'); root.classList.add('ready'); bar && bar.classList.remove('go', 'done'); } });

  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a || still || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.button || a.target === '_blank') return;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin || (url.pathname === location.pathname && url.hash) || a.hasAttribute('download')) return;
    e.preventDefault();
    try { sessionStorage.setItem('tp-nav', '1'); } catch (err) {}
    root.classList.add('leaving'); bar && bar.classList.add('go');
    setTimeout(() => { location.href = a.href; }, 230);
  });

  // ---- theme ----
  $$('[data-theme-toggle]').forEach((b) => b.addEventListener('click', () => {
    const dark = root.dataset.theme !== 'dark';
    root.dataset.theme = dark ? 'dark' : 'light';
    b.setAttribute('aria-pressed', dark);
    try { localStorage.setItem('tp-theme', root.dataset.theme); } catch (e) {}
  }));

  // ---- menu ----
  const sheet = $('.sheet');
  if (sheet) {
    const openBtn = $('.burger');
    const set = (on) => {
      sheet.classList.toggle('open', on); openBtn.setAttribute('aria-expanded', on);
      sheet.inert = !on; document.body.style.overflow = on ? 'hidden' : '';
      (on ? $('.sheet-close') : openBtn).focus();
    };
    sheet.inert = true;
    openBtn.addEventListener('click', () => set(true));
    $('.sheet-close').addEventListener('click', () => set(false));
    addEventListener('keydown', (e) => { if (e.key === 'Escape' && sheet.classList.contains('open')) set(false); });
  }

  // ---- header hides going down; story progress in the mark's three colours ----
  const top = $('.top');
  let last = 0;
  addEventListener('scroll', () => {
    const y = scrollY;
    if (top) top.classList.toggle('away', y > 400 && y > last);
    last = y;
    const prog = $('.prog'), prose = $('.prose');
    if (prog && prose) {
      const r = prose.getBoundingClientRect();
      prog.style.transform = `scaleX(${Math.min(1, Math.max(0, (innerHeight * 0.6 - r.top) / r.height))})`;
    }
  }, { passive: true });

  // ---- reveal ----
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -8% 0px' });
    $$('.rv').forEach((el) => io.observe(el));
  } else $$('.rv').forEach((el) => el.classList.add('in'));

  // ---- rails ----
  $$('[data-rail]').forEach((nav) => {
    const rail = document.getElementById(nav.dataset.rail);
    nav.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      rail.scrollBy({ left: (b.dataset.dir === 'next' ? 1 : -1) * rail.clientWidth * 0.8, behavior: still ? 'auto' : 'smooth' });
    });
  });

  // ---- relative time against the edition's own clock ----
  const now = new Date(document.body.dataset.now || Date.now());
  $$('time[data-rel]').forEach((t) => {
    const mins = Math.round((now - new Date(t.dateTime)) / 60000);
    if (mins < 0) return;
    if (mins < 60) t.textContent = `${Math.max(1, mins)} min ago`;
    else if (mins < 1440) t.textContent = `${Math.round(mins / 60)} hr ago`;
    else if (mins < 10080) t.textContent = `${Math.round(mins / 1440)} d ago`;
  });

  // ---- discover: a story in three leaves (now, why, on record) ----
  const dataEl = $('#shorts-data');
  if (dataEl) {
    const shorts = JSON.parse(dataEl.textContent);
    const base = document.body.dataset.base || '';
    const leaf = '<i class="lf"></i>';
    const viewer = document.createElement('div');
    viewer.className = 'viewer'; viewer.setAttribute('role', 'dialog'); viewer.setAttribute('aria-modal', 'true'); viewer.setAttribute('aria-label', 'Discover');
    viewer.innerHTML = `<div class="stage" data-step="0"><div class="stage-bar"><b></b></div><div class="three">${leaf}${leaf}${leaf}</div><span class="stage-step"></span><div class="stage-hit"><button type="button" aria-label="Back"></button><button type="button" aria-label="Next"></button></div><div class="stage-txt" aria-live="polite"></div><button type="button" class="ib stage-x" aria-label="Close"><svg class="ic" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>`;
    document.body.append(viewer);
    const stage = $('.stage', viewer), txt = $('.stage-txt', stage), leaves = $$('.three .lf', stage), fill = $('.stage-bar b', stage), label = $('.stage-step', stage);
    const img = new Image(); img.alt = ''; stage.prepend(img);
    const NAMES = ['Now', 'Why', 'On record'];
    let at = 0, step = 0, timer = 0, opener = null;
    const DUR = 5600;
    function paint() {
      const s = shorts[at];
      stage.dataset.step = step;
      if (img.dataset.id !== s.id) { img.dataset.id = s.id; if (s.photo) { img.src = `${base}assets/img/${s.id}.webp`; img.hidden = false; } else img.hidden = true; }
      label.textContent = `${NAMES[step]} · ${at + 1} of ${shorts.length}`;
      leaves.forEach((l, i) => l.classList.toggle('on', i <= step));
      txt.innerHTML = step === 0 ? `<span class="tag">${s.tag}</span><h2>${s.title}</h2>`
        : step === 1 ? `<p>${s.gist}</p>`
          : `<p>${s.more}</p><small>${s.sources}</small><a class="btn" href="${base}story/${s.id}.html">Read the story<svg class="ic" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>`;
      fill.getAnimations().forEach((a) => a.cancel());
      clearTimeout(timer);
      if (!still) { fill.animate([{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], { duration: DUR, fill: 'forwards' }); timer = setTimeout(() => go(1), DUR); }
    }
    function go(d) {
      step += d;
      if (step > 2) { step = 0; at = (at + 1) % shorts.length; }
      if (step < 0) { at = (at - 1 + shorts.length) % shorts.length; step = 0; }
      paint();
    }
    function open(id, from) {
      at = Math.max(0, shorts.findIndex((s) => s.id === id)); step = 0; opener = from;
      viewer.classList.add('open'); document.body.style.overflow = 'hidden'; paint(); $('.stage-x', viewer).focus();
    }
    function close() { viewer.classList.remove('open'); document.body.style.overflow = ''; clearTimeout(timer); opener && opener.focus(); }
    const hits = $$('.stage-hit button', viewer);
    hits[0].addEventListener('click', () => go(-1)); hits[1].addEventListener('click', () => go(1));
    $('.stage-x', viewer).addEventListener('click', close);
    viewer.addEventListener('click', (e) => { if (e.target === viewer) close(); });
    addEventListener('keydown', (e) => {
      if (!viewer.classList.contains('open')) return;
      if (e.key === 'Escape') close(); if (e.key === 'ArrowRight') go(1); if (e.key === 'ArrowLeft') go(-1);
    });
    $$('[data-short]').forEach((b) => b.addEventListener('click', () => open(b.dataset.short, b)));
  }

  // ---- search ----
  const form = $('#find');
  if (form) {
    const input = $('input', form), out = $('#results'), count = $('#count');
    const base = document.body.dataset.base || '';
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    fetch(base + 'assets/stories.json').then((r) => r.json()).then((all) => {
      function run() {
        const q = input.value.trim().toLowerCase();
        const words = q.split(/\s+/).filter(Boolean);
        const hits = !q ? all.slice(0, 12) : all.filter((s) => words.every((w) => s.hay.includes(w)));
        const rx = words.length ? new RegExp('(' + words.map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'ig') : null;
        const hi = (t) => rx ? esc(t).replace(rx, '<mark>$1</mark>') : esc(t);
        count.textContent = !q ? 'Latest stories' : hits.length ? `${hits.length} ${hits.length === 1 ? 'story' : 'stories'} for “${input.value.trim()}”` : `Nothing for “${input.value.trim()}” yet. Try a place, a topic or a name.`;
        out.innerHTML = hits.map((s) => `<a class="row" href="${base}story/${s.id}.html">${s.photo ? `<span class="ph"><img src="${base}assets/img/${s.id}-s.webp" alt="" loading="lazy" width="560" height="350"></span>` : '<span class="ph none"><i class="lf"></i></span>'}<div><span class="tag ${s.age}"><i class="lf"></i><b>${esc(s.tag)}</b></span><h3>${hi(s.title)}</h3><span class="when">${esc(s.when)} · ${esc(s.place)}</span></div></a>`).join('');
        const url = new URL(location.href); q ? url.searchParams.set('q', input.value.trim()) : url.searchParams.delete('q'); history.replaceState(null, '', url);
      }
      input.value = new URLSearchParams(location.search).get('q') || '';
      input.addEventListener('input', run); form.addEventListener('submit', (e) => { e.preventDefault(); run(); });
      run();
    });
  }

  // ---- share ----
  $$('[data-share]').forEach((b) => b.addEventListener('click', async () => {
    const label = $('span', b), was = label.textContent;
    try {
      if (b.dataset.share === 'native' && navigator.share) await navigator.share({ title: document.title, url: location.href });
      else { await navigator.clipboard.writeText(location.href); label.textContent = 'Link copied'; setTimeout(() => { label.textContent = was; }, 1800); }
    } catch (e) {}
  }));
})();

/* Kusaidia Afrika – minimal client-side enhancements */

(function () {
  'use strict';

  // ---- Sticky header shadow on scroll ----
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => {
      if (window.scrollY > 8) header.classList.add('is-scrolled');
      else header.classList.remove('is-scrolled');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---- Mobile nav toggle ----
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
      document.body.style.overflow = !open ? 'hidden' : '';
    });

    nav.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
        document.body.style.overflow = '';
      });
    });
  }

  // ---- Hero slideshow ----
  const slides = document.querySelectorAll('.hero__slide');
  if (slides.length > 1) {
    let i = 0;
    setInterval(() => {
      slides[i].classList.remove('is-active');
      i = (i + 1) % slides.length;
      slides[i].classList.add('is-active');
    }, 6000);
  }

  // ---- Reveal on scroll (subtle fade-up) ----
  const reveals = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && reveals.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });
    reveals.forEach(el => io.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('is-visible'));
  }

  // ---- Copy IBAN to clipboard ----
  document.querySelectorAll('[data-copy]').forEach(el => {
    el.addEventListener('click', async () => {
      const value = el.getAttribute('data-copy');
      try {
        await navigator.clipboard.writeText(value);
        const original = el.textContent;
        el.textContent = 'Kopiert ✓';
        setTimeout(() => { el.textContent = original; }, 1600);
      } catch (e) {
        /* no-op */
      }
    });
  });

  // ---- Lightbox (gallery page) ----
  const tiles = document.querySelectorAll('.gallery-tile');
  if (tiles.length) {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.setAttribute('role', 'dialog');
    lightbox.setAttribute('aria-modal', 'true');
    lightbox.setAttribute('aria-label', 'Bildansicht');
    lightbox.innerHTML = `
      <div class="lightbox__counter" aria-live="polite"></div>
      <button class="lightbox__close" type="button" aria-label="Schließen">
        <svg class="lightbox__icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
      <button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Vorheriges Bild">
        <svg class="lightbox__icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>
      </button>
      <button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Nächstes Bild">
        <svg class="lightbox__icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
      </button>
      <div class="lightbox__stage">
        <img class="lightbox__img" alt="" />
        <figcaption class="lightbox__caption"></figcaption>
      </div>
    `;
    document.body.appendChild(lightbox);

    const imgEl = lightbox.querySelector('.lightbox__img');
    const capEl = lightbox.querySelector('.lightbox__caption');
    const counterEl = lightbox.querySelector('.lightbox__counter');
    const tilesArr = Array.from(tiles);
    let idx = 0;

    const show = (i) => {
      idx = (i + tilesArr.length) % tilesArr.length;
      const img = tilesArr[idx].querySelector('img');
      imgEl.src = img.dataset.full || img.src;
      imgEl.alt = img.alt || '';
      capEl.textContent = img.alt || '';
      counterEl.textContent = `${idx + 1} / ${tilesArr.length}`;
    };

    const open = (i) => {
      show(i);
      lightbox.classList.add('is-open');
      document.body.classList.add('is-lightbox-open');
    };
    const close = () => {
      lightbox.classList.remove('is-open');
      document.body.classList.remove('is-lightbox-open');
    };

    tilesArr.forEach((tile, i) => {
      tile.addEventListener('click', () => open(i));
      tile.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i); }
      });
    });

    lightbox.querySelector('.lightbox__close').addEventListener('click', close);
    lightbox.querySelector('.lightbox__nav--prev').addEventListener('click', () => show(idx - 1));
    lightbox.querySelector('.lightbox__nav--next').addEventListener('click', () => show(idx + 1));
    lightbox.addEventListener('click', (e) => { if (e.target === lightbox) close(); });

    document.addEventListener('keydown', (e) => {
      if (!lightbox.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
  }
})();

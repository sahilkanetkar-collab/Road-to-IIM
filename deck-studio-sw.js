/* Deck Studio service worker — v1
   IMPORTANT: This SW lives at the repo root, so its scope covers the whole
   Road to IIM site. To avoid interfering with sky.html, tests, or any other
   page, it ONLY intercepts requests for Deck Studio's own assets and the
   Google Fonts it uses. Every other request is passed through untouched. */

const CACHE = 'deck-studio-v1';

const APP_SHELL = [
  './deck_studio.html',
  './deck-studio.webmanifest',
  './icons/deck-studio-192.png',
  './icons/deck-studio-512.png',
  './icons/deck-studio-maskable-512.png',
  './icons/deck-studio-apple-180.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k.startsWith('deck-studio-') && k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

function isDeckStudioAsset(url) {
  const u = new URL(url);
  if (u.origin === self.location.origin) {
    const scopePath = new URL('./', self.location.href).pathname;
    const rel = u.pathname.startsWith(scopePath) ? u.pathname.slice(scopePath.length) : null;
    return rel !== null && (
      rel === 'deck_studio.html' ||
      rel === 'deck-studio.webmanifest' ||
      rel.startsWith('icons/deck-studio-')
    );
  }
  // Google Fonts (stylesheet + font files) — cache at runtime for offline use
  return u.hostname === 'fonts.googleapis.com' || u.hostname === 'fonts.gstatic.com';
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET' || !isDeckStudioAsset(request.url)) return; // pass through untouched

  event.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const cached = await cache.match(request);
      if (cached) {
        // Stale-while-revalidate: serve cache instantly, refresh in background
        event.waitUntil(
          fetch(request).then((res) => {
            if (res && res.ok) cache.put(request, res.clone());
          }).catch(() => {})
        );
        return cached;
      }
      try {
        const res = await fetch(request);
        if (res && res.ok) cache.put(request, res.clone());
        return res;
      } catch (err) {
        // Offline and not cached — for the HTML, try the precached shell
        if (request.mode === 'navigate') {
          const shell = await cache.match('./deck_studio.html');
          if (shell) return shell;
        }
        throw err;
      }
    })
  );
});

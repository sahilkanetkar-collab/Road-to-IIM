/* Current Affairs — Road to IIM
   Service Worker v2
   - No precaching on install (avoids install failure)
   - Cache on demand — stale-while-revalidate for app shell
   - Network only for all news/API calls
   - Scoped to current_affairs.html only
*/

const CACHE = 'ca-v2';

const NETWORK_ONLY = [
  'api.rss2json.com',
  'api.allorigins.win',
  'corsproxy.io',
  'api.wikimedia.org',
  'www.google.com',
];

/* ── INSTALL: no precaching, just activate immediately ── */
self.addEventListener('install', event => {
  self.skipWaiting();
});

/* ── ACTIVATE: clear old caches ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

/* ── FETCH ── */
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  /* News APIs → always network, never cache */
  if (NETWORK_ONLY.some(h => url.hostname.includes(h))) return;

  /* Everything else → stale-while-revalidate */
  event.respondWith(
    caches.open(CACHE).then(cache =>
      cache.match(event.request).then(cached => {
        const fresh = fetch(event.request).then(res => {
          if (res && res.status === 200 && res.type !== 'opaque') {
            cache.put(event.request, res.clone());
          }
          return res;
        }).catch(() => cached);
        return cached || fresh;
      })
    )
  );
});

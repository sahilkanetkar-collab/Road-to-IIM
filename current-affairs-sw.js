/* Current Affairs — Road to IIM
   Service Worker v1
   Strategy:
   - App shell (HTML, fonts)  → stale-while-revalidate (loads instantly, updates in background)
   - News API calls           → network only (always fresh data, never cached)
*/

const CACHE_NAME = 'current-affairs-v1';

const APP_SHELL = [
  '/Road-to-IIM/current_affairs.html',
];

/* News data sources — always go to network, never cache */
const NETWORK_ONLY_HOSTS = [
  'api.rss2json.com',
  'api.allorigins.win',
  'corsproxy.io',
  'api.wikimedia.org',
  'www.google.com',        // favicons
];

/* ── INSTALL: cache the app shell ── */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

/* ── ACTIVATE: clear old caches ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

/* ── FETCH: route requests ── */
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  /* News APIs → always hit the network */
  if (NETWORK_ONLY_HOSTS.some(h => url.hostname.includes(h))) {
    return; /* browser handles it */
  }

  /* Everything else → stale-while-revalidate */
  event.respondWith(
    caches.open(CACHE_NAME).then(cache =>
      cache.match(event.request).then(cached => {
        const networkFetch = fetch(event.request)
          .then(response => {
            if (response && response.status === 200 && response.type !== 'opaque') {
              cache.put(event.request, response.clone());
            }
            return response;
          })
          .catch(() => cached); /* offline fallback */

        return cached || networkFetch;
      })
    )
  );
});

/* Deck Studio service worker — v4 (retirement)
   Deck Studio moved to https://prodecked.com/studio on 30 Sep 2026.
   This worker replaces v3 on devices that installed the old app: it deletes
   the saved offline copy, unregisters itself and reloads any open Deck Studio
   window, which then redirects to ProDecked. It intercepts no requests, so it
   cannot affect any other Road to IIM page. */

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k.startsWith('deck-studio-')).map((k) => caches.delete(k)));
    await self.registration.unregister();
    const wins = await self.clients.matchAll({ type: 'window' });
    wins.forEach((c) => {
      if (/deck_studio\.html/.test(c.url)) c.navigate(c.url).catch(() => {});
    });
  })());
});

const CACHE_NAME = 'supportiq-v1';
const STATIC_ASSETS = [
  '/chatbot',
  '/chatbot.html',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.log('Cache failed for some assets:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Never cache API calls
  if (event.request.url.includes('run.app') ||
      event.request.url.includes('formspree')) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request).catch(() => {
        // Return cached chatbot.html for offline
        return caches.match('/chatbot.html');
      });
    })
  );
});

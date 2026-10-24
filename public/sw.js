const CACHE_NAME = 'mindsync-cache-v2';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.svg',
  '/icon-192.svg',
  '/icon-512.svg'
];

// Install event - precache core shell & immediately take over
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

// Activate event - aggressively purge old caches (v1, etc.)
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[MindSync SW] Deleting stale cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const url = event.request.url;

  // Ignore non-http requests
  if (!url.startsWith('http')) return;

  // NEVER intercept or cache backend API or Vite development modules
  if (
    url.includes('/api/') || 
    url.includes('/@vite/') || 
    url.includes('/src/') || 
    url.includes('/node_modules/') || 
    url.includes('/@fs/') ||
    url.includes('?t=') ||
    url.includes('?v=')
  ) {
    return;
  }

  // Navigation requests (HTML pages) -> Network first, fallback to cached index.html
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match('/index.html'))
    );
    return;
  }

  // Static assets (fonts, images, manifest)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Stale-while-revalidate for static assets
        fetch(event.request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse);
            });
          }
        }).catch(() => {});
        return cachedResponse;
      }

      return fetch(event.request).then((response) => {
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }

        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return response;
      }).catch(() => {
        if (event.request.destination === 'image') {
          return caches.match('/favicon.svg');
        }
      });
    })
  );
});

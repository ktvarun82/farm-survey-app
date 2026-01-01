const CACHE_NAME = 'farm-survey-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/index.html',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json',
    'https://cdn-icons-png.flaticon.com/512/2823/2823521.png'
];

// Install event - cache assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Caching all: app shell and content');
                return cache.addAll(ASSETS_TO_CACHE);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    console.log('[Service Worker] Removing old cache', key);
                    return caches.delete(key);
                }
            }));
        })
    );
});

// Fetch event - serve from cache, fall back to network
self.addEventListener('fetch', (event) => {
    // API calls should NOT be cached by this strategy, or handled differently
    if (event.request.url.includes('/surveys/') || event.request.url.includes('/trees/')) {
        // For API calls, try network first, falling back to 'offline' return if needed
        // But for now we just let the app handle the fetch failure
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});

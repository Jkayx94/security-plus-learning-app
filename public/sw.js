const CACHE='security-plus-v2.2.1';const ROOT=new URL('./',self.location).pathname;const CORE=[ROOT,`${ROOT}index.html`,`${ROOT}manifest.webmanifest`,`${ROOT}icons/icon-192.png`,`${ROOT}icons/icon-512.png`];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const url=new URL(e.request.url);if(url.origin!==location.origin)return;e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(res=>{if(res.ok){const copy=res.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));}return res;}).catch(()=>e.request.mode==='navigate'?caches.match(`${ROOT}index.html`):undefined)));});


// v2.2.1: always check the network for page navigation so a cached app shell
// cannot permanently hold users on an older release. Static assets remain
// cache-first for fast offline use.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil((async () => {
  const keys = await caches.keys();
  await Promise.all(keys.filter(key => key !== 'security-plus-v2.2.1').map(key => caches.delete(key)));
  await self.clients.claim();
})()));

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(request, { cache: 'no-store' });
        const cache = await caches.open('security-plus-v2.2.1');
        cache.put('./index.html', response.clone());
        return response;
      } catch {
        return (await caches.match('./index.html')) || Response.error();
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const cached = await caches.match(request);
    if (cached) return cached;
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open('security-plus-v2.2.1');
      cache.put(request, response.clone());
    }
    return response;
  })());
});

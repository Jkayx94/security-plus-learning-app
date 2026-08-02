from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: patch-service-worker-update.py <sw.js>")

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

# Replace existing fetch handlers with a navigation-network-first strategy.
text = re.sub(
    r"self\.addEventListener\(['\"]fetch['\"].*?\n\s*\}\);",
    "",
    text,
    flags=re.S,
)

text += r'''

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
'''

text = text.replace('security-plus-v2.2.0', 'security-plus-v2.2.1')
text = text.replace('2.2.0', '2.2.1')
path.write_text(text, encoding='utf-8')
print('Service worker update handling set to v2.2.1')

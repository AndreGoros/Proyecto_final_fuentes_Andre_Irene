// ══════════════════════════════════════════════════════════
//  service-worker.js — PWA Service Worker
//  Canasta Básica PROFECO + AI
//
//  Estrategia:
//  - Assets estáticos (CSS, JS, fuentes): Cache First
//  - Llamadas a la API (/api/...): Network First (datos frescos)
//  - Página principal: Stale While Revalidate
// ══════════════════════════════════════════════════════════

const CACHE_NAME = "canasta-v1";
const STATIC_CACHE = "canasta-static-v1";
const API_CACHE = "canasta-api-v1";

// Archivos a cachear inmediatamente al instalar
const PRECACHE_URLS = [
  "/",
  "/index.html",
  "/styles.css",
  "/app.js",
  "/manifest.json",
  "/icons/icon-192x192.png",
  "/icons/icon-512x512.png",
];

// ── Instalación: precachear assets críticos ───────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// ── Activación: limpiar caches antiguas ───────────────────
self.addEventListener("activate", (event) => {
  const validCaches = [STATIC_CACHE, API_CACHE];
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) =>
        Promise.all(
          cacheNames
            .filter((name) => !validCaches.includes(name))
            .map((name) => caches.delete(name))
        )
      )
      .then(() => self.clients.claim())
  );
});

// ── Fetch: interceptar peticiones ─────────────────────────
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Solo manejar peticiones GET
  if (request.method !== "GET") return;

  // ── API calls: Network First (siempre datos frescos) ───
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirst(request));
    return;
  }

  // ── Assets estáticos: Cache First ──────────────────────
  if (
    url.pathname.match(/\.(css|js|png|jpg|jpeg|svg|woff2?|ico)$/)
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // ── HTML/páginas: Stale While Revalidate ───────────────
  event.respondWith(staleWhileRevalidate(request));
});

// ── Estrategias de cache ──────────────────────────────────

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(STATIC_CACHE);
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Sin conexión: devolver cache si existe
    const cached = await caches.match(request);
    if (cached) return cached;

    // Respuesta de error offline para la API
    return new Response(
      JSON.stringify({
        error: "Sin conexión a internet",
        mensaje:
          "Verifica tu conexión e intenta de nuevo.",
      }),
      {
        status: 503,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });

  return cached || fetchPromise;
}

// ── Notificaciones Push (preparado para futuro) ───────────
self.addEventListener("push", (event) => {
  if (!event.data) return;

  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || "CanastaAI", {
      body: data.body || "Tienes una nueva notificación",
      icon: "/icons/icon-192x192.png",
      badge: "/icons/icon-96x96.png",
      data: { url: data.url || "/" },
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url));
});

// Service Worker для Push уведомлений + Offline кэширование
const CACHE_NAME = 'momsclub-library-v2';

// Статические ресурсы для кэширования при установке
const STATIC_ASSETS = [
  '/library',
  '/favorites',
  '/history',
  '/profile',
  '/logolibrary.svg',
  '/logonighthem.svg',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/manifest.json',
];

// Установка Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Установка...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Кэширование статических ресурсов');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[SW] Некоторые ресурсы не удалось закэшировать:', err);
      });
    })
  );
  self.skipWaiting();
});

// Активация — очистка старых кэшей
self.addEventListener('activate', (event) => {
  console.log('[SW] Активация...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith('momsclub-') && name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW] Удаление старого кэша:', name);
            return caches.delete(name);
          })
      );
    })
  );
  self.clients.claim();
});

// ==================== OFFLINE CACHING ====================

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Пропускаем non-GET запросы
  if (request.method !== 'GET') return;

  // Пропускаем WebSocket
  if (url.protocol === 'ws:' || url.protocol === 'wss:') return;

  // Пропускаем сторонние ресурсы (кроме API)
  if (!url.origin.includes('librarymomsclub.ru') && !url.origin.includes('localhost')) {
    return;
  }

  // API запросы — Network First с кэшем для offline
  if (url.pathname.includes('/api/')) {
    // Кэшируем только GET запросы к materials и categories
    if (url.pathname.includes('/materials') || url.pathname.includes('/categories')) {
      event.respondWith(
        caches.open(CACHE_NAME).then((cache) => {
          return fetch(request)
            .then((response) => {
              if (response.ok) {
                cache.put(request, response.clone());
              }
              return response;
            })
            .catch(() => {
              console.log('[SW] Offline — возвращаем из кэша:', url.pathname);
              return cache.match(request);
            });
        })
      );
      return;
    }
    // Остальные API — просто пропускаем
    return;
  }

  // Статические ресурсы — Cache First
  if (
    url.pathname.match(/\.(js|css|png|jpg|jpeg|svg|woff2?|ico)$/) ||
    url.pathname.startsWith('/_next/static/')
  ) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        }).catch(() => {
          // Для иконок возвращаем fallback
          if (url.pathname.endsWith('.png') || url.pathname.endsWith('.svg')) {
            return caches.match('/icons/icon-192.png');
          }
        });
      })
    );
    return;
  }

  // HTML страницы — Network First
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok && request.headers.get('accept')?.includes('text/html')) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => {
        console.log('[SW] Offline — пробуем кэш для:', url.pathname);
        return caches.match(request).then((cached) => {
          if (cached) return cached;
          // Fallback на главную библиотеки
          if (request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/library');
          }
        });
      })
  );
});

// ==================== PUSH NOTIFICATIONS ====================

self.addEventListener('push', (event) => {
  console.log('[SW] Push получен:', event);

  let data = {
    title: 'MomsClub Библиотека',
    body: 'Новый материал добавлен!',
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-192.png',
    url: '/library'
  };

  try {
    if (event.data) {
      data = { ...data, ...event.data.json() };
    }
  } catch (e) {
    console.error('[SW] Ошибка парсинга push данных:', e);
  }

  const options = {
    body: data.body,
    icon: data.icon || '/icons/icon-192.png',
    badge: data.badge || '/icons/icon-192.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/library'
    },
    actions: [
      { action: 'open', title: 'Открыть' },
      { action: 'close', title: 'Закрыть' }
    ],
    tag: 'momsclub-notification',
    renotify: true
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Клик по уведомлению
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Клик по уведомлению:', event.action);

  event.notification.close();

  if (event.action === 'close') {
    return;
  }

  const url = event.notification.data?.url || '/library';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        for (const client of clientList) {
          if (client.url.includes('librarymomsclub.ru') && 'focus' in client) {
            client.navigate(url);
            return client.focus();
          }
        }
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});

// Закрытие уведомления
self.addEventListener('notificationclose', (event) => {
  console.log('[SW] Уведомление закрыто');
});

// Сообщения от клиента
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
  if (event.data === 'clearCache') {
    caches.delete(CACHE_NAME).then(() => {
      console.log('[SW] Кэш очищен');
    });
  }
});

console.log('[SW] Service Worker загружен (v2 с offline)');

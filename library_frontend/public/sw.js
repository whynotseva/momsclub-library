// Service Worker для Push уведомлений
const CACHE_NAME = 'momsclub-v1';

// Установка Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker: Установлен');
  self.skipWaiting();
});

// Активация
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Активирован');
  event.waitUntil(clients.claim());
});

// Получение Push уведомления
self.addEventListener('push', (event) => {
  console.log('Push получен:', event);
  
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
    console.error('Ошибка парсинга push данных:', e);
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
  console.log('Клик по уведомлению:', event.action);
  
  event.notification.close();
  
  if (event.action === 'close') {
    return;
  }
  
  const url = event.notification.data?.url || '/library';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Если есть открытое окно — фокусируемся на нём
        for (const client of clientList) {
          if (client.url.includes('librarymomsclub.ru') && 'focus' in client) {
            client.navigate(url);
            return client.focus();
          }
        }
        // Иначе открываем новое окно
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});

// Закрытие уведомления
self.addEventListener('notificationclose', (event) => {
  console.log('Уведомление закрыто');
});

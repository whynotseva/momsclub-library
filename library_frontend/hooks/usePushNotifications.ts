'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'

// VAPID Public Key (должен совпадать с серверным)
const VAPID_PUBLIC_KEY = 'BND4EjUf4S6jkfv6Bhyu3i2qD70xr-RS5Ah7Di8MuKmgo8z995W16go8qNz5WwpCCGMm157t4XWHgWfnsoLBJhY'

// Конвертация base64 в Uint8Array для VAPID
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4)
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/')

  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

export function usePushNotifications() {
  const [isSupported, setIsSupported] = useState(false)
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [permission, setPermission] = useState<NotificationPermission>('default')

  // Проверка поддержки
  useEffect(() => {
    const checkSupport = async () => {
      const supported = 'serviceWorker' in navigator && 
                       'PushManager' in window && 
                       'Notification' in window

      setIsSupported(supported)
      
      if (supported) {
        setPermission(Notification.permission)
        
        // Ждём регистрации SW и проверяем подписку
        try {
          // Сначала регистрируем SW если ещё не зарегистрирован
          await navigator.serviceWorker.register('/sw.js')
          const registration = await navigator.serviceWorker.ready
          const subscription = await registration.pushManager.getSubscription()
          setIsSubscribed(!!subscription)
          console.log('Push subscription check:', !!subscription)
        } catch (e) {
          console.error('Ошибка проверки подписки:', e)
        }
      }
      
      setIsLoading(false)
    }

    // Небольшая задержка для инициализации
    setTimeout(checkSupport, 500)
  }, [])

  // Регистрация Service Worker
  const registerServiceWorker = useCallback(async () => {
    if (!('serviceWorker' in navigator)) return null
    
    try {
      const registration = await navigator.serviceWorker.register('/sw.js')
      console.log('Service Worker зарегистрирован:', registration.scope)
      return registration
    } catch (error) {
      console.error('Ошибка регистрации Service Worker:', error)
      return null
    }
  }, [])

  // Подписка на Push
  const subscribe = useCallback(async () => {
    console.log('🔔 Subscribe called, isSupported:', isSupported)
    
    if (!isSupported) {
      alert('Push уведомления не поддерживаются в этом браузере')
      return false
    }

    setIsLoading(true)

    try {
      // Запрашиваем разрешение
      console.log('🔔 Requesting permission...')
      const permission = await Notification.requestPermission()
      console.log('🔔 Permission result:', permission)
      setPermission(permission)
      
      if (permission !== 'granted') {
        alert('Для получения уведомлений нужно разрешить их в настройках браузера. Текущий статус: ' + permission)
        setIsLoading(false)
        return false
      }

      // Регистрируем SW
      console.log('🔔 Waiting for SW ready...')
      const registration = await navigator.serviceWorker.ready
      console.log('🔔 SW ready:', registration)

      // Подписываемся на push
      console.log('🔔 Subscribing to push...')
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY) as BufferSource
      })

      console.log('🔔 Push subscription created:', subscription.toJSON())

      // Отправляем подписку на сервер
      console.log('🔔 Sending to server...')
      const response = await api.post('/push/subscribe', {
        subscription: subscription.toJSON()
      })
      console.log('🔔 Server response:', response.data)

      setIsSubscribed(true)
      setIsLoading(false)
      return true

    } catch (error) {
      console.error('🔔 Ошибка подписки на push:', error)
      alert('Ошибка: ' + (error instanceof Error ? error.message : String(error)))
      setIsLoading(false)
      return false
    }
  }, [isSupported])

  // Отписка от Push
  const unsubscribe = useCallback(async () => {
    setIsLoading(true)

    try {
      const registration = await navigator.serviceWorker.ready
      const subscription = await registration.pushManager.getSubscription()
      
      if (subscription) {
        // Отписываемся
        await subscription.unsubscribe()
        
        // Уведомляем сервер
        await api.post('/push/unsubscribe', {
          endpoint: subscription.endpoint
        })
      }

      setIsSubscribed(false)
      setIsLoading(false)
      return true

    } catch (error) {
      console.error('Ошибка отписки от push:', error)
      setIsLoading(false)
      return false
    }
  }, [])

  // Переключение подписки
  const toggle = useCallback(async () => {
    if (isSubscribed) {
      return await unsubscribe()
    } else {
      return await subscribe()
    }
  }, [isSubscribed, subscribe, unsubscribe])

  return {
    isSupported,
    isSubscribed,
    isLoading,
    permission,
    subscribe,
    unsubscribe,
    toggle,
    registerServiceWorker
  }
}

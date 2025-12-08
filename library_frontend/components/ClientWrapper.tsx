'use client'

import { ReactNode, useEffect } from 'react'

export default function ClientWrapper({ children }: { children: ReactNode }) {
  // Регистрация Service Worker для Push уведомлений
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('SW registered:', reg.scope))
        .catch(err => console.log('SW registration failed:', err))
    }
  }, [])

  return <>{children}</>
}

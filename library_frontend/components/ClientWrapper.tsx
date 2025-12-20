'use client'

import { ReactNode, useEffect } from 'react'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { SubscriptionGuard, OfflineIndicator } from '@/components/shared'

export default function ClientWrapper({ children }: { children: ReactNode }) {
  // Регистрация Service Worker для Push уведомлений + Offline
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('SW registered:', reg.scope))
        .catch(err => console.log('SW registration failed:', err))
    }
  }, [])

  return (
    <ThemeProvider>
      <AuthProvider>
        <OfflineIndicator />
        <SubscriptionGuard>
          {children}
        </SubscriptionGuard>
      </AuthProvider>
    </ThemeProvider>
  )
}


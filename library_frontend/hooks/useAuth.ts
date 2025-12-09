'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { ADMIN_IDS, DEFAULT_USER, LoyaltyLevel } from '@/lib/constants'

interface UserData {
  name: string
  avatar: string
  username?: string
  telegramId?: number
  loyaltyLevel: LoyaltyLevel
  subscriptionDaysLeft: number
  isAdmin: boolean
  hasSubscription: boolean
}

interface UseAuthReturn {
  user: UserData | null
  loading: boolean
  isAuthenticated: boolean
  isAdmin: boolean
  logout: () => void
  refreshUser: () => Promise<void>
}

/**
 * Хук авторизации пользователя
 * Проверяет токен, загружает данные пользователя, проверяет подписку
 */
export function useAuth(): UseAuthReturn {
  const router = useRouter()
  const [user, setUser] = useState<UserData | null>(null)
  const [loading, setLoading] = useState(true)

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    sessionStorage.removeItem('auth_error')
    setUser(null)
    router.push('/login')
  }, [router])

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    
    if (!token) {
      setLoading(false)
      router.push('/login')
      return
    }

    try {
      // Загружаем данные пользователя
      const meResponse = await api.get('/auth/me')
      const userData = meResponse.data
      
      // Проверяем подписку
      const subResponse = await api.get('/auth/check-subscription')
      const subData = subResponse.data
      
      // НЕ блокируем вход без подписки — редирект делает SubscriptionGuard
      const hasActiveSub = subData.has_active_subscription

      const isAdmin = ADMIN_IDS.includes(userData.telegram_id)
      
      setUser({
        name: userData.first_name || 'Гость',
        avatar: userData.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${userData.username || userData.first_name}&backgroundColor=ffdfbf`,
        username: userData.username,
        telegramId: userData.telegram_id,
        loyaltyLevel: userData.loyalty_level || 'none',
        subscriptionDaysLeft: subData.days_left || 0,
        isAdmin,
        hasSubscription: hasActiveSub,
      })
      
      // Сохраняем в localStorage
      localStorage.setItem('user', JSON.stringify(userData))
      
    } catch (error) {
      console.error('Auth error:', error)
      // Пробуем fallback на localStorage
      const savedUser = localStorage.getItem('user')
      if (savedUser) {
        try {
          const userData = JSON.parse(savedUser)
          setUser({
            name: userData.first_name || 'Гость',
            avatar: userData.photo_url || DEFAULT_USER.avatar,
            username: userData.username,
            telegramId: userData.telegram_id,
            loyaltyLevel: userData.loyalty_level || 'none',
            subscriptionDaysLeft: 0,
            isAdmin: ADMIN_IDS.includes(userData.telegram_id),
            hasSubscription: false, // fallback
          })
        } catch {
          logout()
        }
      } else {
        logout()
      }
    } finally {
      setLoading(false)
    }
  }, [router, logout])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  return {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.isAdmin || false,
    logout,
    refreshUser: loadUser,
  }
}

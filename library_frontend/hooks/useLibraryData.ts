'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import { ADMIN_IDS, DEFAULT_USER } from '@/lib/constants'
import { Notification, Material, Category } from '@/lib/types'

const PAGE_SIZE = 30

/**
 * Хук для загрузки всех данных библиотеки
 * Включает: авторизацию, проверку подписки, загрузку материалов и т.д.
 */
export function useLibraryData() {
  const router = useRouter()
  
  // Состояния
  const [loading, setLoading] = useState(true)
  const [hasSubscription, setHasSubscription] = useState(false)
  const [user, setUser] = useState(DEFAULT_USER)
  const [isAdmin, setIsAdmin] = useState(false)
  const [materials, setMaterials] = useState<Material[]>([])
  const [apiCategories, setApiCategories] = useState<Category[]>([])
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const loadingMoreRef = useRef(false)
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set())
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [recommendations, setRecommendations] = useState<{type: string, title: string, materials: Material[]}>({type: '', title: '', materials: []})

  // Основной эффект загрузки данных
  useEffect(() => {
    const loadUserData = async () => {
      // Проверяем токен
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/login')
        return
      }

      // Загружаем данные пользователя из API
      try {
        const meResponse = await api.get('/auth/me')
        const userData = meResponse.data
        setUser(prev => ({
          ...prev,
          name: userData.first_name || 'Гость',
          avatar: userData.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${userData.username || userData.first_name}&backgroundColor=ffdfbf`,
          loyaltyLevel: userData.loyalty_level || 'none',
        }))
        // Проверяем админа
        if (ADMIN_IDS.includes(userData.telegram_id)) {
          setIsAdmin(true)
        }
        // Обновляем localStorage
        localStorage.setItem('user', JSON.stringify(userData))
      } catch {
        // Fallback на localStorage
        const savedUser = localStorage.getItem('user')
        if (savedUser) {
          try {
            const userData = JSON.parse(savedUser)
            setUser(prev => ({
              ...prev,
              name: userData.first_name || 'Гость',
              avatar: userData.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${userData.username || userData.first_name}&backgroundColor=ffdfbf`,
              loyaltyLevel: userData.loyalty_level || 'none',
            }))
          } catch (err) {
            console.error('Error parsing user data:', err)
          }
        }
      }

      // Загружаем данные подписки из API
      let hasSub = false
      try {
        const response = await api.get('/auth/check-subscription')
        const subData = response.data
        hasSub = subData.has_active_subscription
        setHasSubscription(hasSub)
        
        setUser(prev => ({
          ...prev,
          subscriptionDaysLeft: subData.days_left || 0,
          daysInClub: subData.days_in_club || 0,
        }))
        
        // Если нет подписки — не загружаем данные библиотеки
        // SubscriptionGuard сам редиректит на /profile
        if (!hasSub) {
          setLoading(false)
          return
        }
      } catch (error) {
        console.error('Error loading subscription:', error)
        // При ошибке авторизации — кикаем
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        router.push('/login')
        return
      }

      // Загружаем категории (только если есть подписка)
      try {
        const catResponse = await api.get('/categories')
        setApiCategories(catResponse.data)
      } catch (error) {
        console.error('Error loading categories:', error)
      }

      // Загружаем материалы (первая страница)
      try {
        const matResponse = await api.get('/materials', { params: { page: 1, page_size: PAGE_SIZE } })
        const items = matResponse.data.items || []
        const total = matResponse.data.total || 0
        setMaterials(items)
        setPage(2)
        setHasMore(items.length === PAGE_SIZE && items.length < total)
        setUser(prev => ({
          ...prev,
          totalMaterials: total,
        }))
      } catch (error) {
        console.error('Error loading materials:', error)
      }

      // Загружаем избранные ID для отметки сердечек И счётчик
      try {
        const favResponse = await api.get('/materials/favorites/my')
        const favIds = new Set<number>((favResponse.data || []).map((m: Material) => m.id))
        setFavoriteIds(favIds)
        setUser(prev => ({ ...prev, favorites: favIds.size }))
      } catch (error) {
        console.error('Error loading favorites:', error)
      }

      // Загружаем статистику просмотров
      try {
        const statsResponse = await api.get('/materials/stats/my')
        setUser(prev => ({ 
          ...prev, 
          materialsViewed: statsResponse.data.materials_viewed || 0,
          uniqueViewed: statsResponse.data.unique_viewed || 0,
        }))
      } catch (error) {
        console.error('Error loading stats:', error)
      }

      // Загружаем уведомления
      try {
        const notifResponse = await api.get('/materials/notifications/my')
        setNotifications(notifResponse.data.notifications || [])
        setUser(prev => ({ ...prev, notifications: notifResponse.data.unread_count || 0 }))
      } catch (error) {
        console.error('Error loading notifications:', error)
      }

      // Загружаем рекомендации
      try {
        const recResponse = await api.get('/materials/feed/recommendations')
        setRecommendations(recResponse.data)
      } catch (error) {
        console.error('Error loading recommendations:', error)
      }

      setLoading(false)
    }

    loadUserData()
  }, [router])

  // Прочитать все уведомления
  const markAllAsRead = async () => {
    try {
      await api.post('/materials/notifications/read-all')
      setNotifications(notifications.map(n => ({ ...n, is_read: true })))
      setUser(prev => ({ ...prev, notifications: 0 }))
    } catch (error) {
      console.error('Error marking all as read:', error)
    }
  }

  // Прочитать одно уведомление
  const markAsRead = async (id: number) => {
    try {
      await api.post(`/materials/notifications/${id}/read`)
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, is_read: true } : n
      ))
      const unreadCount = notifications.filter(n => !n.is_read && n.id !== id).length
      setUser(prev => ({ ...prev, notifications: unreadCount }))
    } catch (error) {
      console.error('Error marking as read:', error)
    }
  }

  // Открыть материал и записать просмотр
  const openMaterial = (material: Material) => {
    // Открываем ссылку в новой вкладке через создание <a> элемента
    if (material.external_url) {
      const link = document.createElement('a')
      link.href = material.external_url
      link.target = '_blank'
      link.rel = 'noopener noreferrer'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
    
    // Записываем просмотр асинхронно
    api.post(`/materials/${material.id}/view`)
      .then(() => {
        setUser(prev => ({ ...prev, materialsViewed: prev.materialsViewed + 1 }))
      })
      .catch(error => {
        console.error('Error recording view:', error)
      })
  }

  // Добавить/убрать из избранного
  const toggleFavorite = async (materialId: number) => {
    const isFavorite = favoriteIds.has(materialId)
    
    try {
      if (isFavorite) {
        await api.delete(`/materials/${materialId}/favorite`)
        setFavoriteIds(prev => {
          const newSet = new Set(prev)
          newSet.delete(materialId)
          setUser(u => ({ ...u, favorites: newSet.size }))
          return newSet
        })
        // Уменьшаем счётчик лайков на карточке
        setMaterials(prev => prev.map(m => 
          m.id === materialId ? { ...m, favorites_count: Math.max(0, (m.favorites_count ?? 1) - 1) } : m
        ))
      } else {
        await api.post(`/materials/${materialId}/favorite`)
        setFavoriteIds(prev => {
          const newSet = new Set(prev).add(materialId)
          setUser(u => ({ ...u, favorites: newSet.size }))
          return newSet
        })
        // Увеличиваем счётчик лайков на карточке
        setMaterials(prev => prev.map(m => 
          m.id === materialId ? { ...m, favorites_count: (m.favorites_count ?? 0) + 1 } : m
        ))
      }
    } catch (error) {
      console.error('Error toggling favorite:', error)
    }
  }

  // Загрузить ещё материалы
  const loadMoreMaterials = useCallback(async () => {
    if (loadingMoreRef.current || !hasMore) return
    loadingMoreRef.current = true
    setLoadingMore(true)
    
    try {
      const matResponse = await api.get('/materials', { params: { page, page_size: PAGE_SIZE } })
      const items = matResponse.data.items || []
      const total = matResponse.data.total || 0
      
      setMaterials(prev => [...prev, ...items])
      setPage(prev => prev + 1)
      setHasMore(items.length === PAGE_SIZE && materials.length + items.length < total)
    } catch (error) {
      console.error('Error loading more materials:', error)
    } finally {
      setLoadingMore(false)
      loadingMoreRef.current = false
    }
  }, [page, hasMore, materials.length])

  return {
    // Состояния
    loading,
    loadingMore,
    hasSubscription,
    user,
    isAdmin,
    materials,
    apiCategories,
    favoriteIds,
    notifications,
    recommendations,
    router,
    hasMore,
    
    // Функции
    setUser,
    setMaterials,
    setNotifications,
    markAllAsRead,
    markAsRead,
    openMaterial,
    toggleFavorite,
    loadMoreMaterials,
  }
}

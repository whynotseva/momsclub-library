'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import { Material } from '@/lib/types'

interface UseFavoritesReturn {
  favoriteIds: Set<number>
  favoritesCount: number
  loading: boolean
  isFavorite: (materialId: number) => boolean
  toggleFavorite: (materialId: number) => Promise<boolean>
  reload: () => Promise<void>
}

/**
 * Хук для управления избранными материалами
 */
export function useFavorites(): UseFavoritesReturn {
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set())
  const [loading, setLoading] = useState(true)

  const loadFavorites = useCallback(async () => {
    try {
      setLoading(true)
      const response = await api.get('/materials/favorites/my')
      const ids = new Set<number>((response.data || []).map((m: Material) => m.id))
      setFavoriteIds(ids)
    } catch (err) {
      console.error('Error loading favorites:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const isFavorite = useCallback((materialId: number) => {
    return favoriteIds.has(materialId)
  }, [favoriteIds])

  const toggleFavorite = useCallback(async (materialId: number): Promise<boolean> => {
    const wasFavorite = favoriteIds.has(materialId)
    
    try {
      if (wasFavorite) {
        await api.delete(`/materials/${materialId}/favorite`)
        setFavoriteIds(prev => {
          const newSet = new Set(prev)
          newSet.delete(materialId)
          return newSet
        })
        return false // Теперь НЕ в избранном
      } else {
        await api.post(`/materials/${materialId}/favorite`)
        setFavoriteIds(prev => new Set(prev).add(materialId))
        return true // Теперь в избранном
      }
    } catch (err) {
      console.error('Error toggling favorite:', err)
      return wasFavorite // Вернуть предыдущее состояние при ошибке
    }
  }, [favoriteIds])

  useEffect(() => {
    loadFavorites()
  }, [loadFavorites])

  return {
    favoriteIds,
    favoritesCount: favoriteIds.size,
    loading,
    isFavorite,
    toggleFavorite,
    reload: loadFavorites,
  }
}

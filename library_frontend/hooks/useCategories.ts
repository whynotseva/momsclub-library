'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import { Category } from '@/lib/types'

interface UseCategoriesReturn {
  categories: Category[]
  loading: boolean
  error: string | null
  reload: () => Promise<void>
}

/**
 * Хук для загрузки категорий
 */
export function useCategories(): UseCategoriesReturn {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadCategories = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.get('/categories')
      setCategories(response.data || [])
    } catch (err) {
      console.error('Error loading categories:', err)
      setError('Ошибка загрузки категорий')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadCategories()
  }, [loadCategories])

  return {
    categories,
    loading,
    error,
    reload: loadCategories,
  }
}

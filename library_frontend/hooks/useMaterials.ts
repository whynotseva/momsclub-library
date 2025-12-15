'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { api } from '@/lib/api'
import { Material } from '@/lib/types'

const PAGE_SIZE = 30

interface UseMaterialsReturn {
  materials: Material[]
  loading: boolean
  loadingMore: boolean
  error: string | null
  totalMaterials: number
  hasMore: boolean
  reload: () => Promise<void>
  loadMore: () => Promise<void>
  recordView: (materialId: number) => Promise<void>
}

/**
 * Хук для загрузки и управления материалами с пагинацией
 */
export function useMaterials(): UseMaterialsReturn {
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [totalMaterials, setTotalMaterials] = useState(0)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const loadingRef = useRef(false)

  const loadMaterials = useCallback(async (reset = true) => {
    if (loadingRef.current) return
    loadingRef.current = true
    
    try {
      if (reset) {
        setLoading(true)
        setPage(1)
      } else {
        setLoadingMore(true)
      }
      setError(null)
      
      const currentPage = reset ? 1 : page
      const response = await api.get('/materials', { 
        params: { page: currentPage, page_size: PAGE_SIZE } 
      })
      const items = response.data.items || []
      const total = response.data.total || 0
      
      if (reset) {
        setMaterials(items)
        setPage(2)
      } else {
        setMaterials(prev => [...prev, ...items])
        setPage(prev => prev + 1)
      }
      
      setTotalMaterials(total)
      setHasMore(items.length === PAGE_SIZE && materials.length + items.length < total)
    } catch (err) {
      console.error('Error loading materials:', err)
      setError('Ошибка загрузки материалов')
    } finally {
      setLoading(false)
      setLoadingMore(false)
      loadingRef.current = false
    }
  }, [page, materials.length])

  const loadMore = useCallback(async () => {
    if (!loadingMore && hasMore) {
      await loadMaterials(false)
    }
  }, [loadMaterials, loadingMore, hasMore])

  const reload = useCallback(async () => {
    await loadMaterials(true)
  }, [loadMaterials])

  const recordView = useCallback(async (materialId: number) => {
    try {
      await api.post(`/materials/${materialId}/view`)
    } catch (err) {
      console.error('Error recording view:', err)
    }
  }, [])

  useEffect(() => {
    loadMaterials(true)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return {
    materials,
    loading,
    loadingMore,
    error,
    totalMaterials,
    hasMore,
    reload,
    loadMore,
    recordView,
  }
}

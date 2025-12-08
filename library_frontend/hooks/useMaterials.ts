'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import { Material } from '@/lib/types'

interface UseMaterialsReturn {
  materials: Material[]
  loading: boolean
  error: string | null
  totalMaterials: number
  reload: () => Promise<void>
  recordView: (materialId: number) => Promise<void>
}

/**
 * Хук для загрузки и управления материалами
 */
export function useMaterials(): UseMaterialsReturn {
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalMaterials, setTotalMaterials] = useState(0)

  const loadMaterials = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.get('/materials')
      const items = response.data.items || []
      
      setMaterials(items)
      setTotalMaterials(response.data.total || items.length)
    } catch (err) {
      console.error('Error loading materials:', err)
      setError('Ошибка загрузки материалов')
    } finally {
      setLoading(false)
    }
  }, [])

  const recordView = useCallback(async (materialId: number) => {
    try {
      await api.post(`/materials/${materialId}/view`)
    } catch (err) {
      console.error('Error recording view:', err)
    }
  }, [])

  useEffect(() => {
    loadMaterials()
  }, [loadMaterials])

  return {
    materials,
    loading,
    error,
    totalMaterials,
    reload: loadMaterials,
    recordView,
  }
}

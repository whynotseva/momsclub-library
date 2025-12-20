'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'
import { Material } from '@/lib/types'
import { useScrollVisibility } from '@/hooks/useScrollVisibility'
import { useAuthContext } from '@/contexts/AuthContext'
import { LoadingSpinner, EmptyState } from '@/components/shared'
import { useTheme } from '@/contexts/ThemeContext'

export default function FavoritesPage() {
  // Авторизация из контекста
  const { user, isAdmin, loading: authLoading, logout } = useAuthContext()
  
  const [loadingFavorites, setLoadingFavorites] = useState(true)
  const [favorites, setFavorites] = useState<Material[]>([])
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const isVisible = useScrollVisibility()
  const { resolvedTheme } = useTheme()

  // Загружаем только избранное (авторизация уже проверена в контексте)
  useEffect(() => {
    const loadFavorites = async () => {
      if (authLoading || !user) return
      
      try {
        const response = await api.get('/materials/favorites/my')
        setFavorites(response.data || [])
      } catch (error) {
        console.error('Error loading favorites:', error)
      }
      setLoadingFavorites(false)
    }
    loadFavorites()
  }, [authLoading, user])

  const openMaterial = async (material: Material) => {
    try {
      await api.post(`/materials/${material.id}/view`)
    } catch (error) {
      console.error('Error recording view:', error)
    }
    if (material.external_url) {
      window.open(material.external_url, '_blank')
    }
  }

  const removeFavorite = async (id: number) => {
    try {
      await api.delete(`/materials/${id}/favorite`)
      setFavorites(prev => prev.filter(m => m.id !== id))
    } catch (error) {
      console.error('Error removing favorite:', error)
    }
  }

  if (authLoading || loadingFavorites) {
    return <LoadingSpinner />
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6] dark:from-[#121212] dark:via-[#1A1A1A] dark:to-[#121212] relative">
      <div className="fixed -top-40 -right-40 w-[600px] h-[600px] bg-gradient-to-br from-[#E8D5C4]/30 via-[#D4C4B0]/15 to-transparent rounded-full blur-3xl pointer-events-none dark:from-[#2A2A2A]/20 dark:via-transparent"></div>
      <div className="fixed -bottom-40 -left-40 w-[500px] h-[500px] bg-gradient-to-tr from-[#C9B89A]/15 to-transparent rounded-full blur-3xl pointer-events-none dark:from-[#2A2A2A]/10"></div>

      <header className={`fixed top-0 left-0 right-0 z-50 border-b border-white/50 dark:border-[#3D3D3D] shadow-lg transition-transform duration-300 ease-in-out ${isVisible ? 'translate-y-0' : '-translate-y-full'}`} style={{ background: resolvedTheme === 'dark' ? 'rgba(30,30,30,0.85)' : 'rgba(255,255,255,0.55)', backdropFilter: 'blur(20px) saturate(180%)', paddingTop: 'env(safe-area-inset-top)' }}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <a href="/library" className="flex items-center space-x-3 group">
              <img src={resolvedTheme === 'dark' ? '/logonighthem.svg' : '/logolibrary.svg'} alt="LibriMomsClub" className="h-10 w-auto group-hover:scale-105 transition-transform" />
            </a>
            <nav className="hidden md:flex space-x-8">
              <a href="/library" className="text-[#8B8279] dark:text-[#B0B0B0] hover:text-[#B08968] transition-colors">Библиотека</a>
              <a href="/favorites" className="text-[#B08968] font-semibold">Избранное</a>
              <a href="/history" className="text-[#8B8279] dark:text-[#B0B0B0] hover:text-[#B08968] transition-colors">История</a>
            </nav>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <button onClick={() => setShowProfileMenu(!showProfileMenu)} className="flex items-center space-x-2">
                  <img src={user?.avatar || ''} alt={user?.name || ''} className="w-9 h-9 rounded-full border-2 border-[#E8D4BA] object-cover hover:border-[#B08968] transition-colors" />
                  <span className="text-[#8B8279] dark:text-[#B0B0B0] text-sm font-medium hidden md:block">Выйти</span>
                </button>
                {showProfileMenu && (
                  <div className="absolute right-0 top-12 bg-white dark:bg-[#1E1E1E] rounded-xl shadow-xl border border-[#E8D4BA]/50 dark:border-[#3D3D3D] py-2 min-w-[160px] z-50">
                    <div className="px-4 py-2 border-b border-gray-100 dark:border-[#3D3D3D]">
                      <p className="text-sm font-medium text-[#2D2A26] dark:text-[#E5E5E5]">{user?.name}</p>
                    </div>
                    {isAdmin && (
                      <Link href="/admin" className="block w-full px-4 py-2 text-left text-sm text-[#B08968] hover:bg-[#F5E6D3] dark:hover:bg-[#2A2A2A] transition-colors">
                        ⚙️ Админ-панель
                      </Link>
                    )}
                    <button onClick={logout} className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30">
                      🚪 Выйти
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8" style={{ paddingTop: 'calc(5rem + env(safe-area-inset-top, 0px))' }}>
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-[#2D2A26] dark:text-[#E5E5E5] mb-2">❤️ Избранное</h2>
          <p className="text-[#5C5650] dark:text-[#B0B0B0]">Материалы, которые ты добавил в избранное</p>
        </div>
        
        {favorites.length === 0 ? (
          <EmptyState
            icon="💝"
            title="Пока пусто"
            description="Добавь материалы в избранное, нажав ❤️ на карточке"
            actionText="Перейти в библиотеку"
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {favorites.map((material) => (
              <div key={material.id} className="group bg-white/90 dark:bg-[#1E1E1E]/90 rounded-2xl shadow-lg shadow-[#C9A882]/10 dark:shadow-none hover:shadow-xl dark:hover:shadow-lg dark:hover:shadow-black/20 transition-all p-5 border border-[#E8D4BA]/40 dark:border-[#3D3D3D] hover:-translate-y-1 relative overflow-hidden">
                <button onClick={() => removeFavorite(material.id)} className="absolute bottom-4 right-4 z-10 w-9 h-9 rounded-full flex items-center justify-center bg-red-500 text-white shadow-md">
                  <span className="text-lg">❤️</span>
                </button>
                <div onClick={() => openMaterial(material)} className="cursor-pointer">
                  {(material.cover_url || material.cover_image) ? (
                    <img src={material.cover_url || material.cover_image} alt={material.title} className="w-full h-24 object-cover rounded-xl mb-3" />
                  ) : (
                    <div className="w-full h-24 bg-gradient-to-br from-[#C9A882] to-[#B08968] rounded-xl mb-3 flex items-center justify-center text-3xl">
                      {material.category?.icon || '📄'}
                    </div>
                  )}
                  <span className="text-xs bg-[#F5E6D3] dark:bg-[#2A2A2A] text-[#8B7355] dark:text-[#B0B0B0] px-2 py-1 rounded-full font-medium">{material.category?.name || material.format}</span>
                  <h4 className="font-semibold text-[#2D2A26] dark:text-[#E5E5E5] mt-2 text-sm leading-tight line-clamp-2">{material.title}</h4>
                  <div className="text-xs text-[#8B8279] dark:text-[#707070] mt-2">👁️ {material.views} {material.external_url && '🔗'}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <nav className={`md:hidden fixed bottom-6 left-4 right-4 z-50 transition-all duration-300 ease-in-out ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-24 opacity-0'}`}>
        <div className="flex items-center justify-around rounded-2xl px-2 py-3 shadow-2xl border border-white/50 dark:border-[#3D3D3D]" style={{ background: resolvedTheme === 'dark' ? 'rgba(30,30,30,0.85)' : 'rgba(255,255,255,0.45)', backdropFilter: 'blur(24px) saturate(180%)' }}>
          <a href="/library" className="px-2 py-1.5 rounded-xl text-[#8B8279] dark:text-[#B0B0B0] text-xs font-medium">Библиотека</a>
          <a href="/favorites" className="px-2 py-1.5 rounded-xl bg-[#B08968] text-white text-xs font-semibold shadow-md">Избранное</a>
          <a href="/history" className="px-2 py-1.5 rounded-xl text-[#8B8279] dark:text-[#B0B0B0] text-xs font-medium">История</a>
          <a href="/profile" className="px-2 py-1.5 rounded-xl text-[#8B8279] dark:text-[#B0B0B0] text-xs font-medium">Профиль</a>
        </div>
      </nav>
    </div>
  )
}

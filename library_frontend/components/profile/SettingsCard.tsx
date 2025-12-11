'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

interface UserSettings {
  birthday?: string
  is_recurring_active: boolean
}

export function SettingsCard() {
  const [settings, setSettings] = useState<UserSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await api.get('/auth/settings')
        setSettings(response.data)
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error'
        console.error('[SettingsCard] Error:', err)
        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }
    loadSettings()
  }, [])

  const formatBirthday = (dateStr?: string) => {
    if (!dateStr) return null
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long'
      })
    } catch {
      return dateStr
    }
  }

  if (loading) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg shadow-[#C9A882]/10 border border-[#E8D4BA]/40 p-6">
        <div className="animate-pulse space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#E8D4BA]/50 rounded-xl" />
            <div className="h-5 bg-[#E8D4BA]/50 rounded w-24" />
          </div>
          <div className="space-y-2">
            <div className="h-10 bg-[#E8D4BA]/30 rounded-xl" />
            <div className="h-10 bg-[#E8D4BA]/30 rounded-xl" />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg shadow-[#C9A882]/10 border border-[#E8D4BA]/40 p-6">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-xl">⚙️</span>
          <h2 className="text-lg font-semibold text-[#2D2A26]">Настройки</h2>
        </div>
        <p className="text-sm text-[#8B8279]">Не удалось загрузить данные</p>
      </div>
    )
  }

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg shadow-[#C9A882]/10 border border-[#E8D4BA]/40 p-6 hover:shadow-xl transition-shadow">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-[#B08968] to-[#C9A882] rounded-xl flex items-center justify-center">
          <span className="text-white text-lg">⚙️</span>
        </div>
        <div>
          <h2 className="text-lg font-semibold text-[#2D2A26]">Настройки</h2>
          <p className="text-sm text-[#8B8279]">Управление аккаунтом</p>
        </div>
      </div>

      {/* Settings List */}
      <div className="space-y-3">
        {/* Birthday */}
        <div className="flex items-center justify-between p-3 bg-[#FAF6F1] rounded-xl">
          <div className="flex items-center gap-3">
            <span className="text-xl">🎂</span>
            <div>
              <p className="font-medium text-[#2D2A26]">День рождения</p>
              <p className="text-xs text-[#8B8279]">
                {settings?.birthday 
                  ? formatBirthday(settings.birthday)
                  : 'Не указан'}
              </p>
            </div>
          </div>
          {settings?.birthday && (
            <span className="text-xs text-[#B08968]">✓ Указан</span>
          )}
        </div>

        {/* Auto-renewal */}
        <div className="flex items-center justify-between p-3 bg-[#FAF6F1] rounded-xl">
          <div className="flex items-center gap-3">
            <span className="text-xl">🔄</span>
            <div>
              <p className="font-medium text-[#2D2A26]">Автопродление</p>
              <p className="text-xs text-[#8B8279]">
                {settings?.is_recurring_active 
                  ? 'Подписка продлится автоматически'
                  : 'Выключено'}
              </p>
            </div>
          </div>
          <span className={`px-2 py-0.5 text-xs rounded-full ${
            settings?.is_recurring_active 
              ? 'bg-green-100 text-green-700' 
              : 'bg-gray-100 text-gray-600'
          }`}>
            {settings?.is_recurring_active ? 'Вкл' : 'Выкл'}
          </span>
        </div>
      </div>

      {/* Info */}
      <p className="mt-4 text-xs text-[#8B8279] text-center">
        Для изменения настроек используйте бота
      </p>
    </div>
  )
}

'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

interface LoyaltyInfo {
  current_level: string
  days_in_club: number
  next_level: string | null
  days_to_next_level: number | null
  progress_percent: number
  discount_percent: number
  silver_days: number
  gold_days: number
  platinum_days: number
}

const LEVEL_CONFIG = {
  none: { icon: '⭐', name: 'Новичок', color: 'gray' },
  silver: { icon: '🥈', name: 'Silver', color: 'slate' },
  gold: { icon: '🥇', name: 'Gold', color: 'amber' },
  platinum: { icon: '💎', name: 'Platinum', color: 'purple' },
}

export function LoyaltyCard() {
  const [loyalty, setLoyalty] = useState<LoyaltyInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadLoyalty = async () => {
      try {
        const response = await api.get('/auth/loyalty')
        setLoyalty(response.data)
      } catch (error) {
        console.error('Error loading loyalty:', error)
      } finally {
        setLoading(false)
      }
    }
    loadLoyalty()
  }, [])

  if (loading) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg shadow-[#C9A882]/10 border border-[#E8D4BA]/40 p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-4 bg-gray-200 rounded w-full mb-2" />
        <div className="h-4 bg-gray-200 rounded w-2/3" />
      </div>
    )
  }

  if (!loyalty) return null

  const config = LEVEL_CONFIG[loyalty.current_level as keyof typeof LEVEL_CONFIG] || LEVEL_CONFIG.none
  const nextConfig = loyalty.next_level 
    ? LEVEL_CONFIG[loyalty.next_level as keyof typeof LEVEL_CONFIG] 
    : null

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-lg shadow-[#C9A882]/10 border border-[#E8D4BA]/40 p-6 hover:shadow-xl transition-shadow">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-400 rounded-xl flex items-center justify-center">
          <span className="text-white text-lg">💎</span>
        </div>
        <h2 className="text-lg font-semibold text-[#2D2A26]">Программа лояльности</h2>
      </div>

      {/* Current Level */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-3xl">{config.icon}</span>
        <div>
          <div className="font-semibold text-[#2D2A26]">{config.name}</div>
          <div className="text-sm text-[#8B8279]">
            {loyalty.days_in_club} дней в клубе
          </div>
        </div>
        {loyalty.discount_percent > 0 && (
          <div className="ml-auto px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
            -{loyalty.discount_percent}%
          </div>
        )}
      </div>

      {/* Progress to next level */}
      {nextConfig && loyalty.days_to_next_level !== null && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-[#8B8279]">
              До {nextConfig.name}
            </span>
            <span className="text-[#5D4E3A] font-medium">
              {loyalty.days_to_next_level} дней
            </span>
          </div>
          
          {/* Progress bar */}
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-amber-400 to-orange-400 rounded-full transition-all duration-500"
              style={{ width: `${loyalty.progress_percent}%` }}
            />
          </div>
          
          <div className="text-xs text-[#8B8279] text-right">
            {loyalty.progress_percent}%
          </div>
        </div>
      )}

      {/* Max level */}
      {loyalty.current_level === 'platinum' && (
        <div className="text-center py-2 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
          <span className="text-sm text-purple-700 font-medium">
            🎉 Максимальный уровень достигнут!
          </span>
        </div>
      )}

      {/* Level info */}
      <div className="mt-4 pt-4 border-t border-[#E8D4BA]/30">
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className={loyalty.days_in_club >= loyalty.silver_days ? 'text-[#5D4E3A]' : 'text-[#C9C0B5]'}>
            <div>🥈 Silver</div>
            <div>{loyalty.silver_days}+ дней</div>
          </div>
          <div className={loyalty.days_in_club >= loyalty.gold_days ? 'text-[#5D4E3A]' : 'text-[#C9C0B5]'}>
            <div>🥇 Gold</div>
            <div>{loyalty.gold_days}+ дней</div>
          </div>
          <div className={loyalty.days_in_club >= loyalty.platinum_days ? 'text-[#5D4E3A]' : 'text-[#C9C0B5]'}>
            <div>💎 Platinum</div>
            <div>{loyalty.platinum_days}+ дней</div>
          </div>
        </div>
      </div>
    </div>
  )
}

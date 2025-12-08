'use client'

import { EXTERNAL_URLS } from '@/lib/constants'

interface SubscriptionCardProps {
  daysLeft: number
  total?: number
}

/**
 * Карточка подписки с прогресс-баром
 */
export function SubscriptionCard({ daysLeft, total = 30 }: SubscriptionCardProps) {
  const isExpiringSoon = daysLeft <= 7
  const isUnlimited = daysLeft > 365
  const progressPercent = Math.min((daysLeft / total) * 100, 100)

  return (
    <div className="relative">
      <div className="absolute inset-0 bg-gradient-to-br from-[#B08968]/10 to-[#C9A882]/5 rounded-3xl blur-xl"></div>
      <div className="relative bg-white/90 backdrop-blur-sm rounded-3xl p-6 border border-[#E8D4BA]/40 shadow-xl shadow-[#C9A882]/10 h-full">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm font-medium text-[#8B8279]">Подписка</span>
          {isExpiringSoon && !isUnlimited && (
            <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-medium animate-pulse">
              ⚠️ Скоро истекает
            </span>
          )}
        </div>

        <div className="text-center mb-4">
          <div className="text-5xl font-black text-[#2D2A26]">
            {isUnlimited ? '∞' : daysLeft}
          </div>
          <div className="text-sm text-[#8B8279]">
            {isUnlimited ? 'безлимит' : 'дней осталось'}
          </div>
        </div>

        {/* Прогресс-бар */}
        <div className="mb-4">
          <div className="h-2 bg-[#F5E6D3] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#B08968] to-[#C9A882] rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>

        <a
          href={EXTERNAL_URLS.subscriptionBot}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full text-center py-3 bg-gradient-to-r from-[#B08968] to-[#A67C52] text-white font-semibold rounded-xl hover:shadow-lg transition-all duration-300 text-sm"
        >
          Продлить подписку
        </a>
      </div>
    </div>
  )
}

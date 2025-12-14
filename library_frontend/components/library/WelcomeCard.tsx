'use client'

interface WelcomeCardProps {
  userName: string
  materialsViewed: number
  favorites: number
  uniqueViewed: number
  totalMaterials: number
  subscriptionDaysLeft?: number | null
}

export function WelcomeCard({
  userName,
  materialsViewed,
  favorites,
  uniqueViewed,
  totalMaterials,
  subscriptionDaysLeft,
}: WelcomeCardProps) {
  const isUnlimited = (subscriptionDaysLeft && subscriptionDaysLeft > 1000) || subscriptionDaysLeft === -1

  return (
    <div className="lg:col-span-2 relative">
      <div className="absolute inset-0 bg-gradient-to-r from-[#C9A882]/10 to-[#B08968]/5 rounded-3xl blur-2xl"></div>
      <div className="relative bg-white/80 backdrop-blur-sm rounded-3xl p-6 lg:p-8 border border-[#E8D4BA]/40 shadow-xl shadow-[#C9A882]/10 h-full">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div className="flex-1">
            <h2 className="text-xl lg:text-2xl font-bold text-[#2D2A26] mb-2">👋 Привет, {userName}!</h2>
            <p className="text-[#5C5650] text-sm lg:text-base mb-4">Эксклюзивные идеи для Reels, гайды и стратегии роста</p>
            
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center space-x-1"><span>👁️</span><span><strong>{materialsViewed}</strong> просмотрено</span></div>
              <div className="flex items-center space-x-1"><span>⭐</span><span><strong>{favorites}</strong> в избранном</span></div>
            </div>
            
            {/* Мобилка: блоки */}
            <div className="lg:hidden mt-4 space-y-2">
              <div className="bg-[#F5E6D3]/50 rounded-xl p-3 flex items-center justify-between">
                <span className="text-xs font-medium text-[#8B8279]">📚 Изучено</span>
                <span className="text-xs font-bold text-[#B08968]">{uniqueViewed} из {totalMaterials}</span>
              </div>
              <div className="bg-[#F5E6D3]/50 rounded-xl p-3 flex items-center justify-between">
                <span className="text-xs font-medium text-[#8B8279] flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>Подписка
                </span>
                <span className="text-sm font-bold text-[#B08968]">{isUnlimited ? 'Безлимит ∞' : `${subscriptionDaysLeft} дн.`}</span>
              </div>
              <p className="text-center text-[10px] text-[#A9A29B] mt-2">Подробнее в разделе Профиль</p>
            </div>
          </div>
          
          {/* Десктоп: плашка подписки */}
          <div className="hidden lg:block">
            <div className="bg-[#F5E6D3]/40 rounded-2xl p-4 min-w-[180px]">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-xs font-medium text-[#8B8279]">Подписка активна</span>
              </div>
              <div className="text-xl font-bold text-[#5D4E3A]">
                {isUnlimited ? 'Безлимит ∞' : `${subscriptionDaysLeft} дней`}
              </div>
              <p className="text-[10px] text-[#A9A29B] mt-2">Подробнее в разделе Профиль</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

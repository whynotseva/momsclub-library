'use client'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  uniqueViewed: number
  totalMaterials: number
}

/**
 * Поиск + прогресс изучения
 */
export function SearchBar({
  value,
  onChange,
  uniqueViewed,
  totalMaterials,
}: SearchBarProps) {
  const progressPercent = totalMaterials > 0 ? Math.min((uniqueViewed / totalMaterials) * 100, 100) : 0

  return (
    <div className="mb-6 grid lg:grid-cols-4 gap-4">
      {/* Поиск */}
      <div className="lg:col-span-3 relative">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="🔍 Поиск материалов..."
          className="w-full px-5 py-3 lg:px-6 lg:py-4 rounded-xl lg:rounded-2xl bg-white/90 border border-[#E8D4BA]/40 focus:border-[#B08968] focus:outline-none focus:ring-2 focus:ring-[#B08968]/20 text-[#2D2A26] placeholder-[#A09890] shadow-lg shadow-[#C9A882]/5 transition-all"
        />
        {value && (
          <button 
            onClick={() => onChange('')}
            className="absolute right-3 lg:right-4 top-1/2 -translate-y-1/2 text-[#8B8279] hover:text-[#B08968] text-lg"
          >
            ✕
          </button>
        )}
      </div>
      
      {/* Прогресс изучения — только десктоп */}
      <div className="hidden lg:block bg-white/90 rounded-2xl p-4 border border-[#E8D4BA]/40 shadow-lg shadow-[#C9A882]/5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-[#8B8279]">📚 Изучено материалов</span>
          <span className="text-xs font-bold text-[#B08968]">{Math.round(progressPercent)}%</span>
        </div>
        <div className="h-2 bg-[#F5E6D3] rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-[#B08968] to-[#C9A882] rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>
        <div className="text-xs text-[#8B8279] mt-1">{uniqueViewed} из {totalMaterials}</div>
      </div>
    </div>
  )
}

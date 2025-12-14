'use client'

import { Category } from '@/lib/types'

interface CategoryFilterProps {
  categories: Category[]
  activeCategory: string
  featuredCount?: number
  onChange: (slug: string) => void
}

/**
 * Фильтр по категориям
 */
export function CategoryFilter({
  categories,
  activeCategory,
  featuredCount = 0,
  onChange,
}: CategoryFilterProps) {
  const buttonBase =
    'flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-300'
  const buttonActive =
    'bg-gradient-to-r from-[#B08968] to-[#A67C52] text-white shadow-lg shadow-[#B08968]/25 scale-[1.02]'
  const buttonInactive =
    'bg-white/90 text-[#5C5650] hover:bg-[#F5E6D3] border border-[#E8D4BA]/40 hover:border-[#B08968]/50 hover:shadow-md'

  return (
    <div className="mb-10">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Кнопка "Все" */}
        <button
          onClick={() => onChange('all')}
          className={`${buttonBase} ${activeCategory === 'all' ? buttonActive : buttonInactive}`}
        >
          <span className="text-lg">📚</span>
          <span>Все</span>
        </button>

        {/* Категории из API */}
        {categories.map((cat, index) => {
          const isLast = index === categories.length - 1

          return (
            <button
              key={cat.id}
              onClick={() => onChange(cat.slug)}
              className={`${buttonBase} ${isLast ? 'col-span-2 md:col-span-4' : ''} ${
                activeCategory === cat.slug ? buttonActive : buttonInactive
              }`}
            >
              <span className="text-lg">{cat.icon}</span>
              <span className="truncate">{cat.name}</span>
            </button>
          )
        })}

        {/* Фильтр "Выбор Полины" */}
        <button
          onClick={() => onChange('featured')}
          className={`col-span-2 md:col-span-4 ${buttonBase} ${
            activeCategory === 'featured'
              ? 'bg-gradient-to-r from-amber-400 to-amber-500 text-white shadow-lg shadow-amber-400/25 scale-[1.01]'
              : 'bg-gradient-to-r from-amber-50 to-orange-50 text-amber-700 border border-amber-200/60 hover:border-amber-400/50 hover:shadow-md'
          }`}
        >
          <span className="text-lg">⭐</span>
          <span>Выбор Полины</span>
          <span className="text-xs opacity-70">({featuredCount})</span>
        </button>
      </div>
    </div>
  )
}

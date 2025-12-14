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
          className="w-full px-5 py-3 lg:px-6 lg:py-4 rounded-xl lg:rounded-2xl bg-[var(--bg-card)] border border-[var(--border)] focus:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/20 text-[var(--text-primary)] placeholder-[var(--text-muted)] shadow-lg transition-all"
        />
        {value && (
          <button 
            onClick={() => onChange('')}
            className="absolute right-3 lg:right-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--accent)] text-lg"
          >
            ✕
          </button>
        )}
      </div>
      
      {/* Прогресс изучения — только десктоп */}
      <div className="hidden lg:block bg-[var(--bg-card)] rounded-2xl p-4 border border-[var(--border)] shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-[var(--text-muted)]">📚 Изучено материалов</span>
          <span className="text-xs font-bold text-[var(--accent)]">{Math.round(progressPercent)}%</span>
        </div>
        <div className="h-2 bg-[var(--bg-secondary)] rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-hover)] rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          ></div>
        </div>
        <div className="text-xs text-[var(--text-muted)] mt-1">{uniqueViewed} из {totalMaterials}</div>
      </div>
    </div>
  )
}

'use client'

interface EmptyStateProps {
  icon: string
  title: string
  description: string
  actionText?: string
  actionHref?: string
}

/**
 * Компонент пустого состояния — когда нет данных
 */
export function EmptyState({ 
  icon, 
  title, 
  description, 
  actionText, 
  actionHref = '/library' 
}: EmptyStateProps) {
  return (
    <div className="bg-white/90 dark:bg-[#1E1E1E]/90 rounded-3xl p-16 text-center shadow-xl shadow-[#C9A882]/10 dark:shadow-none border border-[#E8D4BA]/40 dark:border-[#3D3D3D]">
      <div className="text-6xl mb-6">{icon}</div>
      <h3 className="text-xl font-bold text-[#2D2A26] dark:text-[#E5E5E5] mb-2">{title}</h3>
      <p className="text-[#8B8279] dark:text-[#707070] mb-6">{description}</p>
      {actionText && (
        <a 
          href={actionHref} 
          className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-[#B08968] to-[#A67C52] text-white font-semibold rounded-xl hover:shadow-lg transition-all"
        >
          {actionText}
        </a>
      )}
    </div>
  )
}

'use client'

interface LoadingSpinnerProps {
  text?: string
}

/**
 * Компонент загрузки — полноэкранный спиннер
 */
export function LoadingSpinner({ text = 'Загрузка...' }: LoadingSpinnerProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6] flex items-center justify-center">
      <div className="text-center">
        <img 
          src="/logolibrary.svg" 
          alt="LibriMomsClub" 
          className="h-20 sm:h-24 w-auto mx-auto mb-4 animate-pulse" 
        />
        <p className="text-[#8B8279]">{text}</p>
      </div>
    </div>
  )
}

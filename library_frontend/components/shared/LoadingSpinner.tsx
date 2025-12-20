'use client'

interface LoadingSpinnerProps {
  text?: string
}

/**
 * Компонент загрузки — полноэкранный спиннер
 */
export function LoadingSpinner({ text = 'Загрузка...' }: LoadingSpinnerProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6] dark:from-[#121212] dark:via-[#1A1A1A] dark:to-[#121212] flex items-center justify-center">
      <div className="text-center">
        <img 
          src="/logolibrary.svg" 
          alt="LibriMomsClub" 
          className="h-20 sm:h-24 w-auto mx-auto mb-4 animate-pulse dark:hidden" 
        />
        <img 
          src="/logonighthem.svg" 
          alt="LibriMomsClub" 
          className="h-20 sm:h-24 w-auto mx-auto mb-4 animate-pulse hidden dark:block" 
        />
        <p className="text-[#8B8279] dark:text-[#707070]">{text}</p>
      </div>
    </div>
  )
}

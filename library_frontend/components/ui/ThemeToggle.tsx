'use client'

import { useTheme } from '@/contexts/ThemeContext'

interface ThemeToggleProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

/**
 * Кнопка переключения темы в премиальном стиле сайта
 * Иконки солнца и луны с градиентом #B08968
 */
export function ThemeToggle({ className = '', size = 'md' }: ThemeToggleProps) {
  const { resolvedTheme, toggleTheme } = useTheme()
  
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  }
  
  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24,
  }

  const iconSize = iconSizes[size]

  return (
    <button
      onClick={toggleTheme}
      className={`
        ${sizeClasses[size]}
        flex items-center justify-center
        rounded-xl
        bg-[var(--bg-secondary)] hover:bg-[var(--border)]
        border border-[var(--border)]
        transition-all duration-300
        hover:scale-105 active:scale-95
        shadow-sm hover:shadow-md
        ${className}
      `}
      aria-label={resolvedTheme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему'}
      title={resolvedTheme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}
    >
      {resolvedTheme === 'dark' ? (
        // Солнце — для переключения на светлую тему
        <svg
          width={iconSize}
          height={iconSize}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="transition-transform duration-300"
        >
          <defs>
            <linearGradient id="sunGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#C9A882" />
              <stop offset="100%" stopColor="#D4B896" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="5" fill="url(#sunGradient)" />
          <path
            d="M12 2V4M12 20V22M4 12H2M6.31 6.31L4.9 4.9M17.69 6.31L19.1 4.9M6.31 17.69L4.9 19.1M17.69 17.69L19.1 19.1M22 12H20"
            stroke="url(#sunGradient)"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      ) : (
        // Луна — для переключения на тёмную тему
        <svg
          width={iconSize}
          height={iconSize}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="transition-transform duration-300"
        >
          <defs>
            <linearGradient id="moonGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#B08968" />
              <stop offset="100%" stopColor="#A67C52" />
            </linearGradient>
          </defs>
          <path
            d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
            fill="url(#moonGradient)"
            stroke="url(#moonGradient)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </button>
  )
}

'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { ThemeToggle } from '@/components/ui/ThemeToggle'

export default function PaymentSuccessPage() {
  const [showConfetti, setShowConfetti] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setShowConfetti(false), 5000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] relative overflow-hidden flex items-center justify-center">
      {/* Theme Toggle */}
      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle size="sm" />
      </div>
      {/* Premium gradient orbs */}
      <div className="fixed -top-40 -right-40 w-[600px] h-[600px] bg-gradient-to-br from-[#E8D5C4]/30 via-[#D4C4B0]/15 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="fixed -bottom-40 -left-40 w-[500px] h-[500px] bg-gradient-to-tr from-[#C9B89A]/15 to-transparent rounded-full blur-3xl pointer-events-none" />
      
      {/* Confetti animation */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute animate-confetti"
              style={{
                left: `${Math.random() * 100}%`,
                top: '-20px',
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${3 + Math.random() * 2}s`,
              }}
            >
              <span className="text-2xl">
                {['🎉', '✨', '💖', '🩷', '⭐', '💎'][Math.floor(Math.random() * 6)]}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="relative z-10 max-w-lg w-full mx-4">
        <div className="bg-[var(--bg-card)] backdrop-blur-sm rounded-3xl shadow-2xl border border-[var(--border)] p-5 sm:p-8 text-center">
          {/* Success icon */}
          <div className="mb-4 sm:mb-6 relative">
            <div className="w-16 h-16 sm:w-24 sm:h-24 mx-auto bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center shadow-lg shadow-green-400/30 animate-bounce-slow">
              <svg className="w-8 h-8 sm:w-12 sm:h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 text-2xl sm:text-4xl animate-pulse">✨</div>
            <div className="absolute -bottom-1 -left-1 sm:-bottom-2 sm:-left-2 text-xl sm:text-3xl animate-pulse delay-500">💖</div>
          </div>

          {/* Title */}
          <h1 className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)] mb-2">
            Поздравляем, красотка! 🎉
          </h1>
          
          <p className="text-base sm:text-lg text-[var(--text-secondary)] mb-4">
            Платёж успешно прошёл 🩷
          </p>

          {/* Info card */}
          <div className="bg-[var(--bg-secondary)] rounded-xl p-4 mb-4 border border-[var(--border)]">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="text-xl">🎀</span>
              <span className="font-semibold text-[var(--text-primary)] text-sm sm:text-base">Добро пожаловать в клуб!</span>
            </div>
            <p className="text-xs sm:text-sm text-[var(--text-muted)]">
              Теперь тебе доступна библиотека и закрытый чат с девочками 💖
            </p>
          </div>

          {/* What's next - hidden on mobile */}
          <div className="hidden sm:block space-y-3 mb-6">
            <p className="text-sm font-medium text-[var(--text-secondary)]">Что тебя ждёт? ✨</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-[var(--bg-card)] rounded-xl p-3 border border-[var(--border)] shadow-sm">
                <span className="text-xl mb-1 block">📚</span>
                <span className="text-xs text-[var(--text-secondary)]">Библиотека материалов</span>
              </div>
              <div className="bg-[var(--bg-card)] rounded-xl p-3 border border-[var(--border)] shadow-sm">
                <span className="text-xl mb-1 block">🩷</span>
                <span className="text-xs text-[var(--text-secondary)]">Закрытый чат с девочками</span>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="space-y-2 sm:space-y-3">
            <Link
              href="/"
              className="block w-full py-3 sm:py-4 bg-gradient-to-r from-[var(--accent)] via-[var(--accent-hover)] to-[var(--accent)] text-white font-semibold rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 text-center text-sm sm:text-base"
            >
              📚 Перейти в библиотеку
            </Link>
            
            <Link
              href="/profile"
              className="block w-full py-2.5 sm:py-3 bg-[var(--bg-card)] text-[var(--accent)] font-medium rounded-xl border-2 border-[var(--border)] hover:border-[var(--accent)] transition-all text-center text-sm sm:text-base"
            >
              👤 Мой профиль
            </Link>
          </div>

          {/* Footer note - hidden on mobile */}
          <p className="hidden sm:block mt-6 text-xs text-[var(--text-muted)]">
            💌 Чек об оплате отправлен на твой email
          </p>
        </div>

        {/* Logo - hidden on mobile */}
        <div className="hidden sm:block mt-6 text-center">
          <img 
            src="/logolibrary.svg" 
            alt="LibriMomsClub" 
            className="h-8 mx-auto opacity-60"
          />
        </div>
      </div>

      {/* Custom animation styles */}
      <style jsx>{`
        @keyframes confetti {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }
        .animate-confetti {
          animation: confetti 4s ease-out forwards;
        }
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }
        .animate-bounce-slow {
          animation: bounce-slow 2s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}

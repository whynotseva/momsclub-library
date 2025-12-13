'use client'

import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6] relative overflow-hidden flex items-center justify-center">
      {/* Premium gradient orbs */}
      <div className="fixed -top-40 -right-40 w-[600px] h-[600px] bg-gradient-to-br from-[#E8D5C4]/30 via-[#D4C4B0]/15 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="fixed -bottom-40 -left-40 w-[500px] h-[500px] bg-gradient-to-tr from-[#C9B89A]/15 to-transparent rounded-full blur-3xl pointer-events-none" />
      
      {/* Floating elements */}
      <div className="fixed top-20 left-20 text-6xl opacity-20 animate-float">📚</div>
      <div className="fixed bottom-32 right-20 text-5xl opacity-20 animate-float-delayed">✨</div>
      <div className="fixed top-1/3 right-32 text-4xl opacity-15 animate-float">🩷</div>

      {/* Content */}
      <div className="relative z-10 max-w-lg w-full mx-4 text-center">
        {/* 404 Number */}
        <div className="mb-8">
          <div className="relative inline-block">
            <span className="text-[150px] font-bold bg-gradient-to-br from-[#B08968] via-[#C9A882] to-[#A67C52] bg-clip-text text-transparent leading-none">
              404
            </span>
            <div className="absolute -top-4 -right-4 text-5xl animate-bounce">
              🔍
            </div>
          </div>
        </div>

        {/* Card */}
        <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl shadow-[#C9A882]/20 border border-[#E8D4BA]/40 p-8">
          {/* Icon */}
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-[#FAF6F1] to-[#F5EFE6] rounded-2xl flex items-center justify-center border border-[#E8D4BA]/30">
            <span className="text-4xl">🗺️</span>
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold text-[#2D2A26] mb-3">
            Упс, красотка! 🙈
          </h1>
          
          <p className="text-[#5D4E3A] mb-6">
            Кажется, эта страница решила поиграть в прятки. 
            Но не переживай — мы поможем тебе вернуться! 🩷
          </p>

          {/* Suggestions */}
          <div className="bg-gradient-to-r from-[#FAF6F1] to-[#F5EFE6] rounded-2xl p-4 mb-6 border border-[#E8D4BA]/30">
            <p className="text-sm text-[#8B8279] mb-3">Возможно, тебе будет интересно:</p>
            <div className="flex flex-wrap justify-center gap-2">
              <Link 
                href="/"
                className="px-3 py-1.5 bg-white rounded-full text-sm text-[#5D4E3A] border border-[#E8D4BA]/50 hover:border-[#B08968] hover:text-[#B08968] transition-colors"
              >
                📚 Библиотека
              </Link>
              <Link 
                href="/profile"
                className="px-3 py-1.5 bg-white rounded-full text-sm text-[#5D4E3A] border border-[#E8D4BA]/50 hover:border-[#B08968] hover:text-[#B08968] transition-colors"
              >
                👤 Профиль
              </Link>
            </div>
          </div>

          {/* Main button */}
          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 w-full py-4 bg-gradient-to-r from-[#B08968] via-[#A67C52] to-[#96704A] text-white font-semibold rounded-xl shadow-lg shadow-[#B08968]/25 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            На главную
          </Link>
        </div>

        {/* Logo */}
        <div className="mt-8">
          <img 
            src="/logolibrary.svg" 
            alt="LibriMomsClub" 
            className="h-8 mx-auto opacity-60"
          />
        </div>
      </div>

      {/* Custom animation styles */}
      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0) rotate(0deg);
          }
          50% {
            transform: translateY(-20px) rotate(5deg);
          }
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animate-float-delayed {
          animation: float 6s ease-in-out infinite;
          animation-delay: 2s;
        }
      `}</style>
    </div>
  )
}

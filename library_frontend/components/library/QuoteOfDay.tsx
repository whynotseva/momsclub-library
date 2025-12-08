'use client'

import { useState, useCallback } from 'react'
import { DAILY_QUOTES, getDayOfYear } from '@/lib/quotes'

interface QuoteOfDayProps {
  author?: string
}

/**
 * Компонент цитаты дня с возможностью обновления
 */
export function QuoteOfDay({ author = 'Полина' }: QuoteOfDayProps) {
  const [quoteIndex, setQuoteIndex] = useState(getDayOfYear() % DAILY_QUOTES.length)
  const [isAnimating, setIsAnimating] = useState(false)

  const refreshQuote = useCallback(() => {
    if (isAnimating) return

    setIsAnimating(true)

    setTimeout(() => {
      let newIndex: number
      do {
        newIndex = Math.floor(Math.random() * DAILY_QUOTES.length)
      } while (newIndex === quoteIndex)
      setQuoteIndex(newIndex)

      setTimeout(() => {
        setIsAnimating(false)
      }, 300)
    }, 300)
  }, [isAnimating, quoteIndex])

  return (
    <div className="mb-8 bg-gradient-to-r from-[#F5E6D3]/50 to-[#ECD9C8]/30 rounded-2xl p-4 lg:p-6 border border-[#E8D4BA]/30">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start space-x-3 flex-1">
          <span className="text-2xl lg:text-3xl">💬</span>
          <div
            className={`transition-all duration-300 ${isAnimating ? 'opacity-0 translate-y-2' : 'opacity-100 translate-y-0'}`}
          >
            <p className="text-[#2D2A26] font-medium italic text-sm lg:text-base">
              &ldquo;{DAILY_QUOTES[quoteIndex]}&rdquo;
            </p>
            <p className="text-[#B08968] text-xs lg:text-sm mt-2">— {author}</p>
          </div>
        </div>
        <button
          onClick={refreshQuote}
          disabled={isAnimating}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 flex-shrink-0 ${
            isAnimating
              ? 'bg-[#E8D4BA]/50 text-[#8B8279] cursor-not-allowed'
              : 'bg-white/70 hover:bg-white text-[#B08968] hover:shadow-md border border-[#E8D4BA]/50'
          }`}
        >
          <span className={`transition-transform duration-300 ${isAnimating ? 'animate-spin' : ''}`}>✨</span>
          <span className="hidden sm:inline">Новая цитата</span>
        </button>
      </div>
    </div>
  )
}

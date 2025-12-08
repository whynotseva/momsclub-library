'use client'

import { useState, useEffect } from 'react'

export default function InstallPrompt() {
  const [show, setShow] = useState(false)
  const [isIOS, setIsIOS] = useState(false)
  const [isTelegram, setIsTelegram] = useState(false)

  useEffect(() => {
    const ua = navigator.userAgent || ''
    
    // PWA уже установлено?
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                         (window.navigator as unknown as { standalone?: boolean }).standalone === true
    
    // Telegram браузер?
    const inTelegram = ua.includes('Telegram') || 
                       /\(iPhone.*Mobile.*Safari\)/.test(ua) && !ua.includes('CriOS') && !ua.includes('FxiOS') && !ua.includes('Safari/')
    setIsTelegram(inTelegram || document.referrer.includes('t.me'))
    
    // Проверяем счётчик показов
    const showCount = parseInt(localStorage.getItem('pwa_prompt_count') || '0')
    const lastShown = parseInt(localStorage.getItem('pwa_prompt_last') || '0')
    const dismissed = localStorage.getItem('pwa_prompt_dismissed') === 'true'
    
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000
    let shouldShow = true
    
    if (dismissed && showCount >= 3) {
      shouldShow = false
    } else if (lastShown > oneDayAgo && showCount > 0) {
      shouldShow = false
    }
    
    setIsIOS(/iPad|iPhone|iPod/.test(ua))
    const isMobile = /iPhone|iPad|iPod|Android/i.test(ua)
    
    if (isMobile && !isStandalone && shouldShow) {
      setTimeout(() => {
        setShow(true)
        localStorage.setItem('pwa_prompt_count', String(showCount + 1))
        localStorage.setItem('pwa_prompt_last', String(Date.now()))
      }, 1500)
    }
  }, [])

  const handleDismiss = () => {
    setShow(false)
    localStorage.setItem('pwa_prompt_dismissed', 'true')
  }

  const handleRemindLater = () => {
    setShow(false)
  }

  if (!show) return null

  // Инструкция для Telegram браузера
  if (isTelegram) {
    return (
      <div className="fixed inset-0 z-[9999] flex items-end justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden animate-slide-up">
          <div className="bg-gradient-to-r from-[#B08968] to-[#C9A882] p-6 text-white text-center">
            <div className="text-4xl mb-2">🌐</div>
            <h2 className="text-xl font-bold">Открой в браузере!</h2>
            <p className="text-white/80 text-sm mt-1">Для добавления на рабочий стол</p>
          </div>
          <div className="p-6">
            <p className="text-[#5D5550] text-center mb-4">
              В Telegram браузере нельзя добавить на рабочий стол. Открой в Safari/Chrome:
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">1️⃣</span>
                <span className="text-[#2D2A26]">Нажми <strong>(...)</strong> справа вверху</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">2️⃣</span>
                <span className="text-[#2D2A26]">Выбери <strong>«Открыть в Safari»</strong></span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">3️⃣</span>
                <span className="text-[#2D2A26]">Там добавишь на рабочий стол 📲</span>
              </div>
            </div>
          </div>
          <div className="p-4 pt-0 flex gap-3">
            <button onClick={handleRemindLater} className="flex-1 py-3 text-[#8B8279] font-medium rounded-xl">Позже</button>
            <button onClick={handleDismiss} className="flex-1 py-3 bg-[#B08968] text-white font-semibold rounded-xl">Понятно!</button>
          </div>
        </div>
        <style jsx>{`
          @keyframes slide-up { from { transform: translateY(100%); } to { transform: translateY(0); } }
          .animate-slide-up { animation: slide-up 0.3s ease-out; }
        `}</style>
      </div>
    )
  }

  // Инструкция для обычного браузера (Safari/Chrome)
  return (
    <div className="fixed inset-0 z-[9999] flex items-end justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden animate-slide-up">
        <div className="bg-gradient-to-r from-[#B08968] to-[#C9A882] p-6 text-white text-center">
          <div className="text-4xl mb-2">📲</div>
          <h2 className="text-xl font-bold">Добавь на рабочий стол!</h2>
          <p className="text-white/80 text-sm mt-1">Будет как приложение</p>
        </div>
        <div className="p-6">
          <p className="text-[#5D5550] text-center mb-4">
            Библиотека будет открываться быстрее и удобнее! ✨
          </p>
          {isIOS ? (
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">1️⃣</span>
                <span className="text-[#2D2A26]">Нажми <strong>⬆️ Поделиться</strong> внизу</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">2️⃣</span>
                <span className="text-[#2D2A26]">Выбери <strong>«На экран Домой»</strong></span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">3️⃣</span>
                <span className="text-[#2D2A26]">Нажми <strong>Добавить</strong></span>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">1️⃣</span>
                <span className="text-[#2D2A26]">Нажми <strong>⋮</strong> (меню браузера)</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-[#FDF8F3] rounded-xl">
                <span className="text-2xl">2️⃣</span>
                <span className="text-[#2D2A26]">Выбери <strong>«Добавить на главный экран»</strong></span>
              </div>
            </div>
          )}
        </div>
        <div className="p-4 pt-0 flex gap-3">
          <button onClick={handleRemindLater} className="flex-1 py-3 text-[#8B8279] font-medium rounded-xl">Позже</button>
          <button onClick={handleDismiss} className="flex-1 py-3 bg-[#B08968] text-white font-semibold rounded-xl">Понятно!</button>
        </div>
      </div>
      <style jsx>{`
        @keyframes slide-up { from { transform: translateY(100%); } to { transform: translateY(0); } }
        .animate-slide-up { animation: slide-up 0.3s ease-out; }
      `}</style>
    </div>
  )
}

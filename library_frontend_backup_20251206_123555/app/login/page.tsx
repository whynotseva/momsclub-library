'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

export default function LoginPage() {
  const router = useRouter()
  const [authError, setAuthError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      router.push('/library')
      return
    }

    // Обработка callback от Telegram (query параметры после редиректа)
    const urlParams = new URLSearchParams(window.location.search)
    const tgId = urlParams.get('id')
    const tgHash = urlParams.get('hash')
    
    // Проверяем нет ли флага ошибки (чтобы не зацикливаться)
    const hadError = sessionStorage.getItem('auth_error')
    
    if (tgId && tgHash && !hadError) {
      setIsProcessing(true)
      // Пришли данные от Telegram — авторизуемся
      const authData = {
        id: parseInt(tgId),
        first_name: urlParams.get('first_name') || '',
        last_name: urlParams.get('last_name') || undefined,
        username: urlParams.get('username') || undefined,
        photo_url: urlParams.get('photo_url') || undefined,
        auth_date: parseInt(urlParams.get('auth_date') || '0'),
        hash: tgHash
      }
      
      handleTelegramAuth(authData)
      return
    }
    
    // Если был редирект с ошибкой, очищаем URL
    if (tgId && hadError) {
      window.history.replaceState({}, '', '/login')
    }

    // Добавляем виджет Telegram
    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.setAttribute('data-telegram-login', process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || 'momsclubsubscribe_bot')
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-radius', '12')
    script.setAttribute('data-auth-url', window.location.origin + '/login')
    script.setAttribute('data-request-access', 'write')
    script.async = true

    const container = document.getElementById('telegram-login-container')
    if (container) {
      container.innerHTML = '' // Очищаем перед добавлением
      container.appendChild(script)
    }
  }, [router])
  
  // Обработка авторизации через Telegram
  const handleTelegramAuth = async (authData: { id: number; first_name: string; last_name?: string; username?: string; photo_url?: string; auth_date: number; hash: string }) => {
    try {
      const response = await api.post('/auth/telegram', authData)
      // Успешная авторизация — очищаем флаг ошибки
      sessionStorage.removeItem('auth_error')
      localStorage.setItem('access_token', response.data.access_token)
      // Сохраняем user данные включая photo_url из Telegram
      const userToSave = {
        ...response.data.user,
        photo_url: authData.photo_url // Берём photo_url из данных Telegram
      }
      localStorage.setItem('user', JSON.stringify(userToSave))
      router.push('/library')
    } catch (error: unknown) {
      console.error('Ошибка авторизации:', error)
      // Сохраняем флаг ошибки чтобы не зацикливаться
      sessionStorage.setItem('auth_error', 'true')
      
      // Определяем текст ошибки
      const axiosError = error as { response?: { data?: { detail?: string } } }
      const errorMessage = axiosError.response?.data?.detail || 'Ошибка авторизации'
      setAuthError(errorMessage)
      setIsProcessing(false)
      
      // Очищаем URL от параметров
      window.history.replaceState({}, '', '/login')
    }
  }
  
  // Сброс ошибки для повторной попытки
  const handleRetry = () => {
    sessionStorage.removeItem('auth_error')
    setAuthError(null)
    window.location.reload()
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6] relative overflow-hidden">
      {/* Premium gradient orbs */}
      <div className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-gradient-to-br from-[#E8D5C4]/40 via-[#D4C4B0]/20 to-transparent rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] bg-gradient-to-tr from-[#C9B89A]/20 to-transparent rounded-full blur-3xl"></div>
      
      {/* Shimmer line */}

      <div className="relative min-h-screen flex flex-col">
        {/* Header */}
        <header className="w-full px-6 pb-4 backdrop-blur-sm" style={{ paddingTop: "max(1rem, env(safe-area-inset-top))" }}>
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            {/* Logo with Santa hat */}
            <a href="/library" className="group relative">
              <img 
                src="/logolibrary.svg" 
                alt="LibriMomsClub" 
                className="h-12 w-auto group-hover:scale-105 transition-transform"
              />
              {/* Santa hat */}
              <span className="absolute -top-3 -left-1 text-2xl transform -rotate-12">🎅</span>
            </a>
            
            <a 
              href="https://t.me/momsclubsupport"
              target="_blank"
              rel="noopener noreferrer" 
              className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-all duration-300 hover:scale-105"
            >
              Нужна помощь?
            </a>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 flex items-center justify-center px-6 py-2">
          <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-16 items-center">
            {/* Left side - Content */}
            <div className="space-y-8">
              <div className="inline-flex items-center space-x-2.5 px-5 py-2.5 bg-gradient-to-r from-[#F5E6D3]/80 to-[#EDD9C4]/80 backdrop-blur-sm rounded-full border border-[#D4B896]/40 shadow-lg shadow-[#C9A882]/10 hover:shadow-xl hover:shadow-[#C9A882]/20 transition-all duration-500 cursor-default">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#B08968] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-gradient-to-r from-[#B08968] to-[#9A7B5B]"></span>
                </span>
                <span className="text-sm font-medium text-[#6B5B4F]">Доступно для участников клуба</span>
              </div>

              <div className="space-y-6">
                <h1 className="text-4xl lg:text-5xl xl:text-6xl font-extrabold text-[#2D2A26] leading-[1.1] tracking-tight">
                  Библиотека<br />
                  для роста<br />
                  <span className="relative inline-block">
                    <span className="bg-gradient-to-r from-[#B08968] via-[#C9A882] to-[#8B7355] bg-clip-text text-transparent">
                      твоего блога
                    </span>
                    <span className="absolute -bottom-2 left-0 w-full h-1 bg-gradient-to-r from-[#B08968]/60 via-[#C9A882]/40 to-transparent rounded-full"></span>
                  </span>
                </h1>
                
                <p className="text-lg text-[#5C5650] leading-relaxed max-w-lg">
                  Эксклюзивные материалы, проверенные стратегии и готовые идеи для контента от профессионалов
                </p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-6 pt-4">
                <div className="group cursor-default">
                  <div className="text-4xl font-black text-[#2D2A26] group-hover:text-[#B08968] transition-colors duration-300">100+</div>
                  <div className="text-sm font-medium text-[#8B8279] mt-1 uppercase tracking-wider">Материалов</div>
                </div>
                <div className="group cursor-default">
                  <div className="text-4xl font-black text-[#2D2A26] group-hover:text-[#B08968] transition-colors duration-300">50+</div>
                  <div className="text-sm font-medium text-[#8B8279] mt-1 uppercase tracking-wider">Подкастов и статей</div>
                </div>
                <div className="group cursor-default">
                  <div className="text-4xl font-black text-[#2D2A26] group-hover:text-[#B08968] transition-colors duration-300">24/7</div>
                  <div className="text-sm font-medium text-[#8B8279] mt-1 uppercase tracking-wider">Доступ</div>
                </div>
              </div>

              {/* Features */}
              <div className="grid grid-cols-2 gap-4 pt-4">
                {[
                  { icon: '📝', text: 'Статьи по блогингу и контенту' },
                  { icon: '🎙️', text: 'Подкасты' },
                  { icon: '🎬', text: 'Фишки съемки' },
                  { icon: '📚', text: 'Уроки и туториалы' },
                ].map((item, i) => (
                  <div key={i} className="group flex items-center space-x-3 cursor-default">
                    <div className="w-10 h-10 bg-gradient-to-br from-[#F5E6D3] to-[#ECD9C8] rounded-xl flex items-center justify-center border border-[#D4B896]/30 shadow-sm group-hover:shadow-md group-hover:scale-110 transition-all duration-300">
                      <span className="text-base">{item.icon}</span>
                    </div>
                    <span className="text-sm font-medium text-[#5C5650] group-hover:text-[#B08968] transition-colors duration-300">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right side - Login card */}
            <div className="lg:pl-8">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-[#C9A882]/5 to-[#B08968]/5 rounded-3xl blur-xl"></div>
                <div className="relative bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl shadow-[#C9A882]/15 border border-[#E8D4BA]/50 p-10">
                <div className="space-y-6">
                  <div className="text-center">
                    <h2 className="text-3xl font-bold text-[#2D2A26] mb-3">
                      Войти в библиотеку
                    </h2>
                    <p className="text-[#8B8279]">
                      Используйте Telegram для быстрого входа
                    </p>
                  </div>

                  {/* Показываем ошибку если есть */}
                  {authError && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
                      <p className="text-red-600 font-medium mb-3">❌ {authError}</p>
                      <div className="space-y-3">
                        <p className="text-sm text-gray-600">
                          Чтобы войти с другого аккаунта:
                        </p>
                        <ol className="text-sm text-gray-500 text-left space-y-1 pl-4">
                          <li>1. Откройте Telegram</li>
                          <li>2. Переключитесь на нужный аккаунт</li>
                          <li>3. Вернитесь и нажмите кнопку ниже</li>
                        </ol>
                        <button
                          onClick={handleRetry}
                          className="w-full py-2 px-4 bg-[#B08968] hover:bg-[#9A7B5B] text-white font-medium rounded-xl transition-colors"
                        >
                          Войти снова
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Показываем загрузку при обработке */}
                  {isProcessing && (
                    <div className="py-8 text-center">
                      <div className="w-8 h-8 border-3 border-[#B08968] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                      <p className="text-[#8B8279]">Авторизация...</p>
                    </div>
                  )}

                  {/* Telegram Login - показываем если нет ошибки и не обрабатываем */}
                  {!authError && !isProcessing && (
                    <div className="py-4">
                      <div id="telegram-login-container" className="flex justify-center"></div>
                    </div>
                  )}

                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-200"></div>
                    </div>
                    <div className="relative flex justify-center text-xs">
                      <span className="px-3 bg-white/80 text-gray-500 uppercase tracking-wider">или</span>
                    </div>
                  </div>

                  {/* CTA */}
                  <a 
                    href="https://t.me/momsclubsubscribe_bot" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="group w-full inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-[#B08968] via-[#A67C52] to-[#96704A] text-white font-bold rounded-2xl shadow-lg shadow-[#B08968]/25 hover:shadow-xl hover:shadow-[#B08968]/40 hover:-translate-y-0.5 transition-all duration-300"
                  >
                    <span className="flex items-center space-x-2">
                      <span>Оформить подписку</span>
                      <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                      </svg>
                    </span>
                  </a>

                  <p className="text-center text-xs text-[#A09890] mt-4">
                    🔒 Требуется активная подписка MomsClub
                  </p>
                </div>
              </div>
              </div>

              {/* Trust badge */}
              <div className="mt-6 flex items-center justify-center space-x-6 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                  <span>Безопасный вход</span>
                </div>
                <div className="flex items-center space-x-1">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Проверено</span>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="w-full px-6 py-2 border-t border-gray-200/50">
          <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-gray-600">
            <p>© 2025 MomsClub. Все права защищены.</p>
            <div className="flex items-center space-x-6">
              <a href="/privacy" className="hover:text-gray-900 transition-colors">Политика</a>
              <a href="/terms" className="hover:text-gray-900 transition-colors">Условия</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}

'use client'

import { useEffect, useState } from 'react'

/**
 * Компонент-индикатор offline режима.
 * Показывает уведомление когда пользователь offline.
 * Использует SVG иконки в стиле сайта с поддержкой тем.
 */
export function OfflineIndicator() {
    const [isOffline, setIsOffline] = useState(false)
    const [showBanner, setShowBanner] = useState(false)

    useEffect(() => {
        // Начальное состояние
        setIsOffline(!navigator.onLine)
        setShowBanner(!navigator.onLine)

        const handleOnline = () => {
            setIsOffline(false)
            // Показываем "Подключение восстановлено" на 3 секунды
            setShowBanner(true)
            setTimeout(() => setShowBanner(false), 3000)
        }

        const handleOffline = () => {
            setIsOffline(true)
            setShowBanner(true)
        }

        window.addEventListener('online', handleOnline)
        window.addEventListener('offline', handleOffline)

        return () => {
            window.removeEventListener('online', handleOnline)
            window.removeEventListener('offline', handleOffline)
        }
    }, [])

    if (!showBanner) return null

    return (
        <div
            className={`fixed top-0 left-0 right-0 z-[100] py-2.5 px-4 text-center text-sm font-medium transition-all duration-300 backdrop-blur-md border-b ${isOffline
                    ? 'bg-[#F5E6D3]/95 dark:bg-[#2A2520]/95 text-[#5C5650] dark:text-[#E5E5E5] border-[#E8D4BA]/50 dark:border-[#3D3D3D]'
                    : 'bg-green-50/95 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200/50 dark:border-green-800/50'
                }`}
            style={{ paddingTop: 'calc(0.625rem + env(safe-area-inset-top))' }}
        >
            <div className="max-w-7xl mx-auto flex items-center justify-center gap-2">
                {isOffline ? (
                    <>
                        {/* Wifi Off Icon */}
                        <svg
                            className="w-5 h-5 text-[#B08968] dark:text-[#C9A882]"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={2}
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a5 5 0 01-7.072-7.072l2.829 2.829M12 12a1 1 0 11-2 0 1 1 0 012 0z"
                            />
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 3l18 18" />
                        </svg>
                        <span>Нет подключения к интернету. Показаны сохранённые материалы.</span>
                    </>
                ) : (
                    <>
                        {/* Check Circle Icon */}
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={2}
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <span>Подключение восстановлено!</span>
                    </>
                )}
            </div>
        </div>
    )
}

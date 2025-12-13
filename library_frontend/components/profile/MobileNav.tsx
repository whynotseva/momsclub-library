'use client'

import { useState, useEffect } from 'react'

interface ProfileMobileNavProps {
  isVisible?: boolean
}

/**
 * Мобильная навигация для ЛК (floating)
 */
export function ProfileMobileNav({ isVisible: externalVisible = true }: ProfileMobileNavProps) {
  const [isVisible, setIsVisible] = useState(true)
  const [lastScrollY, setLastScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setIsVisible(false)
      } else {
        setIsVisible(true)
      }
      setLastScrollY(currentScrollY)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [lastScrollY])

  const visible = externalVisible && isVisible

  return (
    <nav
      className={`md:hidden fixed bottom-6 left-4 right-4 z-50 transition-all duration-300 ease-in-out ${
        visible ? 'translate-y-0 opacity-100' : 'translate-y-24 opacity-0'
      }`}
    >
      <div
        className="flex items-center justify-around rounded-2xl px-2 py-3 shadow-2xl border border-white/50"
        style={{ background: 'rgba(255,255,255,0.45)', backdropFilter: 'blur(24px) saturate(180%)' }}
      >
        <a
          href="/library"
          className="px-4 py-2 rounded-xl text-sm font-medium text-[#8B8279]"
        >
          Библиотека
        </a>
        <a
          href="/profile"
          className="px-4 py-2 rounded-xl text-sm font-semibold bg-[#B08968] text-white shadow-md"
        >
          Профиль
        </a>
      </div>
    </nav>
  )
}

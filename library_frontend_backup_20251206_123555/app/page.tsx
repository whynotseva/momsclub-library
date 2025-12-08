'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Проверяем авторизацию
    const token = localStorage.getItem('token')
    
    if (token) {
      // Есть токен — в библиотеку
      router.push('/library')
    } else {
      // Нет токена — на логин
      router.push('/login')
    }
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6] flex items-center justify-center">
      <div className="text-center">
        <img 
          src="/logolibrary.svg" 
          alt="LibriMomsClub" 
          className="h-20 sm:h-24 w-auto mx-auto mb-6 animate-pulse"
        />
        <p className="text-[#8B8279] font-medium">Загрузка...</p>
      </div>
    </div>
  )
}

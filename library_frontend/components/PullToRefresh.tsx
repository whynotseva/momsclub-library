'use client'

import { useState, useRef, ReactNode } from 'react'

interface Props {
  children: ReactNode
  onRefresh: () => Promise<void>
}

export default function PullToRefresh({ children, onRefresh }: Props) {
  const [pullY, setPullY] = useState(0)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const touchStartY = useRef(0)

  const threshold = 100

  const handleTouchStart = (e: React.TouchEvent) => {
    if (window.scrollY === 0) {
      touchStartY.current = e.touches[0].clientY
    }
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    if (isRefreshing || window.scrollY > 0) return
    
    const diff = e.touches[0].clientY - touchStartY.current
    
    if (diff > 0) {
      setPullY(Math.min(diff * 0.5, 150))
    }
  }

  const handleTouchEnd = async () => {
    if (isRefreshing) return
    
    if (pullY >= threshold) {
      setIsRefreshing(true)
      setPullY(50)
      
      try {
        await onRefresh()
      } catch (e) {
        console.error('Refresh failed:', e)
      }
      
      setIsRefreshing(false)
    }
    
    setPullY(0)
    touchStartY.current = 0
  }

  const progress = Math.min(pullY / threshold, 1)

  // Выбираем эмодзи
  const getEmoji = () => {
    if (isRefreshing) return String.fromCodePoint(0x2728) // ✨
    if (pullY >= threshold) return String.fromCodePoint(0x1F389) // 🎉
    return String.fromCodePoint(0x1F447) // 👇
  }

  return (
    <div 
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      style={{ minHeight: '100vh' }}
    >
      {(pullY > 5 || isRefreshing) && (
        <div 
          className="fixed left-1/2 z-[9999] pointer-events-none"
          style={{ 
            top: Math.min(pullY, 60) + 20,
            transform: 'translateX(-50%)',
            transition: pullY === 0 ? 'top 0.2s ease' : 'none'
          }}
        >
          <div 
            className={isRefreshing ? 'animate-spin' : ''}
            style={{
              width: 52,
              height: 52,
              borderRadius: '50%',
              background: 'linear-gradient(145deg, #FDF8F3, #F5E6D3)',
              border: '2px solid #D4C4A8',
              boxShadow: '0 4px 15px rgba(176, 137, 104, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              transform: isRefreshing ? 'none' : `rotate(${progress * 360}deg)`,
            }}
          >
            <span style={{ transform: isRefreshing ? 'none' : `rotate(${-progress * 360}deg)` }}>
              {getEmoji()}
            </span>
          </div>
        </div>
      )}
      
      {children}
    </div>
  )
}

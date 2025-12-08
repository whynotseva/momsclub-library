'use client'

interface PushPromoModalProps {
  isOpen: boolean
  onEnable: () => Promise<boolean>
  onDismiss: () => void
}

/**
 * Модалка предложения включить Push-уведомления
 */
export function PushPromoModal({ isOpen, onEnable, onDismiss }: PushPromoModalProps) {
  if (!isOpen) return null

  const handleEnable = async () => {
    const success = await onEnable()
    if (success) {
      alert('🎉 Уведомления включены!')
    }
  }

  const handleDismiss = () => {
    localStorage.setItem('push_promo_dismissed', 'true')
    onDismiss()
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-3xl p-6 max-w-sm w-full shadow-2xl animate-in fade-in zoom-in duration-300">
        <div className="text-center">
          <div className="mb-4 flex justify-center">
            <svg
              className="w-16 h-16 text-[#B08968]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-[#2D2A26] mb-2">Не пропусти новинки!</h3>
          <p className="text-[#8B8279] mb-6">
            Включи уведомления, чтобы узнавать о новых материалах, идеях для Reels и полезных гайдах
            первой!
          </p>
          <div className="space-y-3">
            <button
              onClick={handleEnable}
              className="w-full py-3 px-4 bg-gradient-to-r from-[#B08968] to-[#A67C52] text-white font-semibold rounded-xl hover:shadow-lg transition-all"
            >
              ✨ Включить уведомления
            </button>
            <button
              onClick={handleDismiss}
              className="w-full py-2 text-[#8B8279] text-sm hover:text-[#2D2A26] transition-colors"
            >
              Позже
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

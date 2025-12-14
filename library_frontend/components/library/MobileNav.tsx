'use client'

interface MobileNavProps {
  activePage?: 'library' | 'favorites' | 'history' | 'profile'
  isPWA?: boolean
  isVisible?: boolean
}

/**
 * Мобильная навигация (floating)
 */
export function MobileNav({ activePage = 'library', isPWA = false, isVisible = true }: MobileNavProps) {
  const navItems = [
    { href: '/library', label: 'Библиотека', key: 'library' },
    { href: '/favorites', label: 'Избранное', key: 'favorites' },
    { href: '/history', label: 'История', key: 'history' },
    { href: '/profile', label: 'Профиль', key: 'profile' },
  ]

  return (
    <nav
      className={`md:hidden fixed bottom-6 left-4 right-4 z-50 transition-all duration-300 ease-in-out ${
        isVisible ? 'translate-y-0 opacity-100' : 'translate-y-24 opacity-0'
      }`}
    >
      <div
        className="flex items-center justify-around rounded-2xl px-2 py-3 shadow-2xl border border-[var(--border)]"
        style={{ background: 'var(--bg-header)', backdropFilter: 'blur(24px) saturate(180%)' }}
      >
        {isPWA && (
          <button
            onClick={() => window.location.reload()}
            className="p-2.5 rounded-xl text-[var(--accent)] hover:bg-[var(--bg-secondary)] transition-colors"
            title="Обновить"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
              <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
              <path d="M21 21v-5h-5" />
            </svg>
          </button>
        )}

        {navItems.map((item) => (
          <a
            key={item.key}
            href={item.href}
            className={`px-2 py-1.5 rounded-xl text-xs font-medium ${
              activePage === item.key
                ? 'font-semibold bg-[var(--accent)] text-white shadow-md'
                : 'text-[var(--text-muted)]'
            }`}
          >
            {item.label}
          </a>
        ))}
      </div>
    </nav>
  )
}

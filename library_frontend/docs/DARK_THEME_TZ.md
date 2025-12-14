# 🌙 ТЗ: Ночная тема для библиотеки Mom's Club

**Дата:** 14.12.2024  
**Статус:** Готово к реализации  
**Бэкап:** ✅ Сделан (`library_frontend_20251214_223826.tar.gz`)

---

## 📋 Содержание

1. [Цель](#цель)
2. [Оценка](#оценка)
3. [Цветовая схема](#цветовая-схема)
4. [Структура файлов](#структура-файлов)
5. [Пошаговая реализация](#пошаговая-реализация)
6. [Чеклист](#чеклист)

---

## 🎯 Цель

Добавить тёмную/ночную тему для:
- ✅ Десктоп
- ✅ Мобилка
- ✅ PWA

Функционал:
- Автоопределение системной темы (`prefers-color-scheme`)
- Ручное переключение 🌙/☀️
- Сохранение выбора в `localStorage`
- Плавная анимация переключения

---

## 📊 Оценка

| Параметр | Значение |
|----------|----------|
| **Сложность** | ⭐⭐⭐ Средняя |
| **Время** | 3-4 часа |
| **Файлов изменить** | ~25-30 |
| **Риск сломать** | Низкий |

---

## 🎨 Цветовая схема

### Основные цвета

| Элемент | Светлая тема | Тёмная тема |
|---------|--------------|-------------|
| Фон страницы | `#FDFCFA` | `#121212` |
| Фон карточек | `white/90` | `#1E1E1E` |
| Фон вторичный | `#F5E6D3` | `#2D2D2D` |
| Текст основной | `#2D2A26` | `#E5E5E5` |
| Текст вторичный | `#5D4E3A` | `#B0B0B0` |
| Текст muted | `#8B8279` | `#707070` |
| Акцент (кнопки) | `#B08968` | `#C9A882` |
| Акцент hover | `#A67C52` | `#D4B896` |
| Бордеры | `#E8D4BA` | `#3D3D3D` |
| Тени | `rgba(0,0,0,0.1)` | `rgba(0,0,0,0.4)` |

### Header

| Элемент | Светлая | Тёмная |
|---------|---------|--------|
| Фон | `rgba(255,255,255,0.55)` | `rgba(30,30,30,0.85)` |
| Бордер | `white/50` | `#3D3D3D` |
| Лого | Без изменений | Без изменений |

### Карточки материалов

| Элемент | Светлая | Тёмная |
|---------|---------|--------|
| Фон | `white` | `#1E1E1E` |
| Бордер | `#E8D4BA/40` | `#3D3D3D` |
| Hover | `shadow-lg` | `shadow-lg shadow-black/30` |

---

## 📁 Структура файлов

### Новые файлы (создать)

```
library_frontend/
├── contexts/
│   └── ThemeContext.tsx        # Контекст темы
├── hooks/
│   └── useTheme.ts             # Хук для работы с темой
├── components/
│   └── ui/
│       └── ThemeToggle.tsx     # Кнопка переключения
└── lib/
    └── theme.ts                # Константы цветов темы
```

### Существующие файлы (изменить)

```
library_frontend/
├── tailwind.config.ts          # Добавить darkMode: 'class'
├── app/
│   ├── globals.css             # CSS переменные для темы
│   └── layout.tsx              # Обернуть в ThemeProvider
├── components/
│   ├── library/
│   │   ├── Header.tsx          # dark: классы + ThemeToggle
│   │   ├── MaterialCard.tsx    # dark: классы
│   │   ├── CategoryFilter.tsx  # dark: классы
│   │   ├── WelcomeCard.tsx     # dark: классы
│   │   ├── SearchBar.tsx       # dark: классы
│   │   └── ...
│   ├── profile/
│   │   ├── ProfileCard.tsx     # dark: классы
│   │   ├── SubscriptionCard.tsx# dark: классы
│   │   └── ...
│   ├── shared/
│   │   ├── Avatar.tsx          # dark: классы
│   │   ├── LoadingSpinner.tsx  # dark: классы
│   │   └── ...
│   └── ui/
│       └── ...
└── app/
    ├── library/page.tsx        # dark: классы
    ├── profile/page.tsx        # dark: классы
    ├── favorites/page.tsx      # dark: классы
    ├── history/page.tsx        # dark: классы
    └── admin/page.tsx          # dark: классы
```

---

## 🔧 Пошаговая реализация

### ШАГ 1: Настройка Tailwind (5 мин)

**Файл:** `tailwind.config.ts`

```diff
const config: Config = {
+ darkMode: 'class',
  content: [
    ...
  ],
```

---

### ШАГ 2: CSS переменные (10 мин)

**Файл:** `app/globals.css`

Добавить в начало после `@tailwind`:

```css
:root {
  /* Светлая тема */
  --bg-primary: #FDFCFA;
  --bg-secondary: #F5E6D3;
  --bg-card: rgba(255, 255, 255, 0.9);
  --text-primary: #2D2A26;
  --text-secondary: #5D4E3A;
  --text-muted: #8B8279;
  --accent: #B08968;
  --accent-hover: #A67C52;
  --border: #E8D4BA;
}

.dark {
  /* Тёмная тема */
  --bg-primary: #121212;
  --bg-secondary: #2D2D2D;
  --bg-card: rgba(30, 30, 30, 0.9);
  --text-primary: #E5E5E5;
  --text-secondary: #B0B0B0;
  --text-muted: #707070;
  --accent: #C9A882;
  --accent-hover: #D4B896;
  --border: #3D3D3D;
}

/* Плавный переход темы */
html {
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

Изменить:
```css
@layer base {
  body {
-   @apply bg-[#FDFCFA] text-gray-900;
+   @apply bg-[var(--bg-primary)] text-[var(--text-primary)];
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

/* В конце файла изменить */
html, body {
- background-color: #FDFCFA !important;
+ background-color: var(--bg-primary) !important;
}
```

---

### ШАГ 3: Контекст темы (15 мин)

**Файл:** `contexts/ThemeContext.tsx` (новый)

```tsx
'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

type Theme = 'light' | 'dark' | 'system'

interface ThemeContextType {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>('system')
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    // Загружаем сохранённую тему
    const saved = localStorage.getItem('theme') as Theme | null
    if (saved) {
      setThemeState(saved)
    }
  }, [])

  useEffect(() => {
    const root = document.documentElement
    
    const applyTheme = (isDark: boolean) => {
      if (isDark) {
        root.classList.add('dark')
        setResolvedTheme('dark')
      } else {
        root.classList.remove('dark')
        setResolvedTheme('light')
      }
    }

    if (theme === 'system') {
      const media = window.matchMedia('(prefers-color-scheme: dark)')
      applyTheme(media.matches)
      
      const listener = (e: MediaQueryListEvent) => applyTheme(e.matches)
      media.addEventListener('change', listener)
      return () => media.removeEventListener('change', listener)
    } else {
      applyTheme(theme === 'dark')
    }
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme)
    localStorage.setItem('theme', newTheme)
  }

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

---

### ШАГ 4: Кнопка переключения (10 мин)

**Файл:** `components/ui/ThemeToggle.tsx` (новый)

```tsx
'use client'

import { useTheme } from '@/contexts/ThemeContext'

interface ThemeToggleProps {
  className?: string
}

export function ThemeToggle({ className = '' }: ThemeToggleProps) {
  const { resolvedTheme, setTheme, theme } = useTheme()
  
  const toggle = () => {
    // Если system — переключаем на противоположную от текущей
    // Если уже выбрана тема — переключаем между light/dark
    if (theme === 'system') {
      setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
    } else {
      setTheme(theme === 'dark' ? 'light' : 'dark')
    }
  }

  return (
    <button
      onClick={toggle}
      className={`p-2 rounded-xl transition-all duration-300 
        bg-[var(--bg-secondary)] hover:bg-[var(--border)]
        ${className}`}
      aria-label={resolvedTheme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему'}
    >
      {resolvedTheme === 'dark' ? (
        <span className="text-xl">☀️</span>
      ) : (
        <span className="text-xl">🌙</span>
      )}
    </button>
  )
}
```

---

### ШАГ 5: Обернуть приложение (5 мин)

**Файл:** `app/layout.tsx`

```diff
+ import { ThemeProvider } from '@/contexts/ThemeContext'

export default function RootLayout({ children }) {
  return (
-   <html lang="ru">
+   <html lang="ru" suppressHydrationWarning>
      <body>
+       <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
+       </ThemeProvider>
      </body>
    </html>
  )
}
```

---

### ШАГ 6: Добавить ThemeToggle в Header (10 мин)

**Файл:** `components/library/Header.tsx`

Добавить кнопку в навигацию (десктоп и мобилка).

---

### ШАГ 7: Обновить компоненты (2-2.5 часа)

Пройтись по каждому компоненту и добавить `dark:` классы.

**Пример трансформации:**

```diff
- <div className="bg-white/90 text-[#5D4E3A] border-[#E8D4BA]">
+ <div className="bg-white/90 dark:bg-[#1E1E1E] text-[#5D4E3A] dark:text-[#B0B0B0] border-[#E8D4BA] dark:border-[#3D3D3D]">
```

**Порядок файлов:**

1. `components/library/Header.tsx`
2. `components/library/MaterialCard.tsx`
3. `components/library/CategoryFilter.tsx`
4. `components/library/WelcomeCard.tsx`
5. `components/library/SearchBar.tsx`
6. `components/library/Pagination.tsx`
7. `components/profile/ProfileCard.tsx`
8. `components/profile/SubscriptionCard.tsx`
9. `components/shared/Avatar.tsx`
10. `components/shared/LoadingSpinner.tsx`
11. `app/library/page.tsx`
12. `app/profile/page.tsx`
13. `app/favorites/page.tsx`
14. `app/history/page.tsx`
15. `app/login/page.tsx`
16. `app/admin/page.tsx`
17. Остальные компоненты...

---

### ШАГ 8: PWA и meta теги (10 мин)

**Файл:** `app/layout.tsx` — добавить meta для темы:

```tsx
<meta name="theme-color" content="#FDFCFA" media="(prefers-color-scheme: light)" />
<meta name="theme-color" content="#121212" media="(prefers-color-scheme: dark)" />
```

---

## ✅ Чеклист

### Инфраструктура
- [ ] `tailwind.config.ts` — добавить `darkMode: 'class'`
- [ ] `globals.css` — CSS переменные
- [ ] `ThemeContext.tsx` — создать
- [ ] `ThemeToggle.tsx` — создать
- [ ] `layout.tsx` — ThemeProvider

### Компоненты
- [ ] Header.tsx
- [ ] MaterialCard.tsx
- [ ] CategoryFilter.tsx
- [ ] WelcomeCard.tsx
- [ ] SearchBar.tsx
- [ ] Pagination.tsx
- [ ] ProfileCard.tsx
- [ ] SubscriptionCard.tsx
- [ ] Avatar.tsx
- [ ] LoadingSpinner.tsx
- [ ] MobileNav.tsx (если есть)

### Страницы
- [ ] library/page.tsx
- [ ] profile/page.tsx
- [ ] favorites/page.tsx
- [ ] history/page.tsx
- [ ] login/page.tsx
- [ ] admin/page.tsx

### Финализация
- [ ] Тест на десктопе
- [ ] Тест на мобилке
- [ ] Тест PWA
- [ ] Переключение работает
- [ ] Сохранение в localStorage
- [ ] Автоопределение системной темы

---

## 🚀 Готово к реализации

**Бэкап есть:** `library_frontend_20251214_223826.tar.gz`  
**Путь:** `/root/backups/`

Можно начинать! 🎉

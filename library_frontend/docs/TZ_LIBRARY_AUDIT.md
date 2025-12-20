# ТЗ: Полный аудит библиотеки Mom's Club

## 📋 Общая информация

**Проект:** Mom's Club Library  
**Компоненты:** `library_frontend` (Next.js) + `library_backend` (FastAPI)  
**Дата создания ТЗ:** 2024-12-20  
**Цель:** Полный аудит кода на ошибки, уязвимости, производительность и качество

---

## 🏗 Архитектура проекта

### Frontend (`library_frontend/`)
- **Фреймворк:** Next.js 14 (App Router)
- **Язык:** TypeScript
- **Стили:** Tailwind CSS
- **Состояние:** React Context (ThemeContext, AuthContext)
- **API:** Axios

### Backend (`library_backend/`)
- **Фреймворк:** FastAPI
- **Язык:** Python 3.11+
- **БД:** SQLite (SQLAlchemy ORM)
- **Аутентификация:** JWT (Telegram Web App)

---

## 📁 Структура файлов для аудита

### Frontend (library_frontend/)

```
app/
├── layout.tsx              # Root layout
├── page.tsx                # Landing page
├── globals.css             # Global styles
├── not-found.tsx           # 404 page
├── admin/page.tsx          # Admin panel (~800 строк)
├── library/page.tsx        # Main library page (~370 строк)
├── favorites/page.tsx      # Favorites page
├── history/page.tsx        # History page
├── profile/page.tsx        # User profile
├── login/page.tsx          # Auth page
├── payment/success/page.tsx
├── terms/page.tsx
└── privacy/page.tsx

components/
├── library/
│   ├── Header.tsx          # Main header with nav
│   ├── MobileNav.tsx       # Mobile bottom navigation
│   ├── MaterialCard.tsx    # Material card component
│   ├── FeaturedSection.tsx # Featured materials carousel
│   ├── CategoryFilter.tsx  # Category filter
│   ├── SearchBar.tsx       # Search component
│   ├── QuoteOfDay.tsx      # Daily quote
│   ├── WelcomeCard.tsx     # Welcome card
│   ├── PushPromoModal.tsx  # Push notification promo
│   └── SubscriptionCard.tsx
├── admin/
│   ├── StatsTab.tsx        # Statistics tab (~430 строк)
│   ├── MaterialsTab.tsx    # Materials management
│   ├── CategoriesTab.tsx   # Categories management
│   ├── UsersTab.tsx        # Users management
│   ├── HistoryTab.tsx      # Activity history
│   ├── BotStatsTab.tsx     # Bot statistics
│   ├── MaterialFormModal.tsx (~500 строк)
│   ├── CategoryFormModal.tsx
│   └── UserDetailsModal.tsx
├── profile/
│   ├── MobileNav.tsx
│   ├── LoyaltyCard.tsx
│   ├── ReferralCard.tsx
│   ├── PaymentHistoryCard.tsx
│   ├── SettingsCard.tsx
│   └── PaymentModal.tsx
├── shared/
│   ├── LoadingSpinner.tsx
│   ├── EmptyState.tsx
│   ├── Badge.tsx
│   ├── Avatar.tsx
│   └── SubscriptionGuard.tsx
└── ui/
    └── ThemeToggle.tsx

hooks/
├── useLibraryData.ts       # Main data hook (~340 строк)
├── useAdminData.ts         # Admin data hook
├── useAuth.ts              # Authentication
├── useFavorites.ts         # Favorites management
├── useMaterials.ts         # Materials loading
├── useCategories.ts        # Categories
├── useNotifications.ts     # Notifications
├── usePushNotifications.ts # Push notifications
├── usePresence.ts          # WebSocket presence
└── useScrollVisibility.ts  # Scroll visibility

contexts/
├── ThemeContext.tsx        # Dark/light theme
└── AuthContext.tsx         # Authentication context

lib/
├── api.ts                  # Axios instance
├── types.ts                # TypeScript types
├── constants.ts            # App constants
├── quotes.ts               # Daily quotes
└── utils.ts                # Utility functions
```

### Backend (library_backend/)

```
app/
├── __init__.py
├── config.py               # Configuration
├── database.py             # DB connection
├── api/
│   ├── __init__.py
│   ├── main.py             # FastAPI app
│   ├── auth.py             # Authentication endpoints
│   ├── materials.py        # Materials CRUD (~650 строк)
│   ├── categories.py       # Categories CRUD
│   ├── favorites.py        # Favorites endpoints
│   ├── admin.py            # Admin endpoints (~500 строк)
│   ├── activity.py         # Activity logging
│   ├── push.py             # Push notifications
│   ├── subscription_push.py
│   ├── websocket.py        # WebSocket presence
│   ├── dependencies.py     # FastAPI dependencies
│   └── material_service.py # Business logic
├── models/
│   ├── __init__.py
│   └── library_models.py   # SQLAlchemy models
├── schemas/
│   ├── __init__.py
│   ├── library.py          # Pydantic schemas
│   ├── auth.py
│   └── user_schemas.py
├── services/
│   ├── __init__.py
│   ├── admin_service.py    # Admin business logic
│   ├── material_service.py # Material operations
│   ├── recommendation_service.py # AI recommendations
│   └── notification_service.py
└── utils/
    ├── __init__.py
    ├── auth.py             # JWT utilities
    └── cache.py            # Caching

migrations/
├── 001_create_library_tables.sql
├── add_admin_activity_log.py
└── add_materials_categories.py
```

---

## 🔍 Чеклист аудита

### 1. TypeScript / JavaScript (Frontend)

#### 1.1 Типизация
- [ ] Все компоненты имеют proper типы props
- [ ] Нет использования `any` без необходимости
- [ ] Все API responses типизированы
- [ ] Все хуки возвращают типизированные значения
- [ ] Нет `@ts-ignore` без комментария причины

#### 1.2 React Best Practices
- [ ] Нет утечек памяти (cleanup в useEffect)
- [ ] Правильное использование useMemo/useCallback
- [ ] Нет лишних ререндеров
- [ ] Keys в списках уникальны и стабильны
- [ ] Нет прямой мутации state

#### 1.3 Обработка ошибок
- [ ] Все API вызовы в try/catch
- [ ] Error boundaries для критичных компонентов
- [ ] Пользователю показываются понятные ошибки
- [ ] Логирование ошибок в консоль

#### 1.4 Безопасность
- [ ] Нет XSS уязвимостей (dangerouslySetInnerHTML)
- [ ] Токены хранятся безопасно
- [ ] Нет sensitive data в localStorage (кроме токена)
- [ ] CSRF защита

### 2. Python (Backend)

#### 2.1 Код качество
- [ ] Type hints везде
- [ ] Docstrings для функций
- [ ] Нет дублирования кода
- [ ] Правильное использование async/await
- [ ] Нет blocking calls в async функциях

#### 2.2 Безопасность
- [ ] SQL injection защита (параметризованные запросы)
- [ ] Валидация входных данных (Pydantic)
- [ ] Rate limiting на эндпоинтах
- [ ] Проверка прав доступа (is_admin)
- [ ] Нет hardcoded secrets

#### 2.3 База данных
- [ ] Индексы на часто запрашиваемых полях
- [ ] Нет N+1 queries
- [ ] Транзакции где нужно
- [ ] Миграции обратимы

#### 2.4 API Design
- [ ] RESTful endpoints
- [ ] Правильные HTTP статусы
- [ ] Pagination на списках
- [ ] Консистентный формат ответов

### 3. Производительность

#### 3.1 Frontend
- [ ] Lazy loading для тяжёлых компонентов
- [ ] Оптимизация изображений
- [ ] Минимизация bundle size
- [ ] Кэширование API запросов
- [ ] Debounce на поиске

#### 3.2 Backend
- [ ] Кэширование частых запросов (Redis)
- [ ] Оптимизированные SQL запросы
- [ ] Connection pooling
- [ ] Gzip compression

### 4. UI/UX

#### 4.1 Dark Theme
- [ ] Все элементы имеют dark: варианты
- [ ] Нет "вспышек" при переключении темы
- [ ] Контрастность текста достаточна
- [ ] Иконки адаптированы под тему

#### 4.2 Responsive
- [ ] Mobile-first подход
- [ ] Breakpoints консистентны
- [ ] Touch targets достаточного размера (44px)
- [ ] Нет горизонтального скролла

#### 4.3 Accessibility
- [ ] Семантический HTML
- [ ] ARIA labels где нужно
- [ ] Keyboard navigation
- [ ] Focus states видны

---

## 🐛 Известные проблемы для проверки

1. **Пагинация материалов** — загружается 30 из 73, нужен infinite scroll
2. **WebSocket reconnect** — проверить переподключение при потере связи
3. **Push notifications** — проверить работу на iOS Safari
4. **Admin panel** — большой файл (~800 строк), возможно нужен рефакторинг
5. **Image optimization** — обложки материалов могут быть тяжёлыми

---

## 📊 Метрики качества

После аудита ожидаем:
- **0 критических ошибок**
- **TypeScript strict mode** без ошибок
- **ESLint** без warnings
- **Lighthouse score** > 90
- **Python type checking** (mypy) без ошибок

---

## 🚀 Порядок аудита

1. **Фаза 1: Статический анализ**
   - ESLint + TypeScript strict
   - Pylint + mypy
   - Security audit (npm audit, safety)

2. **Фаза 2: Code Review**
   - Проверка архитектуры
   - Проверка бизнес-логики
   - Проверка edge cases

3. **Фаза 3: Тестирование**
   - Unit tests coverage
   - Integration tests
   - E2E tests (Playwright)

4. **Фаза 4: Отчёт**
   - Список найденных проблем
   - Приоритизация (critical/high/medium/low)
   - Рекомендации по исправлению

---

## 📝 Формат отчёта

Для каждой найденной проблемы:

```markdown
### [SEVERITY] Название проблемы

**Файл:** `path/to/file.tsx:123`
**Тип:** Bug / Security / Performance / Code Quality
**Описание:** Что не так
**Риск:** Что может случиться
**Решение:** Как исправить
**Код до:**
```code
// проблемный код
```
**Код после:**
```code
// исправленный код
```
```

---

## ✅ Критерии завершения

Аудит считается завершённым когда:
1. Все файлы проверены по чеклисту
2. Все критические и высокие проблемы задокументированы
3. Предложены решения для каждой проблемы
4. Создан план исправления с приоритетами

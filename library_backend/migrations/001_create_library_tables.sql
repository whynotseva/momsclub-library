-- ============================================
-- МИГРАЦИЯ: Создание таблиц для LibriMomsClub
-- Дата: 30 ноября 2025
-- Версия: 1.0
-- ============================================

-- 1. Таблица категорий
CREATE TABLE IF NOT EXISTS library_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,  -- emoji иконка
    position INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Таблица тегов
CREATE TABLE IF NOT EXISTS library_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    category TEXT,  -- 'format', 'niche', 'topic', 'trend'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Таблица материалов (основная)
CREATE TABLE IF NOT EXISTS library_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    content TEXT,  -- Markdown или HTML
    category_id INTEGER NOT NULL,
    
    -- Поля для блогинга
    format TEXT NOT NULL,  -- 'reels', 'post', 'story', 'guide', 'podcast', 'challenge', 'template'
    level TEXT,  -- 'beginner', 'intermediate', 'advanced'
    duration INTEGER,  -- минуты на изучение
    topic TEXT,  -- 'expertise', 'storytelling', 'lifestyle', 'selling', 'personal_brand'
    niche TEXT,  -- 'motherhood', 'beauty', 'business', 'lifestyle', 'psychology'
    viral_score INTEGER,  -- 1-10 (для Reels)
    
    -- Мета-данные
    author TEXT,
    cover_image TEXT,
    is_published BOOLEAN DEFAULT 1,
    is_featured BOOLEAN DEFAULT 0,  -- "Выбор Полины"
    
    -- Даты
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Статистика
    views INTEGER DEFAULT 0,
    
    FOREIGN KEY (category_id) REFERENCES library_categories(id)
);

-- 4. Связь материалов и тегов (many-to-many)
CREATE TABLE IF NOT EXISTS materials_tags (
    material_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (material_id, tag_id),
    FOREIGN KEY (material_id) REFERENCES library_materials(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES library_tags(id) ON DELETE CASCADE
);

-- 5. Таблица вложений (файлы, видео, PDF)
CREATE TABLE IF NOT EXISTS library_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- 'pdf', 'video', 'image', 'link', 'audio'
    url TEXT NOT NULL,
    title TEXT,
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES library_materials(id) ON DELETE CASCADE
);

-- 6. Таблица избранного
CREATE TABLE IF NOT EXISTS library_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, material_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES library_materials(id) ON DELETE CASCADE
);

-- 7. Таблица просмотров (история + аналитика)
CREATE TABLE IF NOT EXISTS library_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER,
    FOREIGN KEY (material_id) REFERENCES library_materials(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- ИНДЕКСЫ для оптимизации запросов
-- ============================================

CREATE INDEX IF NOT EXISTS idx_materials_category ON library_materials(category_id);
CREATE INDEX IF NOT EXISTS idx_materials_format ON library_materials(format);
CREATE INDEX IF NOT EXISTS idx_materials_published ON library_materials(is_published);
CREATE INDEX IF NOT EXISTS idx_materials_featured ON library_materials(is_featured);
CREATE INDEX IF NOT EXISTS idx_materials_created ON library_materials(created_at);

CREATE INDEX IF NOT EXISTS idx_views_material ON library_views(material_id);
CREATE INDEX IF NOT EXISTS idx_views_user ON library_views(user_id);
CREATE INDEX IF NOT EXISTS idx_views_date ON library_views(viewed_at);

CREATE INDEX IF NOT EXISTS idx_favorites_user ON library_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_material ON library_favorites(material_id);

CREATE INDEX IF NOT EXISTS idx_attachments_material ON library_attachments(material_id);

-- ============================================
-- НАЧАЛЬНЫЕ ДАННЫЕ: Категории
-- ============================================

INSERT OR IGNORE INTO library_categories (name, slug, description, icon, position) VALUES
('Reels — тренды и идеи', 'reels', 'Вирусные Reels недели, идеи под тренды, готовые форматы', '🎬', 1),
('Идеи для контента', 'content-ideas', 'Идеи для сторис, постов, вдохновляющие подборки', '💡', 2),
('Блогинг', 'blogging', 'Сценарии прогревов, продающие сторис, аналитика', '📱', 3),
('Личный бренд', 'personal-brand', 'Упаковка профиля, УТП, ниша, визуал', '✨', 4),
('Марафоны и задания', 'challenges', 'Контент-марафоны, челленджи, ежедневные задания', '🏆', 5),
('Подкасты и разборы', 'podcasts', 'Разборы блогов, ответы на вопросы, лекции', '🎙️', 6),
('Бренды и сотрудничества', 'brands', 'Бренды для коллабораций, как писать брендам', '🤝', 7);

-- ============================================
-- НАЧАЛЬНЫЕ ДАННЫЕ: Теги
-- ============================================

-- Форматы
INSERT OR IGNORE INTO library_tags (name, slug, category) VALUES
('Reels', 'reels', 'format'),
('Пост', 'post', 'format'),
('Сторис', 'story', 'format'),
('Гайд', 'guide', 'format'),
('Подкаст', 'podcast', 'format'),
('Челлендж', 'challenge', 'format'),
('Шаблон', 'template', 'format');

-- Ниши
INSERT OR IGNORE INTO library_tags (name, slug, category) VALUES
('Материнство', 'motherhood', 'niche'),
('Красота', 'beauty', 'niche'),
('Бизнес', 'business', 'niche'),
('Лайфстайл', 'lifestyle', 'niche'),
('Психология', 'psychology', 'niche'),
('Здоровье', 'health', 'niche'),
('Саморазвитие', 'self-development', 'niche');

-- Темы
INSERT OR IGNORE INTO library_tags (name, slug, category) VALUES
('Экспертность', 'expertise', 'topic'),
('Сторителлинг', 'storytelling', 'topic'),
('Продажи', 'selling', 'topic'),
('Личный бренд', 'personal-brand', 'topic'),
('Вовлечение', 'engagement', 'topic');

-- Тренды
INSERT OR IGNORE INTO library_tags (name, slug, category) VALUES
('Тренд 2025', 'trend-2025', 'trend'),
('Вирусный звук', 'viral-sound', 'trend'),
('Популярный формат', 'popular-format', 'trend');

-- ============================================
-- КОНЕЦ МИГРАЦИИ
-- ============================================

"""
SQLAlchemy модели для LibriMomsClub
Таблицы библиотеки материалов
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    ForeignKey, DateTime, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

# Импортируем Base из моделей бота (если они используют SQLAlchemy)
# Если нет - создаём свой Base
try:
    from database.models import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


# ============================================
# ТАБЛИЦА СВЯЗИ: materials_tags (many-to-many)
# ============================================

materials_tags = Table(
    'materials_tags',
    Base.metadata,
    Column('material_id', Integer, ForeignKey('library_materials.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('library_tags.id', ondelete='CASCADE'), primary_key=True)
)

# ============================================
# ТАБЛИЦА СВЯЗИ: materials_categories (many-to-many)
# ============================================

materials_categories = Table(
    'materials_categories',
    Base.metadata,
    Column('material_id', Integer, ForeignKey('library_materials.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('library_categories.id', ondelete='CASCADE'), primary_key=True)
)


# ============================================
# МОДЕЛЬ: Категория
# ============================================

class LibraryCategory(Base):
    __tablename__ = 'library_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String)  # emoji
    position = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    materials = relationship('LibraryMaterial', secondary='materials_categories', back_populates='categories')
    
    def __repr__(self):
        return f"<LibraryCategory(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'materials_count': len(self.materials) if self.materials else 0
        }


# ============================================
# МОДЕЛЬ: Тег
# ============================================

class LibraryTag(Base):
    __tablename__ = 'library_tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
    category = Column(String)  # 'format', 'niche', 'topic', 'trend'
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    materials = relationship('LibraryMaterial', secondary=materials_tags, back_populates='tags')
    
    def __repr__(self):
        return f"<LibraryTag(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================
# МОДЕЛЬ: Материал (основная)
# ============================================

class LibraryMaterial(Base):
    __tablename__ = 'library_materials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)  # Markdown или HTML
    external_url = Column(String)  # Ссылка на Notion/Telegram/YouTube
    category_id = Column(Integer, ForeignKey('library_categories.id'), nullable=True)  # Deprecated, используем categories
    
    # Поля для блогинга
    format = Column(String, nullable=False)  # 'reels', 'post', 'story', 'guide', 'podcast', 'challenge', 'template'
    level = Column(String)  # 'beginner', 'intermediate', 'advanced'
    duration = Column(Integer)  # минуты
    topic = Column(String)  # 'expertise', 'storytelling', 'lifestyle', 'selling', 'personal_brand'
    niche = Column(String)  # 'motherhood', 'beauty', 'business', 'lifestyle', 'psychology'
    viral_score = Column(Integer)  # 1-10
    
    # Мета-данные
    author = Column(String)
    cover_image = Column(String)
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # "Выбор Полины"
    
    # Даты
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Статистика
    views = Column(Integer, default=0)
    
    # Relationships
    category = relationship('LibraryCategory', foreign_keys=[category_id])  # Deprecated
    categories = relationship('LibraryCategory', secondary=materials_categories, back_populates='materials')
    tags = relationship('LibraryTag', secondary=materials_tags, back_populates='materials')
    attachments = relationship('LibraryAttachment', back_populates='material', cascade='all, delete-orphan')
    favorites = relationship('LibraryFavorite', back_populates='material', cascade='all, delete-orphan')
    view_records = relationship('LibraryView', back_populates='material', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<LibraryMaterial(id={self.id}, title='{self.title}', format='{self.format}')>"
    
    def to_dict(self, include_content=False):
        # Новое: массив категорий
        categories_list = [cat.to_dict() for cat in self.categories] if self.categories else []
        
        # Обратная совместимость: category_id берём из первой категории или старого поля
        first_category_id = categories_list[0]['id'] if categories_list else self.category_id
        first_category = categories_list[0] if categories_list else (self.category.to_dict() if self.category else None)
        
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'external_url': self.external_url,
            'category_id': first_category_id,  # Deprecated, для обратной совместимости
            'category': first_category,  # Deprecated, для обратной совместимости
            'category_ids': [cat['id'] for cat in categories_list],  # Новое: массив ID
            'categories': categories_list,  # Новое: массив категорий
            'format': self.format,
            'level': self.level,
            'duration': self.duration,
            'topic': self.topic,
            'niche': self.niche,
            'viral_score': self.viral_score,
            'author': self.author,
            'cover_image': self.cover_image,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'views': self.views,
            'tags': [tag.to_dict() for tag in self.tags] if self.tags else [],
            'attachments': [att.to_dict() for att in self.attachments] if self.attachments else [],
            'favorites_count': len(self.favorites) if self.favorites else 0
        }
        
        if include_content:
            data['content'] = self.content
        
        return data


# ============================================
# МОДЕЛЬ: Вложение
# ============================================

class LibraryAttachment(Base):
    __tablename__ = 'library_attachments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey('library_materials.id', ondelete='CASCADE'), nullable=False)
    type = Column(String, nullable=False)  # 'pdf', 'video', 'image', 'link', 'audio'
    url = Column(String, nullable=False)
    title = Column(String)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    material = relationship('LibraryMaterial', back_populates='attachments')
    
    def __repr__(self):
        return f"<LibraryAttachment(id={self.id}, type='{self.type}', material_id={self.material_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'type': self.type,
            'url': self.url,
            'title': self.title,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================
# МОДЕЛЬ: Избранное
# ============================================

class LibraryFavorite(Base):
    __tablename__ = 'library_favorites'
    __table_args__ = (UniqueConstraint('user_id', 'material_id', name='uq_user_material'),)
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # ID пользователя из таблицы users
    material_id = Column(Integer, ForeignKey('library_materials.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    material = relationship('LibraryMaterial', back_populates='favorites')
    
    def __repr__(self):
        return f"<LibraryFavorite(user_id={self.user_id}, material_id={self.material_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'material_id': self.material_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'material': self.material.to_dict() if self.material else None
        }


# ============================================
# МОДЕЛЬ: Просмотр
# ============================================

class LibraryView(Base):
    __tablename__ = 'library_views'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(Integer, ForeignKey('library_materials.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, nullable=False)  # ID пользователя из таблицы users
    viewed_at = Column(DateTime, default=func.now())
    duration_seconds = Column(Integer)
    
    # Relationships
    material = relationship('LibraryMaterial', back_populates='view_records')
    
    def __repr__(self):
        return f"<LibraryView(user_id={self.user_id}, material_id={self.material_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'user_id': self.user_id,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'duration_seconds': self.duration_seconds
        }


# ============================================
# МОДЕЛЬ: Лог активности админов
# ============================================

class AdminActivityLog(Base):
    """Логирование действий админов в библиотеке"""
    __tablename__ = 'admin_activity_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, nullable=False)  # telegram_id админа
    admin_name = Column(String, nullable=False)  # имя для отображения
    action = Column(String, nullable=False)  # 'create', 'edit', 'delete', 'publish', 'unpublish'
    entity_type = Column(String, nullable=False)  # 'material', 'category', 'tag'
    entity_id = Column(Integer)  # ID сущности
    entity_title = Column(String)  # название для отображения
    details = Column(Text)  # дополнительные детали (JSON)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<AdminActivityLog(admin={self.admin_name}, action={self.action}, entity={self.entity_title})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_name': self.admin_name,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_title': self.entity_title,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

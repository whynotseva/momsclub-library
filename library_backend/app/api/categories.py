"""
API endpoints для категорий и тегов
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.schemas import Category, Tag
from app.models.library_models import LibraryCategory, LibraryTag
from app.api.dependencies import get_current_user_with_subscription


router = APIRouter(tags=["Категории и теги"])


@router.get("/categories", response_model=List[Category])
def get_categories(
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Получить список всех категорий
    
    Требуется активная подписка
    """
    categories = db.execute(
        select(LibraryCategory).order_by(LibraryCategory.position)
    ).scalars().all()
    
    return [Category.model_validate(c) for c in categories]


@router.get("/categories/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Получить информацию о категории
    
    Требуется активная подписка
    """
    category = db.execute(
        select(LibraryCategory).where(LibraryCategory.id == category_id)
    ).scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    
    return Category.model_validate(category)


@router.get("/tags", response_model=List[Tag])
def get_tags(
    category: str = None,
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Получить список всех тегов
    
    Опционально можно фильтровать по категории тега (format, niche, topic, trend)
    
    Требуется активная подписка
    """
    query = select(LibraryTag)
    
    if category:
        query = query.where(LibraryTag.category == category)
    
    tags = db.execute(query.order_by(LibraryTag.name)).scalars().all()
    
    return [Tag.model_validate(t) for t in tags]

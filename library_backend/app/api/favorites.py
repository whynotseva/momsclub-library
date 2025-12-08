"""
API endpoints для избранного и истории просмотров
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, text

from app.database import get_db
from app.schemas import Favorite, MaterialListItem
from app.models.library_models import LibraryFavorite, LibraryView, LibraryMaterial
from app.api.dependencies import get_current_user_with_subscription


router = APIRouter(tags=["Избранное и история"])


# ============================================
# ИЗБРАННОЕ
# ============================================

@router.get("/favorites", response_model=List[MaterialListItem])
def get_favorites(
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Получить список избранных материалов пользователя
    
    Требуется активная подписка
    """
    favorites = db.execute(
        select(LibraryFavorite)
        .where(LibraryFavorite.user_id == current_user["user_id"])
        .order_by(desc(LibraryFavorite.created_at))
    ).scalars().all()
    
    materials = [fav.material for fav in favorites if fav.material and fav.material.is_published]
    
    return [MaterialListItem.model_validate(m) for m in materials]


@router.post("/favorites/{material_id}")
def add_to_favorites(
    material_id: int,
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Добавить материал в избранное
    
    Требуется активная подписка
    """
    # Проверяем, что материал существует
    material = db.execute(
        select(LibraryMaterial).where(LibraryMaterial.id == material_id)
    ).scalar_one_or_none()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Материал не найден"
        )
    
    # Проверяем, не добавлен ли уже
    existing = db.execute(
        select(LibraryFavorite).where(
            LibraryFavorite.user_id == current_user["user_id"],
            LibraryFavorite.material_id == material_id
        )
    ).scalar_one_or_none()
    
    if existing:
        return {"status": "ok", "message": "Материал уже в избранном"}
    
    # Добавляем в избранное
    favorite = LibraryFavorite(
        user_id=current_user["user_id"],
        material_id=material_id
    )
    db.add(favorite)
    
    # Логируем действие
    db.execute(
        text("INSERT INTO activity_log (user_id, action_type, material_id) VALUES (:user_id, 'favorite_add', :material_id)"),
        {"user_id": current_user["user_id"], "material_id": material_id}
    )
    
    db.commit()
    
    return {"status": "ok", "message": "Материал добавлен в избранное"}


@router.delete("/favorites/{material_id}")
def remove_from_favorites(
    material_id: int,
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Удалить материал из избранного
    
    Требуется активная подписка
    """
    favorite = db.execute(
        select(LibraryFavorite).where(
            LibraryFavorite.user_id == current_user["user_id"],
            LibraryFavorite.material_id == material_id
        )
    ).scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Материал не найден в избранном"
        )
    
    db.delete(favorite)
    
    # Логируем удаление
    db.execute(
        text("INSERT INTO activity_log (user_id, action_type, material_id) VALUES (:user_id, 'favorite_remove', :material_id)"),
        {"user_id": current_user["user_id"], "material_id": material_id}
    )
    
    db.commit()
    
    return {"status": "ok", "message": "Материал удалён из избранного"}


@router.get("/favorites/check/{material_id}")
def check_favorite(
    material_id: int,
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Проверить, находится ли материал в избранном
    
    Требуется активная подписка
    """
    favorite = db.execute(
        select(LibraryFavorite).where(
            LibraryFavorite.user_id == current_user["user_id"],
            LibraryFavorite.material_id == material_id
        )
    ).scalar_one_or_none()
    
    return {"is_favorite": favorite is not None}


# ============================================
# ИСТОРИЯ ПРОСМОТРОВ
# ============================================

@router.get("/history", response_model=List[MaterialListItem])
def get_history(
    limit: int = Query(50, ge=1, le=100, description="Количество материалов"),
    current_user: dict = Depends(get_current_user_with_subscription),
    db: Session = Depends(get_db)
):
    """
    Получить историю просмотров пользователя
    
    Требуется активная подписка
    """
    # Получаем последние просмотры (уникальные материалы)
    views = db.execute(
        select(LibraryView)
        .where(LibraryView.user_id == current_user["user_id"])
        .order_by(desc(LibraryView.viewed_at))
        .limit(limit)
    ).scalars().all()
    
    # Получаем уникальные материалы (сохраняя порядок)
    seen_ids = set()
    materials = []
    for view in views:
        if view.material_id not in seen_ids and view.material and view.material.is_published:
            seen_ids.add(view.material_id)
            materials.append(view.material)
    
    return [MaterialListItem.model_validate(m) for m in materials]

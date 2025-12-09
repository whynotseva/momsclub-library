"""
API endpoints для админ-панели библиотеки
Доступ только для указанных telegram_id
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.library_models import (
    LibraryCategory, LibraryMaterial, LibraryTag, 
    LibraryAttachment, materials_tags
)
from app.schemas.library import (
    MaterialCreate, MaterialUpdate, Material, MaterialListItem,
    CategoryCreate, Category,
    TagCreate, Tag
)
from app.services import AdminService, is_admin, ADMIN_IDS

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: dict = Depends(get_current_user)):
    """Проверка что пользователь — админ"""
    if not is_admin(current_user.get("telegram_id")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён. Только для администраторов."
        )
    return current_user


# ==================== СТАТИСТИКА ====================

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Получить статистику библиотеки"""
    service = AdminService(db)
    return service.get_stats()


# ==================== МАТЕРИАЛЫ ====================

@router.get("/materials", response_model=List[MaterialListItem])
def get_all_materials(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin),
    page: int = 1,
    limit: int = 20,
    category_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    search: Optional[str] = None
):
    """Получить все материалы (включая черновики)"""
    service = AdminService(db)
    return service.get_materials_list(page, limit, category_id, is_published, search)


@router.post("/materials", response_model=Material)
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Создать новый материал"""
    
    # Создаём материал
    db_material = LibraryMaterial(
        title=material.title,
        description=material.description,
        content=material.content,
        external_url=material.external_url,
        cover_image=material.cover_image,
        category_id=material.category_id,
        format=material.format,
        level=material.level,
        duration=material.duration,
        topic=material.topic,
        niche=material.niche,
        viral_score=material.viral_score,
        is_published=material.is_published,
        is_featured=material.is_featured,
        author=material.author
    )
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    # Добавляем теги если есть
    if material.tag_ids:
        for tag_id in material.tag_ids:
            db.execute(
                materials_tags.insert().values(
                    material_id=db_material.id,
                    tag_id=tag_id
                )
            )
        db.commit()
    
    return db_material


@router.get("/materials/{material_id}", response_model=Material)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Получить материал по ID"""
    
    result = db.execute(
        select(LibraryMaterial).where(LibraryMaterial.id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    return material


@router.put("/materials/{material_id}", response_model=Material)
def update_material(
    material_id: int,
    material: MaterialUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Обновить материал"""
    
    result = db.execute(
        select(LibraryMaterial).where(LibraryMaterial.id == material_id)
    )
    db_material = result.scalar_one_or_none()
    
    if not db_material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    # Обновляем поля
    update_data = material.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "tag_ids":
            setattr(db_material, field, value)
    
    db_material.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_material)
    
    # Обновляем теги если переданы
    if material.tag_ids is not None:
        # Удаляем старые теги
        db.execute(
            delete(materials_tags).where(materials_tags.c.material_id == material_id)
        )
        # Добавляем новые
        for tag_id in material.tag_ids:
            db.execute(
                materials_tags.insert().values(
                    material_id=material_id,
                    tag_id=tag_id
                )
            )
        db.commit()
    
    return db_material


@router.delete("/materials/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Удалить материал"""
    
    result = db.execute(
        select(LibraryMaterial).where(LibraryMaterial.id == material_id)
    )
    db_material = result.scalar_one_or_none()
    
    if not db_material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    db.delete(db_material)
    db.commit()
    
    return {"message": "Материал удалён", "id": material_id}


@router.post("/materials/{material_id}/publish")
def publish_material(
    material_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Опубликовать материал"""
    
    db.execute(
        update(LibraryMaterial)
        .where(LibraryMaterial.id == material_id)
        .values(is_published=True, published_at=datetime.utcnow())
    )
    db.commit()
    
    return {"message": "Материал опубликован", "id": material_id}


@router.post("/materials/{material_id}/unpublish")
def unpublish_material(
    material_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Снять материал с публикации"""
    
    db.execute(
        update(LibraryMaterial)
        .where(LibraryMaterial.id == material_id)
        .values(is_published=False)
    )
    db.commit()
    
    return {"message": "Материал снят с публикации", "id": material_id}


# ==================== КАТЕГОРИИ ====================

@router.post("/categories", response_model=Category)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Создать категорию"""
    
    db_category = LibraryCategory(
        name=category.name,
        slug=category.slug or generate_slug(category.name),
        description=category.description,
        icon=category.icon,
        position=category.position or 0
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Обновить категорию"""
    
    result = db.execute(
        select(LibraryCategory).where(LibraryCategory.id == category_id)
    )
    db_category = result.scalar_one_or_none()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    db_category.name = category.name
    db_category.slug = category.slug or db_category.slug
    db_category.description = category.description
    db_category.icon = category.icon
    db_category.position = category.position if category.position is not None else db_category.position
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Удалить категорию"""
    
    # Проверяем есть ли материалы в категории
    materials_count = db.scalar(
        select(func.count(LibraryMaterial.id))
        .where(LibraryMaterial.category_id == category_id)
    )
    
    if materials_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Нельзя удалить категорию с материалами ({materials_count} шт.)"
        )
    
    db.execute(
        delete(LibraryCategory).where(LibraryCategory.id == category_id)
    )
    db.commit()
    
    return {"message": "Категория удалена", "id": category_id}


# ==================== ТЕГИ ====================

@router.get("/tags", response_model=List[Tag])
def get_all_tags(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Получить все теги"""
    
    result = db.execute(
        select(LibraryTag).order_by(LibraryTag.name)
    )
    return result.scalars().all()


@router.post("/tags", response_model=Tag)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Создать тег"""
    
    db_tag = LibraryTag(
        name=tag.name,
        slug=tag.slug or generate_slug(tag.name)
    )
    
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    
    return db_tag


@router.delete("/tags/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Удалить тег"""
    
    db.execute(delete(LibraryTag).where(LibraryTag.id == tag_id))
    db.commit()
    
    return {"message": "Тег удалён", "id": tag_id}


# ==================== ЗАГРУЗКА ФАЙЛОВ ====================

UPLOAD_DIR = "uploads"

@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin)
):
    """Загрузить файл (обложка, PDF, видео)"""
    
    # Создаём директорию если нет
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Генерируем уникальное имя
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    
    # Сохраняем файл
    with open(file_path, "wb") as f:
        content = file.read()
        f.write(content)
    
    return {
        "filename": unique_name,
        "original_name": file.filename,
        "url": f"/uploads/{unique_name}",
        "size": len(content)
    }


# ==================== УТИЛИТЫ ====================

def generate_slug(text: str) -> str:
    """Генерация slug из текста"""
    import re
    from transliterate import translit
    
    try:
        # Транслитерация кириллицы
        text = translit(text, 'ru', reversed=True)
    except:
        pass
    
    # Очищаем от спецсимволов
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    
    return slug

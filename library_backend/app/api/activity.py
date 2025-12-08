"""
API для ленты активности
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, desc

from app.database import get_db
from app.api.dependencies import get_current_user
from app.models import AdminActivityLog


router = APIRouter(prefix="/activity", tags=["Активность"])


# ============================================
# HELPER: Логирование админских действий
# ============================================

async def log_admin_action(
    db: Session,
    admin_id: int,
    admin_name: str,
    action: str,
    entity_type: str,
    entity_id: int = None,
    entity_title: str = None,
    details: str = None
):
    """
    Записывает действие админа в лог
    
    action: 'create', 'edit', 'delete', 'publish', 'unpublish'
    entity_type: 'material', 'category', 'tag'
    """
    log_entry = AdminActivityLog(
        admin_id=admin_id,
        admin_name=admin_name,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_title=entity_title,
        details=details
    )
    db.add(log_entry)
    db.commit()
    return log_entry


# ============================================
# ENDPOINT: История действий админов
# ============================================

@router.get("/admin-history")
def get_admin_activity_history(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить историю действий админов в библиотеке
    """
    logs = db.query(AdminActivityLog)\
        .order_by(desc(AdminActivityLog.created_at))\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return [log.to_dict() for log in logs]


@router.get("/recent")
def get_recent_activity(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить последние действия пользователей
    - Просмотры материалов
    - Добавления в избранное
    """
    
    # Получаем последние просмотры
    views = db.execute(
        text("""
        SELECT 
            'view' as action_type,
            v.viewed_at,
            u.telegram_id,
            u.first_name,
            u.username,
            u.photo_url,
            m.title as material_title,
            m.id as material_id,
            c.icon as category_icon
        FROM library_views v
        JOIN users u ON v.user_id = u.id
        JOIN library_materials m ON v.material_id = m.id
        LEFT JOIN library_categories c ON m.category_id = c.id
        ORDER BY v.viewed_at DESC
        LIMIT :limit
        """),
        {"limit": limit}
    ).fetchall()
    
    # Получаем действия из лога (добавление/удаление избранного)
    activity_logs = db.execute(
        text("""
        SELECT 
            a.action_type,
            a.created_at,
            u.telegram_id,
            u.first_name,
            u.username,
            u.photo_url,
            m.title as material_title,
            m.id as material_id,
            c.icon as category_icon
        FROM activity_log a
        JOIN users u ON a.user_id = u.id
        JOIN library_materials m ON a.material_id = m.id
        LEFT JOIN library_categories c ON m.category_id = c.id
        ORDER BY a.created_at DESC
        LIMIT :limit
        """),
        {"limit": limit}
    ).fetchall()
    
    # Объединяем и сортируем
    all_activities = []
    
    for v in views:
        all_activities.append({
            "type": "view",
            "created_at": v[1],
            "user": {
                "telegram_id": v[2],
                "first_name": v[3],
                "username": v[4],
                "photo_url": v[5]
            },
            "material": {
                "id": v[7],
                "title": v[6],
                "icon": v[8] or "📄"
            }
        })
    
    for a in activity_logs:
        all_activities.append({
            "type": a[0],  # favorite_add или favorite_remove
            "created_at": a[1],
            "user": {
                "telegram_id": a[2],
                "first_name": a[3],
                "username": a[4],
                "photo_url": a[5]
            },
            "material": {
                "id": a[7],
                "title": a[6],
                "icon": a[8] or "📄"
            }
        })
    
    # Сортируем по времени
    all_activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    return all_activities[:limit]

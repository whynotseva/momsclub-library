"""
Сервис для персональных рекомендаций материалов.
Использует гибридный подход: collaborative filtering + content-based.
"""

import logging
from typing import Dict, Any, List, Set
from sqlalchemy.orm import Session
from sqlalchemy import text
from collections import defaultdict

from app.services.material_service import add_cover_url

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Сервис персональных рекомендаций.
    
    Алгоритм (гибридный):
    1. Collaborative Filtering — находим пользователей с похожими просмотрами,
       рекомендуем то, что смотрели они, но не смотрел текущий пользователь.
    2. Content-Based — материалы из тех же категорий.
    3. Popularity Fallback — если мало данных, добавляем популярные.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recommendations(self, user_id: int, limit: int = 6) -> Dict[str, Any]:
        """
        Получить персональные рекомендации.
        
        Returns:
            dict с type, title, materials
        """
        # 1. Получаем просмотренные материалы пользователя
        viewed_ids = self._get_user_viewed_materials(user_id)
        
        # Если нет истории — возвращаем популярные
        if not viewed_ids:
            return self._get_popular_recommendations(limit)
        
        recommendations = []
        used_ids: Set[int] = set(viewed_ids)
        
        # 2. Collaborative Filtering — "пользователи с похожими интересами смотрели"
        collab_results = self._get_collaborative_recommendations(user_id, viewed_ids, limit)
        for item in collab_results:
            if item["id"] not in used_ids:
                recommendations.append(item)
                used_ids.add(item["id"])
        
        # 3. Content-Based — материалы из тех же категорий
        if len(recommendations) < limit:
            category_ids = self._get_user_categories(user_id)
            if category_ids:
                content_results = self._get_category_recommendations(
                    category_ids, list(used_ids), limit - len(recommendations)
                )
                for item in content_results:
                    if item["id"] not in used_ids:
                        recommendations.append(item)
                        used_ids.add(item["id"])
        
        # 4. Popularity Fallback
        if len(recommendations) < limit:
            extra = self._get_extra_popular(list(used_ids), limit - len(recommendations))
            for item in extra:
                if item["id"] not in used_ids:
                    recommendations.append(item)
                    used_ids.add(item["id"])
        
        rec_type = "personalized" if collab_results else "category_based"
        title = "Вам понравится" if rec_type == "personalized" else "Похожие материалы"
        
        return {
            "type": rec_type,
            "title": title,
            "materials": recommendations[:limit]
        }
    
    def _get_user_viewed_materials(self, user_id: int) -> List[int]:
        """Получить список ID просмотренных материалов"""
        result = self.db.execute(text("""
            SELECT DISTINCT material_id FROM library_views WHERE user_id = :user_id
        """), {"user_id": user_id}).fetchall()
        return [r[0] for r in result]
    
    def _get_user_categories(self, user_id: int) -> List[int]:
        """Получить категории просмотренных материалов"""
        result = self.db.execute(text("""
            SELECT DISTINCT m.category_id 
            FROM library_views v
            JOIN library_materials m ON m.id = v.material_id
            WHERE v.user_id = :user_id AND m.category_id IS NOT NULL
        """), {"user_id": user_id}).fetchall()
        return [r[0] for r in result]
    
    def _get_collaborative_recommendations(
        self, 
        user_id: int, 
        viewed_ids: List[int], 
        limit: int
    ) -> List[dict]:
        """
        Collaborative Filtering: находим пользователей с похожими просмотрами,
        рекомендуем материалы, которые смотрели они.
        
        Алгоритм:
        1. Находим пользователей, которые смотрели хотя бы 2 тех же материала
        2. Подсчитываем "вес" каждого пользователя (количество общих просмотров)
        3. Собираем материалы этих пользователей, взвешивая по весу
        4. Фильтруем уже просмотренные, сортируем по весу
        """
        if len(viewed_ids) < 2:
            return []
        
        # Берём не больше 20 последних просмотров для производительности
        recent_viewed = viewed_ids[:20] if len(viewed_ids) > 20 else viewed_ids
        
        # Создаём параметры для IN clause
        viewed_params = {f"v{i}": vid for i, vid in enumerate(recent_viewed)}
        viewed_placeholders = ",".join([f":v{i}" for i in range(len(recent_viewed))])
        
        excluded_params = {f"e{i}": vid for i, vid in enumerate(viewed_ids)}
        excluded_placeholders = ",".join([f":e{i}" for i in range(len(viewed_ids))])
        
        # Находим похожих пользователей и их материалы
        query = f"""
            WITH similar_users AS (
                -- Пользователи с общими просмотрами (минимум 2)
                SELECT v.user_id, COUNT(DISTINCT v.material_id) as common_views
                FROM library_views v
                WHERE v.material_id IN ({viewed_placeholders})
                  AND v.user_id != :current_user
                GROUP BY v.user_id
                HAVING COUNT(DISTINCT v.material_id) >= 2
                ORDER BY common_views DESC
                LIMIT 50
            ),
            recommended_materials AS (
                -- Материалы похожих пользователей
                SELECT 
                    lv.material_id,
                    SUM(su.common_views) as score
                FROM library_views lv
                JOIN similar_users su ON lv.user_id = su.user_id
                WHERE lv.material_id NOT IN ({excluded_placeholders})
                GROUP BY lv.material_id
                ORDER BY score DESC
                LIMIT :limit
            )
            SELECT 
                m.id, m.title, m.description, m.cover_image, c.icon,
                m.external_url, m.category_id, c.name as category_name,
                (SELECT COUNT(*) FROM library_views WHERE material_id = m.id) as views_count,
                rm.score
            FROM recommended_materials rm
            JOIN library_materials m ON m.id = rm.material_id
            LEFT JOIN library_categories c ON c.id = m.category_id
            WHERE m.is_published = 1
            ORDER BY rm.score DESC, views_count DESC
            LIMIT :limit
        """
        
        params = {**viewed_params, **excluded_params, "current_user": user_id, "limit": limit}
        
        try:
            results = self.db.execute(text(query), params).fetchall()
            return [self._row_to_dict(r) for r in results]
        except Exception as e:
            logger.warning(f"Collaborative filtering failed: {e}")
            return []
    
    def _get_popular_recommendations(self, limit: int) -> Dict[str, Any]:
        """Получить популярные материалы (fallback)"""
        popular = self.db.execute(text("""
            SELECT m.id, m.title, m.description, m.cover_image, c.icon, 
                   m.external_url, m.category_id, c.name as category_name,
                   (SELECT COUNT(*) FROM library_views WHERE material_id = m.id) as views_count
            FROM library_materials m
            LEFT JOIN library_categories c ON c.id = m.category_id
            WHERE m.is_published = 1
            ORDER BY views_count DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        materials = [self._row_to_dict(r) for r in popular]
        
        return {
            "type": "popular",
            "title": "Популярное",
            "materials": materials
        }
    
    def _get_category_recommendations(
        self, 
        category_ids: List[int], 
        excluded_ids: List[int], 
        limit: int
    ) -> List[dict]:
        """Получить рекомендации из тех же категорий"""
        if not category_ids:
            return []
        
        cat_params = {f"cat{i}": cid for i, cid in enumerate(category_ids)}
        cat_placeholders = ",".join([f":cat{i}" for i in range(len(category_ids))])
        
        exc_params = {f"exc{i}": eid for i, eid in enumerate(excluded_ids)} if excluded_ids else {}
        exc_placeholders = ",".join([f":exc{i}" for i in range(len(excluded_ids))]) if excluded_ids else "0"
        
        params = {**cat_params, **exc_params, "limit": limit}
        
        results = self.db.execute(text(f"""
            SELECT m.id, m.title, m.description, m.cover_image, c.icon, 
                   m.external_url, m.category_id, c.name as category_name,
                   (SELECT COUNT(*) FROM library_views WHERE material_id = m.id) as views_count
            FROM library_materials m
            LEFT JOIN library_categories c ON c.id = m.category_id
            WHERE m.is_published = 1
              AND m.category_id IN ({cat_placeholders})
              AND m.id NOT IN ({exc_placeholders})
            ORDER BY views_count DESC
            LIMIT :limit
        """), params).fetchall()
        
        return [self._row_to_dict(r) for r in results]
    
    def _get_extra_popular(self, excluded_ids: List[int], limit: int) -> List[dict]:
        """Получить дополнительные популярные материалы"""
        params = {f"exc{i}": eid for i, eid in enumerate(excluded_ids)} if excluded_ids else {}
        params["limit"] = limit
        exc_placeholders = ",".join([f":exc{i}" for i in range(len(excluded_ids))]) if excluded_ids else "0"
        
        results = self.db.execute(text(f"""
            SELECT m.id, m.title, m.description, m.cover_image, c.icon, 
                   m.external_url, m.category_id, c.name as category_name,
                   (SELECT COUNT(*) FROM library_views WHERE material_id = m.id) as views_count
            FROM library_materials m
            LEFT JOIN library_categories c ON c.id = m.category_id
            WHERE m.is_published = 1 AND m.id NOT IN ({exc_placeholders})
            ORDER BY views_count DESC
            LIMIT :limit
        """), params).fetchall()
        
        return [self._row_to_dict(r) for r in results]
    
    def _row_to_dict(self, row) -> dict:
        """Конвертировать строку в dict с cover_url"""
        return add_cover_url({
            "id": row[0], 
            "title": row[1], 
            "description": row[2], 
            "cover_image": row[3], 
            "icon": row[4], 
            "external_url": row[5],
            "category_id": row[6], 
            "category_name": row[7], 
            "views": row[8]
        })

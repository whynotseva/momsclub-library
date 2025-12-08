"""
Миграция: Добавление таблицы materials_categories (many-to-many)
Дата: 2025-12-04
Описание: Позволяет материалам иметь несколько категорий
"""

import sqlite3

DB_PATH = "/root/home/library_backend/library.db"

def run_migration():
    """Создаёт таблицу materials_categories и мигрирует данные"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем существует ли уже таблица
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='materials_categories'
        """)
        if cursor.fetchone():
            print("✅ Таблица materials_categories уже существует")
            return True
        
        # Создаём таблицу связи
        cursor.execute("""
            CREATE TABLE materials_categories (
                material_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                PRIMARY KEY (material_id, category_id),
                FOREIGN KEY (material_id) REFERENCES library_materials(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES library_categories(id) ON DELETE CASCADE
            )
        """)
        print("✅ Таблица materials_categories создана")
        
        # Мигрируем данные из category_id в новую таблицу
        cursor.execute("""
            INSERT INTO materials_categories (material_id, category_id)
            SELECT id, category_id FROM library_materials
            WHERE category_id IS NOT NULL
        """)
        migrated_count = cursor.rowcount
        print(f"✅ Мигрировано {migrated_count} связей материал-категория")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()

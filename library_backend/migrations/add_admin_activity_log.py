"""
Миграция: Добавление таблицы admin_activity_log
Дата: 2025-12-04
Описание: Логирование действий админов в библиотеке
"""

import sqlite3

DB_PATH = "/root/home/library_backend/library.db"

def run_migration():
    """Создаёт таблицу admin_activity_log"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем существует ли уже таблица
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='admin_activity_log'
        """)
        if cursor.fetchone():
            print("✅ Таблица admin_activity_log уже существует")
            return True
        
        # Создаём таблицу
        cursor.execute("""
            CREATE TABLE admin_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                admin_name VARCHAR NOT NULL,
                action VARCHAR NOT NULL,
                entity_type VARCHAR NOT NULL,
                entity_id INTEGER,
                entity_title VARCHAR,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Создаём индекс для быстрой выборки
        cursor.execute("""
            CREATE INDEX idx_admin_activity_created_at 
            ON admin_activity_log(created_at DESC)
        """)
        
        conn.commit()
        print("✅ Таблица admin_activity_log создана")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()

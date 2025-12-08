"""
Миграция: Добавление поля autopay_streak в таблицу users
Дата: 2025-12-03
Описание: Счётчик успешных автопродлений подряд для системы бонусов
"""

import sqlite3
import os

DB_PATH = "/root/home/momsclub/momsclub.db"

def run_migration():
    """Добавляет поле autopay_streak в таблицу users"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Проверяем существует ли уже колонка
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'autopay_streak' in columns:
            print("✅ Колонка autopay_streak уже существует")
            return True
        
        # Добавляем колонку
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN autopay_streak INTEGER DEFAULT 0
        """)
        
        conn.commit()
        print("✅ Колонка autopay_streak успешно добавлена")
        
        # Проверяем
        cursor.execute("SELECT COUNT(*) FROM users WHERE autopay_streak = 0")
        count = cursor.fetchone()[0]
        print(f"   Установлено значение 0 для {count} пользователей")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()

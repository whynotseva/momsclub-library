"""
Система бонусов за автопродление (Streak Bonus System)
Запуск: 3 декабря 2025

Шкала бонусов:
- 1-е автопродление: +3 дня
- 2-е автопродление: +5 дней
- 3-е автопродление: +7 дней
- 4-5-е автопродление: +8 дней
- 6-е и далее: +10 дней
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def get_streak_bonus_days(streak: int) -> int:
    """
    Возвращает количество бонусных дней для текущего стрика.
    
    Args:
        streak: Номер текущего автопродления (1, 2, 3, ...)
        
    Returns:
        Количество бонусных дней
    """
    if streak <= 0:
        return 0
    elif streak == 1:
        return 3
    elif streak == 2:
        return 5
    elif streak == 3:
        return 7
    elif streak in [4, 5]:
        return 8
    else:  # 6+
        return 10


def get_next_streak_bonus_days(streak: int) -> int:
    """
    Возвращает количество бонусных дней для СЛЕДУЮЩЕГО стрика.
    Используется для показа пользователю что его ждёт.
    """
    return get_streak_bonus_days(streak + 1)


async def process_autopay_streak_bonus(
    db: AsyncSession,
    user,
    subscription
) -> dict:
    """
    Обрабатывает бонус за автопродление.
    Вызывается после успешного автосписания.
    
    Args:
        db: Сессия БД
        user: Объект пользователя
        subscription: Объект подписки
        
    Returns:
        dict с информацией о бонусе:
        {
            'streak': int,  # Новый стрик
            'bonus_days': int,  # Начисленные дни
            'next_bonus_days': int,  # Бонус в следующем месяце
            'new_end_date': datetime  # Новая дата окончания
        }
    """
    try:
        # Увеличиваем стрик
        user.autopay_streak = (user.autopay_streak or 0) + 1
        new_streak = user.autopay_streak
        
        # Получаем бонусные дни
        bonus_days = get_streak_bonus_days(new_streak)
        next_bonus_days = get_next_streak_bonus_days(new_streak)
        
        # Добавляем дни к подписке
        if bonus_days > 0 and subscription:
            old_end_date = subscription.end_date
            subscription.end_date = subscription.end_date + timedelta(days=bonus_days)
            new_end_date = subscription.end_date
            
            logger.info(
                f"🎁 Streak bonus для user_id={user.id}: "
                f"streak={new_streak}, bonus={bonus_days} дней, "
                f"end_date: {old_end_date} → {new_end_date}"
            )
        else:
            new_end_date = subscription.end_date if subscription else None
        
        await db.commit()
        
        return {
            'streak': new_streak,
            'bonus_days': bonus_days,
            'next_bonus_days': next_bonus_days,
            'new_end_date': new_end_date
        }
        
    except Exception as e:
        logger.error(f"Ошибка при начислении streak bonus: {e}", exc_info=True)
        await db.rollback()
        return {
            'streak': user.autopay_streak or 0,
            'bonus_days': 0,
            'next_bonus_days': 0,
            'new_end_date': subscription.end_date if subscription else None
        }


async def reset_autopay_streak(db: AsyncSession, user) -> int:
    """
    Сбрасывает стрик пользователя.
    Вызывается при отключении автопродления.
    
    Returns:
        Старый стрик (для логирования/отображения)
    """
    old_streak = user.autopay_streak or 0
    user.autopay_streak = 0
    await db.commit()
    
    logger.info(f"🔄 Streak reset для user_id={user.id}: {old_streak} → 0")
    return old_streak


def format_streak_bonus_message(streak: int, bonus_days: int, next_bonus_days: int, new_end_date: datetime) -> str:
    """
    Форматирует сообщение о бонусе для пользователя.
    """
    date_str = new_end_date.strftime("%d.%m.%Y") if new_end_date else "—"
    
    if streak == 1:
        # Первое автопродление
        return (
            f"🔥 <b>Поздравляем!</b> Твой стрик автопродлений начался!\n"
            f"🎁 Бонус: <b>+{bonus_days} дня</b> в подарок!\n"
            f"📅 Новая дата подписки: <b>{date_str}</b>\n\n"
            f"💡 Держи автопродление включённым —\n"
            f"бонусы растут каждый месяц! ✨\n"
            f"➡️ Следующий бонус: <b>+{next_bonus_days} дней</b>"
        )
    else:
        # Последующие
        streak_emoji = "🔥" * min(streak, 5)  # Максимум 5 огоньков
        return (
            f"{streak_emoji} <b>Это твоё {streak}-е автопродление подряд!</b>\n"
            f"🎁 Бонус: <b>+{bonus_days} дней</b>!\n"
            f"📅 Новая дата подписки: <b>{date_str}</b>\n\n"
            f"✨ Следующий бонус: <b>+{next_bonus_days} дней</b>"
        )


def format_streak_warning_message(streak: int, next_bonus_days: int) -> str:
    """
    Форматирует предупреждение при отключении автопродления.
    """
    return (
        f"⚠️ <b>Красотка, подожди!</b>\n\n"
        f"🔥 У тебя уже <b>{streak}</b> автопродлений подряд!\n"
        f"🎁 В следующем месяце ты получишь <b>+{next_bonus_days} дней</b> бонусом!\n\n"
        f"Если отключишь автопродление сейчас —\n"
        f"стрик сбросится и придётся начинать сначала 😢\n\n"
        f"<i>Точно хочешь отключить?</i>"
    )

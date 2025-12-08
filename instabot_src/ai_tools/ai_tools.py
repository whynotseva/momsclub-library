import asyncio
import logging
import base64
import os
import urllib.parse
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from openai import OpenAI
from dotenv import load_dotenv
from config import OPENAI_API_KEY, OPENAI_PROXY_ENABLED, HTTPS_PROXY, NO_PROXY, MOMS_CLUB_INTEGRATION
from database import Database
from hendler.helpers import get_main_menu_reply_keyboard, get_ai_tools_keyboard
from moms_club_auth import (
    check_moms_club_subscription, 
    is_moms_club_subscriber,
    MOMS_CLUB_BOT_URL,
    MOMS_CLUB_ACCESS_DENIED_TEXT,
    MOMS_CLUB_ABOUT_TEXT
)

ai_tools_router = Router()

# Загружаем переменные окружения из .env файла
load_dotenv()

# Переменная для хранения клиента OpenAI, инициализируется позже
_client = None

# Асинхронная функция для инициализации OpenAI клиента с поддержкой прокси
async def get_openai_client():
    global _client
    if _client is not None:
        return _client
        
    # Создаем клиент OpenAI с API ключом
    _client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Добавляем настройки прокси, если включено
    if OPENAI_PROXY_ENABLED:
        logging.info(f"Включено использование прокси для OpenAI: {HTTPS_PROXY}")
        _client.proxy = HTTPS_PROXY
    
    return _client

# Укажите полный путь к ffmpeg, если он не находится автоматически
FFMPEG_PATH = "ffmpeg"  # Полный путь для Windows

# Создание конечного автомата для управления состояниями диалога
class AIToolsStates(StatesGroup):
    # Состояния для генерации оформления профиля
    ProfileDesign = State()  # Ожидание информации о профиле
    ProfileDesignReview = State()  # Обсуждение сгенерированных вариантов

    # Состояния для генерации контент-плана постов
    ContentPlanPosts = State()  # Ожидание информации о нише и ЦА
    ContentPlanPostsReview = State()  # Обсуждение сгенерированного плана

    # Состояния для генерации контент-плана Reels
    ContentPlanReels = State()  # Ожидание информации о нише и ЦА
    ContentPlanReelsReview = State()  # Обсуждение сгенерированного плана

    # Состояния для транскрибации аудио/видео
    TranscribeAudio = State()
    
    # Состояния для скачивания контента из Instagram
    InstagramDownload = State()  # Ожидание ссылки на контент
    
    # Состояния для анализа Reels
    ReelsAnalysis = State()  # Ожидание видео для анализа

# Определим класс состояний для генерации изображений
class ImageGenerationStates(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_style = State()
    waiting_for_generation = State()

# Список стилей для генерации изображений
DALLE_STYLES = [
    {"name": "Реалистичный", "emoji": "📷", "prompt": "Фотореалистичное изображение с высокой детализацией, естественным освещением и текстурами"},
    {"name": "Аниме", "emoji": "🎌", "prompt": "В стиле японского аниме, с яркими цветами и характерными чертами персонажей"},
    {"name": "Акварель", "emoji": "🎨", "prompt": "Акварельная живопись с мягкими переходами и прозрачными слоями краски"},
    {"name": "Пиксель-арт", "emoji": "👾", "prompt": "Пиксельная графика в стиле ретро-игр, с ограниченной цветовой палитрой"},
    {"name": "Неоновый", "emoji": "💫", "prompt": "Яркие неоновые цвета на темном фоне, с эффектами свечения и кибер-эстетикой"},
    {"name": "Карикатура", "emoji": "🤪", "prompt": "Мультяшный стиль с утрированными чертами и комичными элементами"},
    {"name": "Минимализм", "emoji": "⬜", "prompt": "Минималистичный дизайн с простыми формами, чистыми линиями и ограниченной цветовой гаммой"},
    {"name": "Масляная живопись", "emoji": "🖌️", "prompt": "В стиле масляной живописи с выраженной текстурой мазков и богатыми цветами"},
    {"name": "Фэнтези", "emoji": "🧙", "prompt": "Фэнтезийный мир с магическими элементами, мистическими существами и необычными пейзажами"},
    {"name": "Ретро", "emoji": "🕰️", "prompt": "Винтажный стиль с характерными для прошлых десятилетий визуальными элементами и приглушенными цветами"}
]

# Основной обработчик для меню AI инструментов
async def show_ai_tools_menu(message: Message):
    user_id = message.from_user.id
    
    # Проверяем доступ пользователя
    has_subscription = await check_user_access(user_id)
    
    keyboard = get_ai_tools_keyboard(has_subscription=has_subscription)
    image_path = "media/ai_tools.png"
    image = FSInputFile(image_path)
    
    # Разный текст в зависимости от наличия подписки
    if has_subscription:
        caption = "🤖 *AI Студия* — всё, что нужно для контента: от идей до оформления. Быстро. Умно. С помощью нейросетей."
    else:
        caption = (
            "🤖 *AI Студия* — всё, что нужно для контента: от идей до оформления.\n\n"
            "Выберите инструмент для работы с контентом. Для использования требуется активная подписка."
        )
    
    await message.answer_photo(
        photo=image,
        caption=caption,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    return True

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@ai_tools_router.callback_query(F.data == "back_to_main")
async def back_to_main_with_cleanup(callback: types.CallbackQuery, state: FSMContext):
    # Удаляем временный файл если он есть
    state_data = await state.get_data()
    temp_image_path = state_data.get("profile_image_path", None)
    if temp_image_path and os.path.exists(temp_image_path):
        try:
            os.remove(temp_image_path)
        except Exception as e:
            logging.error(f"Ошибка при удалении временного файла: {e}")
    
    await state.clear()
    await callback.message.delete()
    keyboard = get_main_menu_reply_keyboard()
    await callback.message.answer("Вы вернулись в главное меню", reply_markup=keyboard)
    await callback.answer()

# Обработчик для возврата в меню AI инструментов (если используется)
@ai_tools_router.callback_query(F.data == "back_to_ai_menu")
async def back_to_ai_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    # Проверяем доступ пользователя
    has_subscription = await check_user_access(user_id)
    
    await callback.message.delete() # Удаляем предыдущее сообщение
    keyboard = get_ai_tools_keyboard(has_subscription=has_subscription)
    image_path = "media/ai_tools.png"
    image = FSInputFile(image_path)
    
    # Разный текст в зависимости от наличия подписки
    if has_subscription:
        caption = "🤖 *AI Студия* — всё, что нужно для контента: от идей до оформления. Быстро. Умно. С помощью нейросетей."
    else:
        caption = (
            "🤖 *AI Студия* — всё, что нужно для контента: от идей до оформления.\n\n"
            "Выберите инструмент для работы с контентом. Для использования требуется активная подписка."
        )
    
    await callback.message.answer_photo(
        photo=image,
        caption=caption,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# Обработчик для команды "Завершить диалог"
@ai_tools_router.message(F.text == "Завершить диалог")
async def finish_dialog(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # Удаляем временный файл если он есть
    state_data = await state.get_data()
    temp_image_path = state_data.get("profile_image_path", None)
    if temp_image_path and os.path.exists(temp_image_path):
        try:
            os.remove(temp_image_path)
        except Exception as e:
            logging.error(f"Ошибка при удалении временного файла: {e}")
    
    await state.clear()
    
    # Проверяем доступ пользователя
    has_subscription = await check_user_access(user_id)
    
    # Сначала убираем reply клавиатуру
    await message.answer(
        "Диалог завершен.", 
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Затем отправляем фото с inline клавиатурой
    keyboard = get_ai_tools_keyboard(has_subscription=has_subscription)
    image_path = "media/ai_tools.png" # Путь к изображению
    image = FSInputFile(image_path)
    
    # Разный текст в зависимости от наличия подписки
    if has_subscription:
        caption = "🤖 *AI Студия* — всё, что нужно для контента: от идей до оформления. Быстро. Умно. С помощью нейросетей."
    else:
        caption = (
            "🤖 *AI Студия* — всё, что нужно для контента: от идей до оформления.\n\n"
            "Выберите инструмент для работы с контентом. Для использования требуется активная подписка."
        )
    
    await message.answer_photo(
        photo=image, 
        caption=caption, 
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Добавляем основное меню через ReplyKeyboardMarkup
    main_menu_keyboard = get_main_menu_reply_keyboard()
    await message.answer(
        "Вы вернулись в главное меню", 
        reply_markup=main_menu_keyboard
    )
    
    return True

# Определение функции для получения модели GPT на основе уровня подписки пользователя
async def get_user_model(user_id: int) -> str:
    """
    Возвращает модель GPT в зависимости от уровня подписки пользователя
    """
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    
    # По умолчанию используем базовую модель
    default_model = "gpt-4o-mini"
    
    if not user:
        return default_model
        
    # Проверка типа подписки
    subscription_type = user.get("subscription_type")
    
    # Для всех пользователей с подпиской (кроме пробной)
    if subscription_type in ["month_1", "month_3", "month_12"]:
        return "gpt-4o"  # Более продвинутая модель
    
    # Для пробной подписки и базовой
    return default_model

# Функция для генерации текста с использованием OpenAI API
async def generate_ai_response(model, row_data, prompt):
    try:
        client = await get_openai_client()
        max_tokens = 2000 if model == "gpt-4o" else 4000  # 4000 для gpt-4o-mini, 2000 для gpt-4o
        response = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Данные для обработки или запрос пользователя: {row_data}"}
            ],
            model=model,
            temperature=0.7,
            max_tokens=max_tokens,
            timeout=60
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.exception("Ошибка при запросе к OpenAI:")
        return f"Ошибка при запросе к OpenAI: {e}"

# Функция для генерации текста с использованием OpenAI API, включая анализ изображения через base64
async def generate_ai_response_with_image(model, prompt, image_data):
    try:
        client = await get_openai_client()
        # Используем gpt-4o для анализа изображений (она поддерживает мультимодальные запросы)
        vision_model = "gpt-4o"
        max_tokens = 2000 if model == "gpt-4o" else 4000
        
        # Формируем base64-строку
        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {
                    "role": "system", 
                    "content": "Ты опытный SMM-специалист и эксперт по Instagram. Твоя задача - помогать пользователям создавать качественный контент и улучшать их профили."
                },
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            model=vision_model,
            temperature=0.7,
            max_tokens=max_tokens,
            timeout=60
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.exception("Ошибка при запросе к OpenAI Vision:")
        return f"Ошибка при запросе к OpenAI Vision: {e}"

# Изменение функции проверки наличия ffmpeg
async def check_ffmpeg_installed():
    try:
        # Пытаемся найти ffmpeg по прямому пути
        cmd = FFMPEG_PATH
        logging.info(f"Проверяю наличие ffmpeg по пути: {cmd}")
        
        process = await asyncio.create_subprocess_exec(
            cmd, "-version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            ffmpeg_version = stdout.decode().split('\n')[0] if stdout else "Неизвестная версия"
            logging.info(f"ffmpeg установлен: {ffmpeg_version}")
            return True
        else:
            logging.warning(f"Ошибка при проверке ffmpeg: {stderr.decode() if stderr else 'Нет вывода'}")
            return False
    except Exception as e:
        logging.error(f"Исключение при проверке ffmpeg: {e}")
        return False

# Обработчик кнопки "Оформить подписку Mom's Club"
@ai_tools_router.callback_query(F.data == "buy_subscription")
async def ai_tools_moms_club_redirect(callback: types.CallbackQuery):
    """Перенаправляет пользователя в Mom's Club для оформления подписки"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💖 Перейти к Mom's Club", 
            url=MOMS_CLUB_BOT_URL
        )],
        [InlineKeyboardButton(
            text="❓ Что такое Mom's Club?", 
            callback_data="about_moms_club"
        )],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_ai_menu")]
    ])
    
    await callback.message.edit_caption(
        caption=MOMS_CLUB_ACCESS_DENIED_TEXT,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик информации о Mom's Club
@ai_tools_router.callback_query(F.data == "about_moms_club")
async def about_moms_club(callback: types.CallbackQuery):
    """Показывает информацию о Mom's Club"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💖 Присоединиться к Mom's Club", 
            url=MOMS_CLUB_BOT_URL
        )],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_ai_menu")]
    ])
    
    await callback.message.edit_caption(
        caption=MOMS_CLUB_ABOUT_TEXT,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

# Обработчик для совместимости (если где-то остались старые кнопки)
@ai_tools_router.callback_query(F.data == "sub_trial")
async def ai_tools_trial_redirect(callback: types.CallbackQuery):
    """Перенаправляет на Mom's Club вместо пробной подписки"""
    await ai_tools_moms_club_redirect(callback)

# Универсальная функция проверки доступа
async def check_user_access(user_id: int) -> bool:
    """
    Универсальная проверка доступа пользователя к AI инструментам
    
    Args:
        user_id: Telegram ID пользователя
        
    Returns:
        bool: True если есть доступ
    """
    if MOMS_CLUB_INTEGRATION:
        return await is_moms_club_subscriber(user_id)
    else:
        # Fallback на старую систему (для совместимости)
        db = await Database.get_instance()
        has_subscription, _ = await db.check_subscription(user_id)
        return has_subscription

# Функция для корректного закрытия сессии при остановке бота
async def close_openai_sessions():
    global _client
    if _client is not None and hasattr(_client, "http_client") and _client.http_client is not None:
        try:
            _client.http_client.close()
            logging.info("OpenAI HTTP клиент закрыт корректно")
        except Exception as e:
            logging.error(f"Ошибка при закрытии OpenAI HTTP клиента: {e}")
        _client = None
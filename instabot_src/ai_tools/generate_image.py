import asyncio
import logging
import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, FSInputFile
import aiohttp
from io import BytesIO
from aiogram.filters import Command
from dotenv import load_dotenv
from config import OPENAI_API_KEY
from database import Database
from hendler.helpers import get_main_menu_reply_keyboard, get_ai_tools_keyboard
from ai_tools.ai_tools import DALLE_STYLES, get_cancel_dialog_keyboard, get_openai_client, check_user_access
from moms_club_auth import MOMS_CLUB_ACCESS_DENIED_TEXT

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Настройка маршрута для транскрибации
generate_image_router = Router()

# Определим класс состояний для генерации изображений
class ImageGenerationStates(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_style = State()
    waiting_for_generation = State()

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@generate_image_router.callback_query(F.data == "back_to_main")
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

# Обработчик для команды "Завершить диалог"
@generate_image_router.message(F.text == "Завершить диалог")
async def finish_dialog(message: types.Message, state: FSMContext):
    # Удаляем временный файл если он есть
    state_data = await state.get_data()
    temp_image_path = state_data.get("profile_image_path", None)
    if temp_image_path and os.path.exists(temp_image_path):
        try:
            os.remove(temp_image_path)
        except Exception as e:
            logging.error(f"Ошибка при удалении временного файла: {e}")
    
    await state.clear()
    
    # Сначала убираем reply клавиатуру
    await message.answer(
        "Диалог завершен.", 
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Получаем данные о подписке для меню AI
    db = await Database.get_instance()
    user_id = message.from_user.id
    has_subscription, _ = await db.check_subscription(user_id)
    
    # Затем отправляем фото с inline клавиатурой
    keyboard = get_ai_tools_keyboard(has_subscription=has_subscription)
    image_path = "media/ai_tools.png" # Путь к изображению
    image = FSInputFile(image_path)
    
    await message.answer_photo(
        photo=image, 
        caption="Вы вернулись в меню AI инструментов:", 
        reply_markup=keyboard
    )
    
    # Добавляем основное меню через ReplyKeyboardMarkup
    main_menu_keyboard = get_main_menu_reply_keyboard()
    await message.answer(
        "Вы вернулись в главное меню", 
        reply_markup=main_menu_keyboard
    )
    
    return True

#
# ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ
#

# Функция для создания клавиатуры выбора стилей
def get_style_selection_keyboard():
    keyboard = []
    row = []
    
    # Размещаем кнопки стилей по 2 в ряд
    for idx, style in enumerate(DALLE_STYLES):
        row.append(InlineKeyboardButton(text=f"{style['emoji']} {style['name']}", callback_data=f"style:{idx}"))
        
        if len(row) == 2 or idx == len(DALLE_STYLES) - 1:
            keyboard.append(row.copy())
            row = []
    
    # Добавляем кнопку "Без стиля"
    keyboard.append([InlineKeyboardButton(text="🔄 Без стиля", callback_data="style:none")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Обработчик для запуска генерации изображений
@generate_image_router.message(Command("generate_image"))
async def image_generation_start(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(ImageGenerationStates.waiting_for_prompt)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await message.answer(
        "🖼️ *Генерация изображений с DALL·E 3*\n\n"
        "Нужна яркая, стильная или атмосферная картинка под задачу? Я помогу тебе её сгенерировать.\n\n"
        "💭 *Опиши, что ты хочешь увидеть*:\n"
        "• сюжет, объекты, герои\n"
        "• стиль (реализм, 3D, аниме, арт и т.д.)\n"
        "• настроение (уютно, мрачно, футуристично, сказочно…)\n"
        "• важные детали: одежда, локация, цветовая гамма, эмоции и т.п.\n\n"
        "📌 *Чем точнее описание — тем круче результат!*",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )


# Обработчик для запуска генерации изображений
@generate_image_router.callback_query(F.data == "ai_tool_image_generation")
async def image_generation_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    has_subscription = await check_user_access(user_id)
    
    if not has_subscription:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        
        builder.button(text="💖 Оформить подписку Mom's Club", callback_data="buy_subscription")
        builder.button(text="❓ Что такое Mom's Club?", callback_data="about_moms_club")
        builder.button(text="↩️ Назад", callback_data="back_to_ai_menu")
        builder.adjust(1)
        
        await callback.message.edit_caption(
            caption=MOMS_CLUB_ACCESS_DENIED_TEXT,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer("Требуется подписка Mom's Club для использования InstaBot")
        return
    
    await callback.message.delete()
    await state.set_state(ImageGenerationStates.waiting_for_prompt)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await callback.message.answer(
        "🖼️ *Генерация изображений с DALL·E 3*\n\n"
        "Нужна яркая, стильная или атмосферная картинка под задачу? Я помогу тебе её сгенерировать.\n\n"
        "💭 *Опиши, что ты хочешь увидеть*:\n"
        "• сюжет, объекты, герои\n"
        "• стиль (реализм, 3D, аниме, арт и т.д.)\n"
        "• настроение (уютно, мрачно, футуристично, сказочно…)\n"
        "• важные детали: одежда, локация, цветовая гамма, эмоции и т.п.\n\n"
        "📌 *Чем точнее описание — тем круче результат!*",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# Обработчик для получения промпта от пользователя
@generate_image_router.message(ImageGenerationStates.waiting_for_prompt)
async def process_image_prompt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    # Сохраняем промпт в состоянии
    await state.update_data(image_prompt=message.text)
    
    # Предлагаем выбрать стиль изображения
    await message.answer(
        "Выберите стиль для генерации изображения или продолжите без применения стиля:",
        reply_markup=get_style_selection_keyboard()
    )
    
    # Переходим к состоянию ожидания выбора стиля
    await state.set_state(ImageGenerationStates.waiting_for_style)

# Обработчик для выбора стиля
@generate_image_router.callback_query(ImageGenerationStates.waiting_for_style, lambda c: c.data.startswith("style:"))
async def process_style_selection(callback: types.CallbackQuery, state: FSMContext):
    # Сразу отвечаем на колбек, чтобы избежать таймаута
    await callback.answer()

    # Получаем данные о выбранном стиле
    style_data = callback.data.split(":", 1)[1]
    
    # Получаем сохраненный промпт
    data = await state.get_data()
    original_prompt = data.get("image_prompt", "")
    
    # Обрабатываем выбор стиля
    if style_data == "none":
        # Пользователь выбрал "Без стиля"
        prompt = original_prompt
        style_name = "Без стиля"
    else:
        # Пользователь выбрал один из предложенных стилей
        style_idx = int(style_data)
        style = DALLE_STYLES[style_idx]
        prompt = f"{original_prompt}. {style['prompt']}"
        style_name = style["name"]
    
    # Сохраняем окончательный промпт в состоянии
    await state.update_data(final_prompt=prompt, style_name=style_name)
    
    # Переходим к состоянию генерации изображения
    await state.set_state(ImageGenerationStates.waiting_for_generation)
    
    # Обновляем сообщение, чтобы показать, что стиль выбран и начинается генерация
    await callback.message.edit_text(
        f"Выбран стиль: {style_name}\n\n"
        "🔄 Генерирую изображение, это может занять несколько секунд..."
    )
    
    # Проверка наличия подписки пользователя
    user_id = callback.from_user.id
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    
    if not user or not user.get("subscription_type"):
        await callback.message.edit_text(
            "❌ Для генерации изображения требуется активная подписка.\n"
            "Пожалуйста, оформите подписку."
        )
        await state.clear()
        return
    
    try:
        # Получаем клиент OpenAI
        client = await get_openai_client()
        
        # Генерируем изображение через DALL-E 3
        response = await asyncio.to_thread(
            client.images.generate,
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        # Получаем URL сгенерированного изображения
        image_url = response.data[0].url
        
        # Скачиваем изображение
        image_data = None
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
        
        if not image_data:
            raise Exception("Не удалось скачать сгенерированное изображение")
        
        # Отправляем изображение пользователю
        photo = BytesIO(image_data)
        photo.name = "generated_image.png"
        
        # Создаем подпись к изображению
        caption = (
            f"✅ Изображение сгенерировано! 🖼️\n"
            f"🎨 Стиль: {style_name}"
        )
        
        # Отправляем фото с подписью
        from aiogram.types import BufferedInputFile
        await callback.message.answer_photo(
            photo=BufferedInputFile(photo.getvalue(), filename="generated_image.png"),
            caption=caption
        )
        
        # Предлагаем сгенерировать еще одно изображение
        await callback.message.answer(
            "🎨 Хотите сгенерировать еще одно изображение?\n"
            "• ✏️ Напишите новый запрос\n"
            "• 🚪 Или нажмите 'Завершить диалог', чтобы вернуться в главное меню",
            reply_markup=get_cancel_dialog_keyboard()
        )
        
        # Возвращаемся к состоянию ожидания промпта
        await state.set_state(ImageGenerationStates.waiting_for_prompt)
        
    except Exception as e:
        logging.exception(f"Ошибка при генерации изображения: {e}")
        await callback.message.edit_text(
            f"❌ Произошла ошибка при генерации изображения: {str(e)}\n"
            "Пожалуйста, попробуйте еще раз или измените запрос."
        )
        # Возвращаемся к состоянию ожидания промпта
        await state.set_state(ImageGenerationStates.waiting_for_prompt)

# Обработчик текстовых сообщений в состоянии ожидания генерации
@generate_image_router.message(ImageGenerationStates.waiting_for_generation)
async def generation_text_fallback(message: types.Message, state: FSMContext):
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    await message.answer(
        "⏳ Пожалуйста, подождите. Идет процесс генерации изображения..."
    )
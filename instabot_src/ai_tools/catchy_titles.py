import logging
import os
from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from dotenv import load_dotenv
from config import OPENAI_API_KEY
from database import Database
from hendler.helpers import get_main_menu_reply_keyboard, get_ai_tools_keyboard
from ai_tools.ai_tools import generate_ai_response, get_user_model, get_openai_client, check_user_access
from moms_club_auth import MOMS_CLUB_ACCESS_DENIED_TEXT

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка маршрута для генерации заголовков
catchy_titles_router = Router()

# Настройка состояний для генерации заголовков
class CatchyTitlesStates(StatesGroup):
    WaitingForInfo = State()  # Ожидание информации для генерации заголовков
    TitlesReview = State()  # Обсуждение сгенерированных заголовков

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@catchy_titles_router.callback_query(F.data == "back_to_main")
async def back_to_main_with_cleanup(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    keyboard = get_main_menu_reply_keyboard()
    await callback.message.answer("Вы вернулись в главное меню", reply_markup=keyboard)
    await callback.answer()

# Обработчик для команды "Завершить диалог"
@catchy_titles_router.message(F.text == "Завершить диалог")
async def finish_dialog(message: types.Message, state: FSMContext):
    await state.clear()
    
    # Сначала убираем reply клавиатуру
    await message.answer(
        "Диалог завершен.", 
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Получаем данные о подписке для меню AI
    user_id = message.from_user.id
    has_subscription = await check_user_access(user_id)
    
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
# ЦЕПЛЯЮЩИЕ ЗАГОЛОВКИ
#

@catchy_titles_router.message(Command("catchy_titles"))
async def catchy_titles_start_cmd(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(CatchyTitlesStates.WaitingForInfo)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await message.answer(
        "🎯 *Цепляющие заголовки под твой контент*\n\n"
        "Хочешь, чтобы заголовки притягивали внимание с первых секунд и заставляли читать до последней строчки?\n\n"
        "✍️ *Просто расскажи мне:*\n"
        "• Для чего тебе нужны заголовки — пост, рилс, статья, реклама?\n"
        "• В какой теме или нише ты работаешь?\n"
        "• Кто твоя аудитория и какую задачу должен решать контент?\n\n"
        "💡 Эта информация поможет мне создать 10 мощных, вовлекающих заголовков — под твою аудиторию, цели и формат.\n"
        "Каждый из них будет не просто «текстом в начале», а настоящим крючком, за который цепляются глазами, эмоциями и кликами.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )

@catchy_titles_router.callback_query(F.data == "ai_tool_catchy_titles")
async def catchy_titles_start_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    has_subscription = await check_user_access(user_id)
    
    if not has_subscription:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        
        # Новые кнопки для MomsClub интеграции
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
    await state.set_state(CatchyTitlesStates.WaitingForInfo)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await callback.message.answer(
        "🎯 *Цепляющие заголовки под твой контент*\n\n"
        "Хочешь, чтобы заголовки притягивали внимание с первых секунд и заставляли читать до последней строчки?\n\n"
        "✍️ *Просто расскажи мне:*\n"
        "• Для чего тебе нужны заголовки — пост, рилс, статья, реклама?\n"
        "• В какой теме или нише ты работаешь?\n"
        "• Кто твоя аудитория и какую задачу должен решать контент?\n\n"
        "💡 Эта информация поможет мне создать 10 мощных, вовлекающих заголовков — под твою аудиторию, цели и формат.\n"
        "Каждый из них будет не просто «текстом в начале», а настоящим крючком, за который цепляются глазами, эмоциями и кликами.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@catchy_titles_router.message(CatchyTitlesStates.WaitingForInfo)
async def process_titles_info(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    model = await get_user_model(user_id)

    if not user or not user.get("subscription_type"):
        await message.answer(
            "❌ Для генерации заголовков требуется активная подписка."
        )
        return

    await state.update_data(titles_info=message.text)
    
    # Отправка сообщения о начале генерации
    wait_msg = await message.answer("🔄 Генерирую цепляющие заголовки...")
    
    raw_data = message.text

    # Формирование промпта для OpenAI
    prompt = f"""
    Ты — сильный копирайтер с нейромаркетинговым мышлением.
    Ты не просто пишешь заголовки — ты понимаешь аудиторию глубже, чем она сама себя.
    Твоя задача — создавать заголовки и хуки, которые мгновенно привлекают внимание, вызывают интерес и побуждают к действию.

    🎯 Твоя цель:
    Создать 10 вариантов заголовков, которые:
    • Соответствуют формату (пост, сторис, рилс, реклама, лендинг, статья и т.д.)
    • Учитывают нишу, стиль и задачу контента (прогрев, продажи, вовлечение, экспертность)
    • Подходят под ЦА — её язык, боли, страхи, желания, мечты
    • Основаны на психологии внимания: триггеры, интрига, эмоция, конкретика, контраст

    💡 Что у тебя встроено:
    • Знание боли, мотивации и поведения клиента
    • Умение работать с JTBD — "что человек хочет на самом деле"
    • Глубокое понимание 3 уровней прогрева: холодные, тёплые, горячие
    • Гибкость — ты умеешь писать легко, экспертно, по-дружески, с нотками юмора, провокации или заботы (по ситуации)

    🧰 Формулы, которые ты применяешь:
    • AIDA
    • PAS
    • 4P
    • Reason Why
    • Hook → Pain → Twist → Desire → CTA
    • Заголовок → Интрига → Выгода → Эмоция → Триггер

    🔧 Как ты работаешь:
    1. Читаешь ввод: ниша, формат, цель, стиль, кто ЦА
    2. Анализируешь: какая эмоция или потребность у клиента стоит за этим
    3. Выдаёшь 10 заголовков, которые хочется читать, кликать и запоминать
    4. Каждый заголовок — не просто строка, а маленький мостик к действию

    📦 Формат ответа:
    🎯 10 заголовков для [указать формат, нишу, цель]:
    1. ...
    2. ...
    3. ...
    4. ...
    5. ...
    6. ...
    7. ...
    8. ...
    9. ...
    10. ...

    🧠 Помни:
    Ты не просто копирайтер.
    Ты — тот, кто превращает идею в интерес, интерес — в клик, а клик — в результат.
    Каждый твой заголовок — это шанс на охват, отклик, продажу или эмоцию.
    Ты создаёшь контент, который останавливает взгляд и остаётся в памяти.

    ###Максимум 4000 символов!
    Используй базовый Markdown для форматирования: *жирный текст* для выделения важной информации, _курсив_ для акцентов. Не используй заголовки и разделители при генерации ответа.
    """
    
    # Получение ответа от OpenAI
    try:
        response = await generate_ai_response(model, raw_data, prompt)
    except Exception as e:
        logger.error(f"Ошибка OpenAI при генерации заголовков для {user_id}: {e}")
        await wait_msg.edit_text("❌ Произошла ошибка при генерации заголовков.")
        return
    
    # Удаление сообщения о ожидании
    await wait_msg.delete()
    
    # Сохраняем полученный ответ в состоянии для дальнейшего использования
    await state.update_data(previous_ai_response=response)

    # Отправка результатов пользователю
    result_header = "✅ *Цепляющие заголовки готовы!*\n\n"
    full_response = result_header + response
    # Проверяем длину ответа
    if len(full_response) > 4000:
        await message.answer(result_header + "Заголовки слишком длинные, отправляю частями:", parse_mode="Markdown")
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for i, chunk in enumerate(chunks):
            await message.answer(f"Часть {i+1}/{len(chunks)}:\n\n{chunk}", parse_mode="Markdown")
    else:
        await message.answer(full_response, parse_mode="Markdown")

    # Переход к состоянию обсуждения
    await state.set_state(CatchyTitlesStates.TitlesReview)
    await message.answer(
        f"✅ Вот 10 цепляющих заголовков для твоего контента! Ты можешь:\n"
        f"1️⃣ Запросить еще варианты заголовков\n"
        f"2️⃣ Уточнить детали и получить более точные варианты\n"
        f"3️⃣ Изменить формат или ЦА для новых вариантов\n"
        f"🚪 Или нажми 'Завершить диалог', чтобы вернуться в главное меню.",
        reply_markup=get_cancel_dialog_keyboard()
    )

@catchy_titles_router.message(CatchyTitlesStates.TitlesReview)
async def titles_review(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    model = await get_user_model(user_id)

    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для доработки заголовков требуется активная подписка.",
            reply_markup=get_cancel_dialog_keyboard()
        )
        return

    # Отправка сообщения о начале генерации
    wait_msg = await message.answer("🔄 Обрабатываю ваш запрос...")
    
    state_data = await state.get_data()
    titles_info = state_data.get("titles_info", "")
    previous_ai_response = state_data.get("previous_ai_response", "") # Получаем предыдущий ответ AI
    user_request = message.text # Новый запрос пользователя
    
    # Формирование промпта для OpenAI
    prompt = f"""
    Ты продолжаешь диалог с пользователем по генерации цепляющих заголовков.
    
    Первоначальная информация от пользователя (формат, ниша, ЦА): {titles_info}
    
    Предыдущий сгенерированный тобой ответ (заголовки):
    {previous_ai_response}
    
    Твоя задача: Ответь на новый запрос пользователя, учитывая всю предыдущую информацию и контекст.
    Если пользователь просит новые варианты, сгенерируй еще 10 уникальных заголовков.
    Если просит уточнить детали, адаптируй заголовки под новые вводные.
    
    Используй базовый Markdown для форматирования: *жирный текст* для выделения важной информации, _курсив_ для акцентов. Не используй заголовки и разделители при генерации ответа.
    """
    
    # Получение ответа от OpenAI
    try:
        response = await generate_ai_response(model, user_request, prompt)
    except Exception as e:
        logger.error(f"Ошибка OpenAI при доработке заголовков для {user_id}: {e}")
        await wait_msg.edit_text("❌ Произошла ошибка при обработке вашего запроса.")
        return
    
    # Удаление сообщения о ожидании
    await wait_msg.delete()
    
    # Обновляем сохраненный ответ AI новым результатом
    await state.update_data(previous_ai_response=response)

    # Отправка результатов пользователю
    result_header = "✅ *Новые заголовки готовы!*\n\n"
    full_response = result_header + response
    # Проверяем длину ответа
    if len(full_response) > 4000:
        await message.answer(result_header + "Заголовки слишком длинные, отправляю частями:", parse_mode="Markdown")
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for i, chunk in enumerate(chunks):
            await message.answer(f"Часть {i+1}/{len(chunks)}:\n\n{chunk}", parse_mode="Markdown")
    else:
        await message.answer(full_response, parse_mode="Markdown", reply_markup=get_cancel_dialog_keyboard())

    await message.answer(
        f"Хочешь попробовать еще варианты или завершить диалог?",
        reply_markup=get_cancel_dialog_keyboard()
    ) 
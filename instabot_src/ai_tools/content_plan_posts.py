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

# Настройка маршрута для транскрибации
content_plan_router = Router()

# Настройка состояний для транскрибации
class ContentPlanStates(StatesGroup):
    ContentPlanPosts = State()  # Ожидание информации о нише и ЦА
    ContentPlanPostsReview = State()  # Обсуждение сгенерированного плана

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@content_plan_router.callback_query(F.data == "back_to_main")
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
@content_plan_router.message(F.text == "Завершить диалог")
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
# КОНТЕНТ-ПЛАН ДЛЯ ПОСТОВ
#

@content_plan_router.message(Command("content_posts"))
async def content_plan_posts_start(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(ContentPlanStates.ContentPlanPosts)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await message.answer(
        "📝 *Контент-план для постов*\n\n"
        "Хочешь системно и без боли генерировать идеи для контента?\n\n"
        "🔍 *Расскажи немного о себе:*\n"
        "• Чем ты занимаешься?\n"
        "• В какой нише работаешь?\n"
        "• Кто твоя целевая аудитория?\n\n"
        "💡 Эта информация поможет мне создать *продуманный, цепляющий контент-план*, который будет говорить на языке твоей аудитории — и работать на результат.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )

@content_plan_router.callback_query(F.data == "ai_tool_content_plan_posts")
async def content_plan_posts_start(callback: types.CallbackQuery, state: FSMContext):
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
    await state.set_state(ContentPlanStates.ContentPlanPosts)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await callback.message.answer(
        "📝 *Контент-план для постов*\n\n"
        "Хочешь системно и без боли генерировать идеи для контента?\n\n"
        "🔍 *Расскажи немного о себе:*\n"
        "• Чем ты занимаешься?\n"
        "• В какой нише работаешь?\n"
        "• Кто твоя целевая аудитория?\n\n"
        "💡 Эта информация поможет мне создать *продуманный, цепляющий контент-план*, который будет говорить на языке твоей аудитории — и работать на результат.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@content_plan_router.message(ContentPlanStates.ContentPlanPosts)
async def process_content_plan_posts_info(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    model = await get_user_model(user_id)

    if not user or not user.get("subscription_type"): # Администраторы также имеют subscription_type
        await message.answer(
            "❌ Для генерации контент-плана требуется активная подписка."
        )
        return

    await state.update_data(content_plan_info=message.text)
    
    # Отправка сообщения о начале генерации
    wait_msg = await message.answer("🔄 Генерирую контент-план для постов...")
    
    raw_data = message.text

    # Формирование промпта для OpenAI
    prompt = f"""
    🗓 Контент-план для постов и каруселей

    Ты — Instagram-контент-стратег и текстовой продюсер.
    Твоя задача — создать эффективный, стратегически выстроенный и цепляющий контент-план для постов и каруселей в Instagram на основе данных от пользователя.

    📌 Как работать:

    1. Проанализируй, чем занимается пользователь, какая у него ниша и цель блога.
    2. Определи подходящие рубрики и смысловой скелет:
       - Прогрев
       - Продающий контент
       - Вовлекающий
       - История / опыт
       - Ответы на боли и вопросы ЦА
       - Уникальные фишки

    3. Построй контент-план на 7 или 14 дней (если срок не указан — по умолчанию 7).
    4. Учитывай: ты создаёшь только идеи для текстовых постов и каруселей. Видео и Reels — не включать.

    📦 Формат ответа:

    🗓 Контент-план на [7/14] дней для [ниша пользователя]:

    📍 День 1
    Тип: Пост / Карусель
    Рубрика: [например: Вовлекающий, Прогрев, Продажа]
    Тема: ...
    Заголовок: ...
    Описание идеи: ...
    Призыв к действию: ...

    📍 День 2
    ...

    💡 Дополнительно:
    – Если пользователь дал мало информации — предложи 1–2 гипотезы и вариант на выбор.
    – Пиши конкретно: каждая идея должна быть чёткой, без воды, без банальщины.
    – Подстраивай стиль под нишу: экспертный, мягкий, личный, дерзкий и т.д.
    – Помни: ты не просто предлагаешь темы — ты помогаешь вести блог осознанно, системно и результативно.

    Ты — продюсер контента в текстах, твой фокус — глубина, польза, вовлечение и продажи через посты и карусели.
   
    ###Максимум 4000 символов!
    Используй базовый Markdown для форматирования: *жирный текст* для выделения важной информации, _курсив_ для акцентов, `код` для технических терминов. Не используй заголовки и разделители при генерации ответа."
    """
    
    # Получение ответа от OpenAI
    try:
        response = await generate_ai_response(model, raw_data, prompt)
    except Exception as e:
        logging.error(f"Ошибка OpenAI при генерации контент-плана для постов {user_id}: {e}")
        await wait_msg.edit_text("❌ Произошла ошибка при генерации контент-плана.")
        return
    
    # Удаление сообщения о ожидании
    await wait_msg.delete()
    
    # Сохраняем полученный ответ в состоянии для дальнейшего использования
    await state.update_data(previous_ai_response=response)

    # Отправка результатов пользователю
    result_header = "✅ *Контент-план для постов готов!*"
    full_response = result_header + response
    # Проверяем длину ответа
    if len(full_response) > 4000:
        await message.answer(result_header + "План слишком длинный, отправляю частями:", parse_mode="Markdown")
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for i, chunk in enumerate(chunks):
            await message.answer(f"Часть {i+1}/{len(chunks)}:\n\n{chunk}")
    else:
        await message.answer(full_response, parse_mode="Markdown")

    # Переход к состоянию обсуждения
    await state.set_state(ContentPlanStates.ContentPlanPostsReview)
    await message.answer(
        f"✅ Вот контент-план для ваших постов! Вы можете:\n"
        f"1️⃣ Уточнить детали по конкретным постам\n"
        f"2️⃣ Попросить изменить тематику или формат\n"
        f"3️⃣ Запросить дополнительные идеи\n"
        f"Или нажмите 'Завершить диалог' 🚪, чтобы вернуться в главное меню.",
        reply_markup=get_cancel_dialog_keyboard()
    )

@content_plan_router.message(ContentPlanStates.ContentPlanPostsReview)
async def content_plan_posts_review(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    model = await get_user_model(user_id)

    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для доработки плана требуется активная подписка.",
            reply_markup=get_cancel_dialog_keyboard() 
        )
        return

    # Отправка сообщения о начале генерации
    wait_msg = await message.answer("🔄 Обрабатываю ваш запрос...")
    
    state_data = await state.get_data()
    content_plan_info = state_data.get("content_plan_info", "")
    previous_ai_response = state_data.get("previous_ai_response", "") # Получаем предыдущий ответ AI
    user_request = message.text # Новый запрос пользователя
    
    # Формирование промпта для OpenAI
    prompt = f"""
    Ты продолжаешь диалог с пользователем по контент-плану для Instagram постов.
    
    Первоначальная информация от пользователя (ниша, ЦА): {content_plan_info}
    
    Предыдущий сгенерированный тобой ответ (контент-план):
    {previous_ai_response}
    
    Твоя задача: Ответь на новый запрос пользователя, учитывая всю предыдущую информацию и контекст.
    Если пользователь просит уточнить детали поста, расскажи подробнее. Если просит изменить тематику, предложи альтернативы.
    Используй базовый Markdown для форматирования: *жирный текст* для выделения важной информации, _курсив_ для акцентов, `код` для технических терминов. Не используй заголовки и разделители при генерации ответа."
    """
    
    # Получение ответа от OpenAI
    try:
        response = await generate_ai_response(model, user_request, prompt)
    except Exception as e:
        logging.error(f"Ошибка OpenAI при доработке контент-плана для постов {user_id}: {e}")
        await wait_msg.edit_text("❌ Произошла ошибка при обработке вашего запроса.")
        return
    
    # Удаление сообщения о ожидании
    await wait_msg.delete()
    
    # Обновляем сохраненный ответ AI новым результатом
    await state.update_data(previous_ai_response=response)

    # Отправка результатов пользователю
    result_header = "✅ *План доработан!*"
    full_response = result_header + response
    # Проверяем длину ответа
    if len(full_response) > 4000:
        await message.answer(result_header + "Обновленный план слишком длинный, отправляю частями:", parse_mode="Markdown")
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for i, chunk in enumerate(chunks):
            await message.answer(f"Часть {i+1}/{len(chunks)}:\n\n{chunk}")
    else:
        await message.answer(full_response, parse_mode="Markdown", reply_markup=get_cancel_dialog_keyboard())

    await message.answer(
        f"Хотите внести еще правки или завершить диалог?",
        reply_markup=get_cancel_dialog_keyboard()
    )
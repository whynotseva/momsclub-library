import asyncio
import logging
import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from dotenv import load_dotenv
from config import OPENAI_API_KEY
from aiogram.filters import Command
from database import Database
from hendler.helpers import get_main_menu_reply_keyboard, get_ai_tools_keyboard
from ai_tools.ai_tools import generate_ai_response, get_user_model, get_openai_client, check_user_access
from moms_club_auth import MOMS_CLUB_ACCESS_DENIED_TEXT


# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка маршрута для генерации контент-плана для Reels
content_plan_reels_router = Router()

# Настройка состояний для транскрибации
class ContentPlanReelsStates(StatesGroup):
    ContentPlanReels = State()  # Ожидание информации о нише и ЦА
    ContentPlanReelsReview = State()  # Обсуждение сгенерированного плана

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@content_plan_reels_router.callback_query(F.data == "back_to_main")
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
@content_plan_reels_router.message(F.text == "Завершить диалог")
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
# КОНТЕНТ-ПЛАН ДЛЯ REELS
#

@content_plan_reels_router.message(Command("content_reels"))
async def content_plan_reels_start(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(ContentPlanReelsStates.ContentPlanReels)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await message.answer(
        "🎬 *Контент-план для Reels*\n\n"
        "Хочешь снимать Reels, которые цепляют, набирают просмотры и ведут к результату?\n\n"
        "🔍 *Напиши мне:*\n"
        "• Чем ты занимаешься?\n"
        "• В какой нише работаешь?\n"
        "• Кто твоя целевая аудитория?\n\n"
        "💡 На основе этих данных я соберу для тебя *контент-план с идеями для Reels*, которые будут *вовлекать, продавать и раскачивать твой блог*.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )

@content_plan_reels_router.callback_query(F.data == "ai_tool_content_plan_reels")
async def content_plan_reels_start(callback: types.CallbackQuery, state: FSMContext):
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
    await state.set_state(ContentPlanReelsStates.ContentPlanReels)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await callback.message.answer(
        "🎬 *Контент-план для Reels*\n\n"
        "Хочешь снимать Reels, которые цепляют, набирают просмотры и ведут к результату?\n\n"
        "🔍 *Напиши мне:*\n"
        "• Чем ты занимаешься?\n"
        "• В какой нише работаешь?\n"
        "• Кто твоя целевая аудитория?\n\n"
        "💡 На основе этих данных я соберу для тебя *контент-план с идеями для Reels*, которые будут *вовлекать, продавать и раскачивать твой блог*.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@content_plan_reels_router.message(ContentPlanReelsStates.ContentPlanReels)
async def process_content_plan_reels_info(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    model = await get_user_model(user_id)

    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для генерации контент-плана Reels требуется активная подписка."
        )
        return

    await state.update_data(reels_plan_info=message.text)
    
    # Отправка сообщения о начале генерации
    wait_msg = await message.answer("🔄 Генерирую контент-план для Reels...")
    
    raw_data = message.text

    # Формирование промпта для OpenAI
    prompt = f"""
    🎬 Контент-план для Instagram Reels

    Ты — AI-продюсер коротких видео (Reels) для Instagram с глубоким пониманием трендов, алгоритмов и видеомаркетинга.
    Твоя задача — сформировать мощный, вовлекающий и стратегически осмысленный контент-план Reels на основе информации, предоставленной пользователем.

    📌 Как работать:

    1. Проанализируй нишу, цели пользователя и стиль ведения блога (если он указан).
    2. Составь контент-план на 7 или 14 дней (по умолчанию 7 дней, если срок не указан).
    3. Используй самые актуальные форматы Reels:
       - Говорящая голова (экспертные советы)
       - Мини-влоги (повседневность, лайфстайл)
       - Тренды (адаптация трендов под нишу)
       - Полезные подборки (топ-3, топ-5)
       - Мотивационные/вдохновляющие видео
       - Обучающие мини-видео
       - Сторителлинг (истории, кейсы, ошибки)

    4. Дай чёткие и конкретные идеи для видео, указав:
       - Тип (например, экспертный совет, тренд, сторителлинг)
       - Тему и цепляющий заголовок для обложки Reels
       - Краткое описание идеи (сюжет, что показывать)
       - Основной посыл / вывод
       - Призыв к действию

    📦 Формат ответа:

    🎬 Контент-план для Reels на [7/14] дней для [ниша пользователя]:

    📍 Reels №1
    Тип: ...
    Тема: ...
    Заголовок на обложку: ...
    Идея (сюжет/что показывать): ...
    Основной посыл: ...
    Призыв к действию: ...

    📍 Reels №2
    ...

    💡 Важно:

    – Если пользователь дал мало инфы — предложи 1-2 гипотезы и уточни, что улучшит результат.
    – Генерируй конкретные идеи, которые легко снять. Не общие советы.
    – Говори языком Instagram: живо, просто и цепляюще.
    – Стиль выбирай по ситуации: экспертный, эмоциональный, юмористический, мотивирующий, искренний и т.д.
    – Добавляй рекомендации, если знаешь подходящие тренды, звуки или приёмы монтажа под тему.

    ⚠️ Не включай:  
    – Текстовые посты и карусели (фокус строго на видео Reels).

    Ты — не просто генератор идей, а AI-продюсер, который создаёт готовый к реализации контент-план для взрывных Reels, помогающих набирать подписчиков, увеличивать вовлечение и продавать через видео.

    ###Максимум 4000 символов!
    """
    
    # Получение ответа от OpenAI
    try:
        response = await generate_ai_response(model, raw_data, prompt)
    except Exception as e:
        logger.error(f"Ошибка OpenAI при генерации контент-плана для Reels {user_id}: {e}")
        await wait_msg.edit_text("❌ Произошла ошибка при генерации контент-плана Reels.")
        return
    
    # Удаление сообщения о ожидании
    await wait_msg.delete()
    
    # Сохраняем полученный ответ в состоянии для дальнейшего использования
    await state.update_data(previous_ai_response=response)

    # Отправка результатов пользователю
    result_header = "✅ *Контент-план для Reels готов!*"
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
    await state.set_state(ContentPlanReelsStates.ContentPlanReelsReview)
    await message.answer(
        f"✅ Вот контент-план для ваших Reels! 🎬\n"
        f"1️⃣ Уточнить детали по конкретным видео\n"
        f"2️⃣ Попросить более подробный сценарий для выбранной идеи\n"
        f"3️⃣ Запросить варианты с другими трендами\n"
        f"🚪 Или нажмите 'Завершить диалог', чтобы вернуться в главное меню.",
        reply_markup=get_cancel_dialog_keyboard()
    )

@content_plan_reels_router.message(ContentPlanReelsStates.ContentPlanReelsReview)
async def content_plan_reels_review(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)
    
    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    
    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для доработки плана Reels требуется активная подписка.",
            reply_markup=get_cancel_dialog_keyboard() # Добавляем клавиатуру
        )
        return

    # Отправка сообщения о начале генерации
    wait_msg = await message.answer("🔄 Обрабатываю ваш запрос...")
    
    # Получение модели пользователя и данных состояния
    model = await get_user_model(user_id)
    state_data = await state.get_data()
    reels_plan_info = state_data.get("reels_plan_info", "")
    previous_ai_response = state_data.get("previous_ai_response", "") # Получаем предыдущий ответ AI
    user_request = message.text # Новый запрос пользователя
    
    # Формирование промпта для OpenAI
    prompt = f"""
    Ты продолжаешь диалог с пользователем по контент-плану для Instagram Reels.
    
    Первоначальная информация от пользователя (ниша, ЦА): {reels_plan_info}
    
    Предыдущий сгенерированный тобой ответ (план Reels):
    {previous_ai_response}
    
    Твоя задача: Ответь на новый запрос пользователя, учитывая всю предыдущую информацию и контекст.
    Если пользователь просит уточнить сценарий, распиши его подробнее. Если просит другие тренды, предложи их.
    Используй базовый Markdown для форматирования: *жирный текст* для выделения важной информации, _курсив_ для акцентов, `код` для технических терминов. Не используй заголовки и разделители при генерации ответа."
    """
    
    # Получение ответа от OpenAI
    try:
        response = await generate_ai_response(model, user_request, prompt)
    except Exception as e:
        logger.error(f"Ошибка OpenAI при доработке контент-плана для Reels {user_id}: {e}")
        await wait_msg.edit_text("❌ Произошла ошибка при обработке вашего запроса.")
        return
    
    # Удаление сообщения о ожидании
    await wait_msg.delete()
    
    # Обновляем сохраненный ответ AI новым результатом
    await state.update_data(previous_ai_response=response)

    # Отправка результатов пользователю
    result_header = "✅ *План Reels доработан!*"
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
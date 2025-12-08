import asyncio
import logging
import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile, InputMediaPhoto, InputMediaVideo
from dotenv import load_dotenv
from config import API_KEY
import re
from aiogram.filters import Command
from database import Database
from hendler.helpers import get_main_menu_reply_keyboard, get_ai_tools_keyboard
from ai_tools.instagram_api_test import download_instagram_content_via_api
from ai_tools.ai_tools import check_user_access
from moms_club_auth import MOMS_CLUB_ACCESS_DENIED_TEXT

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройка маршрута для транскрибации
instagram_download_router = Router()

# Настройка состояний для транскрибации
class InstagramDownloadStates(StatesGroup):
    InstagramDownload = State()  # Ожидание ссылки на контент

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@instagram_download_router.callback_query(F.data == "back_to_main")
async def back_to_main_with_cleanup(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    keyboard = get_main_menu_reply_keyboard()
    await callback.message.answer("Вы вернулись в главное меню", reply_markup=keyboard)
    await callback.answer()

# Обработчик для команды "Завершить диалог"
@instagram_download_router.message(F.text == "Завершить диалог")
async def finish_dialog(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Диалог завершен.", 
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Получаем данные о подписке для меню AI
    db = await Database.get_instance()
    user_id = message.from_user.id
    has_subscription, _ = await db.check_subscription(user_id)
    
    keyboard = get_ai_tools_keyboard(has_subscription=has_subscription)
    image_path = "media/ai_tools.png"
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
# СКАЧИВАНИЕ КОНТЕНТА ИЗ INSTAGRAM (Обновлено)
#

@instagram_download_router.message(Command("download_inst"))
async def instagram_download_start_cmd(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(InstagramDownloadStates.InstagramDownload)
    cancel_keyboard = get_cancel_dialog_keyboard()
    await message.answer(
        "📥 *Скачать из Instagram*\n\n"
        "Хочешь сохранить пост или Reels себе?\n\n"
        "📎 *Просто отправь ссылку* на нужный контент из Instagram —\n"
        "я скачаю его для тебя и пришлю файл.\n\n"
        "📌 *Поддерживаются только публичные посты и Reels.*",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard
    )

# Функция скрыта - кнопка удалена из интерфейса
# @instagram_download_router.callback_query(F.data == "ai_tool_instagram_download")
# async def instagram_download_start_callback(callback: types.CallbackQuery, state: FSMContext):
#     user_id = callback.from_user.id
#     db = await Database.get_instance()
#     has_subscription, _ = await db.check_subscription(user_id)
#     
#     if not has_subscription:
#         from aiogram.utils.keyboard import InlineKeyboardBuilder
#         builder = InlineKeyboardBuilder()
#         
#         # Проверяем, использовал ли пользователь пробную подписку
#         has_used_trial = await db.has_used_trial_subscription(user_id)
#         
#         # Если пользователь НЕ использовал пробную подписку, показываем кнопку "Купить доступ за 1₽"
#         if not has_used_trial:
#             builder.button(text="🚀 Купить доступ за 1₽", callback_data="sub_trial")
#         
#         # Добавляем стандартную кнопку покупки подписки
#         builder.button(text="💎 Купить подписку", callback_data="buy_subscription")
#         builder.button(text="↩️ Назад", callback_data="back_to_ai_menu")
#         builder.adjust(1)
#         
#         await callback.message.edit_caption(
#             caption=(
#                 "⛔️ *Доступ ограничен*\n\n"
#                 "Этот AI инструмент доступен только для пользователей с активной подпиской.\n\n"
#                 "Приобретите подписку, чтобы получить доступ ко всем возможностям бота:\n"
#                 "• Оформление личного профиля для Instagram\n"
#                 "• Контент-план для постов и каруселей\n"
#                 "• Контент-план для Reels\n"
#                 "• Расшифровка аудио и видео\n"
#                 "• Кради как художник (анализ чужих Reels)\n"
#                 "• Генерация изображений\n"
#                 "• Скачивание постов и Reels из Instagram"
#             ),
#             reply_markup=builder.as_markup(),
#             parse_mode="Markdown"
#         )
#         await callback.answer("Требуется подписка для использования этого инструмента")
#         return
#     
#     await callback.message.delete()
#     await state.set_state(InstagramDownloadStates.InstagramDownload)
#     cancel_keyboard = get_cancel_dialog_keyboard()
#     await callback.message.answer(
#         "📥 *Скачать из Instagram*\n\n"
#         "Хочешь сохранить пост или Reels себе?\n\n"
#         "📎 *Просто отправь ссылку* на нужный контент из Instagram —\n"
#         "я скачаю его для тебя и пришлю файл.\n\n"
#         "📌 *Поддерживаются только публичные посты и Reels.*",
#         parse_mode="Markdown",
#         reply_markup=cancel_keyboard
#     )
#     await callback.answer()

@instagram_download_router.message(InstagramDownloadStates.InstagramDownload)
async def process_instagram_download(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    input_text = message.text

    # Базовая проверка на текст и команду завершения
    if not input_text or input_text == "Завершить диалог":
        if input_text == "Завершить диалог":
            return await finish_dialog(message, state)
        else:
            await message.answer("⚠️ Пожалуйста, отправьте ссылку на пост или рилс из Instagram.")
            return

    # Улучшенное извлечение URL, включая варианты с ddinstagram и необязательные параметры
    url_pattern = r'https?://(?:www\.)?(?:instagram\.com|ddinstagram\.com)/(?:p|reel|stories)/[\w.-]+/?(?=\s|$|\?)'
    url_match = re.search(url_pattern, input_text)

    if not url_match:
        logger.warning(f"Не найдена корректная ссылка Instagram в сообщении от {user_id}: {input_text}")
        await message.answer("⚠️ Не удалось найти корректную ссылку Instagram в вашем сообщении. Убедитесь, что ссылка верна и ведет на публичный пост или Reels.")
        return

    # Извлекаем найденный URL и убираем слэш в конце
    found_url = url_match.group(0).strip('/')
    logger.info(f"Найдена ссылка Instagram от {user_id}: {found_url}")

    # Проверяем тип ссылки (поддерживаем только посты и рилсы)
    if '/stories/' in found_url:
        await message.answer("❌ Извините, скачивание Stories пока не поддерживается этим API.")
        # Предлагаем продолжить или завершить
        await message.answer(
            "Пришлите ссылку на пост или Reels, или нажмите 'Завершить диалог'.",
            reply_markup=get_cancel_dialog_keyboard()
        )
        return # Остаемся в том же состоянии

    # Определяем тип контента (для сообщения пользователю)
    content_type = "рилс" if "/reel/" in found_url else "пост"

    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)

    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для скачивания контента требуется активная подписка."
        )
        return

    # Сообщаем о начале скачивания через API
    processing_message = await message.answer(f"⏳ Начинаю скачивание {content_type}... Пожалуйста, подождите.")

    # Изменили переменную на список
    downloaded_file_paths: list[str] | None = None 
    try:
        # Создаем директорию для сохранения временных файлов (если ее нет)
        output_dir = f"downloads/instagram/{user_id}"

        # Вызываем обновленную функцию, ожидаем список
        downloaded_file_paths = await download_instagram_content_via_api(
            api_key=API_KEY, 
            instagram_url=found_url, 
            download_folder=output_dir, 
            user_id=user_id
        )

        # Проверяем результат (список путей)
        if not downloaded_file_paths:
            logger.warning(f"Не удалось скачать контент для URL {found_url} от пользователя {user_id}")
            await processing_message.edit_text("❌ Не удалось скачать контент. Возможно, API недоступен, ссылка неверна, пост приватный или удален.")
             # Предлагаем продолжить или завершить
            await message.answer(
                "Попробуйте другую ссылку или нажмите 'Завершить диалог'.",
                reply_markup=get_cancel_dialog_keyboard()
            )
            return # Остаемся в состоянии

        # Удаляем сообщение о процессе
        try:
            await processing_message.delete()
        except Exception as del_err:
            logger.warning(f"Не удалось удалить сообщение о процессе: {del_err}")

        # Отправляем сообщение с успешным результатом
        await message.answer(
            f"✅ {content_type.capitalize()} успешно скачан!\n"
            f"Отправляю медиа ({len(downloaded_file_paths)} шт.)..."
        )

        # --- Логика отправки одного файла или медиагруппы --- 
        if len(downloaded_file_paths) == 1:
            # Отправляем один файл
            file_path = downloaded_file_paths[0]
            file_ext = os.path.splitext(file_path)[1].lower()
            input_file = FSInputFile(file_path)
            try:
                if file_ext in ['.jpg', '.jpeg', '.png']:
                    await message.answer_photo(input_file)
                elif file_ext in ['.mp4', '.mov']:
                    await message.answer_video(input_file)
                else:
                    logger.warning(f"Неизвестное расширение {file_ext}, отправляем как документ.")
                    await message.answer_document(input_file)
                logger.info(f"Одиночный файл {file_path} отправлен {user_id}")
            except Exception as send_err:
                logger.error(f"Ошибка отправки одиночного файла {file_path} для {user_id}: {send_err}")
                await message.answer(f"⚠️ Не удалось отправить файл {os.path.basename(file_path)}.")
        
        elif len(downloaded_file_paths) > 1:
            # Отправляем медиагруппу (до 10 элементов)
            media_group = []
            # Ограничиваем 10 элементами для Telegram
            for file_path in downloaded_file_paths[:10]: 
                file_ext = os.path.splitext(file_path)[1].lower()
                input_file = FSInputFile(file_path)
                
                if file_ext in ['.jpg', '.jpeg', '.png']:
                    media_group.append(InputMediaPhoto(media=input_file))
                elif file_ext in ['.mp4', '.mov']:
                     media_group.append(InputMediaVideo(media=input_file)) 
                else:
                    logger.warning(f"Пропуск файла с неизвестным расширением {file_ext} в медиагруппе.")

            if media_group:
                try:
                    await message.answer_media_group(media=media_group)
                    logger.info(f"Медиагруппа ({len(media_group)} шт.) отправлена {user_id} для {found_url}")
                except Exception as send_err:
                    # Если ошибка медиагруппы, пробуем отправить по одному
                    logger.error(f"Ошибка отправки медиагруппы для {user_id}: {send_err}. Пробуем по одному.")
                    await message.answer("⚠️ Не удалось отправить медиа группой. Попробую отправить по одному:")
                    for file_path in downloaded_file_paths[:10]:
                         input_file_single = FSInputFile(file_path)
                         file_ext_single = os.path.splitext(file_path)[1].lower()
                         try:
                              if file_ext_single in ['.jpg', '.jpeg', '.png']:
                                   await message.answer_photo(input_file_single)
                              elif file_ext_single in ['.mp4', '.mov']:
                                   await message.answer_video(input_file_single)
                              else:
                                   await message.answer_document(input_file_single)
                              await asyncio.sleep(0.5) # Небольшая задержка между файлами
                         except Exception as send_single_err:
                              logger.error(f"Ошибка отправки файла {file_path} по одному: {send_single_err}")
                              await message.answer(f"⚠️ Не удалось отправить файл {os.path.basename(file_path)}.")
            else:
                 logger.warning(f"Не удалось создать медиагруппу для {user_id} (нет подходящих файлов?).")
                 await message.answer("⚠️ Не удалось сгруппировать медиа файлы для отправки.")
        
        # Если было больше 10 файлов, сообщаем об этом
        if len(downloaded_file_paths) > 10:
             await message.answer(f"⚠️ В посте было больше 10 медиафайлов. Отправлены первые 10.")
             
        # Предлагаем скачать еще
        await message.answer(
            f"✅ Готово!\n"
            "Пришлите следующую ссылку для скачивания или нажмите 'Завершить диалог'.",
            reply_markup=get_cancel_dialog_keyboard()
        )
        
        # Остаемся в текущем состоянии для следующей загрузки

    except Exception as e:
        logger.exception(f"Критическая ошибка при обработке ссылки {found_url} для пользователя {user_id}: {e}")
        try:
            await processing_message.edit_text(f"❌ Произошла критическая ошибка: {str(e)}")
        except Exception: # Если сообщение уже удалено или недоступно
            await message.answer(f"❌ Произошла критическая ошибка: {str(e)}")
        await state.clear() # Очищаем состояние в случае КРИТИЧЕСКОЙ ошибки
    finally:
        # Удаляем все временные файлы из списка
        if downloaded_file_paths:
            for file_path in downloaded_file_paths:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Удален временный файл: {file_path}")
                    except Exception as e:
                        logger.error(f"Ошибка при удалении временного файла {file_path}: {e}")

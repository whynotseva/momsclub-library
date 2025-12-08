import asyncio
import logging
import os
from typing import Optional
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command
from openai import OpenAI
from dotenv import load_dotenv
from config import OPENAI_API_KEY, API_KEY
from database import Database
import re
from hendler.helpers import get_main_menu_reply_keyboard, get_ai_tools_keyboard
from ai_tools.ai_tools import generate_ai_response, get_user_model, check_ffmpeg_installed, FFMPEG_PATH, check_user_access
from ai_tools.instagram_api_test import download_instagram_content_via_api
from moms_club_auth import MOMS_CLUB_ACCESS_DENIED_TEXT

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

# Настройка маршрута для транскрибации
still_inst_reels_router = Router()

# Настройка состояний для анализа Reels
class StillInstReelsStates(StatesGroup):
    ReelsAnalysis = State()  # Ожидание видео или ссылки для анализа
    ReelsAnalysisReview = State() # Ожидание обратной связи по сгенерированному сценарию

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@still_inst_reels_router.callback_query(F.data == "back_to_main")
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
@still_inst_reels_router.message(F.text == "Завершить диалог")
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
# КРАДИТЬ КАК ХУДОЖНИК
#

@still_inst_reels_router.message(Command("steal_reels"))
async def reels_analysis_start_cmd(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(StillInstReelsStates.ReelsAnalysis)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await message.answer(
        "🥷 *Кради как художник*\n"
        "Хочешь сделать круче, чем у конкурента?\n"
        "📎 Пришли ссылку на *разговорный Reels* или пост с *говорящей головой* из Instagram.\n"
        "Я:\n"
        "• скачаю видео\n"
        "• извлеку аудио\n"
        "• расшифрую текст\n"
        "• проанализирую сценарий\n"
        "• и выдам тебе улучшенную версию — с твоим стилем и сильной подачей!\n\n"
        "🔥 Работает только с *разговорными форматами* — когда кто-то говорит в кадре.\n"
        "📌 Поддерживаются только публичные посты и Reels.\n\n"
        "_Тарификация будет завсисеть от выбранной вами модели._",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )

@still_inst_reels_router.callback_query(F.data == "ai_tool_reels_analysis")
async def reels_analysis_start(callback: types.CallbackQuery, state: FSMContext):
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
    await state.set_state(StillInstReelsStates.ReelsAnalysis)
    
    # Устанавливаем клавиатуру для отмены диалога
    cancel_keyboard = get_cancel_dialog_keyboard()
    
    await callback.message.answer(
        "🥷 *Кради как художник*\n"
        "Хочешь сделать круче, чем у конкурента?\n"
        "📎 Пришли ссылку на *разговорный Reels* или пост с *говорящей головой* из Instagram.\n"
        "Я:\n"
        "• скачаю видео\n"
        "• извлеку аудио\n"
        "• расшифрую текст\n"
        "• проанализирую сценарий\n"
        "• и выдам тебе улучшенную версию — с твоим стилем и сильной подачей!\n\n"
        "🔥 Работает только с *разговорными форматами* — когда кто-то говорит в кадре.\n"
        "📌 Поддерживаются только публичные посты и Reels.\n\n"
        "_Тарификация будет завсисеть от выбранной вами модели._",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@still_inst_reels_router.message(StillInstReelsStates.ReelsAnalysis, F.video | F.document)
async def process_reels_video(message: types.Message, state: FSMContext, downloaded_file_path: Optional[str] = None):
    user_id = message.from_user.id

    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    
    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для анализа Reels требуется активная подписка."
        )
        return

    model = await get_user_model(user_id) 

    wait_msg = await message.answer("🔄 <b>Этап 2/5:</b> Начинаю обработку видео...", parse_mode="HTML")

    temp_files_to_delete = []
    processing_file_path = None
    audio_path = None
    is_mov = False 
    try:
        temp_dir = f"temp_files/{user_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            logger.info(f"Используем файл, скачанный через API: {downloaded_file_path}")
            processing_file_path = downloaded_file_path
            temp_files_to_delete.append(processing_file_path) 
            is_mov = processing_file_path.lower().endswith('.mov')
            await wait_msg.edit_text("✅ Видео скачано, начинаю обработку...") 
        else:
            await wait_msg.edit_text("🔄 Файл получен, обрабатываю...") 
            file_id = None
            file_name = None
            
            if message.video:
                file_id = message.video.file_id
                file_name = message.video.file_name or f"video_{message.video.file_id}.mp4"
                is_mov = file_name.lower().endswith('.mov')
            elif message.document:
                mime_type = message.document.mime_type or ""
                file_name = message.document.file_name or f"document_{message.document.file_id}"
                if (mime_type.startswith("video/") or mime_type == "video/quicktime" or 
                    (file_name and file_name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')))):
                    file_id = message.document.file_id
                    is_mov = file_name.lower().endswith('.mov') or mime_type == "video/quicktime"
                else:
                    await wait_msg.edit_text("❌ Неподдерживаемый тип документа. Отправьте видеофайл.")
                    return
            
            if not file_id:
                await wait_msg.edit_text("❌ Не удалось определить видеофайл.")
                return
            
            file_info = await message.bot.get_file(file_id)
            if file_info.file_size > 25 * 1024 * 1024:
                await wait_msg.edit_text("❌ Файл слишком большой (> 25 МБ).")
                return
                
            downloaded_file_bytes = await message.bot.download_file(file_info.file_path)
            processing_file_path = os.path.join(temp_dir, f"input_{user_id}_{file_name}")
            with open(processing_file_path, "wb") as f:
                f.write(downloaded_file_bytes.read())
            temp_files_to_delete.append(processing_file_path)
        
        ffmpeg_installed = await check_ffmpeg_installed()
        if not ffmpeg_installed:
            logger.error("FFmpeg не установлен! Невозможно извлечь аудио для анализа.")
            await wait_msg.edit_text("❌ Ошибка сервера: FFmpeg не найден. Обработка невозможна.")
            return

        if is_mov:
            await wait_msg.edit_text("🔄 Конвертирую MOV в MP4...")
            mp4_file_path = os.path.join(temp_dir, f"converted_{user_id}.mp4")
            temp_files_to_delete.append(mp4_file_path)
            try:
                cmd = [FFMPEG_PATH, "-y", "-i", processing_file_path,
                       "-c:v", "libx264", "-preset", "fast", "-c:a", "aac",
                       "-b:a", "192k", "-pix_fmt", "yuv420p", mp4_file_path]
                logger.info(f"Конвертирую MOV: {' '.join(cmd)}")
                process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                _, stderr = await process.communicate()
                if process.returncode != 0:
                    raise Exception(f"Ошибка конвертации MOV: {stderr.decode()}")
                if not os.path.exists(mp4_file_path) or os.path.getsize(mp4_file_path) == 0:
                    raise Exception("Не удалось сконвертировать MOV в MP4.")
                processing_file_path = mp4_file_path 
                await wait_msg.edit_text("✅ MOV конвертирован, извлекаю аудио...")
            except Exception as conv_err:
                logger.error(f"Ошибка конвертации MOV для {user_id}: {conv_err}")
                await wait_msg.edit_text("⚠️ Не удалось конвертировать MOV. Попробую обработать исходный файл...")

        extracted_audio_path = os.path.join(temp_dir, f"extracted_audio_{user_id}.mp3")
        temp_files_to_delete.append(extracted_audio_path)
        try:
            await wait_msg.edit_text("🔄 Извлекаю аудио из видео...")
            cmd = [FFMPEG_PATH, "-y", "-i", processing_file_path, 
                   "-vn", "-acodec", "libmp3lame", "-ar", "44100", 
                   "-ab", "192k", "-f", "mp3", extracted_audio_path]
            logger.info(f"Извлекаю аудио: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            _, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Ошибка извлечения аудио: {stderr.decode()}")
            if not os.path.exists(extracted_audio_path) or os.path.getsize(extracted_audio_path) == 0:
                raise Exception("Не удалось извлечь аудио.")
            audio_path = extracted_audio_path
        except Exception as extr_err:
            logger.error(f"Ошибка извлечения аудио для {user_id}: {extr_err}")
            await wait_msg.edit_text("❌ Ошибка при извлечении аудио из видео.")
            return

        try:
            await wait_msg.edit_text("✅ <b>Этап 2 завершен</b> — аудио извлечено!\n🔄 <b>Этап 3/5:</b> Транскрибирую текст...", parse_mode="HTML")
            with open(audio_path, "rb") as audio_file_obj:
                transcription = await asyncio.to_thread(
                    client.audio.transcriptions.create,
                    file=audio_file_obj,
                    model="whisper-1"
                )
            raw_text = transcription.text
            await state.update_data(original_transcription=raw_text)
            logger.info(f"Транскрибация для анализа Reels ({user_id}) завершена. Длина: {len(raw_text)}")
        except Exception as whisper_err:
            logger.error(f"Ошибка Whisper API для анализа Reels ({user_id}): {whisper_err}")
            await wait_msg.edit_text("❌ Ошибка при транскрибации аудио.")
            return

        await wait_msg.edit_text("✅ <b>Этап 3 завершен</b> — текст расшифрован!\n🔄 <b>Этап 4/5:</b> Генерирую улучшенный сценарий...", parse_mode="HTML")
        analysis_prompt = f"""
        Ты — Instagram-продюсер с 50-летним стажем, эксперт по созданию уникальных, захватывающих и высококонверсионных коротких видео формата Reels и Shorts.

        Отнесись к этой задаче как к самому приоритетному проекту.
        Ты создаёшь уникальные сценарии, вдохновлённые идеей чужого видео, но выполненные полностью по-новому: со своей драматургией, подачей, голосом и визуалом.

        🎯 Твоя задача:
        1. Получи текст оригинального Reels.
        2. Определи основную идею и посыл.
        3. На её основе создай полноценный, готовый сценарий для нового Reels, который:
           – цепляет с первых секунд;
           – не повторяет структуру и фразы оригинала;
           – даёт новую подачу и энергию;
           – помогает пользователю легко снять свой ролик.

        📦 Формат твоего ответа:

        🎬 *Готовый сценарий Reels по мотивам оригинала*

        🔥 *Заголовок (обложка):*
        [максимально кликабельный заголовок]

        🎤 *Текст/реплики (что говорить):*
        [Полный сценарий, как будто ты диктуешь текст автору — от первой до последней фразы. С конкретными формулировками, юмором, фреймами, акцентами]

        🎥 *Что показывать в кадре:*
        [Пошагово, с визуальными идеями — как снимать, какие сцены, какие детали или эмоции в кадре]

        🎯 *Призыв к действию (в конце):*
        [Что должен сделать зритель: написать в комменты, перейти по ссылке, сохранить, подписаться и т.п.]

        🧠 *Комментарий для автора (если нужно):*
        [1–2 строки: зачем такая структура, как подать сильнее, как усилить ролик]

        ⛔️ *Запрещено:*
        – Повторять структуру или текст оригинала
        – Переписывать синонимами
        – Делать пересказ — только новая форма

        💡 *Напоминание:*
        Ты — не помощник. Ты — автор сценария, который потом увидят тысячи людей.
        Каждый твой ролик — это мощный месседж, стиль и результат.
        Думай, как креативный продюсер и копирайтер в одном лице.
        """
        try:
            analysis_text = await generate_ai_response(model, raw_text, analysis_prompt)
        except Exception as gpt_err:
            logger.error(f"Ошибка GPT при анализе Reels для {user_id}: {gpt_err}")
            await wait_msg.edit_text("❌ Ошибка AI при генерации сценария.")
            return

        result_header = f"✅ <b>Все этапы завершены!</b> 🎉\n\n<i>Готовый анализ и сценарий:</i>\n\n"
        full_result_message = result_header + analysis_text

        if len(full_result_message) > 4000:
            await wait_msg.edit_text(result_header + "Результат будет отправлен частями.", parse_mode="HTML")
            chunks = [analysis_text[i:i+4000] for i in range(0, len(analysis_text), 4000)]
            for i, chunk in enumerate(chunks):
                await message.answer(f"<b>Часть {i+1}/{len(chunks)}:</b>\n\n{chunk}", parse_mode="HTML")
        else:
            await message.answer(full_result_message, parse_mode="HTML")
            try:
                await wait_msg.delete() 
            except Exception: pass 

        await state.update_data(generated_script=analysis_text)
        await state.set_state(StillInstReelsStates.ReelsAnalysisReview)
        await message.answer(
            f"✅ Сценарий готов! Хотите что-то уточнить или изменить?\n"
            f"Напишите ваши правки. Каждая доработка требует активной подписки.\n"
            f"Или нажмите 'Завершить диалог'.",
            reply_markup=get_cancel_dialog_keyboard()
        )

    except Exception as e:
        logger.exception(f"Критическая ошибка при обработке видеофайла для анализа Reels ({user_id}): {e}")
        try:
            await message.answer(f"❌ Произошла критическая ошибка: {str(e)}")
            await wait_msg.delete() 
        except Exception: pass
    finally:
        for temp_file in temp_files_to_delete:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.info(f"Удален временный файл: {temp_file}")
                except Exception as rem_err:
                    logger.error(f"Ошибка удаления временного файла {temp_file}: {rem_err}")

# Обработчик для ТЕКСТОВЫХ сообщений (ссылки Instagram)
@still_inst_reels_router.message(StillInstReelsStates.ReelsAnalysis)
async def reels_analysis_text_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    input_text = message.text

    if not input_text or input_text == "Завершить диалог":
        if input_text == "Завершить диалог":
            return await finish_dialog(message, state)
        else:
            await message.answer(
                "Пожалуйста, отправьте ссылку на Instagram пост/рилс или видеофайл.",
                reply_markup=get_cancel_dialog_keyboard()
            )
            return

    url_pattern = r'https?://(?:www\.)?(?:instagram\.com|ddinstagram\.com)/(?:p|reel|stories)/[\w.-]+/?(?=\s|$|\?)'
    url_match = re.search(url_pattern, input_text)

    if not url_match:
        await message.answer(
            "Пожалуйста, отправьте ссылку на Instagram пост/рилс или видеофайл.",
            reply_markup=get_cancel_dialog_keyboard()
        )
        return

    found_url = url_match.group(0).strip('/')
    logger.info(f"Найдена ссылка Instagram от {user_id} для анализа Reels: {found_url}")

    if '/stories/' in found_url:
        await message.answer("❌ Скачивание Stories не поддерживается для анализа.")
        await message.answer("Пришлите ссылку на пост или Reels.", reply_markup=get_cancel_dialog_keyboard())
        return

    # Проверяем наличие подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)

    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для анализа Reels по ссылке требуется активная подписка."
        )
        return

    content_type = "рилс" if "/reel/" in found_url else "пост"
    wait_msg = await message.answer(f"🔄 <b>Этап 1/5:</b> Скачиваю {content_type}... ⏱️ это может занять 1-2 минуты", parse_mode="HTML")

    downloaded_file_paths: list[str] | None = None
    first_file_path: str | None = None 

    temp_dir = f"temp_files/{user_id}" 
    try:
        downloaded_file_paths = await download_instagram_content_via_api(
            api_key=API_KEY, 
            instagram_url=found_url,
            download_folder=temp_dir, 
            user_id=user_id,
            media_type_filter='video' 
        )

        if not downloaded_file_paths:
            logger.warning(f"Не удалось скачать видео по ссылке {found_url} (тип ответа API не 'video' или ошибка).")
            await wait_msg.edit_text("❌ Не удалось скачать видео по ссылке (возможно, пост не содержит видео или API вернул не видео). Попробуйте другую ссылку или загрузите файл.")
            return
        
        video_file_path = None
        for file_path in downloaded_file_paths:
             if file_path and isinstance(file_path, str) and file_path.lower().endswith(('.mp4', '.mov')):
                 video_file_path = file_path
                 break 
                 
        if not video_file_path:
             logger.warning(f"API вернул {len(downloaded_file_paths)} файлов для {found_url}, но среди них не найдено видео (.mp4, .mov). Файлы: {downloaded_file_paths}")
             await wait_msg.edit_text("❌ Не удалось найти видеофайл среди скачанных данных.")
             return
             
        if len(downloaded_file_paths) > 1:
             logger.info(f"Для анализа Reels ({found_url}) будет использован файл {video_file_path}. Остальные скачанные файлы ({[p for p in downloaded_file_paths if p != video_file_path]}) будут удалены.")

        await wait_msg.edit_text("✅ <b>Этап 1 завершен</b> — видео скачано!\n🔄 <b>Этап 2/5:</b> Извлекаю аудио...", parse_mode="HTML")

        await process_reels_video(message, state, downloaded_file_path=video_file_path)

    except Exception as e:
        logger.exception(f"Критическая ошибка при обработке Instagram ссылки для анализа Reels {found_url} ({user_id}): {e}")
        try:
            await message.answer(f"❌ Произошла критическая ошибка: {str(e)}")
            await wait_msg.delete()
        except Exception: pass
        await state.clear()
    finally:
        if downloaded_file_paths:
            for file_path in downloaded_file_paths:
                if file_path and isinstance(file_path, str) and os.path.exists(file_path):
                    try:
                        os.remove(file_path) 
                        logger.info(f"Удален временный файл (из списка API): {file_path}")
                    except Exception as rem_err:
                        logger.error(f"Ошибка удаления временного файла {file_path} (из списка API): {rem_err}")

# Обработчик для состояния обсуждения сгенерированного сценария
@still_inst_reels_router.message(StillInstReelsStates.ReelsAnalysisReview)
async def reels_analysis_review(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text == "Завершить диалог":
        return await finish_dialog(message, state)

    # Проверка наличия подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)

    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для доработки сценария требуется активная подписка.",
            reply_markup=get_cancel_dialog_keyboard()
        )
        return

    wait_msg = await message.answer("🔄 Обрабатываю ваш запрос...")

    model = await get_user_model(user_id)
    state_data = await state.get_data()
    original_transcription = state_data.get("original_transcription", "Не найдено")
    previous_script = state_data.get("generated_script", "Не найдено")
    user_request = message.text

    prompt = f"""
    🤖 Ты — AI-драматург, продолжающий диалог с пользователем по улучшению сценария Reels.

    📜 Исходная расшифровка оригинального Reels:
    "{original_transcription}"

    📝 Предыдущий сгенерированный тобой сценарий:
    "{previous_script}"

    🎯 Твоя задача:
    1. Внимательно проанализируй запрос пользователя.
    2. Внеси изменения в *предыдущий сгенерированный сценарий*, учитывая пожелания пользователя.
    3. Сохраняй основную структуру и формат ответа, который ты давал ранее (Концепция/фрейм, Структура, Тезисы и т.д.), но модифицируй содержание согласно запросу.
    4. Если запрос непонятен или слишком абстрактный, уточни его или предложи свой вариант доработки.
    5. Сохраняй стиль Instagram-продюсера.

    💡 Действуй как ассистент, помогающий довести идею до идеала.

    📝 Формат твоего ответа (сохраняй структуру):
    *Обновленный сценарий Reels по вашему запросу:*

    🎬 Обновленный сценарий:
    - Концепция/фрейм: ...
    - Структура: ...
    - Тезисы/что сказать: ...
    - Визуальные рекомендации: ...
    - Стиль и тон: ...
    - CTA: ...

    🚫 Не нужно заново пересказывать идею оригинала или повторять старый сценарий без изменений. Сразу давай обновленную версию.
    Используй базовый Markdown для форматирования: *жирный текст* для выделения важной информации, _курсив_ для акцентов. Не используй заголовки h1-h6 и разделители ---.
    """

    try:
        response = await generate_ai_response(model, user_request, prompt)
        await wait_msg.delete()
        await state.update_data(generated_script=response)

        result_header = "✅ *Сценарий доработан!*"
        await message.answer(result_header + "\n\n" + response, reply_markup=get_cancel_dialog_keyboard())
        await message.answer(
            f"Что скажете? Вносим еще правки или завершаем? Каждая доработка требует активной подписки.",
            reply_markup=get_cancel_dialog_keyboard()
        )

    except Exception as e:
        logger.error(f"Ошибка GPT при доработке сценария Reels для {user_id}: {e}")
        await wait_msg.edit_text("❌ Ошибка AI при обработке вашего запроса.")
        await message.answer(
            "Не удалось обработать ваш запрос. Попробуйте еще раз или завершите диалог.",
            reply_markup=get_cancel_dialog_keyboard()
        )
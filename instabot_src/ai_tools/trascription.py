import asyncio
import logging
import os
import re
from typing import Optional
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command
from dotenv import load_dotenv
from config import OPENAI_API_KEY, API_KEY 
from database import Database
from hendler.helpers import get_main_menu_reply_keyboard, get_ai_tools_keyboard
from ai_tools.ai_tools import generate_ai_response, get_user_model, check_ffmpeg_installed, FFMPEG_PATH, get_openai_client, check_user_access
from ai_tools.instagram_api_test import download_instagram_content_via_api
from moms_club_auth import MOMS_CLUB_ACCESS_DENIED_TEXT


# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройка маршрута для транскрибации
trascription_router = Router()

# Настройка состояний для транскрибации
class TranscribeStates(StatesGroup):
    TranscribeAudio = State()

# Клавиатура для завершения диалога
def get_cancel_dialog_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")]
        ],
        resize_keyboard=True
    )

# Обработчик для возврата в главное меню
@trascription_router.callback_query(F.data == "back_to_main")
async def back_to_main_with_cleanup(callback: types.CallbackQuery, state: FSMContext):
    # Очистка состояния
    await state.clear()
    await callback.message.delete()
    keyboard = get_main_menu_reply_keyboard()
    await callback.message.answer("Вы вернулись в главное меню", reply_markup=keyboard)
    await callback.answer()

# Обработчик для команды "Завершить диалог"
@trascription_router.message(F.text == "Завершить диалог")
async def finish_dialog(message: types.Message, state: FSMContext):
    # Очистка состояния
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
# РАСШИФРОВКА АУДИО/ВИДЕО
#

@trascription_router.message(Command("transcribe"))
async def transcribe_start_cmd(message: types.Message, state: FSMContext):
    await message.delete()
    await state.set_state(TranscribeStates.TranscribeAudio)
    cancel_keyboard = get_cancel_dialog_keyboard()
    text = (
        "🎙️ *Расшифровка речи из видео, аудио и голосовых сообщений*\n"
        "Хочешь превратить видео или голос в текст — для подписей, сценариев или постов?\n\n"
        "📎 Просто пришли:\n"
        "• ссылку на видео из Instagram (Reels или пост)\n"
        "• или *загрузи файл* — видео, аудио, *голосовое сообщение*\n\n"
        "Я всё сам: скачаю, обработаю и сделаю чёткую расшифровку речи в текст.\n\n"
        "Подходит для:\n"
        "• подписей к Reels\n"
        "• сценариев и скриптов\n"
        "• текстов для постов или статей\n"
        "• быстрого конспекта голосовух\n\n"
        "📌 Поддерживаются *публичные видео* из Instagram и файлы в популярных форматах (mp4, mp3, wav, m4a и др.).\n\n"
        "_Тарификация будет завсисеть от выбранной вами модели._"
    )
    await message.answer(
        text=text,
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )

@trascription_router.callback_query(F.data == "ai_tool_transcribe")
async def transcribe_start_callback(callback: types.CallbackQuery, state: FSMContext):
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
    await state.set_state(TranscribeStates.TranscribeAudio)
    cancel_keyboard = get_cancel_dialog_keyboard()
    text = (
        "🎙️ *Расшифровка речи из видео, аудио и голосовых сообщений*\n"
        "Хочешь превратить видео или голос в текст — для подписей, сценариев или постов?\n\n"
        "📎 Просто пришли:\n"
        "• ссылку на видео из Instagram (Reels или пост)\n"
        "• или *загрузи файл* — видео, аудио, *голосовое сообщение*\n\n"
        "Я всё сам: скачаю, обработаю и сделаю чёткую расшифровку речи в текст.\n\n"
        "Подходит для:\n"
        "• подписей к Reels\n"
        "• сценариев и скриптов\n"
        "• текстов для постов или статей\n"
        "• быстрого конспекта голосовух\n\n"
        "📌 Поддерживаются *публичные видео* из Instagram и файлы в популярных форматах (mp4, mp3, wav, m4a и др.).\n\n"
        "_Тарификация будет завсисеть от выбранной вами модели._"
    )
    await callback.message.answer(
        text=text,
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# Обработчик для получения файлов (аудио, видео, голос, документ) или обработки скачанных по ссылке
@trascription_router.message(TranscribeStates.TranscribeAudio, F.audio | F.voice | F.video | F.document)
# Добавляем параметр для пути к файлу
async def process_audio_video(message: types.Message, state: FSMContext, downloaded_file_path: Optional[str] = None):
    user_id = message.from_user.id
    # Этот обработчик вызывается для загруженных файлов ИЛИ из process_instagram_link

    # Проверяем наличие подписки пользователя
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    
    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для транскрибации требуется активная подписка."
        )
        return
    
    model = await get_user_model(user_id) # Для GPT улучшения

    # Используем message.answer для wait_msg
    wait_msg = await message.answer("🔄 Начинаю обработку...")
    
    temp_files_to_delete = [] # Список для временных файлов, созданных в этом обработчике
    processing_file_path = None
    audio_path = None
    is_video = False # Определяем здесь
    is_mov = False # Определяем здесь
    try:
        temp_dir = f"temp_files/{user_id}"
        os.makedirs(temp_dir, exist_ok=True)

        # --- Определение источника файла: скачан по ссылке или загружен --- 
        if downloaded_file_path and os.path.exists(downloaded_file_path):
            # Файл был скачан по ссылке и путь передан
            logger.info(f"Используем файл, скачанный через API: {downloaded_file_path}")
            processing_file_path = downloaded_file_path
            temp_files_to_delete.append(processing_file_path)
            # Определяем тип по расширению
            file_ext = os.path.splitext(processing_file_path)[1].lower()
            is_video = file_ext in ['.mp4', '.mov']
            is_mov = file_ext == '.mov'
            await wait_msg.edit_text("✅ Видео скачано, начинаю обработку для транскрибации...")
        else:
            # Файл был загружен пользователем напрямую
            await wait_msg.edit_text("🔄 Файл получен, обрабатываю...")
            file_id = None
            file_name = None
            file_extension = None # Переименовали, чтобы не конфликтовать
            
            if message.audio:
                file_id = message.audio.file_id
                file_name = message.audio.file_name or f"audio_{message.audio.file_id}.mp3"
                is_video = False
                is_mov = False
            elif message.voice:
                file_id = message.voice.file_id
                file_name = f"voice_{message.voice.file_id}.ogg"
                is_video = False
                is_mov = False
            elif message.video:
                file_id = message.video.file_id
                file_name = message.video.file_name or f"video_{message.video.file_id}.mp4"
                is_video = True
                is_mov = file_name.lower().endswith('.mov')
            elif message.document:
                mime_type = message.document.mime_type or ""
                file_name = message.document.file_name or f"document_{message.document.file_id}"
                file_extension = os.path.splitext(file_name)[1].lower()
                if (mime_type.startswith("audio/") or mime_type.startswith("video/") or 
                    mime_type == "video/quicktime" or 
                    (file_name and file_name.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a', '.mp4', '.mov', '.avi', '.mkv')))):
                    file_id = message.document.file_id
                    if (mime_type.startswith("video/") or mime_type == "video/quicktime" or 
                        (file_name and file_name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')))):
                        is_video = True
                        is_mov = file_extension == '.mov' or mime_type == "video/quicktime"
                    else:
                        is_video = False
                        is_mov = False
                else:
                    await wait_msg.edit_text(
                        "❌ Неподдерживаемый тип файла. Отправьте аудио/видео."
                    )
                    return
            
            if not file_id:
                await wait_msg.edit_text("❌ Не удалось определить тип файла.")
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
        
        # --- Конец определения источника файла --- 

        # --- Общая логика обработки (извлечение аудио, транскрибация) --- 
        if not is_video:
            audio_path = processing_file_path # Если это аудио, используем его напрямую
        else:
            # Обработка видео (конвертация MOV, извлечение аудио)
            ffmpeg_installed = await check_ffmpeg_installed()
            if not ffmpeg_installed:
                logger.warning(f"ffmpeg не установлен, пытаемся использовать видео {processing_file_path} напрямую.")
                await wait_msg.edit_text(
                    "⚠️ ffmpeg не установлен. Попробую передать видео напрямую в Whisper API..."
                )
                audio_path = processing_file_path # Пытаемся использовать видео как аудио
            else:
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
                        processing_file_path = mp4_file_path # Обновляем путь для извлечения аудио
                        await wait_msg.edit_text("✅ MOV конвертирован, извлекаю аудио...")
                    except Exception as conv_err:
                        logger.error(f"Ошибка конвертации MOV: {conv_err}")
                        await wait_msg.edit_text("⚠️ Не удалось конвертировать MOV. Попробую обработать исходный файл...")
            
                # Извлекаем аудио из видео (MP4 или исходного)
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
                    logger.error(f"Ошибка извлечения аудио: {extr_err}")
                    await wait_msg.edit_text("❌ Ошибка при извлечении аудио из видео.")
                    return

        # Проверяем наличие аудиофайла для транскрибации
        if not audio_path or not os.path.exists(audio_path):
            logger.error(f"Файл аудио для транскрибации не найден: {audio_path}")
            await wait_msg.edit_text("❌ Ошибка: не удалось подготовить аудиофайл для транскрибации.")
            return

        # Транскрибация через Whisper API
        try:
            await wait_msg.edit_text("🔄 Транскрибирую аудио...")
            client = await get_openai_client()
            with open(audio_path, "rb") as audio_file:
                transcription = await asyncio.to_thread(
                    client.audio.transcriptions.create,
                    model="whisper-1",
                    file=audio_file,
                    language="ru",
                    response_format="text"
                )
            raw_text = transcription
            model = await get_user_model(user_id)
            logger.info(f"Транскрибация для {user_id} завершена. Длина текста: {len(raw_text)}")
        except Exception as whisper_err:
            logger.error(f"Ошибка Whisper API для {user_id}: {whisper_err}")
            await wait_msg.edit_text("❌ Ошибка при транскрибации через Whisper API.")
            return

        # Улучшение текста
        await wait_msg.edit_text("🔄 Улучшаю текст...")
        prompt = (
            f"Обработай и улучши следующую транскрипцию аудио.\n\n"
            "Задачи:\n1. Исправь ошибки транскрибации\n2. Добавь пунктуацию и форматирование\n"
            "3. Раздели на абзацы для лучшей читаемости\n4. Сохрани все важные детали и информацию\n\n"
            "Не добавляй от себя дополнительное содержание или интерпретации.\n"
            "Используй базовый Markdown: *жирный текст*, _курсив_. Не используй заголовки."
        )
        try:
            improved_text = await generate_ai_response(model, raw_text, prompt)
        except Exception as gpt_err:
            logger.error(f"Ошибка GPT-4o mini при улучшении текста для {user_id}: {gpt_err}")
            await wait_msg.edit_text("⚠️ Ошибка при улучшении текста. Отправляю необработанную транскрипцию.")
            improved_text = raw_text

        # Отправка результата
        result_header = (
            f"✅ *Транскрибация завершена*\n\n"
        )
        full_result_message = result_header + improved_text

        if len(full_result_message) > 4000:
            await wait_msg.edit_text(result_header + "Текст будет отправлен несколькими сообщениями.", parse_mode="Markdown")
            chunks = [improved_text[i:i+4000] for i in range(0, len(improved_text), 4000)]
            for i, chunk in enumerate(chunks):
                await message.answer(f"Часть {i+1}/{len(chunks)}:\n\n{chunk}")
        else:
            # Используем message.answer для финального ответа
            await message.answer(full_result_message, parse_mode="Markdown")
            try:
                await wait_msg.delete() # Удаляем промежуточное сообщение
            except Exception: pass

        # Предлагаем продолжить
        await message.answer(
            "Хотите транскрибировать еще один файл (отправьте ссылку/файл) или завершить диалог?",
            reply_markup=get_cancel_dialog_keyboard()
        )

    except Exception as e:
        logger.exception(f"Критическая ошибка при обработке файла от {user_id}: {e}")
        try:
            # Используем message.answer для ошибки
            await message.answer(f"❌ Произошла критическая ошибка: {str(e)}")
            await wait_msg.delete()
        except Exception: pass
        await state.clear()
        if downloaded_file_path and os.path.exists(downloaded_file_path):
             try: os.remove(downloaded_file_path) 
             except Exception as rem_err: logger.error(f"Ошибка удаления файла {downloaded_file_path} после ошибки: {rem_err}")

# Обработчик для текстовых сообщений (ссылки Instagram)
@trascription_router.message(TranscribeStates.TranscribeAudio)
async def process_instagram_link(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    input_text = message.text

    # Проверка на команду завершения или пустой текст
    if not input_text or input_text == "Завершить диалог":
        if input_text == "Завершить диалог":
            return await finish_dialog(message, state)
        else:
             await message.answer(
                 "Пожалуйста, отправьте ссылку на Instagram пост/рилс или аудио/видео файл. "
                 "Либо нажмите 'Завершить диалог'.",
                 reply_markup=get_cancel_dialog_keyboard()
             )
             return

    # Ищем URL Instagram
    url_pattern = r'https?://(?:www\.)?(?:instagram\.com|ddinstagram\.com)/(?:p|reel|stories)/[\w.-]+/?(?=\s|$|\?)'
    url_match = re.search(url_pattern, input_text)

    if not url_match:
        await message.answer(
            "Пожалуйста, отправьте ссылку на Instagram пост/рилс или аудио/видео файл. "
            "Либо нажмите 'Завершить диалог'.",
            reply_markup=get_cancel_dialog_keyboard()
        )
        return
        
    found_url = url_match.group(0).strip('/')
    logger.info(f"Найдена ссылка Instagram от {user_id} для транскрибации: {found_url}")

    if '/stories/' in found_url:
        await message.answer("❌ Скачивание Stories пока не поддерживается.")
        await message.answer("Пришлите ссылку на пост или Reels, или аудио/видео файл.", reply_markup=get_cancel_dialog_keyboard())
        return
        
    # Проверяем наличие подписки
    db = await Database.get_instance()
    user = await db.get_user(user_id)
    if not user or not user.get("subscription_type"):
        await message.answer(
            f"❌ Для транскрибации по ссылке требуется активная подписка."
        )
        return
        
    content_type = "рилс" if "/reel/" in found_url else "пост"
    wait_msg = await message.answer(f"🔄 Начинаю скачивание {content_type} для транскрибации...⏳")

    downloaded_file_paths: list[str] | None = None # Ожидаем список
    first_file_path: str | None = None # Путь к первому файлу

    temp_dir = f"temp_files/{user_id}"
    try:
        # Скачиваем контент, ожидая список путей, ПРИМЕНЯЕМ ФИЛЬТР
        downloaded_file_paths = await download_instagram_content_via_api(
            api_key=API_KEY,
            instagram_url=found_url,
            download_folder=temp_dir,
            user_id=user_id,
            media_type_filter='video' # Фильтр для запроса к API
        )

        # Проверяем, скачался ли хотя бы один файл (API мог вернуть None)
        if not downloaded_file_paths:
            logger.warning(f"Не удалось скачать видео по ссылке {found_url} для транскрибации (тип ответа API не 'video' или ошибка).")
            await wait_msg.edit_text("❌ Не удалось скачать видео по ссылке (возможно, пост не содержит видео или API вернул не видео). Попробуйте другую ссылку или загрузите файл напрямую.")
            return
        
        # --- Ищем видеофайл (.mp4 или .mov) в списке скачанных файлов --- 
        video_file_path = None
        for file_path in downloaded_file_paths:
             if file_path and isinstance(file_path, str) and file_path.lower().endswith(('.mp4', '.mov')):
                 video_file_path = file_path
                 break
                 
        # Проверяем, нашли ли мы видеофайл
        if not video_file_path:
             logger.warning(f"API вернул {len(downloaded_file_paths)} файлов для {found_url} (транскрибация), но среди них не найдено видео (.mp4, .mov). Файлы: {downloaded_file_paths}")
             await wait_msg.edit_text("❌ Не удалось найти видеофайл среди скачанных данных.")
             # Удаление файлов будет в finally
             return
             
        # Логируем, если было скачано что-то кроме найденного видео
        if len(downloaded_file_paths) > 1:
             logger.info(f"Для транскрибации ({found_url}) будет использован файл {video_file_path}. Остальные скачанные файлы ({[p for p in downloaded_file_paths if p != video_file_path]}) будут удалены.")
             
        await wait_msg.edit_text("✅ Видео скачано, передаю на обработку...")
        # Передаем путь к видеофайлу в обработчик
        await process_audio_video(message, state, downloaded_file_path=video_file_path)
        # process_audio_video удалит этот файл, остальные удалим в finally

    except Exception as e:
        logger.exception(f"Критическая ошибка при обработке Instagram ссылки {found_url} для транскрибации ({user_id}): {e}")
        try:
            await message.answer(f"❌ Произошла критическая ошибка: {str(e)}")
            await wait_msg.delete()
        except Exception: pass
        await state.clear()
    finally:
        # Удаляем ВСЕ файлы, которые могли быть скачаны функцией API
        if downloaded_file_paths:
            for file_path in downloaded_file_paths:
                 # Доп. проверка, что файл все еще существует
                 if file_path and isinstance(file_path, str) and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        logger.info(f"Удален временный файл (из списка API): {file_path}")
                    except Exception as rem_err:
                        logger.error(f"Ошибка удаления временного файла {file_path} (из списка API): {rem_err}")
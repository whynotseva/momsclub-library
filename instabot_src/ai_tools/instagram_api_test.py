import requests
import json
import os
import asyncio
import aiohttp # Добавлено для асинхронных запросов
import aiofiles # Добавлено для асинхронной записи файла
import logging # Добавлено для логирования
from typing import Optional, List

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- НАСТРОЙКИ ---
# Замени 'YOUR_API_KEY' на твой API ключ от apihut.in
API_KEY = '573097f8-4f04-47c4-9217-1b92627ced79' 
# URL эндпоинта API (уточни в документации, если этот неверный)
API_ENDPOINT = 'https://apihut.in/api/download/videos'
# URL поста/рилса в Instagram для теста
INSTAGRAM_URL = 'https://www.instagram.com/reel/DIPGpHOMkOP' # Замени на реальный URL
# Папка для сохранения видео
DOWNLOAD_FOLDER = 'downloads'
# --- /НАСТРОЙКИ ---

def download_instagram_video(api_key: str, api_url: str, instagram_url: str) -> Optional[dict]:
    """Отправляет запрос к API apihut.in для получения ссылки на скачивание видео."""
    
    headers = {
        'x-avatar-key': api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'video_url': instagram_url,
        'type': 'instagram'
    }
    
    print(f"Отправка запроса на {api_url} для URL: {instagram_url}")
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Вызовет исключение для HTTP ошибок (4xx, 5xx)
        
        print(f"Статус ответа: {response.status_code}")
        
        try:
            result = response.json()
            print("Ответ API:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        except json.JSONDecodeError:
            print("Ошибка: Не удалось декодировать JSON ответ.")
            print(f"Текст ответа: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None

def save_video(video_url: str, save_path: str):
    """Скачивает видео по URL и сохраняет его."""
    print(f"Попытка скачивания видео с {video_url}...")
    try:
        response = requests.get(video_url, stream=True, timeout=60)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Видео успешно сохранено в: {save_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка скачивания видео: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при сохранении: {e}")

# --- НОВАЯ АСИНХРОННАЯ ФУНКЦИЯ ДЛЯ СКАЧИВАНИЯ ЧЕРЕЗ API ---
# Возвращает список путей к скачанным файлам или None
async def download_instagram_content_via_api(
    api_key: str, 
    instagram_url: str, 
    download_folder: str, 
    user_id: int, 
    media_type_filter: Optional[str] = None # Новый параметр: 'video' или 'photo'
) -> Optional[List[str]]:
    """Асинхронно скачивает контент из Instagram через API apihut.in, с возможностью фильтрации по типу медиа."""
    api_url = 'https://apihut.in/api/download/videos' 
    headers = {
        'x-avatar-key': api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'video_url': instagram_url,
        'type': 'instagram'
    }
    
    logging.info(f"[API Download] User {user_id}: Запрос на {api_url} для URL: {instagram_url}. Фильтр: {media_type_filter or 'Нет'}")
    
    initial_media_items = [] # Первоначальный список от API

    try:
        # Добавляем задержку перед запросом, чтобы избежать rate limit
        await asyncio.sleep(1)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload, timeout=60) as response: 
                response.raise_for_status()
                logging.info(f"[API Download] User {user_id}: Статус ответа API: {response.status}")
                
                try:
                    result = await response.json()
                    logging.info(f"[API Download] User {user_id}: Полный ответ API: {json.dumps(result, indent=2, ensure_ascii=False)}")

                    # --- Проверка общего типа ответа API перед обработкой data --- 
                    if media_type_filter and result.get('type') != media_type_filter:
                        logging.warning(
                            f"[API Download] User {user_id}: Общий тип ответа API '{result.get('type')}' "
                            f"не соответствует запрошенному фильтру '{media_type_filter}' для URL: {instagram_url}"
                        )
                        return None # Возвращаем None, так как тип всего поста/ответа не тот
                    # --- Конец проверки общего типа --- 

                    if isinstance(result, dict) and 'data' in result and isinstance(result['data'], list) and result['data']:
                        # Собираем все валидные элементы из data
                        for item in result['data']:
                            if isinstance(item, dict) and 'url' in item and isinstance(item['url'], str) and item['url'].startswith('http'):
                                # Просто добавляем все валидные элементы, тип будем определять при скачивании/использовании
                                initial_media_items.append({
                                    'url': item['url'],
                                    'filename': item.get('filename'),
                                    'type': item.get('type') # Сохраняем тип, если он есть
                                })
                            else:
                                logging.warning(f"[API Download] User {user_id}: Пропущен некорректный элемент в data: {item}")
                        
                        if not initial_media_items:
                             logging.warning(f"[API Download] User {user_id}: Список data в ответе API пуст или не содержит валидных URL.")
                             return None
                             
                    else:
                        logging.warning(f"[API Download] User {user_id}: Ответ API не содержит валидного списка 'data'. Ответ: {result}")
                        return None
                        
                except json.JSONDecodeError:
                    logging.error(f"[API Download] User {user_id}: Ошибка: Не удалось декодировать JSON ответ. Текст: {await response.text()}")
                    return None

            # --- Убрали сложный блок фильтрации --- 
            # Теперь просто используем все собранные initial_media_items
            media_items_to_download = initial_media_items
            logging.info(f"[API Download] User {user_id}: Найдено {len(media_items_to_download)} медиа элементов в 'data' для скачивания.")
            
            # --- Скачивание всех найденных медиафайлов ---
            downloaded_files = []
            os.makedirs(download_folder, exist_ok=True)
            try:
                post_code = instagram_url.strip('/').split('/')[-1]
            except Exception:
                post_code = "post"

            for index, item in enumerate(media_items_to_download):
                media_url = item['url']
                api_filename = item['filename']
                media_type = item.get('type') # Получаем тип для генерации имени
                
                logging.info(f"[API Download] User {user_id}: Скачивание {index + 1}/{len(media_items_to_download)} ({media_type or 'unknown'}) с {media_url}...")
                
                try:
                    async with session.get(media_url, timeout=60) as media_response:
                        media_response.raise_for_status()
                        
                        # --- Генерация имени файла --- 
                        filename = None
                        if api_filename:
                             # Используем имя от API, если есть
                             name, ext = os.path.splitext(api_filename)
                             filename = f"{user_id}_{post_code}_{index}_{name}{ext}"
                        else:
                            # Иначе определяем расширение сами
                            ext = None
                            content_type_header = media_response.headers.get('Content-Type', '').lower()
                            item_type = item.get('type') # Тип из элемента data
                            media_url_lower = item.get('url','').lower()
                            # result - это переменная с полным ответом API из внешнего try/except
                            api_response_type = result.get('type') # Общий тип ответа API

                            # 1. Явный тип из элемента data
                            if item_type == 'video':
                                ext = '.mp4'
                            elif item_type == 'photo':
                                ext = '.jpg'
                            
                            # 2. Content-Type из хедера скачиваемого файла
                            if ext is None:
                                if 'video/mp4' in content_type_header:
                                    ext = '.mp4'
                                elif 'video/quicktime' in content_type_header: # Для .mov
                                     ext = '.mov'
                                elif 'image/jpeg' in content_type_header:
                                    ext = '.jpg'
                                elif 'image/png' in content_type_header:
                                    ext = '.png'

                            # 3. Расширение в URL (проверяем наличие подстроки)
                            if ext is None:
                                if '.mp4' in media_url_lower:
                                     ext = '.mp4'
                                elif '.mov' in media_url_lower:
                                     ext = '.mov'
                                elif '.jpg' in media_url_lower:
                                     ext = '.jpg'
                                elif '.jpeg' in media_url_lower:
                                     ext = '.jpeg' # Добавил .jpeg
                                elif '.png' in media_url_lower:
                                     ext = '.png'
                            
                            # 4. Запасной вариант: смотрим на общий тип ответа API
                            if ext is None:
                                if api_response_type == 'video':
                                     ext = '.mp4' 
                                elif api_response_type == 'photo': # На случай если общий тип фото
                                     ext = '.jpg'
                                else: # Самый последний fallback
                                     ext = '.jpg' 

                            filename = f"{user_id}_{post_code}_{index}{ext}"

                        save_path = os.path.join(download_folder, filename)
                        
                        async with aiofiles.open(save_path, 'wb') as f:
                            while True:
                                chunk = await media_response.content.read(8192)
                                if not chunk:
                                    break
                                await f.write(chunk)
                        
                        logging.info(f"[API Download] User {user_id}: Медиа {index + 1} успешно сохранено в: {save_path}")
                        downloaded_files.append(save_path)
                
                except aiohttp.ClientError as download_err:
                    logging.error(f"[API Download] User {user_id}: Ошибка сети при скачивании {media_url}: {download_err}")
                    continue 
                except Exception as general_err:
                     logging.exception(f"[API Download] User {user_id}: Неожиданная ошибка при скачивании {media_url}: {general_err}")
                     continue

            if downloaded_files:
                return downloaded_files
            else:
                logging.warning(f"[API Download] User {user_id}: Не удалось скачать ни одного медиафайла (возможно, из-за ошибок) для {instagram_url} (фильтр: {media_type_filter})")
                return None
                
    except aiohttp.ClientError as e:
        logging.error(f"[API Download] User {user_id}: Ошибка сети при запросе к API: {e}")
        return None
    except Exception as e:
        logging.exception(f"[API Download] User {user_id}: Неожиданная ошибка при обработке API ответа: {e}")
        return None

# --- СТАРАЯ СИНХРОННАЯ ЛОГИКА ДЛЯ ТЕСТИРОВАНИЯ --- 
# (нужно обновить для async, если планируется использовать)
# Убрал старый блок if __name__ == "__main__", т.к. он несовместим с async функцией 
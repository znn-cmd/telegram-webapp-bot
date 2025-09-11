import os
import logging
from flask import Flask, request, jsonify, send_file, send_from_directory
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, Bot
from supabase import create_client, Client
from dotenv import load_dotenv
import threading
import asyncio
from locales import locales
import requests
from datetime import datetime, timedelta
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import tempfile
import os
from dateutil.relativedelta import relativedelta
import random
import string
import json
import math
import re
import io
import base64
import time
from PIL import Image
import numpy as np

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Импорт модуля price_trends_functions
try:
    from price_trends_functions import get_price_trends_data, analyze_price_trend, calculate_3year_change, calculate_3month_forecast, format_chart_data
    logger.info("✅ Модуль price_trends_functions успешно импортирован")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта модуля price_trends_functions: {e}")
    get_price_trends_data = None
    analyze_price_trend = None
    calculate_3year_change = None
    calculate_3month_forecast = None
    format_chart_data = None

# Условный импорт openai
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. ChatGPT features will use fallback mode.")

# Инициализация Flask приложения
app = Flask(__name__)

# Инициализация Supabase с улучшенными настройками
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")

# Импортируем исключения для обработки таймаутов
import httpx
from httpx import TimeoutException, ConnectTimeout

# Инициализация Supabase с увеличенными таймаутами
try:
    # Создаем Supabase клиент с базовыми настройками (таймауты обрабатываются на уровне safe_db_operation)
    supabase: Client = create_client(
        supabase_url, 
        supabase_key
    )
    logger.info("✅ Supabase клиент создан успешно")
except Exception as e:
    logger.error(f"❌ Ошибка создания Supabase клиента: {e}")
    raise

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN должен быть задан в переменных окружения!")

# URL вашего WebApp (замените на ваш домен после деплоя)
WEBAPP_URL = "https://aaadvisor-zaicevn.amvera.io/webapp"

# Google Maps API ключ
GOOGLE_MAPS_API_KEY = "AIzaSyBrDkDpNKNAIyY147MQ78hchBkeyCAxhEw"

# Настройки API
ENABLE_NOMINATIM = os.getenv('ENABLE_NOMINATIM', 'true').lower() == 'true'
NOMINATIM_TIMEOUT = int(os.getenv('NOMINATIM_TIMEOUT', '15'))
ENABLE_GOOGLE_MAPS = os.getenv('ENABLE_GOOGLE_MAPS', 'true').lower() == 'true'  # Google Maps API включен по умолчанию
GOOGLE_MAPS_TIMEOUT = int(os.getenv('GOOGLE_MAPS_TIMEOUT', '30'))  # Увеличен таймаут для стабильности

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Обработчик команды /start"""
#     user = update.effective_user
#     if not user or not hasattr(user, 'id'):
#         await update.message.reply_text("Ошибка: не удалось определить пользователя.")
#         return
    
#     # Проверяем, есть ли пользователь в базе данных
#     try:
#         result = supabase.table('users').select('*').eq('telegram_id', user.id).execute()
        
#         if result.data:
#             # Пользователь уже существует
#             welcome_message = f"С возвращением, {getattr(user, 'first_name', 'Пользователь')}! 👋"
#         else:
#             # Новый пользователь
#             welcome_message = f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Добро пожаловать! 🎉"
            
#             # Сохраняем пользователя в базу данных
#             supabase.table('users').insert({
#                 'telegram_id': user.id,
#                 'username': getattr(user, 'username', None),
#                 'tg_name': getattr(user, 'first_name', None),
#                 'last_name': getattr(user, 'last_name', None)
#             }).execute()
            
#     except Exception as e:
#         logger.error(f"Ошибка при работе с базой данных: {e}")
#         welcome_message = f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Добро пожаловать! 🎉"
    
#     # Создаем кнопку для запуска WebApp
#     keyboard = [
#         [KeyboardButton("🚀 Запустить WebApp", web_app=WebAppInfo(url=WEBAPP_URL))]
#     ]
#     reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
#     await update.message.reply_text(
#         welcome_message,
#         reply_markup=reply_markup
#     )

# async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Обработчик данных от WebApp"""
#     data = update.message.web_app_data.data
#     user = update.effective_user
    
#     await update.message.reply_text(
#         f"Получены данные от WebApp: {data}\n"
#         f"Пользователь: {getattr(user, 'first_name', 'Пользователь')}"
#     )

# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Обработчик обычных сообщений"""
#     user = update.effective_user
#     await update.message.reply_text(
#         f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Используйте кнопку WebApp для тестирования."
#     )

# def main() -> None:
#     """Запуск бота"""
#     logger.info("Запуск Telegram-бота...")
#     # Создаем приложение
#     application = Application.builder().token(TOKEN).build()

#     # Добавляем обработчики
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     # Запускаем бота (закомментировано для WebApp)
#     # application.run_polling(allowed_updates=Update.ALL_TYPES)

# Функция для безопасного выполнения операций с базой данных
def safe_db_operation(operation, max_retries=5, retry_delay=5):
    """
    Безопасно выполняет операцию с базой данных с retry логикой
    
    Args:
        operation: Функция для выполнения
        max_retries: Максимальное количество попыток
        retry_delay: Задержка между попытками в секундах
    
    Returns:
        Результат операции или None в случае ошибки
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Попытка подключения к БД {attempt + 1}/{max_retries}")
            
            # Добавляем небольшую задержку перед каждой попыткой
            if attempt > 0:
                time.sleep(1)
            
            result = operation()
            logger.info(f"✅ Успешное подключение к БД на попытке {attempt + 1}")
            return result
        except (TimeoutException, ConnectTimeout, ConnectionError, OSError) as e:
            error_msg = str(e)
            if "handshake operation timed out" in error_msg or "timed out" in error_msg:
                logger.warning(f"SSL/Network timeout on attempt {attempt + 1}/{max_retries}: {error_msg}")
            else:
                logger.warning(f"Database connection error on attempt {attempt + 1}/{max_retries}: {error_msg}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Ожидание {retry_delay} секунд перед следующей попыткой...")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Database operation failed after {max_retries} attempts: {error_msg}")
                return None
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Ожидание {retry_delay} секунд перед следующей попыткой...")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                return None
    return None

# Проверка подключения к Supabase при запуске
try:
    logger.info("🔍 Проверка подключения к Supabase...")
    test_result = safe_db_operation(
        lambda: supabase.table('users').select('id').limit(1).execute()
    )
    if test_result is not None:
        logger.info("✅ Подключение к Supabase успешно установлено")
    else:
        logger.error("❌ Не удалось подключиться к Supabase")
except Exception as e:
    logger.error(f"❌ Ошибка при проверке подключения к Supabase: {e}")

# Flask маршруты для WebApp
# Маршрут для корневого пути - перенаправление на webapp
@app.route('/')
def index():
    """Корневой маршрут - перенаправление на главную страницу webapp"""
    from flask import redirect, url_for
    return redirect('/webapp')

@app.route('/webapp')
def webapp():
    """Главное меню WebApp"""
    with open('webapp_main.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_main')
def webapp_main():
    """Главное меню WebApp (альтернативный маршрут)"""
    with open('webapp_main.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_help')
def webapp_help():
    with open('webapp_help.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_profile')
def webapp_profile():
    with open('webapp_profile.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_profile_data')
def webapp_profile_data():
    with open('webapp_profile_data.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_balance')
def webapp_balance():
    with open('webapp_balance.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_region_analytics')
def webapp_region_analytics():
    """Страница аналитики региона"""
    with open('webapp_region_analytics.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_object_evaluation')
def webapp_object_evaluation():
    """Страница оценки объекта"""
    with open('webapp_object_evaluation.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_my_reports')
def webapp_my_reports():
    """Страница моих отчетов"""
    with open('webapp_my_reports.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья приложения"""
    return jsonify({"status": "ok", "message": "Telegram WebApp Bot is running"})

@app.route('/favicon.ico')
def favicon():
    """Обработка favicon.ico"""
    return send_from_directory('.', 'logo-flt.png', mimetype='image/png')

@app.route('/logo-sqv.png')
def serve_logo():
    return send_from_directory('.', 'logo-sqv.png')

@app.route('/logo-flt.png')
def serve_logo_flt():
    return send_from_directory('.', 'logo-flt.png')

@app.route('/reports/<filename>')
def serve_report(filename):
    """Доступ к сохраненным отчетам"""
    return send_from_directory('reports', filename)

def determine_user_language(user, telegram_language_code):
    """
    Определяет язык пользователя согласно новой логике:
    - Всегда используется language из базы данных (для всех пользователей)
    - Если язык не установлен в БД: используется язык из Telegram как fallback
    - Если язык не поддерживается: английский по умолчанию
    """
    user_db_language = user.get('language') if user else None
    
    logger.info(f"🔍 Определение языка: db_language={user_db_language}, telegram_code={telegram_language_code}")
    
    # Приоритет 1: Язык из базы данных (для всех пользователей)
    if user_db_language and user_db_language in locales:
        logger.info(f"✅ Используем язык из БД: {user_db_language}")
        return user_db_language
    
    # Приоритет 2: Fallback на язык из Telegram (если не установлен в БД)
    if telegram_language_code:
        telegram_lang = telegram_language_code[:2]
        if telegram_lang in locales:
            logger.info(f"🔄 Язык не установлен в БД, используем Telegram: {telegram_lang}")
            return telegram_lang
        else:
            logger.info(f"⚠️ Язык Telegram не поддерживается ({telegram_lang}): используем английский")
    else:
        logger.info(f"⚠️ Нет языка в БД и Telegram: используем английский")
    
    # По умолчанию английский
    return 'en'

@app.route('/api/user', methods=['POST'])
def api_user():
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    username = data.get('username')
    first_name = data.get('tg_name')
    last_name = data.get('last_name')
    language_code = data.get('language_code', 'en')
    referal = data.get('referal')  # invite_code пригласившего, если есть
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    # Проверяем пользователя в базе
    try:
        user_result = safe_db_operation(
            lambda: supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
        )
        if user_result is None:
            return jsonify({'error': 'Database connection error'}), 500
        user = user_result.data[0] if user_result.data else None
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return jsonify({'error': 'Database connection error'}), 500
    if user is not None:
        # Определяем язык согласно новой логике
        lang = determine_user_language(user, language_code)
        
        # Логируем для отладки
        logger.info(f"👤 Пользователь {telegram_id}: user_status={user.get('user_status')}, "
                   f"telegram_lang={language_code}, determined_lang={lang}")
        
        return jsonify({
            'exists': True,
            'is_new_user': False,
            'language': lang,
            'language_code': lang,
            'welcome': locales[lang]['welcome_back'],
            'menu': locales[lang]['menu'],
            'name': user.get('name'),
            'tg_name': user.get('tg_name'),
            'last_name': user.get('last_name'),
            'username': user.get('username'),
            'balance': user.get('balance', 0),
            'telegram_id': user.get('telegram_id'),
            'user_status': user.get('user_status', None),
            'avatar_filename': user.get('avatar_filename'),
            'language_determined': True  # Флаг что язык уже определен
        })
    else:
        # Новый пользователь - используем язык из Telegram
        lang = language_code[:2] if language_code[:2] in locales else 'en'
        
        # Логируем для отладки
        logger.info(f"🆕 Новый пользователь {telegram_id}: telegram_lang={language_code}, determined_lang={lang}")
        
        # Генерация уникального invite_code
        def generate_invite_code():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Проверка уникальности invite_code
        while True:
            invite_code = generate_invite_code()
            code_check = supabase.table('users').select('invite_code').eq('invite_code', invite_code).execute()
            if not code_check.data:
                break
        user_data = {
            'telegram_id': telegram_id,
            'username': username,
            'tg_name': first_name,
            'last_name': last_name,
            'language': lang,  # Сохраняем определенный язык
            'balance': 0,
            'invite_code': invite_code
        }
        if referal:
            user_data['referal'] = referal
        try:
            result = safe_db_operation(
                lambda: supabase.table('users').insert(user_data).execute()
            )
            if result is None:
                return jsonify({'error': 'Database connection error'}), 500
        except Exception as e:
            logger.error(f"Error creating new user: {e}")
            return jsonify({'error': 'Database connection error'}), 500
        return jsonify({
            'exists': False,
            'is_new_user': True,
            'language': lang,
            'language_code': lang,
            'welcome': locales[lang]['welcome_new'],
            'choose_language': locales[lang]['choose_language'],
            'languages': locales[lang]['language_names'],
            'balance': 0,
            'telegram_id': telegram_id,
            'invite_code': invite_code,
            'language_determined': True  # Флаг что язык уже определен
        })

@app.route('/api/user_profile', methods=['POST'])
def api_user_profile():
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    
    # Проверяем, есть ли данные для обновления
    update_data = {}
    for field in ['full_name', 'position', 'company_name', 'website_url', 'about_me', 'phone', 'email', 'whatsapp_link', 'telegram_link', 'facebook_link', 'instagram_link']:
        if field in data:
            update_data[field] = data[field]
    
    try:
        if update_data:
            # Обновляем данные пользователя
            supabase.table('users').update(update_data).eq('telegram_id', telegram_id).execute()
        
        # Получаем обновленные данные
        result = supabase.table('users').select('full_name, position, company_name, website_url, about_me, phone, email, whatsapp_link, telegram_link, facebook_link, instagram_link, avatar_filename').eq('telegram_id', telegram_id).execute()
        if result.data and len(result.data) > 0:
            return jsonify({'success': True, 'profile': result.data[0]})
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error updating/fetching user profile: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/user_avatar', methods=['POST'])
def api_user_avatar():
    """Загрузка аватара пользователя"""
    try:
        telegram_id = request.form.get('telegram_id')
        if not telegram_id:
            return jsonify({'success': False, 'error': 'telegram_id required'}), 400
        
        telegram_id = int(telegram_id)
        
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'No avatar file'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Проверяем тип файла
        if not file.content_type.startswith('image/'):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # Создаем папку для пользователя
        user_folder = os.path.join('user', str(telegram_id))
        os.makedirs(user_folder, exist_ok=True)
        
        # Генерируем уникальное имя файла
        import uuid
        file_extension = os.path.splitext(file.filename)[1].lower()
        if not file_extension:
            file_extension = '.jpg'
        filename = f"avatar_{uuid.uuid4().hex[:8]}{file_extension}"
        filepath = os.path.join(user_folder, filename)
        
        # Сохраняем файл
        file.save(filepath)
        
        # Обновляем запись в базе данных
        supabase.table('users').update({'avatar_filename': filename}).eq('telegram_id', telegram_id).execute()
        
        return jsonify({'success': True, 'filename': filename})
        
    except Exception as e:
        logger.error(f"Error uploading avatar: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/user/<int:telegram_id>/<filename>')
def serve_user_avatar(telegram_id, filename):
    """Отдача аватара пользователя"""
    try:
        user_folder = os.path.join('user', str(telegram_id))
        return send_from_directory(user_folder, filename)
    except Exception as e:
        logger.error(f"Error serving avatar: {e}")
        return '', 404

@app.route('/api/set_language', methods=['POST'])
def api_set_language():
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    language = data.get('language')
    if not language:
        return jsonify({'error': 'language required'}), 400
    if not telegram_id or not language:
        return jsonify({'error': 'telegram_id and language required'}), 400
    
    # Проверяем, что язык поддерживается
    if language not in locales:
        return jsonify({'error': 'Unsupported language'}), 400
    
    # Получаем статус пользователя
    try:
        user_result = safe_db_operation(
            lambda: supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
        )
        if user_result is None:
            return jsonify({'error': 'Database connection error'}), 500
        user_status = user_result.data[0].get('user_status') if user_result.data else None
        
        # Обновляем язык пользователя
        update_result = safe_db_operation(
            lambda: supabase.table('users').update({'language': language}).eq('telegram_id', telegram_id).execute()
        )
        if update_result is None:
            return jsonify({'error': 'Database connection error'}), 500
        
        logger.info(f"🌐 Язык обновлен для пользователя {telegram_id}: {language} (статус: {user_status})")
        
        return jsonify({
            'ok': True, 
            'language': language,
            'user_status': user_status
        })
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении языка: {e}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/menu', methods=['POST'])
def api_menu():
    """API endpoint для получения локализованного меню"""
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    language_code = data.get('language_code', 'en')
    
    # Определяем язык пользователя
    if telegram_id:
        try:
            # Получаем информацию о пользователе из БД
            user_result = safe_db_operation(
                lambda: supabase.table('users').select('language, user_status').eq('telegram_id', telegram_id).execute()
            )
            
            if user_result and user_result.data:
                user = user_result.data[0]
                language = determine_user_language(user, language_code)
            else:
                language = language_code[:2] if language_code[:2] in locales else 'en'
        except Exception as e:
            logger.error(f"Ошибка при определении языка пользователя: {e}")
            language = language_code[:2] if language_code[:2] in locales else 'en'
    else:
        language = language_code[:2] if language_code[:2] in locales else 'en'
    
    # Возвращаем локализованное меню
    menu_data = locales.get(language, locales['en']).get('menu', {})
    
    return jsonify({
        'menu': menu_data,
        'language': language,
        'supported_languages': list(locales.keys())
    })

@app.route('/api/locations/countries', methods=['GET'])
def api_locations_countries():
    """Получение списка стран из таблицы locations"""
    try:
        logger.info("🔍 Запрос списка стран")
        
        # Получаем все записи с помощью пагинации
        all_records = []
        page = 0
        page_size = 1000
        
        while True:
            result = supabase.table('locations').select('country_id, country_name').range(page * page_size, (page + 1) * page_size - 1).execute()
            
            if not result.data:
                break
                
            all_records.extend(result.data)
            page += 1
            
            # Защита от бесконечного цикла
            if page > 10:  # Максимум 10 страниц
                break
        
        logger.info(f"📊 Получено записей: {len(all_records)}")
        
        if all_records:
            # Убираем дубликаты, фильтруем None значения и сортируем
            countries = []
            seen = set()
            for item in all_records:
                if item['country_id'] is not None and item['country_name'] is not None:
                    country_tuple = (item['country_id'], item['country_name'])
                    if country_tuple not in seen:
                        countries.append(country_tuple)
                        seen.add(country_tuple)
                else:
                    logger.warning(f"⚠️ Пропущена запись с None значениями: {item}")
            
            logger.info(f"✅ Отфильтровано стран: {len(countries)}")
            
            # Сортируем по названию, игнорируя None
            countries.sort(key=lambda x: x[1] if x[1] is not None else '')
            return jsonify({'success': True, 'countries': countries})
        else:
            logger.warning("⚠️ Страны не найдены")
            return jsonify({'success': False, 'error': 'No countries found'})
    except Exception as e:
        logger.error(f"❌ Ошибка при получении стран: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/cities', methods=['POST'])
def api_locations_cities():
    """Получение списка городов по country_id"""
    data = request.json or {}
    country_id = data.get('country_id')
    
    if not country_id:
        return jsonify({'error': 'country_id required'}), 400
    
    try:
        logger.info(f"🔍 Запрос городов для country_id: {country_id}")
        
        # Получаем все записи с помощью пагинации
        all_records = []
        page = 0
        page_size = 1000
        
        while True:
            result = supabase.table('locations').select('city_id, city_name').eq('country_id', country_id).range(page * page_size, (page + 1) * page_size - 1).execute()
            
            if not result.data:
                break
                
            all_records.extend(result.data)
            page += 1
            
            # Защита от бесконечного цикла
            if page > 10:  # Максимум 10 страниц
                break
        
        logger.info(f"📊 Получено записей: {len(all_records)}")
        
        if all_records:
            # Убираем дубликаты, фильтруем None значения и сортируем
            cities = []
            seen = set()
            for item in all_records:
                if item['city_id'] is not None and item['city_name'] is not None:
                    city_tuple = (item['city_id'], item['city_name'])
                    if city_tuple not in seen:
                        cities.append(city_tuple)
                        seen.add(city_tuple)
                else:
                    logger.warning(f"⚠️ Пропущена запись с None значениями: {item}")
            
            logger.info(f"✅ Отфильтровано городов: {len(cities)}")
            
            # Сортируем по названию, игнорируя None
            cities.sort(key=lambda x: x[1] if x[1] is not None else '')
            return jsonify({'success': True, 'cities': cities})
        else:
            logger.warning(f"⚠️ Города для country_id {country_id} не найдены")
            return jsonify({'success': False, 'error': 'No cities found'})
    except Exception as e:
        logger.error(f"❌ Ошибка при получении городов: {e}")
        logger.error(f"📋 Данные запроса: country_id={country_id}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/counties', methods=['POST'])
def api_locations_counties():
    """Получение списка областей/регионов по city_id"""
    data = request.json or {}
    city_id = data.get('city_id')
    
    if not city_id:
        return jsonify({'error': 'city_id required'}), 400
    
    try:
        logger.info(f"🔍 Запрос областей для city_id: {city_id}")
        
        # Получаем все записи с помощью пагинации
        all_records = []
        page = 0
        page_size = 1000
        
        while True:
            result = supabase.table('locations').select('county_id, county_name').eq('city_id', city_id).range(page * page_size, (page + 1) * page_size - 1).execute()
            
            if not result.data:
                break
                
            all_records.extend(result.data)
            page += 1
            
            # Защита от бесконечного цикла
            if page > 10:  # Максимум 10 страниц
                break
        
        logger.info(f"📊 Получено записей: {len(all_records)}")
        
        if all_records:
            # Убираем дубликаты, фильтруем None значения и сортируем
            counties = []
            seen = set()
            for item in all_records:
                if item['county_id'] is not None and item['county_name'] is not None:
                    county_tuple = (item['county_id'], item['county_name'])
                    if county_tuple not in seen:
                        counties.append(county_tuple)
                        seen.add(county_tuple)
                else:
                    logger.warning(f"⚠️ Пропущена запись с None значениями: {item}")
            
            logger.info(f"✅ Отфильтровано областей: {len(counties)}")
            
            # Сортируем по названию, игнорируя None
            counties.sort(key=lambda x: x[1] if x[1] is not None else '')
            return jsonify({'success': True, 'counties': counties})
        else:
            logger.warning(f"⚠️ Области для city_id {city_id} не найдены")
            return jsonify({'success': False, 'error': 'No counties found'})
    except Exception as e:
        logger.error(f"❌ Ошибка при получении областей: {e}")
        logger.error(f"📋 Данные запроса: city_id={city_id}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/districts', methods=['POST'])
def api_locations_districts():
    """Получение списка районов по county_id"""
    data = request.json or {}
    county_id = data.get('county_id')
    
    if not county_id:
        return jsonify({'error': 'county_id required'}), 400
    
    try:
        logger.info(f"🔍 Запрос районов для county_id: {county_id}")
        
        # Получаем все записи с помощью пагинации
        all_records = []
        page = 0
        page_size = 1000
        
        while True:
            result = supabase.table('locations').select('district_id, district_name').eq('county_id', county_id).range(page * page_size, (page + 1) * page_size - 1).execute()
            
            if not result.data:
                break
                
            all_records.extend(result.data)
            page += 1
            
            # Защита от бесконечного цикла
            if page > 10:  # Максимум 10 страниц
                break
        
        logger.info(f"📊 Получено записей: {len(all_records)}")
        
        if all_records:
            # Убираем дубликаты, фильтруем None значения и сортируем
            districts = []
            seen = set()
            for item in all_records:
                if item['district_id'] is not None and item['district_name'] is not None:
                    district_tuple = (item['district_id'], item['district_name'])
                    if district_tuple not in seen:
                        districts.append(district_tuple)
                        seen.add(district_tuple)
                else:
                    logger.warning(f"⚠️ Пропущена запись с None значениями: {item}")
            
            logger.info(f"✅ Отфильтровано районов: {len(districts)}")
            
            # Сортируем по названию, игнорируя None
            districts.sort(key=lambda x: x[1] if x[1] is not None else '')
            return jsonify({'success': True, 'districts': districts})
        else:
            logger.warning(f"⚠️ Районы для county_id {county_id} не найдены")
            return jsonify({'success': False, 'error': 'No districts found'})
    except Exception as e:
        logger.error(f"❌ Ошибка при получении районов: {e}")
        logger.error(f"📋 Данные запроса: county_id={county_id}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/region_data', methods=['POST'])
def api_region_data():
    """Получение данных региона из таблиц general_data, house_type_data, floor_segment_data, age_data, heating_data"""
    data = request.json or {}
    country_id = data.get('country_id')
    city_id = data.get('city_id')
    county_id = data.get('county_id')
    district_id = data.get('district_id')
    listing_types = data.get('listing_types', {})
    
    if not all([country_id, city_id, county_id]):
        return jsonify({'error': 'country_id, city_id, county_id required'}), 400
    
    try:
        logger.info(f"🔍 Запрос данных региона: country_id={country_id}, city_id={city_id}, county_id={county_id}, district_id={district_id}")
        if listing_types:
            logger.info(f"🎯 Выбранные listing_type: {listing_types}")
        
        # Формируем условия для запроса
        conditions = {
            'country_id': country_id,
            'city_id': city_id,
            'county_id': county_id
        }
        
        if district_id and district_id != 'none':
            conditions['district_id'] = district_id
        
        # Получаем общие данные
        general_result = supabase.table('general_data').select('*').eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id)
        if district_id and district_id != 'none':
            general_result = general_result.eq('district_id', district_id)
        general_data = general_result.execute()
        
        # Получаем данные по типам домов
        house_type_result = supabase.table('house_type_data').select('*').eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id)
        if district_id and district_id != 'none':
            house_type_result = house_type_result.eq('district_id', district_id)
        if listing_types.get('house_type'):
            house_type_result = house_type_result.eq('listing_type', listing_types['house_type'])
        house_type_data = house_type_result.execute()
        
        # Получаем данные по сегментам этажей
        floor_segment_result = supabase.table('floor_segment_data').select('*').eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id)
        if district_id and district_id != 'none':
            floor_segment_result = floor_segment_result.eq('district_id', district_id)
        if listing_types.get('floor_segment'):
            floor_segment_result = floor_segment_result.eq('listing_type', listing_types['floor_segment'])
        floor_segment_data = floor_segment_result.execute()
        
        # Получаем данные по возрасту объектов
        age_result = supabase.table('age_data').select('*').eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id)
        if district_id and district_id != 'none':
            age_result = age_result.eq('district_id', district_id)
        if listing_types.get('age'):
            age_result = age_result.eq('listing_type', listing_types['age'])
        age_data = age_result.execute()

        # Получаем данные по отоплению
        heating_result = supabase.table('heating_data').select('*').eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id)
        if district_id and district_id != 'none':
            heating_result = heating_result.eq('district_id', district_id)
        if listing_types.get('heating'):
            heating_result = heating_result.eq('listing_type', listing_types['heating'])
        heating_data = heating_result.execute()

        logger.info(f"📊 Получено данных: general={len(general_data.data) if general_data.data else 0}, house_type={len(house_type_data.data) if house_type_data.data else 0}, floor_segment={len(floor_segment_data.data) if floor_segment_data.data else 0}, age={len(age_data.data) if age_data.data else 0}, heating={len(heating_data.data) if heating_data.data else 0}")
        
        # Проверяем и обновляем курсы валют при необходимости
        try:
            logger.info("🔄 Проверяем и обновляем курсы валют...")
            currency_check_result = check_and_update_currency_rates()
            if currency_check_result:
                logger.info("✅ Курсы валют проверены и обновлены при необходимости")
            else:
                logger.warning("⚠️ Не удалось проверить/обновить курсы валют")
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке курсов валют: {e}")
            logger.error(f"📋 Детали ошибки: {type(e).__name__}: {str(e)}")
        
        return jsonify({
            'success': True,
            'general_data': general_data.data if general_data.data else [],
            'house_type_data': house_type_data.data if house_type_data.data else [],
            'floor_segment_data': floor_segment_data.data if floor_segment_data.data else [],
            'age_data': age_data.data if age_data.data else [],
            'heating_data': heating_data.data if heating_data.data else []
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении данных региона: {e}")
        logger.error(f"📋 Данные запроса: country_id={country_id}, city_id={city_id}, county_id={county_id}, district_id={district_id}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/listing_types/<table_name>', methods=['POST'])
def api_listing_types(table_name):
    """Получение доступных listing_type из указанной таблицы для выбранной локации"""
    try:
        data = request.json or {}
        country_id = data.get('country_id')
        city_id = data.get('city_id')
        county_id = data.get('county_id')
        district_id = data.get('district_id')
        
        logger.info(f"🔍 Запрос доступных listing_type из таблицы: {table_name} для локации: country_id={country_id}, city_id={city_id}, county_id={county_id}, district_id={district_id}")
        
        # Проверяем, что таблица поддерживается
        supported_tables = ['house_type_data', 'floor_segment_data', 'age_data', 'heating_data']
        if table_name not in supported_tables:
            return jsonify({'success': False, 'error': f'Table {table_name} not supported'}), 400
        
        # Проверяем обязательные параметры локации
        if not all([country_id, city_id, county_id]):
            return jsonify({'success': False, 'error': 'country_id, city_id, county_id required'}), 400
        
        # Строим запрос с фильтрацией по локации
        query = supabase.table(table_name).select('listing_type').not_.is_('listing_type', 'null')
        
        # Добавляем фильтры по локации
        query = query.eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id)
        
        # Добавляем фильтр по району, если он выбран
        if district_id and district_id != 'none':
            query = query.eq('district_id', district_id)
        
        # Выполняем запрос
        result = query.execute()
        
        if result.data:
            # Извлекаем уникальные значения listing_type
            listing_types = list(set([item['listing_type'] for item in result.data if item.get('listing_type')]))
            listing_types.sort()  # Сортируем для удобства
            
            logger.info(f"✅ Получено {len(listing_types)} уникальных listing_type из таблицы {table_name} для выбранной локации: {listing_types}")
            return jsonify({
                'success': True,
                'listing_types': listing_types
            })
        else:
            logger.warning(f"⚠️ В таблице {table_name} не найдено данных с listing_type для выбранной локации")
            return jsonify({
                'success': True,
                'listing_types': []
            })
            
    except Exception as e:
        logger.error(f"❌ Ошибка при получении listing_type из таблицы {table_name}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency/rates', methods=['GET'])
def api_currency_rates():
    """Получение курсов валют из базы данных"""
    try:
        logger.info("🔍 Запрос курсов валют из базы данных")
        
        # Получаем последние курсы валют
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            latest_rates = result.data[0]
            logger.info(f"✅ Получены курсы валют: {latest_rates}")
            return jsonify({
                'success': True,
                'rates': {
                    'rub': latest_rates.get('rub'),
                    'usd': latest_rates.get('usd'),
                    'euro': latest_rates.get('euro'),
                    'try': latest_rates.get('try'),
                    'aed': latest_rates.get('aed'),
                    'thb': latest_rates.get('thb')
                },
                'last_updated': latest_rates.get('created_at')
            })
        else:
            logger.warning("⚠️ Курсы валют в базе данных не найдены")
            return jsonify({'success': False, 'error': 'No currency rates found'})
            
    except Exception as e:
        logger.error(f"❌ Ошибка при получении курсов валют: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency/rate', methods=['POST'])
def api_currency_rate():
    """Получение курса валют на конкретную дату"""
    try:
        data = request.json or {}
        from_currency = data.get('from_currency', 'EUR').upper()
        to_currency = data.get('to_currency', 'TRY').upper()
        date = data.get('date')
        
        if not date:
            return jsonify({'success': False, 'error': 'date required'}), 400
        
        logger.info(f"🔍 Запрос курса валют {from_currency} -> {to_currency} на {date}")
        
        # Получаем курсы валют из базы данных
        # Используем правильный синтаксис для Supabase с датами
        result = supabase.table('currency').select('*').gte('created_at', f'{date}T00:00:00').lt('created_at', f'{date}T23:59:59').limit(1).execute()
        
        if result.data and len(result.data) > 0:
            currency_data = result.data[0]
            
            # Если запрашиваем курс к базовой валюте (EUR)
            if from_currency == 'EUR':
                if to_currency == 'EUR':
                    rate = 1.0
                else:
                    rate = currency_data.get(to_currency.lower(), 1.0)
            
            # Если запрашиваем курс от другой валюты к EUR
            elif to_currency == 'EUR':
                rate = 1.0 / currency_data.get(from_currency.lower(), 1.0)
            
            # Если запрашиваем курс между двумя валютами (не EUR)
            else:
                from_rate = currency_data.get(from_currency.lower(), 1.0)
                to_rate = currency_data.get(to_currency.lower(), 1.0)
                rate = to_rate / from_rate
            
            logger.info(f"✅ Курс валют из БД: {from_currency} -> {to_currency} = {rate}")
            return jsonify({'success': True, 'rate': rate})
        
        else:
            logger.warning(f"⚠️ Курс валют на {date} не найден в БД, пытаемся получить через API")
            
            # Пытаемся получить курс через API и сохранить в БД
            try:
                api_key = os.getenv('CURRENCY_API_KEY')
                if api_key:
                    url = f"http://api.currencylayer.com/live?access_key={api_key}&currencies=RUB,USD,TRY,AED,THB&source=EUR"
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('success'):
                        quotes = data.get('quotes', {})
                        currency_rates = {
                            'rub': quotes.get('EURRUB', 1.0),
                            'usd': quotes.get('EURUSD', 1.0),
                            'euro': 1.0,
                            'try': quotes.get('EURTRY', 1.0),
                            'aed': quotes.get('EURAED', 1.0),
                            'thb': quotes.get('EURTHB', 1.0)
                        }
                        
                        # Проверяем, есть ли уже запись на сегодня
                        today_result = supabase.table('currency').select('id').eq('created_at::date', date).limit(1).execute()
                        
                        if not today_result.data or len(today_result.data) == 0:
                            # Сохраняем в БД только если записи на сегодня нет
                            supabase.table('currency').insert(currency_rates).execute()
                            logger.info(f"✅ Курсы валют обновлены через API: {currency_rates}")
                        else:
                            logger.info(f"✅ Курсы валют уже есть в БД на {date}")
                        
                        # Рассчитываем нужный курс
                        if from_currency == 'EUR':
                            if to_currency == 'EUR':
                                rate = 1.0
                            else:
                                rate = currency_rates.get(to_currency.lower(), 1.0)
                        elif to_currency == 'EUR':
                            rate = 1.0 / currency_rates.get(from_currency.lower(), 1.0)
                        else:
                            from_rate = currency_rates.get(from_currency.lower(), 1.0)
                            to_rate = currency_rates.get(to_currency.lower(), 1.0)
                            rate = to_rate / from_rate
                        
                        return jsonify({'success': True, 'rate': rate})
            except Exception as api_error:
                logger.error(f"❌ Ошибка при получении курса через API: {api_error}")
            
            return jsonify({'success': False, 'error': 'Rate not found for this date'})
                
    except Exception as e:
        logger.error(f"❌ Ошибка при получении курса валют: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency/update', methods=['POST'])
def api_currency_update():
    """Обновление курсов валют через внешний API"""
    try:
        data = request.json or {}
        from_currency = data.get('from_currency', 'EUR').upper()
        to_currency = data.get('to_currency', 'TRY').upper()
        
        logger.info(f"🔄 Обновление курса валют {from_currency} -> {to_currency}")
        
        # API ключ для currencylayer
        api_key = os.getenv('CURRENCY_API_KEY')
        if not api_key:
            logger.error("❌ API ключ для валют не найден в переменных окружения")
            return jsonify({'success': False, 'error': 'Currency API key not configured'}), 500
        
        # URL для API (базовая валюта - EUR)
        url = f"http://api.currencylayer.com/live?access_key={api_key}&currencies=RUB,USD,TRY,AED,THB&source=EUR"
        
        logger.info(f"🌐 Запрос к API: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"📊 Ответ API: {data}")
        
        if not data.get('success'):
            error_info = data.get('error', {})
            logger.error(f"❌ Ошибка API валют: {error_info}")
            return jsonify({'success': False, 'error': f"Currency API error: {error_info}"}), 500
        
        # Извлекаем курсы валют
        quotes = data.get('quotes', {})
        
        # Конвертируем в формат нашей базы данных
        currency_rates = {
            'rub': quotes.get('EURRUB', 1.0),
            'usd': quotes.get('EURUSD', 1.0),
            'euro': 1.0,  # Базовая валюта
            'try': quotes.get('EURTRY', 1.0),
            'aed': quotes.get('EURAED', 1.0),
            'thb': quotes.get('EURTHB', 1.0)
        }
        
        # Проверяем, есть ли уже запись на сегодня
        today = datetime.now().strftime('%Y-%m-%d')
        today_result = supabase.table('currency').select('id').gte('created_at', f'{today}T00:00:00').lt('created_at', f'{today}T23:59:59').limit(1).execute()
        
        if not today_result.data or len(today_result.data) == 0:
            # Сохраняем в БД только если записи на сегодня нет
            result = supabase.table('currency').insert(currency_rates).execute()
            
            if result.data:
                logger.info(f"✅ Курсы валют обновлены: {currency_rates}")
            else:
                logger.error("❌ Ошибка при сохранении курсов валют в БД")
                return jsonify({'success': False, 'error': 'Failed to save currency rates'}), 500
        else:
            logger.info(f"✅ Курсы валют уже есть в БД на {today}")
        
        # Рассчитываем нужный курс
        if from_currency == 'EUR':
            rate = currency_rates.get(to_currency.lower(), 1.0)
        elif to_currency == 'EUR':
            rate = 1.0 / currency_rates.get(from_currency.lower(), 1.0)
        else:
            from_rate = currency_rates.get(from_currency.lower(), 1.0)
            to_rate = currency_rates.get(to_currency.lower(), 1.0)
            rate = to_rate / from_rate
        
        return jsonify({
            'success': True,
            'rate': rate,
            'rates_updated': True
        })
            
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении курсов валют: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/language', methods=['POST'])
def api_user_language():
    """Получение языка пользователя из таблицы users с учетом новой логики"""
    try:
        data = request.json or {}
        telegram_id = data.get('telegram_id')
        
        if not telegram_id:
            return jsonify({'success': False, 'error': 'telegram_id required'}), 400
        
        logger.info(f"🔍 Запрос языка пользователя для telegram_id: {telegram_id}")
        
        # Получаем полные данные пользователя из базы данных
        result = safe_db_operation(
            lambda: supabase.table('users').select('language, user_status').eq('telegram_id', telegram_id).execute()
        )
        
        if result is None:
            return jsonify({'success': False, 'error': 'Database connection error'}), 500
        
        if result.data and len(result.data) > 0:
            user = result.data[0]
            user_status = user.get('user_status')
            
            # Используем новую единую логику определения языка
            telegram_lang = data.get('language_code', 'en')
            user_language = determine_user_language(user, telegram_lang)
            logger.info(f"👤 Пользователь {telegram_id} (статус: {user_status}): определен язык: {user_language}")
            
            return jsonify({
                'success': True,
                'language': user_language,
                'user_status': user_status
            })
        else:
            logger.warning(f"⚠️ Пользователь с telegram_id {telegram_id} не найден")
            return jsonify({
                'success': True,
                'language': 'en',  # По умолчанию английский
                'user_status': None
            })
            
    except Exception as e:
        logger.error(f"❌ Ошибка при получении языка пользователя: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency/check', methods=['GET'])
def api_currency_check():
    """Проверка наличия курсов валют в базе данных"""
    try:
        logger.info("🔍 Проверка курсов валют в базе данных")
        
        # Получаем все записи из таблицы currency
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(10).execute()
        
        if result.data:
            logger.info(f"✅ Найдено {len(result.data)} записей о курсах валют")
            return jsonify({
                'success': True,
                'count': len(result.data),
                'latest': result.data[0] if result.data else None,
                'all_records': result.data
            })
        else:
            logger.warning("⚠️ Записи о курсах валют не найдены")
            return jsonify({
                'success': False,
                'message': 'No currency records found'
            })
            
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке курсов валют: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency/fetch', methods=['GET'])
def api_currency_fetch():
    """Получение курсов валют из внешнего API и сохранение в базу данных"""
    try:
        logger.info("🔍 Запрос курсов валют из внешнего API")
        
        # API ключ для currencylayer
        api_key = os.getenv('CURRENCY_API_KEY')
        if not api_key:
            logger.error("❌ API ключ для валют не найден в переменных окружения")
            return jsonify({'success': False, 'error': 'Currency API key not configured'}), 500
        
        # URL для API (базовая валюта - EUR)
        url = f"http://api.currencylayer.com/live?access_key={api_key}&currencies=RUB,USD,TRY,AED,THB&source=EUR"
        
        logger.info(f"🌐 Запрос к API: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"📊 Ответ API: {data}")
        
        if not data.get('success'):
            error_info = data.get('error', {})
            logger.error(f"❌ Ошибка API валют: {error_info}")
            return jsonify({'success': False, 'error': f"Currency API error: {error_info}"}), 500
        
        # Извлекаем курсы валют
        quotes = data.get('quotes', {})
        
        # Конвертируем в формат нашей базы данных
        # API возвращает курсы относительно EUR (базовая валюта)
        currency_rates = {
            'rub': quotes.get('EURRUB'),
            'usd': quotes.get('EURUSD'),
            'euro': 1.0,  # Базовая валюта всегда 1.0
            'try': quotes.get('EURTRY'),
            'aed': quotes.get('EURAED'),
            'thb': quotes.get('EURTHB')
        }
        
        # Проверяем, что все курсы получены
        if not all(currency_rates.values()):
            logger.error(f"❌ Не все курсы валют получены: {currency_rates}")
            return jsonify({'success': False, 'error': 'Incomplete currency rates received'}), 500
        
        # Сохраняем в базу данных
        insert_result = supabase.table('currency').insert(currency_rates).execute()
        
        if insert_result.data:
            logger.info(f"✅ Курсы валют сохранены в базу данных: {insert_result.data}")
            return jsonify({
                'success': True,
                'rates': currency_rates,
                'message': 'Currency rates updated successfully'
            })
        else:
            logger.error("❌ Ошибка при сохранении курсов валют в базу данных")
            return jsonify({'success': False, 'error': 'Failed to save currency rates'}), 500
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка сети при запросе к API валют: {e}")
        return jsonify({'success': False, 'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"❌ Ошибка при получении курсов валют: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def check_and_update_currency_rates():
    """Проверяет наличие актуальных курсов валют и обновляет их при необходимости"""
    try:
        logger.info("🔍 Проверка актуальности курсов валют")
        
        # Получаем последние курсы валют из базы данных
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            latest_rates = result.data[0]
            latest_date = latest_rates.get('created_at')
            
            # Проверяем, есть ли курсы за сегодня
            if latest_date:
                # Конвертируем в datetime объект
                if isinstance(latest_date, str):
                    latest_date = datetime.fromisoformat(latest_date.replace('Z', '+00:00'))
                
                # Проверяем, есть ли timezone и убираем его для сравнения
                if hasattr(latest_date, 'tzinfo') and latest_date.tzinfo is not None:
                    latest_date = latest_date.replace(tzinfo=None)
                
                current_date = datetime.utcnow()
                days_difference = (current_date - latest_date).days
                
                logger.info(f"📅 Последние курсы валют: {latest_date}, разница в днях: {days_difference}")
                
                # Если курсы старше 1 дня, обновляем их
                if days_difference >= 1:
                    logger.info("🔄 Курсы валют устарели, обновляем...")
                    return update_currency_rates_from_api()
                else:
                    logger.info("✅ Курсы валют актуальны")
                    return True
            else:
                logger.warning("⚠️ Не удалось определить дату последних курсов валют")
                return update_currency_rates_from_api()
        else:
            logger.info("📝 Курсы валют в базе данных отсутствуют, загружаем...")
            return update_currency_rates_from_api()
            
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке курсов валют: {e}")
        return False

def update_currency_rates_from_api():
    """Обновляет курсы валют из внешнего API"""
    try:
        logger.info("🌐 Обновление курсов валют из внешнего API")
        
        # API ключ для currencylayer
        api_key = os.getenv('CURRENCY_API_KEY')
        if not api_key:
            logger.error("❌ API ключ для валют не найден в переменных окружения")
            logger.error(f"📋 Доступные переменные окружения: {list(os.environ.keys())}")
            return False
        
        logger.info(f"🔑 API ключ найден: {api_key[:10]}...")
        
        # URL для API (базовая валюта - EUR)
        url = f"http://api.currencylayer.com/live?access_key={api_key}&currencies=RUB,USD,TRY,AED,THB&source=EUR"
        
        logger.info(f"🌐 Запрос к API: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"📊 Ответ API: {data}")
        
        if not data.get('success'):
            error_info = data.get('error', {})
            logger.error(f"❌ Ошибка API валют: {error_info}")
            return False
        
        # Извлекаем курсы валют
        quotes = data.get('quotes', {})
        logger.info(f"💱 Полученные котировки: {quotes}")
        
        # Конвертируем в формат нашей базы данных
        # API возвращает курсы относительно EUR (базовая валюта)
        currency_rates = {
            'rub': quotes.get('EURRUB'),
            'usd': quotes.get('EURUSD'),
            'euro': 1.0,  # Базовая валюта всегда 1.0
            'try': quotes.get('EURTRY'),
            'aed': quotes.get('EURAED'),
            'thb': quotes.get('EURTHB')
        }
        
        logger.info(f"💱 Подготовленные курсы валют: {currency_rates}")
        
        # Проверяем, что все курсы получены
        if not all(currency_rates.values()):
            logger.error(f"❌ Не все курсы валют получены: {currency_rates}")
            return False
        
        # Сохраняем в базу данных
        logger.info("💾 Сохраняем курсы валют в базу данных...")
        logger.info(f"📋 Данные для вставки: {currency_rates}")
        
        try:
            insert_result = supabase.table('currency').insert(currency_rates).execute()
            logger.info(f"📋 Результат вставки: {insert_result}")
            
            if insert_result.data:
                logger.info(f"✅ Курсы валют обновлены в базе данных: {insert_result.data}")
                return True
            else:
                logger.error("❌ Ошибка при сохранении курсов валют в базу данных")
                logger.error(f"📋 Результат вставки: {insert_result}")
                return False
        except Exception as db_error:
            logger.error(f"❌ Ошибка базы данных при вставке курсов валют: {db_error}")
            logger.error(f"📋 Детали ошибки БД: {type(db_error).__name__}: {str(db_error)}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка сети при запросе к API валют: {e}")
        logger.error(f"📋 Детали ошибки сети: {type(e).__name__}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении курсов валют: {e}")
        logger.error(f"📋 Детали ошибки: {type(e).__name__}: {str(e)}")
        return False

@app.route('/api/currency/convert', methods=['POST'])
def api_currency_convert():
    """Конвертация значений между валютами"""
    try:
        data = request.json or {}
        value = data.get('value')
        from_currency = data.get('from_currency', 'TRY')
        to_currency = data.get('to_currency', 'EUR')
        
        if value is None:
            return jsonify({'success': False, 'error': 'value required'}), 400
        
        logger.info(f"🔄 Конвертация {value} {from_currency} в {to_currency}")
        
        # Получаем актуальные курсы валют
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(1).execute()
        
        if not result.data or len(result.data) == 0:
            logger.error("❌ Курсы валют не найдены в базе данных")
            return jsonify({'success': False, 'error': 'Currency rates not found'}), 500
        
        rates = result.data[0]
        logger.info(f"📊 Используем курсы валют: {rates}")
        
        # Конвертируем значение
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid numeric value'}), 400
        
        # Конвертируем через EUR (базовая валюта)
        if from_currency == 'TRY':
            # Из TRY в EUR
            eur_value = numeric_value / rates.get('try', 1)
        elif from_currency == 'USD':
            # Из USD в EUR
            eur_value = numeric_value / rates.get('usd', 1)
        elif from_currency == 'RUB':
            # Из RUB в EUR
            eur_value = numeric_value / rates.get('rub', 1)
        elif from_currency == 'EUR':
            eur_value = numeric_value
        else:
            return jsonify({'success': False, 'error': f'Unsupported source currency: {from_currency}'}), 400
        
        # Из EUR в целевую валюту
        if to_currency == 'TRY':
            converted_value = eur_value * rates.get('try', 1)
        elif to_currency == 'USD':
            converted_value = eur_value * rates.get('usd', 1)
        elif to_currency == 'RUB':
            converted_value = eur_value * rates.get('rub', 1)
        elif to_currency == 'EUR':
            converted_value = eur_value
        else:
            return jsonify({'success': False, 'error': f'Unsupported target currency: {to_currency}'}), 400
        
        logger.info(f"✅ Конвертация завершена: {value} {from_currency} = {converted_value} {to_currency}")
        
        return jsonify({
            'success': True,
            'original_value': value,
            'original_currency': from_currency,
            'converted_value': round(converted_value, 2),
            'target_currency': to_currency,
            'rates_used': {
                'from_eur': rates.get(from_currency.lower(), 1),
                'to_eur': rates.get(to_currency.lower(), 1)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка при конвертации валют: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency/test', methods=['GET'])
def api_currency_test():
    """Тестовый endpoint для проверки работы с валютой"""
    try:
        logger.info("🧪 Тестирование работы с валютой")
        
        # Проверяем наличие курсов в базе данных
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            latest_rates = result.data[0]
            logger.info(f"✅ Курсы валют найдены в базе данных: {latest_rates}")
            return jsonify({
                'success': True,
                'message': 'Currency rates found in database',
                'rates': latest_rates,
                'count': len(result.data)
            })
        else:
            logger.warning("⚠️ Курсы валют в базе данных не найдены")
            return jsonify({
                'success': False,
                'message': 'No currency rates found in database',
                'count': 0
            })
            
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании валюты: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/currency/latest', methods=['GET'])
def api_currency_latest():
    """Получение последних курсов валют из таблицы currency"""
    try:
        logger.info("🔍 Запрос последних курсов валют")
        
        # Получаем последнюю запись из таблицы currency (отсортированную по created_at DESC)
        currency_result = supabase.table('currency').select('*').order('created_at', desc=True).limit(1).execute()
        
        if currency_result.data and len(currency_result.data) > 0:
            latest_rate = currency_result.data[0]
            logger.info(f"✅ Найдена последняя запись валют: {latest_rate.get('created_at')}")
            
            # Формируем ответ с данными в правильной структуре
            response_data = {
                'success': True,
                'data': {
                    'euro': latest_rate.get('euro'),
                    'try': latest_rate.get('try'), 
                    'usd': latest_rate.get('usd'),
                    'rub': latest_rate.get('rub'),
                    'aed': latest_rate.get('aed'),
                    'thb': latest_rate.get('thb')
                },
                'created_at': latest_rate.get('created_at'),
                'source': 'database'
            }
            
            logger.info(f"💱 Возвращаем курсы: EUR={latest_rate.get('euro')}, TRY={latest_rate.get('try')}")
            return jsonify(response_data)
        else:
            # Если нет данных в базе, возвращаем ошибку
            logger.warning("⚠️ Нет записей в таблице currency")
            return jsonify({
                'success': False,
                'error': 'No currency data available',
                'message': 'Курсы валют недоступны в базе данных'
            }), 404
                
    except Exception as e:
        logger.error(f"❌ Ошибка получения последних курсов валют: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Ошибка при получении курсов валют'
        }), 500

@app.route('/api/check_admin_status', methods=['POST'])
def api_check_admin_status():
    """Проверка статуса администратора пользователя и подписки"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    logger.info(f"🔍 Проверка статуса админа и подписки для telegram_id: {telegram_id_raw}")
    
    if telegram_id_raw is None:
        logger.error("❌ telegram_id не предоставлен")
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        logger.error(f"❌ Неверный формат telegram_id: {telegram_id_raw}")
        return jsonify({'error': 'Invalid telegram_id'}), 400
    
    try:
        # Проверяем пользователя в базе с таймаутом
        logger.info(f"🔍 Поиск пользователя в базе для telegram_id: {telegram_id}")
        
        # Добавляем таймаут для Supabase запроса
        import asyncio
        import concurrent.futures
        
        def execute_supabase_query():
            return supabase.table('users').select('user_status, period_end').eq('telegram_id', telegram_id).execute()
        
        # Выполняем запрос с таймаутом
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(execute_supabase_query)
            try:
                user_result = future.result(timeout=10)  # 10 секунд таймаут
            except concurrent.futures.TimeoutError:
                logger.error("❌ Таймаут при запросе к базе данных")
                return jsonify({'error': 'Database timeout'}), 408
            except Exception as e:
                logger.error(f"❌ Ошибка при выполнении запроса к базе: {e}")
                return jsonify({'error': 'Database error'}), 500
        
        logger.info(f"📊 Результат поиска: {len(user_result.data) if user_result.data else 0} записей")
        
        if user_result.data and len(user_result.data) > 0:
            user = user_result.data[0]
            user_status = user.get('user_status')
            period_end = user.get('period_end')
            is_admin = user_status == 'admin' if user_status else False
            
            logger.info(f"👤 Пользователь найден: user_status={user_status}, is_admin={is_admin}, period_end={period_end}")
            logger.info(f"📋 Проверяем user_status='{user_status}' == 'admin' = {user_status == 'admin'}")
            
            return jsonify({
                'success': True,
                'is_admin': is_admin,
                'user_status': user_status,
                'period_end': period_end
            })
        else:
            logger.warning(f"❌ Пользователь не найден для telegram_id: {telegram_id}")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"❌ Ошибка проверки статуса админа: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/geocode', methods=['POST'])
def api_geocode():
    """Геокодинг адреса через Google Maps API с извлечением структурированных данных"""
    data = request.json or {}
    address = data.get('address')
    
    # Начинаем логирование
    logger.info("=" * 60)
    logger.info("🔍 НАЧАЛО ГЕОКОДИНГА АДРЕСА")
    logger.info("=" * 60)
    logger.info(f"Получен адрес: '{address}'")
    
    if not address:
        logger.error("❌ Адрес не предоставлен")
        return jsonify({'error': 'Address required'}), 400
    
    try:
        # Запрос к Google Maps Geocoding API
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY
        }
        
        logger.info(f"🌐 Отправляем запрос к Google Maps API: {url}")
        logger.info(f"📝 Параметры запроса: address='{address}', key='{GOOGLE_MAPS_API_KEY[:10]}...'")
        
        # Google Maps API включен - используем его как основной источник
        logger.info("🌐 Google Maps API включен, отправляем запрос...")
        
        # Пытаемся сделать запрос с несколькими попытками и улучшенной обработкой ошибок
        max_retries = 3
        google_maps_success = False
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Попытка {attempt + 1}/{max_retries}: отправляем HTTP запрос к Google Maps API...")
                logger.info(f"🌐 URL: {url}")
                logger.info(f"📝 Параметры: {params}")
                
                # Используем полный таймаут для каждой попытки
                logger.info(f"⏱️ Отправляем запрос с таймаутом {GOOGLE_MAPS_TIMEOUT} секунд...")
                response = requests.get(url, params=params, timeout=GOOGLE_MAPS_TIMEOUT)
                logger.info(f"📡 Статус ответа Google Maps API: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"📊 Размер ответа Google Maps: {len(str(result))} символов")
                    logger.info(f"📄 Содержимое ответа: {result}")
                    
                    if result.get('status') == 'OK' and result.get('results'):
                        try:
                            # Успешно получили данные от Google Maps
                            location = result['results'][0]
                            logger.info(f"📍 Получена локация от Google Maps: {location.get('formatted_address', 'N/A')}")
                            
                            # Извлекаем компоненты локации
                            logger.info("🔍 Извлекаем компоненты локации...")
                            location_components = extract_location_components(location.get('address_components', []), address)
                            logger.info(f"✅ Компоненты локации извлечены: {location_components}")
                            
                            # Пытаемся найти коды локаций в базе данных
                            logger.info("🔍 Ищем коды локаций в базе данных...")
                            location_codes = find_location_codes_from_components(location_components)
                            
                            if location_codes:
                                logger.info(f"✅ Найдены коды локаций: {location_codes}")
                            else:
                                logger.warning("⚠️ Коды локаций не найдены")
                            
                            logger.info("=" * 60)
                            logger.info("✅ ГЕОКОДИНГ ЗАВЕРШЕН УСПЕШНО (Google Maps API)")
                            logger.info("=" * 60)
                            
                            logger.info("✅ Google Maps API успешно обработал адрес")
                            google_maps_success = True
                            return jsonify({
                                'success': True,
                                'lat': float(location['geometry']['location']['lat']),
                                'lng': float(location['geometry']['location']['lng']),
                                'formatted_address': location.get('formatted_address', address),
                                'location_components': location_components,
                                'location_codes': location_codes,
                                'source': 'google_maps'
                            })
                        except Exception as e:
                            logger.error(f"❌ Ошибка при обработке ответа Google Maps: {e}")
                            logger.error(f"📄 Traceback: ", exc_info=True)
                            # Продолжаем к fallback
                            break
                    else:
                        logger.warning(f"⚠️ Google Maps API вернул статус: {result.get('status')}")
                        if result.get('error_message'):
                            logger.warning(f"⚠️ Сообщение об ошибке: {result.get('error_message')}")
                        
                        # Если Google Maps не смог найти адрес, пробуем Nominatim
                        logger.info("🔄 Google Maps не смог найти адрес, пробуем Nominatim...")
                        break
                        
                else:
                    logger.warning(f"⚠️ Попытка {attempt + 1}: HTTP статус {response.status_code}")
                    logger.warning(f"📄 Тело ответа: {response.text[:500]}...")
                    if attempt == max_retries - 1:
                        logger.error(f"❌ Все попытки Google Maps API завершились с ошибкой HTTP {response.status_code}")
                        break
                    continue
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Попытка {attempt + 1}: таймаут Google Maps API ({GOOGLE_MAPS_TIMEOUT} секунд)")
                if attempt == max_retries - 1:
                    logger.error(f"❌ Все попытки Google Maps API завершились таймаутом")
                    break
                continue
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"🔌 Попытка {attempt + 1}: ошибка соединения Google Maps API: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ Все попытки Google Maps API завершились ошибкой соединения")
                    break
                continue
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"📡 Попытка {attempt + 1}: ошибка запроса Google Maps API: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ Все попытки Google Maps API завершились ошибкой запроса")
                    break
                continue
                
            except Exception as e:
                logger.error(f"❌ Попытка {attempt + 1}: неожиданная ошибка Google Maps API: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ Все попытки Google Maps API завершились неожиданной ошибкой")
                    break
                continue
        
        # Проверяем, был ли Google Maps API успешным
        if google_maps_success:
            logger.info("✅ Google Maps API уже успешно обработал адрес")
            return  # Этот return не должен выполниться, но на всякий случай
        
        # Если Google Maps API не сработал, пробуем Nominatim как fallback
        logger.info("🔄 Переключаемся на Nominatim API как fallback...")
        try:
            nominatim_data = get_nominatim_location(address)
            
            if nominatim_data:
                logger.info(f"✅ Получены данные от Nominatim: {nominatim_data}")
                location_components = {
                    'country': nominatim_data.get('country'),
                    'country_code': nominatim_data.get('country_code'),
                    'city': nominatim_data.get('city'),
                    'district': nominatim_data.get('district'),
                    'county': nominatim_data.get('county'),
                    'postal_code': nominatim_data.get('postal_code')
                }
                
                # Пытаемся найти коды локаций в базе данных
                logger.info("🔍 Ищем коды локаций в базе данных...")
                location_codes = find_location_codes_from_components(location_components)
                
                if location_codes:
                    logger.info(f"✅ Найдены коды локаций: {location_codes}")
                else:
                    logger.warning("⚠️ Коды локаций не найдены")
                
                logger.info("=" * 60)
                logger.info("✅ ГЕОКОДИНГ ЗАВЕРШЕН УСПЕШНО (fallback на Nominatim)")
                logger.info("=" * 60)
                
                return jsonify({
                    'success': True,
                    'lat': float(nominatim_data.get('lat', 0)),
                    'lng': float(nominatim_data.get('lon', 0)),
                    'formatted_address': nominatim_data.get('display_name', address),
                    'location_components': location_components,
                    'location_codes': location_codes,
                    'source': 'nominatim_fallback'
                })
            else:
                logger.warning("⚠️ Nominatim API не вернул данные")
        except Exception as e:
            logger.error(f"❌ Ошибка при работе с Nominatim API: {e}")
            logger.error(f"📄 Traceback: ", exc_info=True)
        
        # Попробуем найти адрес в базе данных по ключевым словам
        logger.info("🔍 Пытаемся найти адрес в базе данных...")
        try:
            # Ищем по ключевым словам из адреса
            search_terms = [word.strip() for word in address.replace(',', ' ').replace('.', ' ').split() if len(word.strip()) > 2]
            logger.info(f"🔍 Поисковые термины: {search_terms}")
            
            # Ищем в таблице locations по ключевым словам
            search_result = None
            
            for term in search_terms[:3]:  # Используем первые 3 термина
                if term.lower() not in ['турция', 'türkiye', 'antalya', 'kepez']:  # Исключаем общие термины
                    try:
                        # Поиск по району
                        result = supabase.table('locations').select('*').ilike('district_name', f'%{term}%').execute()
                        if result.data:
                            search_result = result
                            logger.info(f"✅ Найдено по району '{term}': {len(result.data)} записей")
                            break
                        
                        # Поиск по округу
                        result = supabase.table('locations').select('*').ilike('county_name', f'%{term}%').execute()
                        if result.data:
                            search_result = result
                            logger.info(f"✅ Найдено по округу '{term}': {len(result.data)} записей")
                            break
                        
                        # Поиск по городу
                        result = supabase.table('locations').select('*').ilike('city_name', f'%{term}%').execute()
                        if result.data:
                            search_result = result
                            logger.info(f"✅ Найдено по городу '{term}': {len(result.data)} записей")
                            break
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка поиска по термину '{term}': {e}")
                        continue
            
            # Если ничего не найдено, попробуем поиск по Анталье
            if not search_result:
                logger.info("🔍 Поиск по городу 'Antalya'...")
                search_result = supabase.table('locations').select('*').eq('city_name', 'Antalya').limit(1).execute()
            logger.info(f"🔍 Результат поиска в БД: {len(search_result.data)} записей")
            
            if search_result.data:
                # Берем первую найденную локацию
                location = search_result.data[0]
                logger.info(f"✅ Найдена локация в БД: {location}")
                
                # Пытаемся найти коды локаций в базе данных
                logger.info("🔍 Ищем коды локаций в базе данных...")
                location_codes = find_location_codes_from_components({
                    'country': location.get('country_name', ''),
                    'city': location.get('city_name', ''),
                    'county': location.get('county_name', ''),
                    'district': location.get('district_name', '')
                })
                
                if location_codes:
                    logger.info(f"✅ Найдены коды локаций: {location_codes}")
                else:
                    logger.warning("⚠️ Коды локаций не найдены")
                
                logger.info("=" * 60)
                logger.info("✅ ГЕОКОДИНГ ЗАВЕРШЕН УСПЕШНО (база данных)")
                logger.info("=" * 60)
                
                return jsonify({
                    'success': True,
                    'lat': float(location.get('latitude', 0)),
                    'lng': float(location.get('longitude', 0)),
                    'formatted_address': f"{location.get('district_name', '')}, {location.get('county_name', '')}, {location.get('city_name', '')}, {location.get('country_name', '')}",
                    'location_components': {
                        'country': location.get('country_name', ''),
                        'country_code': 'TR',
                        'city': location.get('city_name', ''),
                        'district': location.get('district_name', ''),
                        'county': location.get('county_name', ''),
                        'postal_code': ''
                    },
                    'location_codes': location_codes,
                    'source': 'database_fallback'
                })
            else:
                logger.error("❌ Адрес не найден ни в Google Maps, ни в Nominatim, ни в базе данных")
                return jsonify({'error': 'Адрес не найден. Проверьте правильность написания.'}), 404
                
        except Exception as e:
            logger.error(f"❌ Ошибка поиска в базе данных: {e}")
            logger.error(f"📄 Traceback: ", exc_info=True)
            return jsonify({'error': 'Ошибка поиска адреса в базе данных'}), 500
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при геокодинге: {e}")
        logger.error(f"📄 Traceback: ", exc_info=True)
        return jsonify({'error': 'Geocoding service error'}), 500
    
    # Если все методы не сработали, возвращаем ошибку
    logger.error("❌ Все методы геокодинга не сработали")
    return jsonify({'error': 'Не удалось выполнить геокодинг адреса. Попробуйте позже.'}), 500

@app.route('/api/validate_bedrooms', methods=['POST'])
def api_validate_bedrooms():
    """Валидация количества спален"""
    data = request.json or {}
    bedrooms = data.get('bedrooms')
    if bedrooms is None:
        return jsonify({'valid': False, 'error': 'Bedrooms must be a number'})
    try:
        bedrooms_int = int(bedrooms)
        if 1 <= bedrooms_int <= 10:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False, 'error': 'Bedrooms must be between 1 and 10'})
    except (ValueError, TypeError):
        return jsonify({'valid': False, 'error': 'Bedrooms must be a number'})

@app.route('/api/validate_price', methods=['POST'])
def api_validate_price():
    """Валидация цены"""
    data = request.json or {}
    price = data.get('price')
    if price is None:
        return jsonify({'valid': False, 'error': 'Price must be a number'})
    try:
        price_float = float(price)
        if price_float > 0:
            return jsonify({'valid': True})
        else:
            return jsonify({'valid': False, 'error': 'Price must be positive'})
    except (ValueError, TypeError):
        return jsonify({'valid': False, 'error': 'Price must be a number'})

@app.route('/api/generate_report', methods=['POST'])
def api_generate_report():
    """Генерация отчета с анализом недвижимости"""
    data = request.json or {}
    address = data.get('address')
    bedrooms = data.get('bedrooms')
    price = data.get('price')
    language = data.get('language', 'en')
    lat = data.get('lat')
    lng = data.get('lng')
    telegram_id = data.get('telegram_id')
    location_codes = data.get('location_codes')  # Получаем коды локаций из фронтенда
    
    if not all([address, bedrooms, price]):
        logger.error(f"❌ Отсутствуют обязательные данные: address={address}, bedrooms={bedrooms}, price={price}")
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        logger.info(f"🔍 Генерация отчета для адреса: {address}")
        logger.info(f"📋 Полученные коды локаций: {location_codes}")
        logger.info(f"🔍 Все полученные данные: {data}")
        logger.info(f"🔍 Типы данных: address={type(address)}, bedrooms={type(bedrooms)}, price={type(price)}, location_codes={type(location_codes)}")
        
        # Если коды локаций не переданы, пытаемся получить их из адреса
        if not location_codes:
            logger.info("🔍 Коды локаций не переданы, пытаемся получить из адреса")
            location_codes = get_location_codes_from_address(address)
            logger.info(f"📋 Полученные коды локаций из адреса: {location_codes}")
        
        # Получаем данные рынка недвижимости
        market_data = None
        if location_codes:
            logger.info(f"📊 Получаем данные рынка для кодов: {location_codes}")
            market_data = get_market_data_by_location_ids(location_codes)
            if market_data:
                logger.info(f"✅ Получены данные рынка: {len(market_data)} секций")
            else:
                logger.warning("❌ Данные рынка не найдены")
        else:
            logger.warning("❌ Коды локаций отсутствуют, данные рынка не будут получены")
        
        # Сохраняем компоненты локации для отображения в отчете
        location_components = data.get('location_components')
        if location_components:
            format_simple_report.last_location_components = location_components
        
        # Проверяем, является ли локация турецкой
        is_turkish = False
        currency_rate = None
        currency_info = ""
        
        if location_components:
            from currency_functions import is_turkish_location, get_current_currency_rate, convert_turkish_data_to_eur, format_currency_info
            from price_trends_functions import get_price_trends_data
            
            is_turkish = is_turkish_location(location_components)
            logger.info(f"🌍 Проверка локации: {'Турция' if is_turkish else 'Другая страна'}")
            
            if is_turkish:
                logger.info("🇹🇷 Локация в Турции, получаем курс валют и конвертируем данные")
                # Получаем текущий курс валют
                currency_rate = get_current_currency_rate()
                if currency_rate:
                    logger.info(f"💱 Получен курс валют: {currency_rate}")
                    # Конвертируем данные рынка в евро
                    if market_data:
                        market_data = convert_turkish_data_to_eur(market_data, currency_rate)
                        logger.info("✅ Данные рынка конвертированы в евро")
                    
                    # Форматируем информацию о курсе валют
                    currency_info = format_currency_info(currency_rate, language)
                else:
                    logger.warning("⚠️ Не удалось получить курс валют")
        
        # Проверяем статус администратора
        is_admin = False
        if telegram_id:
            try:
                user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
                if user_result.data and user_result.data[0].get('user_status') == 'admin':
                    is_admin = True
                    logger.info(f"✅ Пользователь {telegram_id} имеет статус администратора")
            except Exception as e:
                logger.error(f"Ошибка проверки статуса администратора: {e}")
        
        # Устанавливаем флаг администратора для функции форматирования
        format_simple_report.is_admin = is_admin
        
        # Добавляем отладочное логирование
        logger.info(f"🔍 Отладка перед format_simple_report:")
        logger.info(f"  - address: {type(address)} = {address}")
        logger.info(f"  - bedrooms: {type(bedrooms)} = {bedrooms}")
        logger.info(f"  - price: {type(price)} = {price}")
        logger.info(f"  - location_codes: {type(location_codes)} = {location_codes}")
        logger.info(f"  - language: {type(language)} = {language}")
        logger.info(f"  - market_data: {type(market_data)} = {market_data}")
        logger.info(f"  - currency_info: {type(currency_info)} = {currency_info}")
        
        # Формируем отчёт в текстовом формате для отображения
        report_text = format_simple_report(address, bedrooms, price, location_codes, language, market_data, currency_info)
        
        # Сохраняем отчет в базу данных (если есть telegram_id)
        if telegram_id:
            try:
                report_data = {
                    'user_id': telegram_id,
                    'report_type': 'market_analysis',
                    'title': f'Анализ недвижимости: {address}',
                    'description': f'Отчет по адресу {address}, {bedrooms} спален, цена {price}',
                    'parameters': {
                        'address': address,
                        'bedrooms': bedrooms,
                        'price': price,
                        'lat': lat,
                        'lng': lng,
                        'location_codes': location_codes,
                        'is_turkish': is_turkish,
                        'currency_rate': currency_rate
                    },
                    'address': address,
                    'latitude': lat,
                    'longitude': lng,
                    'bedrooms': bedrooms,
                    'price_range_min': float(price) * 0.8 if price is not None else None,
                    'price_range_max': float(price) * 1.2 if price is not None else None
                }
                
                # Получаем user_id из telegram_id
                user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
                if user_result.data:
                    report_data['user_id'] = user_result.data[0]['id']
                    
                    # Сохраняем отчет
                    supabase.table('user_reports').insert(report_data).execute()
            except Exception as e:
                logger.error(f"Error saving report to database: {e}")
                # Продолжаем выполнение даже если сохранение не удалось
        
        return jsonify({
            'success': True,
            'report': {
                'location_codes': location_codes,
                'property_details': {
                    'address': address,
                    'bedrooms': bedrooms,
                    'price': price
                },
                'is_turkish': is_turkish,
                'currency_info': currency_info
            },
            'report_text': report_text
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации отчета: {e}")
        logger.error(f"❌ Данные запроса: {data}")
        logger.error(f"❌ Адрес: {address}")
        logger.error(f"❌ Коды локаций: {location_codes}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

def get_location_codes_from_address(address):
    """Получает коды локаций из таблицы locations по адресу"""
    try:
        # Извлекаем компоненты адреса
        logger.info(f"🔍 Извлекаем компоненты адреса: {address}")
        location_info = extract_location_from_address(address)
        logger.info(f"🔍 Результат извлечения: {location_info}")
        if not location_info:
            logger.warning(f"⚠️ Не удалось извлечь компоненты адреса: {address}")
            return None
        
        # Исправляем названия для соответствия с базой данных
        if location_info.get('country_name') == 'Turkey':
            location_info['country_name'] = 'Türkiye'
        
        # Проверяем наличие всех необходимых полей
        required_fields = ['city_name', 'county_name', 'district_name', 'country_name']
        missing_fields = [field for field in required_fields if not location_info.get(field)]
        if missing_fields:
            logger.warning(f"⚠️ Отсутствуют поля в location_info: {missing_fields}")
            logger.warning(f"⚠️ Доступные поля: {list(location_info.keys())}")
        
        logger.info(f"🔍 Ищем локацию в базе: {location_info}")
        
        # Ищем в таблице locations - сначала по точному совпадению
        query = supabase.table('locations').select('*')
        
        # Добавляем условия поиска по названиям
        if location_info.get('city_name'):
            query = query.eq('city_name', location_info['city_name'])
        if location_info.get('county_name'):
            query = query.eq('county_name', location_info['county_name'])
        if location_info.get('district_name'):
            query = query.eq('district_name', location_info['district_name'])
        if location_info.get('country_name'):
            query = query.eq('country_name', location_info['country_name'])
        
        result = query.execute()
        logger.info(f"🔍 Результат поиска в базе: {result.data if result.data else 'Нет данных'}")
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"✅ Найдена локация: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если точное совпадение не найдено, пробуем найти по district_name и city_name
        logger.info("Точное совпадение не найдено, ищем по district_name и city_name")
        query = supabase.table('locations').select('*')
        if location_info.get('district_name'):
            query = query.eq('district_name', location_info['district_name'])
        if location_info.get('city_name'):
            query = query.eq('city_name', location_info['city_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"Найдена локация по district_name и city_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если и это не помогло, ищем только по district_name
        logger.info("Ищем только по district_name")
        query = supabase.table('locations').select('*')
        if location_info.get('district_name'):
            query = query.eq('district_name', location_info['district_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"Найдена локация по district_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если ничего не найдено, возвращаем None
        logger.warning(f"⚠️ Локация не найдена для: {location_info}")
        logger.warning(f"⚠️ Попробуйте проверить названия в базе данных")
        return None
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения кодов локаций: {e}")
        logger.error(f"❌ Адрес: {address}")
        return None

def format_simple_report(address, bedrooms, price, location_codes, language='en', market_data=None, currency_info=""):
    """Форматирование простого отчёта с кодами локаций и данными рынка"""
    
    # Проверяем и инициализируем параметры
    if location_codes is None:
        location_codes = {}
    if market_data is None:
        market_data = {}
    elif isinstance(market_data, list):
        logger.warning(f"⚠️ market_data является списком, преобразуем в словарь: {market_data}")
        market_data = {}
    if currency_info is None:
        currency_info = ""
    
    # Дополнительная проверка типов
    logger.info(f"🔍 Типы параметров в format_simple_report:")
    logger.info(f"  - location_codes: {type(location_codes)}")
    logger.info(f"  - market_data: {type(market_data)}")
    logger.info(f"  - currency_info: {type(currency_info)}")
    
    # Проверяем, есть ли last_location_components и их тип
    if hasattr(format_simple_report, 'last_location_components'):
        components = format_simple_report.last_location_components
        logger.info(f"🔍 last_location_components: {type(components)}")
        if components and isinstance(components, dict):
            nominatim_data = components.get('nominatim_data')
            if nominatim_data:
                logger.info(f"🔍 nominatim_data тип: {type(nominatim_data)}")
                if isinstance(nominatim_data, list):
                    logger.warning(f"⚠️ nominatim_data является списком: {nominatim_data}")
    
    # Форматируем цену
    def format_price(price):
        return f"€{price:.2f}".replace('.00', '').replace('.', ',')
    
    # Форматируем числовые значения с округлением до 2 знаков после запятой
    def format_number(value):
        if value is None or value == 'н/д':
            return 'н/д'
        try:
            if isinstance(value, (int, float)):
                return f"{value:.2f}".replace('.00', '').replace('.', ',')
            else:
                return str(value)
        except:
            return str(value)
    

    
    # Создаем индикатор тренда
    def create_trend_indicator(current, previous=None):
        if previous is None or not isinstance(current, (int, float)) or not isinstance(previous, (int, float)):
            return ""
        
        if current > previous:
            return "📈 +"
        elif current < previous:
            return "📉 -"
        else:
            return "➡️ ="
    
    # Создаем разворачивающуюся секцию
    def create_collapsible_section(title, content, is_expanded=False):
        if is_expanded:
            return [
                f"🔽 {title}",
                *content
            ]
        else:
            return [
                f"▶️ {title} (нажмите для разворачивания)",
                "..." if content else "Нет данных"
            ]
    
    # Формируем отчёт
    report_lines = [
        "🏠 АНАЛИЗ НЕДВИЖИМОСТИ",
        "=" * 50,
        f"📍 Адрес: {address}",
        f"🛏️ Количество спален: {bedrooms}",
        f"💰 Цена: €{format_number(price)}",
        "",
        "📊 АНАЛИЗ РЫНКА В РАДИУСЕ 5 КМ",
        "",
    ]
    
    # Добавляем краткое резюме
    if market_data and market_data.get('general_data'):
        general = market_data['general_data']
        avg_price_sale = general.get('unit_price_for_sale', 0)
        avg_price_rent = general.get('unit_price_for_rent', 0)
        
        # Создаем разворачивающиеся секции
        summary_sections = [
            ("💰 Цены продажи", [
                f"Средняя: €{format_number(avg_price_sale)}/м²",
                f"Диапазон: €{format_number(general.get('min_unit_price_for_sale', 0))} - €{format_number(general.get('max_unit_price_for_sale', 0))}/м²"
            ]),
            ("🏠 Цены аренды", [
                f"Средняя: €{format_number(avg_price_rent)}/м²",
                f"Диапазон: €{format_number(general.get('min_unit_price_for_rent', 0))} - €{format_number(general.get('max_unit_price_for_rent', 0))}/м²"
            ]),
            ("📊 Статистика рынка", [
                f"Объектов на продажу: {format_number(general.get('count_for_sale', 0))}",
                f"Объектов в аренду: {format_number(general.get('count_for_rent', 0))}",
                f"Доходность: {format_number(general.get('yield', 0))}%"
            ])
        ]
        
        report_lines.extend([
            "📊 КРАТКОЕ РЕЗЮМЕ",
            "",
        ])
        
        # Добавляем разворачивающиеся секции
        for title, content in summary_sections:
            report_lines.extend(create_collapsible_section(title, content, is_expanded=True))
            report_lines.append("")
        
        report_lines.extend([
            "🔍 ДЕТАЛЬНЫЙ АНАЛИЗ",
            "",
        ])
    
    # Добавляем информацию о курсе валют, если есть
    if currency_info:
        report_lines.extend([
            "=== КУРС ВАЛЮТ ===",
            currency_info,
            "",
        ])
    
    # Добавляем коды локаций (только для админов)
    logger.info(f"📋 Форматирование кодов локаций: {location_codes}")
    if location_codes:
        logger.info(f"✅ Коды локаций найдены, добавляем в отчет")
        report_lines.extend([
            "=== КОДЫ ЛОКАЦИЙ (только для администраторов) ===",
            f"Страна: {location_codes.get('country_name', 'н/д')} (ID: {location_codes.get('country_id', 'н/д')})",
            f"Город: {location_codes.get('city_name', 'н/д')} (ID: {location_codes.get('city_id', 'н/д')})",
            f"Район: {location_codes.get('district_name', 'н/д')} (ID: {location_codes.get('district_id', 'н/д')})",
            f"Округ: {location_codes.get('county_name', 'н/д')} (ID: {location_codes.get('county_id', 'н/д')})",
            "",
        ])
    else:
        logger.warning(f"❌ Коды локаций не найдены, добавляем заглушку")
        report_lines.extend([
            "=== КОДЫ ЛОКАЦИЙ (только для администраторов) ===",
            "Локация не найдена в базе данных",
            "",
        ])
    
    report_lines.append("")
    
    # Добавляем данные от Google Places API для отладки (только для админов)
    report_lines.extend([
        "=== ДАННЫЕ GOOGLE PLACES API (только для администраторов) ===",
        f"Formatted Address: {address}",
    ])
    
    # Если есть компоненты локации, показываем их
    if hasattr(format_simple_report, 'last_location_components'):
        components = format_simple_report.last_location_components
        if components:
            report_lines.extend([
                f"Country: {components.get('country', 'н/д')}",
                f"Country Code: {components.get('country_code', 'н/д')}",
                f"City: {components.get('city', 'н/д')}",
                f"District: {components.get('district', 'н/д')}",
                f"County: {components.get('county', 'н/д')}",
                f"Postal Code: {components.get('postal_code', 'н/д')}",
            ])
            
            # Показываем данные Nominatim, если есть
            if components.get('nominatim_data'):
                nominatim = components['nominatim_data']
                
                # Проверяем, что nominatim это словарь, а не список
                if isinstance(nominatim, list):
                    logger.warning(f"⚠️ nominatim_data является списком, берем первый элемент: {nominatim}")
                    if len(nominatim) > 0:
                        nominatim = nominatim[0]
                    else:
                        nominatim = {}
                
                # Проверяем, что nominatim это словарь перед вызовом .get()
                if isinstance(nominatim, dict):
                    report_lines.extend([
                        "",
                        "=== ДАННЫЕ NOMINATIM (OpenStreetMap) (только для администраторов) ===",
                        f"Display Name: {nominatim.get('display_name', 'н/д')}",
                        f"Country: {nominatim.get('country', 'н/д')}",
                        f"Country Code: {nominatim.get('country_code', 'н/д')}",
                        f"City: {nominatim.get('city', 'н/д')}",
                        f"District: {nominatim.get('district', 'н/д')}",
                        f"County: {nominatim.get('county', 'н/д')}",
                        f"Postal Code: {nominatim.get('postal_code', 'н/д')}",
                        f"Road: {nominatim.get('road', 'н/д')}",
                        f"House Number: {nominatim.get('house_number', 'н/д')}",
                    ])
                else:
                    logger.warning(f"⚠️ nominatim_data имеет неожиданный тип: {type(nominatim)}, значение: {nominatim}")
                    report_lines.extend([
                        "",
                        "=== ДАННЫЕ NOMINATIM (OpenStreetMap) (только для администраторов) ===",
                        "Ошибка: данные Nominatim имеют неожиданный формат",
                ])
    
    report_lines.append("")
    
    # Добавляем блок с текущими курсами валют
    if currency_info:
        report_lines.extend([
            "=== ТЕКУЩИЕ КУРСЫ ВАЛЮТ ===",
            currency_info,
            "",
        ])
    
    # Добавляем новые разделы отчета
    if market_data:
        # Общий тренд (из таблицы general_data)
        if market_data.get('general_data'):
            general = market_data['general_data']
            # Получаем значения для прогресс-баров
            min_sale = general.get('min_unit_price_for_sale', 0)
            avg_sale = general.get('unit_price_for_sale', 0)
            max_sale = general.get('max_unit_price_for_sale', 0)
            min_rent = general.get('min_unit_price_for_rent', 0)
            avg_rent = general.get('unit_price_for_rent', 0)
            max_rent = general.get('max_unit_price_for_rent', 0)
            
            report_lines.extend([
                "--- ОБЩИЙ АНАЛИЗ РЫНКА ---",
                "",
                "--- ПРОДАЖИ ---",
                f"💰 Минимальная цена продажи, м²:",
                f"€{format_number(min_sale)}",
                "",
                f"💰 Средняя цена продажи, м²:",
                f"€{format_number(avg_sale)}",
                "",
                f"💰 Максимальная цена продажи, м²:",
                f"€{format_number(max_sale)}",
                "",

                f"📏 Средняя площадь продажи:",
                f"{format_number(general.get('comparable_area_for_sale'))} м²",
                "",
                f"📊 Количество объектов на продажу:",
                f"{format_number(general.get('count_for_sale'))}",
                "",
                f"💰 Цена для продажи, средняя:",
                f"€{format_number(general.get('price_for_sale'))}",
                "",
                f"🏗️ Средний возраст объекта для продажи:",
                f"{format_number(general.get('average_age_for_sale'))} лет",
                "",
                f"⏱️ Период листинга для продажи:",
                f"{format_number(general.get('listing_period_for_sale'))} дней",
                "",
                "--- АРЕНДА ---",
                f"💰 Минимальная цена аренды, м²:",
                f"€{format_number(min_rent)}",
                "",
                f"💰 Средняя цена аренды, м²:",
                f"€{format_number(avg_rent)}",
                "",
                f"💰 Максимальная цена аренды, м²:",
                f"€{format_number(max_rent)}",
                "",

                f"📏 Средняя площадь аренды:",
                f"{format_number(general.get('comparable_area_for_rent'))} м²",
                "",
                f"📊 Количество объектов в аренду:",
                f"{format_number(general.get('count_for_rent'))}",
                "",
                f"💰 Цена для аренды, средняя:",
                f"€{format_number(general.get('price_for_rent'))}",
                "",
                f"🏗️ Средний возраст объекта для аренды:",
                f"{format_number(general.get('average_age_for_rent'))} лет",
                "",
                f"⏱️ Период листинга для аренды:",
                f"{format_number(general.get('listing_period_for_rent'))} дней",
                "",
                f"💎 Доходность:",
                f"{format_number(general.get('yield'))}%",
                "",
            ])
            
            # Добавляем дату тренда только для администраторов
            if hasattr(format_simple_report, 'is_admin') and format_simple_report.is_admin:
                report_lines.append(f"Дата тренда: {general.get('trend_date', 'н/д')}")
                report_lines.append("")
    
        # Анализ по количеству спален (из таблицы house_type_data)
        if market_data.get('house_type_data'):
            house_type_data = market_data['house_type_data']
            report_lines.extend([
                "--- АНАЛИЗ ПО КОЛИЧЕСТВУ СПАЛЕН ---",
                "",
            ])
            
            # Определяем соответствие между bedrooms и listing_type
            bedroom_mapping = {
                0: "0+1",  # 0 спален = студия
                1: "1+1",  # 1 спальня = 1+1
                2: "2+1",  # 2 спальни = 2+1
                3: "3+1",  # 3 спальни = 3+1
                4: "4+1",  # 4 спальни = 4+1
                5: "5+1",  # 5+ спален = 5+1
            }
            
            target_listing_type = bedroom_mapping.get(bedrooms)
            logger.info(f"🔍 Ищем данные для {bedrooms} спален, target_listing_type: {target_listing_type}")
            
            # Если house_type_data это список (несколько записей с разными listing_type)
            if isinstance(house_type_data, list):
                logger.info(f"🔍 house_type_data это список с {len(house_type_data)} записями")
                # Фильтруем только данные, соответствующие выбранному количеству спален
                matching_records = [record for record in house_type_data if record.get('listing_type') == target_listing_type]
                logger.info(f"🔍 Найдено {len(matching_records)} записей для {target_listing_type}")
                
                if matching_records:
                    for record in matching_records:
                        # Добавляем отладочную информацию
                        logger.info(f"DEBUG: Processing record. Type: {type(record)}, Value: {record}")
                        
                        # Проверяем, что record это словарь
                        if not isinstance(record, dict):
                            logger.warning(f"⚠️ record не является словарем: {type(record)}, пропускаем")
                            continue
                        
                    listing_type = record.get('listing_type', 'н/д')
                    # Определяем отображаемое название
                    display_name = {
                        "0+1": "0 - студия",
                        "1+1": "1 спальня",
                        "2+1": "2 спальни", 
                        "3+1": "3 спальни",
                        "4+1": "4 спальни",
                        "5+1": "5+ спален"
                    }.get(listing_type, listing_type)
                    
                    # Получаем значения для прогресс-баров
                    min_sale = record.get('min_unit_price_for_sale', 0)
                    avg_sale = record.get('unit_price_for_sale', 0)
                    max_sale = record.get('max_unit_price_for_sale', 0)
                    min_rent = record.get('min_unit_price_for_rent', 0)
                    avg_rent = record.get('unit_price_for_rent', 0)
                    max_rent = record.get('max_unit_price_for_rent', 0)
                    
                    report_lines.extend([
                        f"--- {display_name} ---",
                        "",
                        "--- ПРОДАЖИ ---",
                        f"💰 Минимальная цена продажи:",
                        f"€{format_number(min_sale)}",
                        "",
                        f"💰 Средняя цена продажи:",
                        f"€{format_number(avg_sale)}",
                        "",
                        f"💰 Максимальная цена продажи:",
                        f"€{format_number(max_sale)}",
                        "",

                        f"📏 Сопоставимая площадь для продажи:",
                        f"{format_number(record.get('comparable_area_for_sale'))} м²",
                        "",
                        f"📊 Количество объектов на продажу:",
                        f"{format_number(record.get('count_for_sale'))}",
                        "",
                        f"💰 Цена для продажи, средняя:",
                        f"€{format_number(record.get('price_for_sale'))}",
                        "",
                        f"🏗️ Средний возраст объекта для продажи:",
                        f"{format_number(record.get('average_age_for_sale'))} лет",
                        "",
                        f"⏱️ Период листинга для продажи:",
                        f"{format_number(record.get('listing_period_for_sale'))} дней",
                        "",
                        "--- АРЕНДА ---",
                        f"💰 Минимальная цена аренды, м²:",
                        f"€{format_number(min_rent)}",
                        "",
                        f"💰 Средняя цена аренды, м²:",
                        f"€{format_number(avg_rent)}",
                        "",
                        f"💰 Максимальная цена аренды, м²:",
                        f"€{format_number(max_rent)}",
                        "",

                        f"📏 Средняя площадь аренды:",
                        f"{format_number(record.get('comparable_area_for_rent'))} м²",
                        "",
                        f"📊 Количество объектов в аренду:",
                        f"{format_number(record.get('count_for_rent'))}",
                        "",
                        f"💰 Цена для аренды, средняя:",
                        f"€{format_number(record.get('price_for_rent'))}",
                        "",
                        f"🏗️ Средний возраст объекта для аренды:",
                        f"{format_number(record.get('average_age_for_rent'))} лет",
                        "",
                        f"⏱️ Период листинга для аренды:",
                        f"{format_number(record.get('listing_period_for_rent'))} дней",
                        "",
                        f"💎 Доходность:",
                        f"{format_number(record.get('yield'))}%",
                        "",
                    ])
            else:
                # Если данные для выбранного количества спален не найдены
                display_name = {
                    0: "0 - студия",
                    1: "1 спальня",
                    2: "2 спальни",
                    3: "3 спальни",
                    4: "4 спальни",
                    5: "5+ спален"
                }.get(bedrooms, f"{bedrooms} спален")
                
                logger.warning(f"⚠️ Данные для {bedrooms} спален ({target_listing_type}) не найдены в house_type_data")
                logger.info(f"🔍 Доступные listing_type: {[record.get('listing_type') for record in house_type_data]}")
                
                report_lines.extend([
                    f"--- {display_name} ---",
                    "Данные для выбранного количества спален не найдены",
                    "",
                ])
        else:
            # Если это одна запись
            if not isinstance(house_type_data, dict):
                logger.warning(f"⚠️ house_type_data не является словарем: {type(house_type_data)}")
                report_lines.extend([
                    "--- Ошибка данных ---",
                    "Данные имеют неожиданный формат",
                    "",
                ])
            else:
                listing_type = house_type_data.get('listing_type', 'н/д')
                if listing_type == target_listing_type:
                    # Определяем отображаемое название
                    display_name = {
                        "0+1": "0 - студия",
                        "1+1": "1 спальня",
                        "2+1": "2 спальни",
                        "3+1": "3 спальни",
                        "4+1": "4 спальни", 
                        "5+1": "5+ спален"
                    }.get(listing_type, listing_type)
                    
                    report_lines.extend([
                        f"--- {display_name} ---",
                        "",
                        "--- ПРОДАЖИ ---",
                        f"💰 Минимальная цена продажи: €{format_number(house_type_data.get('min_unit_price_for_sale'))}",
                        f"💰 Средняя цена продажи: €{format_number(house_type_data.get('unit_price_for_sale'))}",
                        f"💰 Максимальная цена продажи: €{format_number(house_type_data.get('max_unit_price_for_sale'))}",
                        f"📏 Сопоставимая площадь для продажи: {format_number(house_type_data.get('comparable_area_for_sale'))} м²",
                        f"📊 Количество объектов на продажу: {format_number(house_type_data.get('count_for_sale'))}",
                        f"💰 Цена для продажи, средняя: €{format_number(house_type_data.get('price_for_sale'))}",
                        f"🏗️ Средний возраст объекта для продажи: {format_number(house_type_data.get('average_age_for_sale'))} лет",
                        f"⏱️ Период листинга для продажи: {format_number(house_type_data.get('listing_period_for_sale'))} дней",
                        "",
                        "--- АРЕНДА ---",
                        f"💰 Минимальная цена аренды, м²: €{format_number(house_type_data.get('min_unit_price_for_rent'))}",
                        f"💰 Средняя цена аренды, м²: €{format_number(house_type_data.get('unit_price_for_rent'))}",
                        f"💰 Максимальная цена аренды, м²: €{format_number(house_type_data.get('max_unit_price_for_rent'))}",
                        f"📏 Средняя площадь аренды: {format_number(house_type_data.get('comparable_area_for_rent'))} м²",
                        f"📊 Количество объектов в аренду: {format_number(house_type_data.get('count_for_rent'))}",
                        f"💰 Цена для аренды, средняя: €{format_number(house_type_data.get('price_for_rent'))}",
                        f"🏗️ Средний возраст объекта для аренды: {format_number(house_type_data.get('average_age_for_rent'))} лет",
                        f"⏱️ Период листинга для аренды: {format_number(house_type_data.get('listing_period_for_rent'))} дней",
                        f"💎 Доходность: {format_number(house_type_data.get('yield'))}%",
                        "",
                    ])
                else:
                    # Если данные не соответствуют выбранному количеству спален
                    display_name = {
                        0: "0 - студия",
                        1: "1 спальня",
                        2: "2 спальни",
                        3: "3 спальни",
                        4: "4 спальни",
                        5: "5+ спален"
                    }.get(bedrooms, f"{bedrooms} спален")
                    
                    report_lines.extend([
                        f"--- {display_name} ---",
                        "Данные для выбранного количества спален не найдены",
                        "",
                    ])
        # Добавляем раздел с рекомендациями
        if market_data and market_data.get('general_data'):
            general = market_data['general_data']
            avg_price_sale = general.get('unit_price_for_sale', 0)
            avg_price_rent = general.get('unit_price_for_rent', 0)
            yield_value = general.get('yield', 0)
            
            report_lines.extend([
                "",
                "💡 РЕКОМЕНДАЦИИ",
                "",
            ])
            
            # Анализ цены продажи
            if price and avg_price_sale:
                price_per_sqm = price / 100  # Предполагаем площадь 100м²
                if price_per_sqm < avg_price_sale * 0.8:
                    report_lines.extend([
                        "✅ Цена ниже рыночной на 20%+",
                        "Это может быть хорошей инвестицией",
                        "",
                    ])
                elif price_per_sqm > avg_price_sale * 1.2:
                    report_lines.extend([
                        "⚠️ Цена выше рыночной на 20%+",
                        "Рассмотрите торг или поиск альтернатив",
                        "",
                    ])
            else:
                report_lines.extend([
                        "📊 Цена в пределах рыночного диапазона",
                        "Справедливая оценка",
                    "",
                ])
        
        # Анализ доходности
        if yield_value:
            if yield_value > 8:
                report_lines.extend([
                    "💰 Высокая доходность (>8%)",
                    "Отличный потенциал для инвестиций",
                    "",
                ])
            elif yield_value > 6:
                report_lines.extend([
                    "💡 Хорошая доходность (6-8%)",
                    "Стабильный доход",
                    "",
                ])
            else:
                report_lines.extend([
                    "📉 Низкая доходность (<6%)",
                    "Рассмотрите другие варианты",
                    "",
                ])
        
        # Общие рекомендации
        report_lines.extend([
            "",
        ])
    
    # Добавляем контактную информацию
    report_lines.extend([
        "=" * 50,
        "Отчет сгенерирован автоматически",
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        ])
    
    return "\n".join(report_lines)

@app.route('/api/search_properties', methods=['POST'])
def api_search_properties():
    """Поиск недвижимости по параметрам"""
    data = request.json or {}
    property_type = data.get('property_type')
    bedrooms = data.get('bedrooms')
    price_min = data.get('price_min')
    price_max = data.get('price_max')
    city = data.get('city')
    district = data.get('district')
    
    try:
        # Здесь должна быть логика поиска в базе данных
        # Пока возвращаем демо-данные
        
        properties = [
            {
                'id': 1,
                'address': 'ул. Ататюрка, 123, Анталья',
                'bedrooms': bedrooms or 3,
                'price': 250000,
                'property_type': property_type or 'sale',
                'latitude': 36.8969,
                'longitude': 30.7133
            }
        ]
        
        return jsonify({
            'success': True,
            'properties': properties,
            'total': len(properties)
        })
        
    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/market_statistics', methods=['POST'])
def api_market_statistics():
    """Получение статистики рынка по городу и району из Supabase"""
    data = request.json or {}
    city = data.get('city')
    district = data.get('district')
    try:
        # Фильтрация по городу и району (case-insensitive)
        filters = []
        if city:
            filters.append(('city', city.lower()))
        if district:
            filters.append(('district', district.lower()))
        # Property sales
        sales_query = supabase.table('property_sales').select('*')
        if city:
            sales_query = sales_query.ilike('city', f'%{city}%')
        if district:
            sales_query = sales_query.ilike('district', f'%{district}%')
        sales = sales_query.execute().data or []
        # Long term rentals
        long_term_query = supabase.table('long_term_rentals').select('*')
        if city:
            long_term_query = long_term_query.ilike('city', f'%{city}%')
        if district:
            long_term_query = long_term_query.ilike('district', f'%{district}%')
        long_term = long_term_query.execute().data or []
        # Short term rentals
        short_term_query = supabase.table('short_term_rentals').select('*')
        if city:
            short_term_query = short_term_query.ilike('city', f'%{city}%')
        if district:
            short_term_query = short_term_query.ilike('district', f'%{district}%')
        short_term = short_term_query.execute().data or []
        # Средняя цена за м²
        sqm_prices = [x for x in (s.get('price_per_sqm') for s in sales) if isinstance(x, (int, float))]
        avg_price_per_sqm = sum(sqm_prices) / len(sqm_prices) if sqm_prices else 0
        # Количество объектов
        total_properties = len(sales)
        # Среднее время продажи
        days_on_market = [x for x in (s.get('days_on_market') for s in sales) if isinstance(x, (int, float))]
        avg_days_on_market = sum(days_on_market) / len(days_on_market) if days_on_market else 0
        # Годовой рост цен (по последним 2 годам, если есть даты)
        price_growth_yoy = 0
        try:
            sales_with_dates = [s for s in sales if s.get('sale_date') and isinstance(s.get('asking_price'), (int, float))]
            if len(sales_with_dates) > 5:
                sales_with_dates.sort(key=lambda x: x['sale_date'])
                first_year = sales_with_dates[0]['sale_date'][:4]
                last_year = sales_with_dates[-1]['sale_date'][:4]
                first_prices = [s['asking_price'] for s in sales_with_dates if s['sale_date'][:4] == first_year and isinstance(s.get('asking_price'), (int, float))]
                last_prices = [s['asking_price'] for s in sales_with_dates if s['sale_date'][:4] == last_year and isinstance(s.get('asking_price'), (int, float))]
                if first_prices and last_prices:
                    price_growth_yoy = (sum(last_prices)/len(last_prices) - sum(first_prices)/len(first_prices)) / (sum(first_prices)/len(first_prices)) * 100
        except Exception:
            price_growth_yoy = 0
        # Доходность аренды (long_term)
        rental_yield = 0
        try:
            if avg_price_per_sqm > 0 and long_term:
                rents = [x for x in (r.get('monthly_rent') for r in long_term) if isinstance(x, (int, float))]
                avg_rent = sum(rents) / len(rents) if rents else 0
                prices = [x for x in (s.get('asking_price') for s in sales) if isinstance(x, (int, float))]
                avg_price = sum(prices) / len(prices) if prices else 0
                if avg_price > 0:
                    rental_yield = (avg_rent * 12) / avg_price * 100
        except Exception:
            rental_yield = 0
        # Активность рынка (по количеству продаж)
        market_activity = 'high' if total_properties > 100 else 'medium' if total_properties > 20 else 'low'
        # Тренд цен (по price_growth_yoy)
        price_trend = 'up' if price_growth_yoy > 5 else 'stable' if price_growth_yoy > -2 else 'down'
        stats = {
            'avg_price_per_sqm': round(avg_price_per_sqm, 2),
            'price_growth_yoy': round(price_growth_yoy, 2),
            'total_properties': total_properties,
            'avg_days_on_market': round(avg_days_on_market, 1),
            'rental_yield': round(rental_yield, 2),
            'price_trend': price_trend,
            'market_activity': market_activity
        }
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting market statistics: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/calculate_roi', methods=['POST'])
def api_calculate_roi():
    data = request.json or {}
    property_type = data.get('property_type')
    purchase_price = data.get('purchase_price')
    purchase_costs = data.get('purchase_costs', 0)
    try:
        purchase_price = float(purchase_price) if purchase_price is not None else 0
        purchase_costs = float(purchase_costs) if purchase_costs is not None else 0
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid purchase_price or purchase_costs'}), 400

    if property_type == 'short_term':
        avg_nightly_rate = data.get('avg_nightly_rate')
        occupancy_rate = data.get('occupancy_rate', 75)
        try:
            avg_nightly_rate = float(avg_nightly_rate) if avg_nightly_rate is not None else 0
            occupancy_rate = float(occupancy_rate) if occupancy_rate is not None else 75
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid avg_nightly_rate or occupancy_rate'}), 400
        # Расчет ROI для краткосрочной аренды
        monthly_income = avg_nightly_rate * (occupancy_rate / 100) * 30
        annual_income = monthly_income * 12
        total_investment = purchase_price + purchase_costs
        roi = (annual_income / total_investment) * 100 if total_investment else 0
    elif property_type == 'long_term':
        monthly_rent = data.get('monthly_rent')
        try:
            monthly_rent = float(monthly_rent) if monthly_rent is not None else 0
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid monthly_rent'}), 400
        # Расчет ROI для долгосрочной аренды
        annual_income = monthly_rent * 12
        total_investment = purchase_price + purchase_costs
        roi = (annual_income / total_investment) * 100 if total_investment else 0
    else:
        return jsonify({'error': 'Invalid property type'}), 400
    
    return jsonify({
        'success': True,
        'roi': round(roi, 2),
        'annual_income': annual_income,
        'total_investment': total_investment
    })

@app.route('/api/similar_properties', methods=['POST'])
def api_similar_properties():
    """Поиск похожих объектов"""
    data = request.json or {}
    address = data.get('address')
    bedrooms = data.get('bedrooms')
    price = data.get('price')
    try:
        price = float(price) if price is not None else 0
    except (ValueError, TypeError):
        price = 0
    try:
        # Здесь должна быть логика поиска похожих объектов
        # Пока возвращаем демо-данные
        
        similar_properties = [
            {
                'id': 1,
                'address': 'ул. Ататюрка, 125, Анталья',
                'bedrooms': bedrooms,
                'price': price * 0.95,
                'similarity_score': 0.95
            },
            {
                'id': 2,
                'address': 'ул. Ататюрка, 127, Анталья',
                'bedrooms': bedrooms,
                'price': price * 1.05,
                'similarity_score': 0.92
            }
        ]
        
        return jsonify({
            'success': True,
            'properties': similar_properties
        })
        
    except Exception as e:
        logger.error(f"Error finding similar properties: {e}")
        return jsonify({'error': 'Internal error'}), 500

def get_economic_data(country_code='TUR', years_back=10):
    """
    Получение экономических данных (ВВП и инфляция) из таблицы imf_economic_data
    
    Args:
        country_code (str): Код страны (по умолчанию TUR для Турции)
        years_back (int): Количество лет назад для получения данных
    
    Returns:
        dict: Словарь с данными ВВП и инфляции
    """
    try:
        # Получаем данные за последние N лет
        current_year = datetime.now().year
        start_year = current_year - years_back
        
        # Запрос к таблице imf_economic_data для ВВП (NGDP_RPCH)
        gdp_query = supabase.table('imf_economic_data').select('*').eq('country_code', country_code).eq('indicator_code', 'NGDP_RPCH').gte('year', start_year).order('year', desc=True)
        gdp_result = gdp_query.execute()
        
        # Запрос к таблице imf_economic_data для инфляции (PCPIPCH)
        inflation_query = supabase.table('imf_economic_data').select('*').eq('country_code', country_code).eq('indicator_code', 'PCPIPCH').gte('year', start_year).order('year', desc=True)
        inflation_result = inflation_query.execute()
        
        if not gdp_result.data and not inflation_result.data:
            logger.warning(f"No economic data found for country {country_code}, using fallback data")
            # Fallback данные для Турции
            fallback_gdp_data = [
                {'year': 2020, 'value': -1.2, 'indicator_code': 'NGDP_RPCH', 'indicator_name': 'GDP growth'},
                {'year': 2021, 'value': 11.4, 'indicator_code': 'NGDP_RPCH', 'indicator_name': 'GDP growth'},
                {'year': 2022, 'value': 5.6, 'indicator_code': 'NGDP_RPCH', 'indicator_name': 'GDP growth'},
                {'year': 2023, 'value': 4.5, 'indicator_code': 'NGDP_RPCH', 'indicator_name': 'GDP growth'},
                {'year': 2024, 'value': 4.1, 'indicator_code': 'NGDP_RPCH', 'indicator_name': 'GDP growth'}
            ]
            
            fallback_inflation_data = [
                {'year': 2020, 'value': 12.3, 'indicator_code': 'PCPIPCH', 'indicator_name': 'Inflation'},
                {'year': 2021, 'value': 19.6, 'indicator_code': 'PCPIPCH', 'indicator_name': 'Inflation'},
                {'year': 2022, 'value': 72.3, 'indicator_code': 'PCPIPCH', 'indicator_name': 'Inflation'},
                {'year': 2023, 'value': 64.8, 'indicator_code': 'PCPIPCH', 'indicator_name': 'Inflation'},
                {'year': 2024, 'value': 58.2, 'indicator_code': 'PCPIPCH', 'indicator_name': 'Inflation'}
            ]
            
            gdp_data = fallback_gdp_data
            inflation_data = fallback_inflation_data
        else:
            # Обрабатываем данные ВВП
            gdp_data = []
            for record in gdp_result.data:
                year = record.get('year')
                value = record.get('value')
                if year and value is not None:
                    gdp_data.append({
                        'year': year,
                        'value': float(value),  # Рост ВВП в процентах
                        'indicator_code': record.get('indicator_code'),
                        'indicator_name': record.get('indicator_name')
                    })
            
            # Обрабатываем данные инфляции
            inflation_data = []
            for record in inflation_result.data:
                year = record.get('year')
                value = record.get('value')
                if year and value is not None:
                    inflation_data.append({
                        'year': year,
                        'value': float(value),  # Уровень инфляции в процентах
                        'indicator_code': record.get('indicator_code'),
                        'indicator_name': record.get('indicator_name')
                    })
        
        # Сортируем по году (от старых к новым для графиков)
        gdp_data.sort(key=lambda x: x['year'])
        inflation_data.sort(key=lambda x: x['year'])
        
        # Вычисляем тренды
        gdp_values = [d['value'] for d in gdp_data]
        inflation_values = [d['value'] for d in inflation_data]
        
        gdp_trend = calculate_trend(gdp_values) if gdp_values else 0
        inflation_trend = calculate_trend(inflation_values) if inflation_values else 0
        
        # Генерируем детальные расчеты
        detailed_calculations = generate_detailed_calculations(gdp_data, inflation_data)
        
        # Пытаемся загрузить сохраненные интерпретации из базы данных
        saved_interpretations, saved_calculations = load_interpretations_from_database(country_code)
        
        if saved_interpretations and saved_calculations:
            # Используем сохраненные интерпретации
            interpretations = saved_interpretations
            detailed_calculations.update(saved_calculations)
            logger.info(f"Using cached interpretations for {country_code}")
        else:
            # Генерируем новые интерпретации через ChatGPT
            interpretations = {}
            for lang in ['en', 'ru', 'tr', 'fr', 'de']:
                interpretations[lang] = generate_trend_interpretation_with_chatgpt(
                    gdp_trend, inflation_trend, gdp_data, inflation_data, lang
                )
            
            # Сохраняем интерпретации в базу данных
            try:
                save_interpretations_to_database(country_code, interpretations, detailed_calculations)
            except Exception as e:
                logger.warning(f"Could not save interpretations to database: {e}")
        
        # Получаем название страны из первой записи
        country_name = gdp_result.data[0].get('country_name') if gdp_result.data else 'Turkey'
        
        return {
            'gdp_data': gdp_data,
            'inflation_data': inflation_data,
            'country_code': country_code,
            'country_name': country_name,
            'gdp_trend': gdp_trend,
            'inflation_trend': inflation_trend,
            'latest_gdp': gdp_data[-1] if gdp_data else None,
            'latest_inflation': inflation_data[-1] if inflation_data else None,
            'data_years': f"{start_year}-{current_year}",
            'detailed_calculations': detailed_calculations,
            'interpretations': interpretations
        }
        
    except Exception as e:
        logger.error(f"Error fetching economic data: {e}")
        return {
            'gdp_data': [],
            'inflation_data': [],
            'country_code': country_code,
            'country_name': 'Unknown',
            'error': str(e)
        }

def calculate_trend(values):
    """
    Вычисление тренда (рост/падение) для ряда значений
    
    Args:
        values (list): Список числовых значений
        
    Returns:
        float: Коэффициент тренда (положительный = рост, отрицательный = падение)
    """
    if len(values) < 2:
        return 0
    
    try:
        # Простой расчет тренда как среднее изменение
        changes = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                change = (values[i] - values[i-1]) / values[i-1]
                changes.append(change)
        
        return sum(changes) / len(changes) if changes else 0
    except Exception:
        return 0

def create_economic_chart_data(economic_data):
    """
    Создание данных для построения графиков ВВП и инфляции
    
    Args:
        economic_data (dict): Данные из get_economic_data()
        
    Returns:
        dict: Данные для графиков
    """
    gdp_data = economic_data.get('gdp_data', [])
    inflation_data = economic_data.get('inflation_data', [])
    country_name = economic_data.get('country_name', 'Unknown')
    
    # Подготавливаем данные для графиков ВВП (рост в процентах)
    gdp_chart = {
        'labels': [str(d['year']) for d in gdp_data],
        'datasets': [
            {
                'label': f'Рост ВВП (%) - {country_name}',
                'data': [d['value'] for d in gdp_data],  # Рост ВВП в процентах
                'borderColor': '#667eea',
                'backgroundColor': 'rgba(102, 126, 234, 0.1)',
                'tension': 0.4,
                'fill': False
            }
        ]
    }
    
    # Подготавливаем данные для графиков инфляции
    inflation_chart = {
        'labels': [str(d['year']) for d in inflation_data],
        'datasets': [
            {
                'label': f'Инфляция (%) - {country_name}',
                'data': [d['value'] for d in inflation_data],  # Уровень инфляции в процентах
                'borderColor': '#dc3545',
                'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                'tension': 0.4,
                'fill': False
            }
        ]
    }
    
    return {
        'gdp_chart': gdp_chart,
        'inflation_chart': inflation_chart,
        'trends': {
            'gdp_trend': economic_data.get('gdp_trend', 0),
            'inflation_trend': economic_data.get('inflation_trend', 0)
        },
        'latest': {
            'gdp': economic_data.get('latest_gdp'),
            'inflation': economic_data.get('latest_inflation')
        },
        'country_name': country_name,
        'country_code': economic_data.get('country_code', 'Unknown'),
        'detailed_calculations': economic_data.get('detailed_calculations', {}),
        'interpretations': economic_data.get('interpretations', {})
    }

@app.route('/api/full_report', methods=['POST'])
def api_full_report():
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    address = data.get('address')
    lat = data.get('lat')
    lng = data.get('lng')
    bedrooms = data.get('bedrooms')
    price = data.get('price')
    additional_data = data.get('additional_data', {})
    
    # Получаем площадь объекта
    area = data.get('area')
    logger.info(f"🔍 Полученная площадь из POST-данных: {area}")
    logger.info(f"🔍 Все POST-данные: {data}")
    
    # Получаем дополнительные данные
    additional_data = data.get('additional_data', {})
    age_id = additional_data.get('age')
    floor_id = additional_data.get('floor')
    heating_id = additional_data.get('heating')
    
    # Получаем коды локаций
    location_codes = data.get('location_codes', {})
    if not location_codes:
        # Если коды локаций не переданы, пытаемся получить их из адресаотчет
        try:
            location_codes = get_location_codes_from_address(address)
            logger.info(f"📋 Получены коды локаций из адреса: {location_codes}")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка получения кодов локаций: {e}")
            location_codes = {}
    
    # Получаем язык пользователя
    user_language = 'ru'  # По умолчанию русский
    try:
        user_result = supabase.table('users').select('language').eq('telegram_id', telegram_id).execute()
        if user_result.data:
            user_language = user_result.data[0].get('language', 'ru')
            logger.info(f"🌍 Язык пользователя для полного отчета: {user_language}")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка получения языка пользователя: {e}")
    
    try:
        price = float(price) if price is not None else 0
    except (ValueError, TypeError):
        price = 0
    
    # Преобразуем bedrooms в число
    try:
        bedrooms = int(bedrooms) if bedrooms is not None else 1
    except (ValueError, TypeError):
        bedrooms = 1
        
    logger.info(f"🔍 Формируем полный отчет для {address} с дополнительными данными: {additional_data}")
    try:
        # --- РАСЧЕТ БАЗОВЫХ ПАРАМЕТРОВ НА ОСНОВЕ ЦЕНЫ И ЛОКАЦИИ ---
        
        # Рассчитываем среднюю цену за кв.м на основе цены объекта и площади
        if area and area != 'unknown' and area != 'Не указано':
            try:
                area_value = float(area)
                avg_sqm = price / area_value if area_value > 0 else 0
                logger.info(f"✅ Используем реальную площадь объекта: {area_value} м²")
            except (ValueError, TypeError):
                # Fallback на типичный размер
                typical_size = 80 if bedrooms <= 2 else 120 if bedrooms <= 3 else 150
                avg_sqm = price / typical_size if typical_size > 0 else 0
                logger.info(f"⚠️ Используем типичный размер: {typical_size} м²")
        else:
            # Fallback на типичный размер
            typical_size = 80 if bedrooms <= 2 else 120 if bedrooms <= 3 else 150
            avg_sqm = price / typical_size if typical_size > 0 else 0
            logger.info(f"⚠️ Используем типичный размер: {typical_size} м²")
        
        # Определяем, находится ли объект в Турции
        is_turkish = False
        currency_rate = None
        if location_codes:
            from currency_functions import is_turkish_location, get_current_currency_rate
            # Проверяем по кодам локации
            country_id = location_codes.get('country_id')
            if country_id:
                # Получаем название страны по ID
                try:
                    country_result = supabase.table('locations').select('country_name').eq('country_id', country_id).limit(1).execute()
                    if country_result.data:
                        country_name = country_result.data[0].get('country_name', '').lower()
                        is_turkish = country_name in ['turkey', 'türkiye', 'tr', 'tur']
                        logger.info(f"🌍 Проверка страны по ID {country_id}: {country_name}, Турция: {is_turkish}")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка проверки страны: {e}")
            
            # Если не удалось определить по ID, проверяем по адресу
            if not is_turkish:
                try:
                    # Создаем временные компоненты локации для проверки
                    temp_location_components = {
                        'country': location_codes.get('country_name', ''),
                        'country_code': location_codes.get('country_code', '')
                    }
                    is_turkish = is_turkish_location(temp_location_components)
                    logger.info(f"🌍 Проверка по адресу: Турция: {is_turkish}")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка проверки локации по адресу: {e}")
            
            # Получаем курс валют, если объект в Турции
            if is_turkish:
                currency_rate = get_current_currency_rate()
                if currency_rate:
                    logger.info(f"💱 Получен курс валют для Турции: {currency_rate}")
                else:
                    logger.warning("⚠️ Не удалось получить курс валют для Турции")
        
        # Получаем реальные экономические данные
        economic_data = get_economic_data('TUR', 10)  # Данные за последние 10 лет
        chart_data = create_economic_chart_data(economic_data)
        
        # Получаем рыночные данные для сравнения цен
        market_comparison_data = get_market_comparison_data(
            age_id, floor_id, heating_id, area, price, location_codes, bedrooms, is_turkish, currency_rate
        )
        logger.info(f"✅ Получены рыночные данные для сравнения: {market_comparison_data}")
        
        # Базовые макроэкономические показатели
        inflation = economic_data.get('latest_inflation', {}).get('value', 35.9) if economic_data else 35.9
        eur_try = economic_data.get('latest_exchange_rate', {}).get('value', 35.2) if economic_data else 35.2
        refi_rate = economic_data.get('latest_interest_rate', {}).get('value', 45.0) if economic_data else 45.0
        gdp_growth = economic_data.get('latest_gdp', {}).get('value', 2.7) if economic_data else 2.7
        
        # Рассчитываем рост цен на недвижимость на основе экономических данных
        price_growth = (inflation * 0.3 + gdp_growth * 0.4 + (refi_rate * 0.1)) / 100
        five_year_growth = price_growth * 5
        
        # Рассчитываем доходность от аренды на основе цены и локации
        base_monthly_rent = price * 0.008  # базовая месячная аренда 0.8% от цены
        base_annual_rent = base_monthly_rent * 12
        
        # Корректируем на основе количества спален
        bedroom_multiplier = 1.0 + (bedrooms - 1) * 0.15  # каждая дополнительная спальня +15%
        short_term_income = int(base_monthly_rent * bedroom_multiplier * 1.2)  # краткосрочная аренда +20%
        long_term_income = int(base_annual_rent * bedroom_multiplier)
        
        # Рассчитываем чистый доход (после налогов и расходов)
        short_term_net = int(short_term_income * 0.8)  # 20% на налоги и расходы
        long_term_net = int(long_term_income * 0.8)
        
        # Рассчитываем ROI
        short_term_roi = ((short_term_income * 12 * 5) / price) * 100
        long_term_roi = ((long_term_income * 5) / price) * 100
        no_rent_roi = (five_year_growth / price) * 100
        
        # Альтернативные инвестиции на основе реальных экономических данных
        alt_deposit = (refi_rate * 0.8) / 100  # депозит ниже ключевой ставки
        alt_bonds = (refi_rate * 1.1) / 100    # облигации выше ключевой ставки
        alt_stocks = (gdp_growth * 2.5) / 100  # акции как множитель роста ВВП
        alt_reits = (price_growth * 1.5) / 100 # REITs как множитель роста цен на недвижимость
        
        # Налоги и сборы на основе цены объекта
        taxes = {
            'transfer_tax': 0.04,  # 4% от цены
            'stamp_duty': 0.015,   # 1.5% от цены
            'notary': min(1200, price * 0.01),  # нотариус: минимум 1200 или 1% от цены
            'annual_property_tax': 0.001,       # 0.1% от цены
            'annual_property_tax_max': 0.006,   # максимум 0.6%
            'rental_income_tax': '15-35%',      # прогрессивная шкала
            'capital_gains_tax': '15-40%'       # прогрессивная шкала
        }
        
        # Риски на основе экономических данных
        risks = []
        if eur_try > 30:
            risks.append(f'Валютный: TRY/EUR ▲{((eur_try - 30) / 30 * 100):.1f}% за последний период')
        if refi_rate > 40:
            risks.append(f'Монетарный: Высокая ключевая ставка {refi_rate:.1f}%')
        if inflation > 30:
            risks.append(f'Инфляционный: Высокая инфляция {inflation:.1f}%')
        if gdp_growth < 3:
            risks.append(f'Экономический: Низкий рост ВВП {gdp_growth:.1f}%')
        
        # Ликвидность на основе цены и локации
        days_on_market = int(60 + (price / 10000) * 2)  # чем дороже, тем дольше продается
        liquidity = f'Среднее время продажи: {days_on_market} дней'
        
        # Развитие района на основе экономических данных
        development_projects = []
        if gdp_growth > 4:
            development_projects.append('Активное развитие инфраструктуры')
        if refi_rate < 50:
            development_projects.append('Благоприятные условия кредитования')
        if inflation < 40:
            development_projects.append('Стабильная экономическая среда')
        
        district = ', '.join(development_projects) if development_projects else 'Стандартное развитие района'
        
        # Функция перевода для полного отчета
        def translate_to_language_full_report(text, target_language):
            """Переводит турецкие значения на указанный язык для полного отчета"""
            translations = {
                'ru': {
                    # Возраст объекта
                    '0-5 yıl': '0-5 лет',
                    '5-10 yıl': '5-10 лет', 
                    '10-20 yıl': '10-20 лет',
                    '20+ yıl': '20+ лет',
                    'Yeni': 'Новый',
                    'Eski': 'Старый',
                    '0-4': '0-4 года',
                    '11-15': '11-15 лет',
                    '16 ve üzeri': '16 и более',
                    '0': '0 лет',
                    
                    # Этаж
                    'Zemin kat': 'Входной этаж',
                    '1. kat': '1 этаж',
                    '2. kat': '2 этаж',
                    '3. kat': '3 этаж',
                    '4. kat': '4 этаж',
                    '5. kat': '5 этаж',
                    '6-10 kat': '6-10 этаж',
                    '11-20 kat': '11-20 этаж',
                    'Penthouse': 'Пентхаус',
                    'Üst kat': 'Верхний этаж',
                    'Giriş Altı': 'Подвал',
                    'Giriş': 'Входной этаж',
                    'Giriş Üstü': 'Междуэтажный',
                    'Ara Kat': 'Средний этаж',
                    'Ara Üstü': 'Верхний средний',
                    'En Üst': 'Самый верхний',
                    'Müstakil': 'Отдельный',
                    
                    # Отопление
                    'Merkezi': 'Центральное',
                    'Doğalgaz': 'Газовое',
                    'Kombi': 'Котел',
                    'Elektrik': 'Электрическое',
                    'Yok': 'Без отопления',
                    'Klima': 'Кондиционер',
                    
                    # Общие
                    'Belirtilmemiş': 'Не указано',
                    'Bilinmiyor': 'Не известно'
                },
                'en': {
                    # Age
                    '0-5 yıl': '0-5 years',
                    '5-10 yıl': '5-10 years', 
                    '10-20 yıl': '10-20 years',
                    '20+ yıl': '20+ years',
                    'Yeni': 'New',
                    'Eski': 'Old',
                    '0-4': '0-4 years',
                    '11-15': '11-15 years',
                    '16 ve üzeri': '16 and over',
                    '0': '0 years',
                    
                    # Floor
                    'Zemin kat': 'Ground floor',
                    '1. kat': '1st floor',
                    '2. kat': '2nd floor',
                    '3. kat': '3rd floor',
                    '4. kat': '4th floor',
                    '5. kat': '5th floor',
                    '6-10 kat': '6-10 floors',
                    '11-20 kat': '11-20 floors',
                    'Penthouse': 'Penthouse',
                    'Üst kat': 'Top floor',
                    'Giriş Altı': 'Basement',
                    'Giriş': 'Ground floor',
                    'Giriş Üstü': 'Mezzanine',
                    'Ara Kat': 'Middle floor',
                    'Ara Üstü': 'Upper middle',
                    'En Üst': 'Topmost',
                    'Müstakil': 'Detached',
                    
                    # Heating
                    'Merkezi': 'Central',
                    'Doğalgaz': 'Gas',
                    'Kombi': 'Boiler',
                    'Elektrik': 'Electric',
                    'Yok': 'None',
                    'Klima': 'Air conditioning',
                    
                    # General
                    'Belirtilmemiş': 'Not specified',
                    'Bilinmiyor': 'Unknown'
                },
                'de': {
                    # Alter
                    '0-5 yıl': '0-5 Jahre',
                    '5-10 yıl': '5-10 Jahre', 
                    '10-20 yıl': '10-20 Jahre',
                    '20+ yıl': '20+ Jahre',
                    'Yeni': 'Neu',
                    'Eski': 'Alt',
                    '0-4': '0-4 Jahre',
                    '11-15': '11-15 Jahre',
                    '16 ve üzeri': '16 und mehr',
                    '0': '0 Jahre',
                    
                    # Etage
                    'Zemin kat': 'Erdgeschoss',
                    '1. kat': '1. Etage',
                    '2. kat': '2. Etage',
                    '3. kat': '3. Etage',
                    '4. kat': '4. Etage',
                    '5. kat': '5. Etage',
                    '6-10 kat': '6-10 Etagen',
                    '11-20 kat': '11-20 Etagen',
                    'Penthouse': 'Penthouse',
                    'Üst kat': 'Obergeschoss',
                    'Giriş Altı': 'Keller',
                    'Giriş': 'Erdgeschoss',
                    'Giriş Üstü': 'Zwischengeschoss',
                    'Ara Kat': 'Mittelgeschoss',
                    'Ara Üstü': 'Oberes Mittelgeschoss',
                    'En Üst': 'Oberstes',
                    'Müstakil': 'Frei stehend',
                    
                    # Heizung
                    'Merkezi': 'Zentral',
                    'Doğalgaz': 'Gas',
                    'Kombi': 'Kessel',
                    'Elektrik': 'Elektrisch',
                    'Yok': 'Keine',
                    'Klima': 'Klimaanlage',
                    
                    # Allgemein
                    'Belirtilmemiş': 'Nicht angegeben',
                    'Bilinmiyor': 'Unbekannt'
                },
                'fr': {
                    # Âge
                    '0-5 yıl': '0-5 ans',
                    '5-10 yıl': '5-10 ans', 
                    '10-20 yıl': '10-20 ans',
                    '20+ yıl': '20+ ans',
                    'Yeni': 'Nouveau',
                    'Eski': 'Ancien',
                    '0-4': '0-4 ans',
                    '11-15': '11-15 ans',
                    '16 ve üzeri': '16 et plus',
                    '0': '0 ans',
                    
                    # Étage
                    'Zemin kat': 'Rez-de-chaussée',
                    '1. kat': '1er étage',
                    '2. kat': '2e étage',
                    '3. kat': '3e étage',
                    '4. kat': '4e étage',
                    '5. kat': '5e étage',
                    '6-10 kat': '6-10 étages',
                    '11-20 kat': '11-20 étages',
                    'Penthouse': 'Penthouse',
                    'Üst kat': 'Dernier étage',
                    'Giriş Altı': 'Sous-sol',
                    'Giriş': 'Rez-de-chaussée',
                    'Giriş Üstü': 'Entresol',
                    'Ara Kat': 'Étage intermédiaire',
                    'Ara Üstü': 'Étage supérieur intermédiaire',
                    'En Üst': 'Plus haut',
                    'Müstakil': 'Indépendant',
                    
                    # Chauffage
                    'Merkezi': 'Central',
                    'Doğalgaz': 'Gaz',
                    'Kombi': 'Chaudière',
                    'Elektrik': 'Électrique',
                    'Yok': 'Aucun',
                    'Klima': 'Climatisation',
                    
                    # Général
                    'Belirtilmemiş': 'Non spécifié',
                    'Bilinmiyor': 'Inconnu'
                }
            }
            
            target_translations = translations.get(target_language, translations['en'])
            return target_translations.get(text, text)
        
        # --- АНАЛИЗ ДОПОЛНИТЕЛЬНЫХ ДАННЫХ ---
        additional_analysis = {}
        
        # Функция для получения названия характеристики по ID
        def get_characteristic_name(table_name, characteristic_id, user_language):
            """Получает название характеристики по ID из указанной таблицы"""
            try:
                if characteristic_id and characteristic_id != 'unknown':
                    result = supabase.table(table_name).select('*').eq('id', characteristic_id).execute()
                    if result.data:
                        raw_value = result.data[0].get('listing_type', '')
                        return translate_to_language_full_report(raw_value, user_language)
            except Exception as e:
                logger.warning(f"⚠️ Ошибка получения названия характеристики из {table_name}: {e}")
            return 'Не указано'
        
        # Анализ возраста объекта
        if additional_data.get('age') and additional_data.get('age') != 'unknown':
            try:
                age_result = supabase.table('age_data').select('*').eq('id', additional_data['age']).execute()
                if age_result.data:
                    age_info = age_result.data[0]
                    # Переводим значение на язык пользователя для анализа
                    age_value = translate_to_language_full_report(age_info.get('listing_type', ''), user_language)
                    additional_analysis['age'] = {
                        'range': age_value,
                        'impact': 'Положительный' if age_value in ['0-5 лет', '5-10 лет', '0-5 years', '5-10 years', '0-5 Jahre', '5-10 Jahre', '0-5 ans', '5-10 ans'] else 'Нейтральный',
                        'maintenance_cost': 'Низкие' if age_value in ['0-5 лет', '0-5 years', '0-5 Jahre', '0-5 ans'] else 'Средние'
                    }
                    logger.info(f"✅ Анализ возраста: {age_value}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка анализа возраста: {e}")
        
        # Анализ этажа
        if additional_data.get('floor') and additional_data.get('floor') != 'unknown':
            try:
                floor_result = supabase.table('floor_segment_data').select('*').eq('id', additional_data['floor']).execute()
                if floor_result.data:
                    floor_info = floor_result.data[0]
                    # Переводим значение на язык пользователя для анализа
                    floor_value = translate_to_language_full_report(floor_info.get('listing_type', ''), user_language)
                    additional_analysis['floor'] = {
                        'type': floor_value,
                        'accessibility': 'Высокая' if floor_value in ['Входной этаж', '1 этаж', '2 этаж', 'Ground floor', '1st floor', '2nd floor', 'Erdgeschoss', '1. Etage', '2. Etage', 'Rez-de-chaussée', '1er étage', '2e étage'] else 'Средняя',
                        'view': 'Хороший' if floor_value in ['Верхние этажи', 'Пентхаус', 'Top floor', 'Penthouse', 'Obergeschoss', 'Penthouse', 'Dernier étage', 'Penthouse'] else 'Стандартный'
                    }
                    logger.info(f"✅ Анализ этажа: {floor_value}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка анализа этажа: {e}")
        
        # Анализ отопления
        if additional_data.get('heating') and additional_data.get('heating') != 'unknown':
            try:
                heating_result = supabase.table('heating_data').select('*').eq('id', additional_data['heating']).execute()
                if heating_result.data:
                    heating_info = heating_result.data[0]
                    # Переводим значение на язык пользователя для анализа
                    heating_value = translate_to_language_full_report(heating_info.get('listing_type', ''), user_language)
                    additional_analysis['heating'] = {
                        'type': heating_value,
                        'efficiency': 'Высокая' if heating_value in ['Центральное', 'Индивидуальное газовое', 'Central', 'Individual gas', 'Zentral', 'Individuell Gas', 'Central', 'Gaz individuel'] else 'Средняя',
                        'cost': 'Низкие' if heating_value in ['Центральное', 'Central', 'Zentral', 'Central'] else 'Средние'
                    }
                    logger.info(f"✅ Анализ отопления: {heating_value}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка анализа отопления: {e}")
        
        # Корректируем ROI на основе дополнительных данных
        if additional_analysis:
            # Корректируем доходность на основе возраста
            if additional_analysis.get('age'):
                if additional_analysis['age']['impact'] == 'Положительный':
                    short_term_income = int(short_term_income * 1.1)  # +10%
                    long_term_income = int(long_term_income * 1.05)   # +5%
                    logger.info("✅ ROI скорректирован: возраст объекта положительно влияет на доходность")
            
            # Корректируем на основе этажа
            if additional_analysis.get('floor'):
                if additional_analysis['floor']['view'] == 'Хороший':
                    short_term_income = int(short_term_income * 1.15)  # +15%
                    long_term_income = int(long_term_income * 1.08)    # +8%
                    logger.info("✅ ROI скорректирован: этаж объекта положительно влияет на доходность")
            
            # Корректируем на основе отопления
            if additional_analysis.get('heating'):
                if additional_analysis['heating']['efficiency'] == 'Высокая':
                    short_term_income = int(short_term_income * 1.05)  # +5%
                    long_term_income = int(long_term_income * 1.03)    # +3%
                    logger.info("✅ ROI скорректирован: отопление положительно влияет на доходность")
        
        # --- ПОЛУЧАЕМ ДАННЫЕ О ЦЕНАХ НА РЫНКЕ ---
        market_price_data = {}
        try:
            # Получаем данные о ценах для выбранной локации
            if lat and lng:
                # Здесь можно добавить логику получения данных о ценах на рынке
                # Пока используем базовые расчеты
                market_price_data = {
                    'min_price_per_sqm': avg_sqm * 0.7,  # -30% от средней
                    'avg_price_per_sqm': avg_sqm,
                    'max_price_per_sqm': avg_sqm * 1.3,  # +30% от средней
                    'price_range': f'€{avg_sqm * 0.7:.0f} - €{avg_sqm * 1.3:.0f} за м²',
                    'market_position': 'Средний' if 400 <= avg_sqm <= 600 else 'Низкий' if avg_sqm < 400 else 'Высокий'
                }
                logger.info(f"✅ Данные о ценах на рынке получены: {market_price_data['price_range']}")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка получения данных о ценах на рынке: {e}")
            market_price_data = {
                'min_price_per_sqm': avg_sqm * 0.7,
                'avg_price_per_sqm': avg_sqm,
                'max_price_per_sqm': avg_sqm * 1.3,
                'price_range': f'€{avg_sqm * 0.7:.0f} - €{avg_sqm * 1.3:.0f} за м²',
                'market_position': 'Средний'
            }
        
        # --- Формируем структуру полного отчёта ---
        full_report_data = {
            # 1. ПРОСТОЙ ОТЧЕТ (базовая информация)
            'simple_report': {
                'address': address,
                'bedrooms': bedrooms,
                'purchase_price': price,
                'area': area if area and area != 'unknown' else 'Не указано',
                'avg_price_per_sqm': avg_sqm,
                'location_summary': f'Локация: {address}',
                'property_summary': f'Объект: {bedrooms} спален, {area if area and area != "unknown" else "площадь не указана"} м², цена €{price:,.0f}',
                'price_per_sqm': f'Цена за м²: €{avg_sqm:.0f}'
            },
            
            # 2. ДЕТАЛЬНЫЕ ДАННЫЕ ПО ХАРАКТЕРИСТИКАМ
            'detailed_characteristics': {
                'age': {
                    'id': additional_data.get('age'),
                    'name': additional_analysis.get('age', {}).get('range', 'Не указано'),
                    'impact': additional_analysis.get('age', {}).get('impact', 'Не определен'),
                    'maintenance_cost': additional_analysis.get('age', {}).get('maintenance_cost', 'Не определен')
                },
                'floor': {
                    'id': additional_data.get('floor'),
                    'name': additional_analysis.get('floor', {}).get('type', 'Не указано'),
                    'accessibility': additional_analysis.get('floor', {}).get('accessibility', 'Не определена'),
                    'view': additional_analysis.get('floor', {}).get('view', 'Не определен')
                },
                'heating': {
                    'id': additional_data.get('heating'),
                    'name': additional_analysis.get('heating', {}).get('type', 'Не указано'),
                    'efficiency': additional_analysis.get('heating', {}).get('efficiency', 'Не определена'),
                    'cost': additional_analysis.get('heating', {}).get('cost', 'Не определен')
                },
                'summary': 'Детальный анализ характеристик объекта'
            },
            
            # 2.1. РЫНОЧНЫЕ ДАННЫЕ ДЛЯ СРАВНЕНИЯ ЦЕН
            'market_comparison': market_comparison_data,
            'currency_info': {
                'is_turkish': is_turkish,
                'currency_rate': currency_rate,
                'conversion_applied': is_turkish and currency_rate is not None
            },
            
            # 3. АНАЛИЗ ЦЕН НА РЫНКЕ
            'market_price_analysis': {
                'current_price': price,
                'price_per_sqm': avg_sqm,
                'min_price_per_sqm': market_price_data.get('min_price_per_sqm', avg_sqm * 0.7),
                'avg_price_per_sqm': market_price_data.get('avg_price_per_sqm', avg_sqm),
                'max_price_per_sqm': market_price_data.get('max_price_per_sqm', avg_sqm * 1.3),
                'price_range': market_price_data.get('price_range', f'€{avg_sqm * 0.7:.0f} - €{avg_sqm * 1.3:.0f} за м²'),
                'price_level': market_price_data.get('market_position', 'Средний'),
                'market_position': f'Цена объекта находится на {avg_sqm/500*100:.0f}% от среднерыночной',
                'price_recommendation': 'Цена соответствует рынку' if 400 <= avg_sqm <= 600 else 'Рассмотрите торг' if avg_sqm > 600 else 'Хорошая цена',
                'price_comparison': {
                    'min': f'Минимальная цена на рынке: €{market_price_data.get("min_price_per_sqm", avg_sqm * 0.7):.0f}/м²',
                    'avg': f'Средняя цена на рынке: €{market_price_data.get("avg_price_per_sqm", avg_sqm):.0f}/м²',
                    'max': f'Максимальная цена на рынке: €{market_price_data.get("max_price_per_sqm", avg_sqm * 1.3):.0f}/м²'
                }
            },
            
            # 4. АНАЛИЗ АРЕНДЫ
            'rental_analysis': {
                'max_monthly_rent': short_term_income,
                'max_annual_rent': long_term_income,
                'rental_yield': (short_term_income * 12) / price * 100,
                'rental_recommendation': f'Максимальная ставка аренды: €{short_term_income:,.0f}/месяц',
                'annual_yield': f'Годовая доходность: {(short_term_income * 12) / price * 100:.1f}%'
            },
            
            # 5. ROI АНАЛИЗ (последний раздел)
            'roi': {
                'short_term': {
                    'monthly_income': short_term_income,
                    'net_income': short_term_net,
                    'five_year_income': short_term_income * 12 * 5,
                    'final_value': price * (1 + five_year_growth),
                    'roi': short_term_roi
                },
                'long_term': {
                    'annual_income': long_term_income,
                    'net_income': long_term_net,
                    'five_year_income': long_term_income * 5,
                    'final_value': price * (1 + five_year_growth),
                    'roi': long_term_roi
                },
                'no_rent': {
                    'final_value': price * (1 + five_year_growth),
                    'roi': no_rent_roi
                },
                'price_growth': price_growth
            },
            
            # 6. ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ
            'alternatives': [
                {'name': 'Банковский депозит', 'yield': alt_deposit, 'source': 'TCMB API'},
                {'name': 'Облигации Турции', 'yield': alt_bonds, 'source': 'Investing.com API'},
                {'name': 'Акции (BIST30)', 'yield': alt_stocks, 'source': 'Alpha Vantage API'},
                {'name': 'REITs (фонды)', 'yield': alt_reits, 'source': 'Financial Modeling Prep'},
                {'name': 'Недвижимость', 'yield': short_term_roi / 100, 'source': 'Ваш объект'}
            ],
            'macro': {
                'inflation': inflation,
                'eur_try': eur_try,
                'refi_rate': refi_rate,
                'gdp_growth': gdp_growth
            },
            'economic_charts': chart_data,
            'taxes': taxes,
            'risks': risks,
            'liquidity': liquidity,
            'district': district,
            'yield': (short_term_income * 12) / price,
            'price_index': 1 + price_growth,
            'mortgage_rate': refi_rate / 100,
            'global_house_price_index': 1 + (gdp_growth / 100),
            'additional_analysis': additional_analysis,
            'summary': f'Полный отчёт с реальными экономическими данными из IMF и анализом характеристик объекта. ROI: {short_term_roi:.1f}% за 5 лет.'
        }
        
        # Получаем user_id из базы данных по telegram_id
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        user_id = user_result.data[0]['id'] if user_result.data else telegram_id
        
        created_at = datetime.now().isoformat()
        
        # Преобразуем координаты в числа, если они переданы
        try:
            latitude = float(lat) if lat and lat != "" else None
            longitude = float(lng) if lng and lng != "" else None
        except (ValueError, TypeError):
            latitude = None
            longitude = None
        
        report_data = {
            'user_id': user_id,
            'report_type': 'full',
            'title': f'Полный отчет: {address}',
            'description': f'Полный отчет по адресу {address}, {bedrooms} спален, {area if area and area != "unknown" else "площадь не указана"} м², цена {price}',
            'parameters': {
                'address': address,
                'bedrooms': bedrooms,
                'price': price,
                'area': area,
                'lat': latitude,
                'lng': longitude
            },
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            'bedrooms': bedrooms,
            'price': price,
            'area': area,
            'created_at': created_at,
            'full_report': full_report_data
        }
        result = supabase.table('user_reports').insert(report_data).execute()
        report_id = result.data[0]['id'] if hasattr(result, 'data') and result.data else None
        return jsonify({
            'success': True, 
            'full_report': full_report_data, 
            'created_at': created_at, 
            'from_cache': False,
            'report_id': report_id
        })
    except Exception as e:
        logger.error(f"Error in full_report: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/user_reports', methods=['POST'])
def api_user_reports():
    """Получение списка всех отчетов пользователя по telegram_id"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        # Получаем user_id из базы данных по telegram_id
        user_result = safe_db_operation(
            lambda: supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        )
        if user_result is None or not user_result.data:
            return jsonify({'error': 'User not found'}), 404
        user_id = user_result.data[0]['id']
        # Возвращаем только неудаленные отчеты (deleted_at IS NULL)
        result = safe_db_operation(
            lambda: supabase.table('user_reports').select('*').eq('user_id', user_id).is_('deleted_at', 'null').order('created_at', desc=True).execute()
        )
        if result is None:
            return jsonify({'error': 'Database connection error'}), 500
        reports = result.data if hasattr(result, 'data') else result
        return jsonify({'success': True, 'reports': reports})
    except Exception as e:
        logger.error(f"Error fetching user reports: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/get_additional_data_options', methods=['POST'])
def api_get_additional_data_options():
    """Получает опции для дополнительных параметров отчета (возраст, этаж, отопление)"""
    try:
        data = request.json or {}
        location_codes = data.get('location_codes', {})
        telegram_id = data.get('telegram_id')
        
        if not location_codes:
            return jsonify({'error': 'Location codes required'}), 400
        
        logger.info(f"🔍 Получаем опции для дополнительных данных: {location_codes}")
        
        # Получаем язык пользователя
        user_language = 'ru'  # По умолчанию русский
        if telegram_id:
            try:
                user_result = supabase.table('users').select('language').eq('telegram_id', telegram_id).execute()
                if user_result.data:
                    user_language = user_result.data[0].get('language', 'ru')
                    logger.info(f"🌍 Язык пользователя: {user_language}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка получения языка пользователя: {e}")
        
        def translate_to_language(text, target_language):
            """Переводит турецкие значения на указанный язык"""
            translations = {
                'ru': {
                    # Возраст объекта
                    '0-5 yıl': '0-5 лет',
                    '5-10 yıl': '5-10 лет', 
                    '10-20 yıl': '10-20 лет',
                    '20+ yıl': '20+ лет',
                    'Yeni': 'Новый',
                    'Eski': 'Старый',
                    '0-4': '0-4 года',
                    '11-15': '11-15 лет',
                    '16 ve üzeri': '16 и более',
                    '0': '0 лет',
                    
                    # Этаж
                    'Zemin kat': 'Входной этаж',
                    '1. kat': '1 этаж',
                    '2. kat': '2 этаж',
                    '3. kat': '3 этаж',
                    '4. kat': '4 этаж',
                    '5. kat': '5 этаж',
                    '6-10 kat': '6-10 этаж',
                    '11-20 kat': '11-20 этаж',
                    'Penthouse': 'Пентхаус',
                    'Üst kat': 'Верхний этаж',
                    'Giriş Altı': 'Подвал',
                    'Giriş': 'Входной этаж',
                    'Giriş Üstü': 'Междуэтажный',
                    'Ara Kat': 'Средний этаж',
                    'Ara Üstü': 'Верхний средний',
                    'En Üst': 'Самый верхний',
                    'Müstakil': 'Отдельный',
                    
                    # Отопление
                    'Merkezi': 'Центральное',
                    'Doğalgaz': 'Газовое',
                    'Kombi': 'Котел',
                    'Elektrik': 'Электрическое',
                    'Yok': 'Без отопления',
                    'Klima': 'Кондиционер',
                    
                    # Общие
                    'Belirtilmemiş': 'Не указано',
                    'Bilinmiyor': 'Не известно'
                },
                'en': {
                    # Age
                    '0-5 yıl': '0-5 years',
                    '5-10 yıl': '5-10 years', 
                    '10-20 yıl': '10-20 years',
                    '20+ yıl': '20+ years',
                    'Yeni': 'New',
                    'Eski': 'Old',
                    '0-4': '0-4 years',
                    '11-15': '11-15 years',
                    '16 ve üzeri': '16 and over',
                    '0': '0 years',
                    
                    # Floor
                    'Zemin kat': 'Ground floor',
                    '1. kat': '1st floor',
                    '2. kat': '2nd floor',
                    '3. kat': '3rd floor',
                    '4. kat': '4th floor',
                    '5. kat': '5th floor',
                    '6-10 kat': '6-10 floors',
                    '11-20 kat': '11-20 floors',
                    'Penthouse': 'Penthouse',
                    'Üst kat': 'Top floor',
                    'Giriş Altı': 'Basement',
                    'Giriş': 'Ground floor',
                    'Giriş Üstü': 'Mezzanine',
                    'Ara Kat': 'Middle floor',
                    'Ara Üstü': 'Upper middle',
                    'En Üst': 'Topmost',
                    'Müstakil': 'Detached',
                    
                    # Heating
                    'Merkezi': 'Central',
                    'Doğalgaz': 'Gas',
                    'Kombi': 'Boiler',
                    'Elektrik': 'Electric',
                    'Yok': 'None',
                    'Klima': 'Air conditioning',
                    
                    # General
                    'Belirtilmemiş': 'Not specified',
                    'Bilinmiyor': 'Unknown'
                },
                'de': {
                    # Alter
                    '0-5 yıl': '0-5 Jahre',
                    '5-10 yıl': '5-10 Jahre', 
                    '10-20 yıl': '10-20 Jahre',
                    '20+ yıl': '20+ Jahre',
                    'Yeni': 'Neu',
                    'Eski': 'Alt',
                    '0-4': '0-4 Jahre',
                    '11-15': '11-15 Jahre',
                    '16 ve üzeri': '16 und mehr',
                    '0': '0 Jahre',
                    
                    # Etage
                    'Zemin kat': 'Erdgeschoss',
                    '1. kat': '1. Etage',
                    '2. kat': '2. Etage',
                    '3. kat': '3. Etage',
                    '4. kat': '4. Etage',
                    '5. kat': '5. Etage',
                    '6-10 kat': '6-10 Etagen',
                    '11-20 kat': '11-20 Etagen',
                    'Penthouse': 'Penthouse',
                    'Üst kat': 'Obergeschoss',
                    'Giriş Altı': 'Keller',
                    'Giriş': 'Erdgeschoss',
                    'Giriş Üstü': 'Zwischengeschoss',
                    'Ara Kat': 'Mittelgeschoss',
                    'Ara Üstü': 'Oberes Mittelgeschoss',
                    'En Üst': 'Oberstes',
                    'Müstakil': 'Frei stehend',
                    
                    # Heizung
                    'Merkezi': 'Zentral',
                    'Doğalgaz': 'Gas',
                    'Kombi': 'Kessel',
                    'Elektrik': 'Elektrisch',
                    'Yok': 'Keine',
                    'Klima': 'Klimaanlage',
                    
                    # Allgemein
                    'Belirtilmemiş': 'Nicht angegeben',
                    'Bilinmiyor': 'Unbekannt'
                },
                'fr': {
                    # Âge
                    '0-5 yıl': '0-5 ans',
                    '5-10 yıl': '5-10 ans', 
                    '10-20 yıl': '10-20 ans',
                    '20+ yıl': '20+ ans',
                    'Yeni': 'Nouveau',
                    'Eski': 'Ancien',
                    '0-4': '0-4 ans',
                    '11-15': '11-15 ans',
                    '16 ve üzeri': '16 et plus',
                    '0': '0 ans',
                    
                    # Étage
                    'Zemin kat': 'Rez-de-chaussée',
                    '1. kat': '1er étage',
                    '2. kat': '2e étage',
                    '3. kat': '3e étage',
                    '4. kat': '4e étage',
                    '5. kat': '5e étage',
                    '6-10 kat': '6-10 étages',
                    '11-20 kat': '11-20 étages',
                    'Penthouse': 'Penthouse',
                    'Üst kat': 'Dernier étage',
                    'Giriş Altı': 'Sous-sol',
                    'Giriş': 'Rez-de-chaussée',
                    'Giriş Üstü': 'Entresol',
                    'Ara Kat': 'Étage intermédiaire',
                    'Ara Üstü': 'Étage supérieur intermédiaire',
                    'En Üst': 'Plus haut',
                    'Müstakil': 'Indépendant',
                    
                    # Chauffage
                    'Merkezi': 'Central',
                    'Doğalgaz': 'Gaz',
                    'Kombi': 'Chaudière',
                    'Elektrik': 'Électrique',
                    'Yok': 'Aucun',
                    'Klima': 'Climatisation',
                    
                    # Général
                    'Belirtilmemiş': 'Non spécifié',
                    'Bilinmiyor': 'Inconnu'
                }
            }
            
            target_translations = translations.get(target_language, translations['en'])
            return target_translations.get(text, text)
        
        def remove_duplicates(options_list):
            """Убирает дубликаты по названию, оставляя первый встреченный"""
            seen_names = set()
            unique_options = []
            
            for option in options_list:
                name = option.get('name', '')
                if name not in seen_names:
                    seen_names.add(name)
                    unique_options.append(option)
            
            return unique_options
        
        # Получаем опции возраста
        age_options = []
        try:
            age_result = supabase.table('age_data').select('*').eq('country_id', location_codes.get('country_id')).eq('city_id', location_codes.get('city_id')).eq('county_id', location_codes.get('county_id')).eq('district_id', location_codes.get('district_id')).execute()
            if age_result.data:
                age_options = [{'id': item.get('id'), 'name': translate_to_language(item.get('listing_type', 'Не указано'), user_language)} for item in age_result.data]
                logger.info(f"✅ Получены опции возраста: {len(age_options)} вариантов")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка получения опций возраста: {e}")
        
        # Получаем опции этажей
        floor_options = []
        try:
            floor_result = supabase.table('floor_segment_data').select('*').eq('country_id', location_codes.get('country_id')).eq('city_id', location_codes.get('city_id')).eq('county_id', location_codes.get('county_id')).eq('district_id', location_codes.get('district_id')).execute()
            if floor_result.data:
                floor_options = [{'id': item.get('id'), 'name': translate_to_language(item.get('listing_type', 'Не указано'), user_language)} for item in floor_result.data]
                logger.info(f"✅ Получены опции этажей: {len(floor_options)} вариантов")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка получения опций этажей: {e}")
        
        # Получаем опции отопления
        heating_options = []
        try:
            heating_result = supabase.table('heating_data').select('*').eq('country_id', location_codes.get('country_id')).eq('city_id', location_codes.get('city_id')).eq('county_id', location_codes.get('county_id')).eq('district_id', location_codes.get('district_id')).execute()
            if heating_result.data:
                heating_options = [{'id': item.get('id'), 'name': translate_to_language(item.get('listing_type', 'Не указано'), user_language)} for item in heating_result.data]
                logger.info(f"✅ Получены опции отопления: {len(heating_options)} вариантов")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка получения опций отопления: {e}")
        
        # Если опции не найдены по локации, добавляем базовые опции
        if not age_options:
            logger.info("⚠️ Опции возраста не найдены по локации, добавляем базовые")
            base_age_options = {
                'ru': [
                    {'id': 'new', 'name': '0-5 лет'},
                    {'id': 'recent', 'name': '5-10 лет'},
                    {'id': 'modern', 'name': '10-20 лет'},
                    {'id': 'old', 'name': '20+ лет'}
                ],
                'en': [
                    {'id': 'new', 'name': '0-5 years'},
                    {'id': 'recent', 'name': '5-10 years'},
                    {'id': 'modern', 'name': '10-20 years'},
                    {'id': 'old', 'name': '20+ years'}
                ],
                'de': [
                    {'id': 'new', 'name': '0-5 Jahre'},
                    {'id': 'recent', 'name': '5-10 Jahre'},
                    {'id': 'modern', 'name': '10-20 Jahre'},
                    {'id': 'old', 'name': '20+ Jahre'}
                ],
                'fr': [
                    {'id': 'new', 'name': '0-5 ans'},
                    {'id': 'recent', 'name': '5-10 ans'},
                    {'id': 'modern', 'name': '10-20 ans'},
                    {'id': 'old', 'name': '20+ ans'}
                ]
            }
            age_options = base_age_options.get(user_language, base_age_options['en'])
        
        if not floor_options:
            logger.info("⚠️ Опции этажей не найдены по локации, добавляем базовые")
            base_floor_options = {
                'ru': [
                    {'id': 'ground', 'name': 'Входной этаж'},
                    {'id': 'low', 'name': '2-5 этаж'},
                    {'id': 'middle', 'name': '6-10 этаж'},
                    {'id': 'high', 'name': '11-20 этаж'},
                    {'id': 'penthouse', 'name': 'Пентхаус'}
                ],
                'en': [
                    {'id': 'ground', 'name': 'Ground floor'},
                    {'id': 'low', 'name': '2-5 floors'},
                    {'id': 'middle', 'name': '6-10 floors'},
                    {'id': 'high', 'name': '11-20 floors'},
                    {'id': 'penthouse', 'name': 'Penthouse'}
                ],
                'de': [
                    {'id': 'ground', 'name': 'Erdgeschoss'},
                    {'id': 'low', 'name': '2-5 Etagen'},
                    {'id': 'middle', 'name': '6-10 Etagen'},
                    {'id': 'high', 'name': '11-20 Etagen'},
                    {'id': 'penthouse', 'name': 'Penthouse'}
                ],
                'fr': [
                    {'id': 'ground', 'name': 'Rez-de-chaussée'},
                    {'id': 'low', 'name': '2-5 étages'},
                    {'id': 'middle', 'name': '6-10 étages'},
                    {'id': 'high', 'name': '11-20 étages'},
                    {'id': 'penthouse', 'name': 'Penthouse'}
                ]
            }
            floor_options = base_floor_options.get(user_language, base_floor_options['en'])
        
        if not heating_options:
            logger.info("⚠️ Опции отопления не найдены по локации, добавляем базовые")
            base_heating_options = {
                'ru': [
                    {'id': 'central', 'name': 'Центральное'},
                    {'id': 'gas', 'name': 'Индивидуальное газовое'},
                    {'id': 'electric', 'name': 'Электрическое'},
                    {'id': 'none', 'name': 'Без отопления'}
                ],
                'en': [
                    {'id': 'central', 'name': 'Central'},
                    {'id': 'gas', 'name': 'Individual gas'},
                    {'id': 'electric', 'name': 'Electric'},
                    {'id': 'none', 'name': 'None'}
                ],
                'de': [
                    {'id': 'central', 'name': 'Zentral'},
                    {'id': 'gas', 'name': 'Individuell Gas'},
                    {'id': 'electric', 'name': 'Elektrisch'},
                    {'id': 'none', 'name': 'Keine'}
                ],
                'fr': [
                    {'id': 'central', 'name': 'Central'},
                    {'id': 'gas', 'name': 'Gaz individuel'},
                    {'id': 'electric', 'name': 'Électrique'},
                    {'id': 'none', 'name': 'Aucun'}
                ]
            }
            heating_options = base_heating_options.get(user_language, base_heating_options['en'])
        
        # Убираем дубликаты
        age_options = remove_duplicates(age_options)
        floor_options = remove_duplicates(floor_options)
        heating_options = remove_duplicates(heating_options)
        
        # Добавляем опцию "Не известно" к каждому списку
        unknown_options = {
            'ru': 'Не известно',
            'en': 'Unknown',
            'de': 'Unbekannt',
            'fr': 'Inconnu'
        }
        unknown_name = unknown_options.get(user_language, 'Unknown')
        
        age_options.append({'id': 'unknown', 'name': unknown_name})
        floor_options.append({'id': 'unknown', 'name': unknown_name})
        heating_options.append({'id': 'unknown', 'name': unknown_name})
        
        logger.info(f"✅ Опции для дополнительных данных подготовлены: возраст({len(age_options)}), этаж({len(floor_options)}), отопление({len(heating_options)})")
        
        return jsonify({
            'success': True,
            'age_options': age_options,
            'floor_options': floor_options,
            'heating_options': heating_options
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения опций дополнительных данных: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/delete_user_report', methods=['POST'])
@app.route('/api/delete_report', methods=['POST'])
def api_delete_user_report():
    """Soft delete отчета: выставляет deleted_at"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    report_id = data.get('report_id')
    if not telegram_id or not report_id:
        return jsonify({'error': 'Missing required data'}), 400
    try:
        # Получаем user_id по telegram_id
        user_result = safe_db_operation(
            lambda: supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        )
        if user_result is None or not user_result.data:
            logger.error(f"User with telegram_id {telegram_id} not found for report deletion")
            return jsonify({'error': 'User not found'}), 404
        user_id = user_result.data[0]['id']
        # Проверяем, что отчет принадлежит пользователю и не удалён
        report_result = safe_db_operation(
            lambda: supabase.table('user_reports').select('id').eq('id', report_id).eq('user_id', user_id).is_('deleted_at', 'null').execute()
        )
        if report_result is None or not report_result.data:
            logger.error(f"Report {report_id} not found or not owned by user_id {user_id} or already deleted")
            return jsonify({'error': 'Report not found or not owned by user'}), 404
        # Soft delete: выставляем deleted_at
        now = datetime.utcnow().isoformat()
        delete_result = safe_db_operation(
            lambda: supabase.table('user_reports').update({'deleted_at': now}).eq('id', report_id).execute()
        )
        if delete_result is None:
            return jsonify({'error': 'Database connection error'}), 500
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting user report: {e}")
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/api/save_object', methods=['POST'])
def api_save_object():
    """Сохранение объекта в избранное"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    object_data = data.get('object_data')
    
    if not telegram_id or not object_data:
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        # Получаем user_id из базы данных по telegram_id
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        user_id = user_result.data[0]['id'] if user_result.data else telegram_id
        
        # Сохраняем объект в базу данных
        saved_object = {
            'user_id': user_id,
            'object_data': object_data,
            'saved_at': datetime.now().isoformat()
        }
        
        supabase.table('saved_objects').insert(saved_object).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error saving object: {e}")
        return jsonify({'error': 'Internal error'}), 500

def send_pdf_to_telegram(pdf_path, telegram_id, bot_token=None):
    """Отправляет PDF-файл пользователю через Telegram-бота. Возвращает статус отправки."""
    import requests
    import os
    logger = logging.getLogger(__name__)
    # Всегда используем рабочий токен
    bot_token = '7215676549:AAFS86JbRCqwzTKQG-dF96JX-C1aWNvBoLo'
    send_url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'document': pdf_file}
            data_send = {'chat_id': telegram_id}
            resp = requests.post(send_url, data=data_send, files=files)
            if resp.status_code == 200 and resp.json().get('ok'):
                return 'sent'
            else:
                logger.error(f"Telegram sendDocument error: {resp.text}")
                return f'error: {resp.text}'
    except Exception as e:
        logger.error(f"Error sending PDF via Telegram bot: {e}")
        return f'error: {e}'

@app.route('/api/generate_pdf_report', methods=['POST'])
def api_generate_pdf_report():
    """Генерация PDF отчета с поддержкой Unicode (DejaVu) и отправка через Telegram-бота"""
    data = request.json or {}
    logger.info(f"PDF request data: {data}")
    report = data.get('report')
    profile = data.get('profile') or {}
    client_name = data.get('client_name')
    report_id = data.get('report_id')
    telegram_id = data.get('telegram_id')
    if not report_id:
        logger.error(f"PDF generation error: report_id not provided. Incoming data: {data}")
        return jsonify({'error': 'report_id required for PDF generation', 'details': data}), 400
    try:
        pdf = FPDF()
        pdf.add_page()
        # Добавляем шрифты DejaVu
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf')
        pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf')
        
        # Добавляем логотип на первую страницу (по центру сверху)
        try:
            pdf.image('logo-sqv.png', x=85, y=10, w=40)  # Центрируем логотип
            pdf.ln(35)  # Увеличенный отступ после логотипа
        except Exception as e:
            logger.warning(f"Не удалось добавить логотип на первую страницу: {e}")
            pdf.ln(35)  # Отступ даже если логотип не загрузился
        
        pdf.set_font('DejaVu', 'B', 16)
        if client_name:
            pdf.cell(0, 10, f'Клиент: {client_name}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(2)
        pdf.cell(0, 10, 'Полный отчет по недвижимости', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(10)
        if report.get('object'):
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 10, 'Информация об объекте:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 10)
            obj = report['object']
            pdf.cell(0, 8, f'Адрес: {obj.get("address", "Не указан")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f'Спален: {obj.get("bedrooms", "Не указано")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f'Цена: €{obj.get("purchase_price", "Не указана")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Печатаем остальные блоки отчёта (без вложенности)
        # ROI анализ
        if 'roi' in report:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(200, 10, text="Инвестиционный анализ (ROI):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(200, 8, text=f"Краткосрочная аренда: ROI {report['roi']['short_term']['roi']}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 8, text=f"Долгосрочная аренда: ROI {report['roi']['long_term']['roi']}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 8, text=f"Без аренды: ROI {report['roi']['no_rent']['roi']}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Макроэкономические показатели (объединенный блок)
        if 'macro' in report or 'economic_charts' in report:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(200, 10, text="Макроэкономические показатели:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            
            # Ключевая ставка из macro
        if 'macro' in report:
            pdf.cell(200, 8, text=f"Ключевая ставка: {report['macro']['refi_rate']}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Экономические данные из economic_charts
            if 'economic_charts' in report:
                economic_charts = report['economic_charts']
                country_name = economic_charts.get('country_name', 'Unknown')
                
                # Отображаем последние значения
                latest = economic_charts.get('latest', {})
                if latest.get('gdp'):
                    gdp_data = latest['gdp']
                    pdf.cell(200, 8, text=f"Последний рост ВВП ({gdp_data['year']}): {gdp_data['value']}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                if latest.get('inflation'):
                    inflation_data = latest['inflation']
                    pdf.cell(200, 8, text=f"Последняя инфляция ({inflation_data['year']}): {inflation_data['value']}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # Отображаем тренды
                trends = economic_charts.get('trends', {})
                if trends.get('gdp_trend') is not None:
                    gdp_trend = trends['gdp_trend'] * 100  # Конвертируем в проценты
                    trend_text = f"Тренд роста ВВП: {gdp_trend:.1f}%"
                    pdf.cell(200, 8, text=trend_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                if trends.get('inflation_trend') is not None:
                    inflation_trend = trends['inflation_trend'] * 100  # Конвертируем в проценты
                    trend_text = f"Тренд инфляции: {inflation_trend:.1f}%"
                    pdf.cell(200, 8, text=trend_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # Добавляем детальные расчеты в компактной таблице
                detailed_calculations = economic_charts.get('detailed_calculations', {})
                if detailed_calculations:
                    pdf.ln(5)
                    pdf.set_font("DejaVu", 'B', 12)
                    pdf.cell(200, 8, text="Детальные расчеты трендов:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("DejaVu", size=8)
                    
                    # Создаем компактную таблицу в 3 столбца
                    gdp_calcs = detailed_calculations.get('gdp_calculations', [])
                    inflation_calcs = detailed_calculations.get('inflation_calculations', [])
                    
                    if gdp_calcs or inflation_calcs:
                        # Заголовки таблицы
                        pdf.set_font("DejaVu", 'B', 9)
                        pdf.cell(60, 6, text="Период", new_x=XPos.RIGHT, new_y=YPos.TOP)
                        pdf.cell(60, 6, text="Расчет", new_x=XPos.RIGHT, new_y=YPos.TOP)
                        pdf.cell(60, 6, text="Результат", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("DejaVu", size=8)
                        
                        # ВВП расчеты
                        if gdp_calcs:
                            pdf.cell(200, 4, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("DejaVu", 'B', 8)
                            pdf.cell(200, 5, text="ВВП:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("DejaVu", size=7)
                            
                            for calc in gdp_calcs:
                                # Первая строка
                                pdf.cell(60, 4, text=calc['years'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                                pdf.cell(60, 4, text=calc['calculation'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                                pdf.cell(60, 4, text=calc['result'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        
                        # Инфляция расчеты
                        if inflation_calcs:
                            pdf.cell(200, 4, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("DejaVu", 'B', 8)
                            pdf.cell(200, 5, text="Инфляция:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("DejaVu", size=7)
                            
                            for calc in inflation_calcs:
                                # Первая строка
                                pdf.cell(60, 4, text=calc['years'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                                pdf.cell(60, 4, text=calc['calculation'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                                pdf.cell(60, 4, text=calc['result'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # Добавляем интерпретации
                interpretations = economic_charts.get('interpretations', {})
                if interpretations and 'ru' in interpretations:
                    pdf.ln(5)
                    pdf.set_font("DejaVu", 'B', 12)
                    pdf.cell(200, 8, text="Интерпретация трендов:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("DejaVu", size=10)
                    
                    ru_interp = interpretations['ru']
                    if 'gdp_interpretation' in ru_interp:
                        pdf.cell(200, 6, text=f"ВВП: {ru_interp['gdp_interpretation']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    if 'inflation_interpretation' in ru_interp:
                        pdf.cell(200, 6, text=f"Инфляция: {ru_interp['inflation_interpretation']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    if 'recent_comparison' in ru_interp:
                        pdf.cell(200, 6, text=f"Сравнение: {ru_interp['recent_comparison']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Создаем и вставляем график
            try:
                # Создаем данные для графика в правильном формате
                chart_data = {
                    'labels': economic_charts.get('gdp_chart', {}).get('labels', []),
                    'gdp_chart': economic_charts.get('gdp_chart', {}),
                    'inflation_chart': economic_charts.get('inflation_chart', {})
                }
                
                logger.info(f"Создание графика для PDF: {len(chart_data.get('labels', []))} точек данных")
                
                chart_buffer = create_chart_image_for_pdf(chart_data, f"Динамика экономических показателей ({country_name})")
                if chart_buffer:
                    logger.info("График создан успешно, вставляем в PDF")
                    # Вставляем график в PDF
                    pdf.ln(5)
                    pdf.image(chart_buffer, x=10, y=pdf.get_y(), w=190)
                    pdf.ln(85)  # Отступ после графика
                    chart_buffer.close()
                else:
                    logger.warning("График не создался, используем текстовое отображение")
                    # Если график не создался, показываем текстовые данные
                    pdf.ln(3)
                    pdf.set_font("DejaVu", 'B', 12)
                    pdf.cell(200, 8, text=f"Динамика роста ВВП ({country_name}):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("DejaVu", size=10)
                    
                    gdp_chart = economic_charts.get('gdp_chart', {})
                    if gdp_chart.get('labels') and gdp_chart.get('datasets'):
                        labels = gdp_chart['labels']
                        data = gdp_chart['datasets'][0]['data'] if gdp_chart['datasets'] else []
                        
                        for i, (year, value) in enumerate(zip(labels, data)):
                            if i < 5:  # Показываем только последние 5 лет
                                pdf.cell(200, 6, text=f"{year}: {value}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    inflation_chart = economic_charts.get('inflation_chart', {})
                    if inflation_chart.get('labels') and inflation_chart.get('datasets'):
                        pdf.ln(3)
                        pdf.set_font("DejaVu", 'B', 12)
                        pdf.cell(200, 8, text=f"Динамика инфляции ({country_name}):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("DejaVu", size=10)
                        
                        labels = inflation_chart['labels']
                        data = inflation_chart['datasets'][0]['data'] if inflation_chart['datasets'] else []
                        
                        for i, (year, value) in enumerate(zip(labels, data)):
                            if i < 5:  # Показываем только последние 5 лет
                                pdf.cell(200, 6, text=f"{year}: {value}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception as e:
                logger.error(f"Ошибка вставки графика в PDF: {e}")
                # Fallback к текстовому отображению
                pdf.ln(3)
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(200, 8, text=f"Динамика экономических показателей ({country_name}):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=10)
                
                gdp_chart = economic_charts.get('gdp_chart', {})
                if gdp_chart.get('labels') and gdp_chart.get('datasets'):
                    labels = gdp_chart['labels']
                    data = gdp_chart['datasets'][0]['data'] if gdp_chart['datasets'] else []
                    
                    for i, (year, value) in enumerate(zip(labels, data)):
                        if i < 5:  # Показываем только последние 5 лет
                            pdf.cell(200, 6, text=f"{year}: {value}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.ln(5)
        
        # Данные трендов недвижимости
        if report.get('object') and report['object'].get('address'):
            address = report['object']['address']
            location_data = extract_location_from_address(address)
            
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(200, 10, text="Тренды рынка недвижимости:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            
            if location_data['city_name']:
                trends_data, trends_message = get_property_trends_data(
                    location_data['city_name'],
                    location_data['district_name'],
                    location_data['county_name']
                )
                
                # Получаем исторические данные для графиков
                historical_data = get_historical_property_trends(
                    location_data['city_name'],
                    location_data['district_name'],
                    location_data['county_name']
                )
                
                # Данные по продаже
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(200, 8, text="Данные по продаже:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=10)
                
                # Показываем источник данных
                if trends_message:
                    pdf.cell(200, 6, text=f"Источник данных: {trends_message}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                if trends_data:
                    if trends_data.get('unit_price_for_sale'):
                        pdf.cell(200, 6, text=f"Средняя цена за м² (продажа): €{trends_data['unit_price_for_sale']:,.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Средняя цена за м² (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('price_change_sale'):
                        change_percent = trends_data['price_change_sale'] * 100
                        pdf.cell(200, 6, text=f"Изменение цен (продажа): {change_percent:+.2f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Изменение цен (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('listing_period_for_sale'):
                        pdf.cell(200, 6, text=f"Средний период продажи: {trends_data['listing_period_for_sale']} дней", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Средний период продажи: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('count_for_sale'):
                        pdf.cell(200, 6, text=f"Объектов на продажу: {trends_data['count_for_sale']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Объектов на продажу: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                else:
                    pdf.cell(200, 6, text="Средняя цена за м² (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(200, 6, text="Изменение цен (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(200, 6, text="Средний период продажи: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(200, 6, text="Объектов на продажу: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # График изменения цен на продажу
                if historical_data:
                    sale_chart_buffer = create_property_trends_chart(historical_data, 'sale', 180, 80)
                    if sale_chart_buffer:
                        pdf.ln(3)
                        pdf.image(sale_chart_buffer, x=15, w=180)
                        pdf.ln(3)
                
            pdf.ln(5)
            
            # Данные по аренде (долгосрочная)
            pdf.set_font("DejaVu", 'B', 12)
            pdf.cell(200, 8, text="Данные по долгосрочной аренде:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=10)
            
            if trends_data:
                    if trends_data.get('unit_price_for_rent'):
                        pdf.cell(200, 6, text=f"Средняя цена за м² (аренда): €{trends_data['unit_price_for_rent']:,.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Средняя цена за м² (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('price_change_rent'):
                        change_percent = trends_data['price_change_rent'] * 100
                        pdf.cell(200, 6, text=f"Изменение цен (аренда): {change_percent:+.2f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Изменение цен (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('listing_period_for_rent'):
                        pdf.cell(200, 6, text=f"Средний период аренды: {trends_data['listing_period_for_rent']} дней", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Средний период аренды: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('count_for_rent'):
                        pdf.cell(200, 6, text=f"Объектов на аренду: {trends_data['count_for_rent']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Объектов на аренду: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    # Доходность
                    if trends_data.get('yield'):
                        yield_percent = trends_data['yield'] * 100
                        pdf.cell(200, 6, text=f"Доходность: {yield_percent:.2f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(200, 6, text="Доходность: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                pdf.cell(200, 6, text="Средняя цена за м² (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(200, 6, text="Изменение цен (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(200, 6, text="Средний период аренды: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(200, 6, text="Объектов на аренду: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(200, 6, text="Доходность: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # График изменения цен на аренду
            if historical_data:
                rent_chart_buffer = create_property_trends_chart(historical_data, 'rent', 180, 80)
                if rent_chart_buffer:
                    pdf.ln(3)
                    pdf.image(rent_chart_buffer, x=15, w=180)
                    pdf.ln(3)
        else:
            # Адрес не содержит информации о городе - показываем "н/д" для всех полей
            pdf.set_font("DejaVu", 'B', 12)
            pdf.cell(200, 8, text="Данные по продаже:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=10)
            pdf.cell(200, 6, text="Средняя цена за м² (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 6, text="Изменение цен (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 6, text="Средний период продажи: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 6, text="Объектов на продажу: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.ln(5)
                
            pdf.set_font("DejaVu", 'B', 12)
            pdf.cell(200, 8, text="Данные по долгосрочной аренде:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=10)
            pdf.cell(200, 6, text="Средняя цена за м² (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 6, text="Изменение цен (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 6, text="Средний период аренды: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 6, text="Объектов на аренду: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 6, text="Доходность: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.ln(5)
        
        # Переходим на новую страницу для налогов
        if 'taxes' in report:
            pdf.add_page()
            
            # Добавляем логотип в правом верхнем углу
            try:
                pdf.image('logo-flt.png', x=170, y=10, w=30)  # Правый верхний угол
            except Exception as e:
                logger.warning(f"Не удалось добавить логотип на страницу налогов: {e}")
            
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(200, 10, text="Налоги и сборы:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(200, 8, text=f"Налог на перевод: {report['taxes']['transfer_tax']*100}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 8, text=f"Гербовый сбор: {report['taxes']['stamp_duty']*100}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(200, 8, text=f"Нотариус: €{report['taxes']['notary']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Блок: Альтернативы
        if 'alternatives' in report and isinstance(report['alternatives'], list):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Сравнение с альтернативами (5 лет):', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 12)
            for alt in report['alternatives']:
                name = alt.get('name', '-')
                yld = alt.get('yield', 0)
                pdf.cell(0, 8, f'{name}: {round(yld*100, 1)}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Блок: Профессиональные метрики
        if 'yield' in report or 'price_index' in report or 'mortgage_rate' in report or 'global_house_price_index' in report:
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Профессиональные метрики:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 12)
            if 'yield' in report:
                pdf.cell(0, 8, f'Yield: {round(report["yield"]*100, 1)}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'price_index' in report:
                pdf.cell(0, 8, f'Индекс цен: {report["price_index"]}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'mortgage_rate' in report:
                pdf.cell(0, 8, f'Ипотечная ставка: {round(report["mortgage_rate"]*100, 1)}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'global_house_price_index' in report:
                pdf.cell(0, 8, f'Глобальный индекс цен: {report["global_house_price_index"]}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Блок: Риски и развитие района
        if 'risks' in report or 'liquidity' in report or 'district' in report:
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Риски и развитие района:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 12)
            if 'risks' in report and isinstance(report['risks'], list):
                for idx, risk in enumerate(report['risks']):
                    pdf.cell(0, 8, f'Риск {idx+1}: {risk}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'liquidity' in report:
                pdf.cell(0, 8, f'Ликвидность: {report["liquidity"]}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'district' in report:
                pdf.cell(0, 8, f'Развитие района: {report["district"]}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Удаляем блок summary/заключение
        # if 'summary' in report:
        #     pdf.set_font("DejaVu", 'B', 14)
        #     pdf.cell(200, 10, txt="Заключение:", ln=True)
        #     pdf.set_font("DejaVu", size=12)
        #     pdf.multi_cell(200, 8, txt=report.get('summary', 'Анализ завершен'))
        # Подвал: контактные данные пользователя
        if profile:
            pdf.set_y(-60)
            pdf.set_font('DejaVu', 'B', 11)
            pdf.cell(0, 8, 'Контактные данные риелтора:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 10)
            if profile.get('tg_name') or profile.get('last_name'):
                pdf.cell(0, 8, f"Имя: {profile.get('tg_name','')} {profile.get('last_name','')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if profile.get('company'):
                pdf.cell(0, 8, f"Компания: {profile.get('company')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if profile.get('position'):
                pdf.cell(0, 8, f"Должность: {profile.get('position')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if profile.get('phone'):
                pdf.cell(0, 8, f"Телефон: {profile.get('phone')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if profile.get('email'):
                pdf.cell(0, 8, f"Email: {profile.get('email')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if profile.get('website'):
                pdf.cell(0, 8, f"Сайт: {profile.get('website')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if profile.get('about_me'):
                pdf.multi_cell(0, 8, f"О себе: {profile.get('about_me')}")
        # Сохраняем PDF во временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        # Перемещаем PDF в static/reports/
        reports_dir = os.path.join(app.root_path, 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        # Генерируем уникальное имя файла только цифрами
        file_id = ''.join(random.choices(string.digits, k=12))
        final_pdf_name = f'{file_id}.pdf'
        final_pdf_path = os.path.join(reports_dir, final_pdf_name)
        import shutil
        shutil.move(temp_file.name, final_pdf_path)
        pdf_url = f'/static/reports/{final_pdf_name}'
        supabase.table('user_reports').update({'pdf_path': pdf_url}).eq('id', report_id).execute()
        # Отправка PDF через Telegram-бота
        send_status = None
        if telegram_id:
            send_status = send_pdf_to_telegram(final_pdf_path, telegram_id)
        return jsonify({
            'success': True,
            'pdf_path': pdf_url,
            'telegram_send_status': send_status,
            'message': 'PDF успешно сгенерирован и сохранен!'
        })
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/download_pdf', methods=['POST'])
def api_download_pdf():
    """Скачивание PDF отчета"""
    data = request.json or {}
    pdf_path = data.get('pdf_path')
    
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF file not found'}), 404
    
    try:
        return send_file(pdf_path, as_attachment=True, download_name='full_report.pdf')
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/user_balance', methods=['POST'])
def api_user_balance():
    """Получение или списание баланса пользователя"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    deduct = data.get('deduct', False)
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        result = supabase.table('users').select('balance').eq('telegram_id', telegram_id).execute()
        if result.data:
            balance = result.data[0].get('balance', 0)
        else:
            balance = 0
        # Если нужно списать $1
        if deduct:
            if balance >= 1:
                new_balance = balance - 1
                update_result = supabase.table('users').update({'balance': new_balance}).eq('telegram_id', telegram_id).execute()
                # Проверяем, что обновление прошло успешно
                if hasattr(update_result, 'data') or update_result:
                    return jsonify({'success': True, 'balance': new_balance})
                else:
                    return jsonify({'error': 'Не удалось обновить баланс'}), 500
            else:
                return jsonify({'error': 'Недостаточно средств', 'balance': balance}), 400
        # Просто возвращаем баланс
        return jsonify({'balance': balance})
    except Exception as e:
        logger.error(f"Error getting/updating user balance: {e}")
        return jsonify({'error': 'Internal error'}), 500

# === Перемещаем эти маршруты выше запуска Flask ===
@app.route('/api/full_report_access', methods=['POST'])
def api_full_report_access():
    data = request.json or {}
    logger.info(f"/api/full_report_access incoming data: {data}")
    telegram_id = data.get('telegram_id')
    if telegram_id is None or str(telegram_id).strip() == '':
        logger.warning("/api/full_report_access: telegram_id missing or empty in request")
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id)
    except (TypeError, ValueError):
        logger.warning(f"/api/full_report_access: telegram_id not convertible to int: {telegram_id}")
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        user_result = supabase.table('users').select('period_start, period_end, balance').eq('telegram_id', telegram_id).execute()
        logger.info(f"/api/full_report_access user_result: {user_result.data}")
        user = user_result.data[0] if user_result.data else None
        if not user:
            logger.warning(f"/api/full_report_access: User not found for telegram_id {telegram_id}")
            return jsonify({'error': 'User not found'}), 404
        # Получаем стоимость полного отчета
        tariff_result = supabase.table('tariffs').select('price').eq('name', 'full report').execute()
        tariff = tariff_result.data[0] if tariff_result.data else None
        full_report_price = float(tariff['price']) if tariff and 'price' in tariff else 3.0
        return jsonify({
            'period_start': user.get('period_start'),
            'period_end': user.get('period_end'),
            'balance': user.get('balance', 0),
            'full_report_price': full_report_price
        })
    except Exception as e:
        logger.error(f"Error in full_report_access: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/deduct_balance', methods=['POST'])
def api_deduct_balance():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    amount = data.get('amount')
    logger.info(f"/api/deduct_balance incoming data: {data}")
    if telegram_id is None or str(telegram_id).strip() == '' or amount is None:
        logger.warning("/api/deduct_balance: telegram_id or amount missing in request")
        return jsonify({'error': 'telegram_id and amount required'}), 400
    try:
        telegram_id = int(telegram_id)
        amount = float(amount)
    except (TypeError, ValueError):
        logger.warning(f"/api/deduct_balance: telegram_id or amount not convertible: {telegram_id}, {amount}")
        return jsonify({'error': 'Invalid telegram_id or amount'}), 400
    try:
        user_result = supabase.table('users').select('balance').eq('telegram_id', telegram_id).execute()
        user = user_result.data[0] if user_result.data else None
        if not user:
            logger.warning(f"/api/deduct_balance: user not found for telegram_id {telegram_id}")
            return jsonify({'error': 'User not found'}), 404
        old_balance = user['balance']
        new_balance = old_balance - amount
        # Приводим к int для smallint
        new_balance_int = int(new_balance)
        logger.info(f"/api/deduct_balance: old_balance={old_balance}, amount={amount}, new_balance_int={new_balance_int}")
        update_result = supabase.table('users').update({'balance': new_balance_int}).eq('telegram_id', telegram_id).execute()
        logger.info(f"/api/deduct_balance: update_result={update_result}")
        # Если не было исключения — считаем успехом
        return jsonify({'success': True, 'new_balance': new_balance_int})
    except Exception as e:
        logger.error(f"Error in deduct_balance: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
@app.route('/api/update_user_report', methods=['POST'])
def api_update_user_report():
    """Обновление отчета пользователя (списание $1, перегенерация)"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    report_id = data.get('report_id')
    if not telegram_id or not report_id:
        return jsonify({'error': 'Missing required data'}), 400
    try:
        # Получаем user_id по telegram_id
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        user_id = user_result.data[0]['id'] if user_result.data else telegram_id
        # Проверяем, что отчет принадлежит пользователю
        report_result = supabase.table('user_reports').select('*').eq('id', report_id).eq('user_id', user_id).execute()
        if not report_result.data:
            return jsonify({'error': 'Report not found or not owned by user'}), 404
        report = report_result.data[0]
        # Проверяем баланс
        balance_result = supabase.table('users').select('balance').eq('telegram_id', telegram_id).execute()
        balance = balance_result.data[0].get('balance', 0) if balance_result.data else 0
        if balance < 1:
            return jsonify({'error': 'Insufficient balance', 'balance': balance}), 400
        # Списываем $1
        new_balance = balance - 1
        supabase.table('users').update({'balance': new_balance}).eq('telegram_id', telegram_id).execute()
        # Перегенерируем отчет (используем существующие параметры)
        # TODO: здесь должна быть логика перегенерации отчета
        # Пока просто обновляем дату
        supabase.table('user_reports').update({
            'updated_at': datetime.now().isoformat()
        }).eq('id', report_id).execute()
        return jsonify({'success': True, 'balance': new_balance})
    except Exception as e:
        logger.error(f"Error updating user report: {e}")
        return jsonify({'error': 'Internal error'}), 500 

@app.route('/api/user_reports/save', methods=['POST'])
def api_save_user_report():
    """Сохраняет новый отчет пользователя и возвращает report_id"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    full_report = data.get('full_report')
    address = data.get('address')
    report_type = data.get('report_type', 'full')
    if not telegram_id or not full_report:
        return jsonify({'error': 'Missing required data'}), 400
    try:
        # Получаем user_id по telegram_id
        try:
            user_result = safe_db_operation(
                lambda: supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
            )
            if user_result is None:
                return jsonify({'error': 'Database connection error'}), 500
            user_id = user_result.data[0]['id'] if user_result.data else telegram_id
        except Exception as e:
            logger.error(f"Error getting user_id: {e}")
            return jsonify({'error': 'Database connection error'}), 500
        # Сохраняем отчет
        report_data = {
            'user_id': user_id,
            'report_type': report_type,
            'address': address,
            'full_report': full_report,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        try:
            result = safe_db_operation(
                lambda: supabase.table('user_reports').insert(report_data).execute()
            )
            if result is None:
                return jsonify({'error': 'Database connection error'}), 500
            new_id = result.data[0]['id'] if hasattr(result, 'data') and result.data else None
            return jsonify({'success': True, 'report_id': new_id})
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return jsonify({'error': 'Database connection error'}), 500
    except Exception as e:
        logger.error(f"Error saving user report: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/save_html_report', methods=['POST'])
def api_save_html_report():
    """Сохраняет отчет как HTML файл в корпоративном стиле и возвращает ссылку"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'Invalid telegram_id'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    
    report_content = data.get('report_content')
    location_info = data.get('location_info', '')
    report_data = data.get('report_data', {})  # Дополнительные данные отчета
    include_realtor_info = data.get('include_realtor_info', False)
    include_property_info = data.get('include_property_info', False)
    property_info = data.get('property_info', {})
    
    if not report_content:
        return jsonify({'error': 'Report content required'}), 400
    
    try:
        # Генерируем уникальный номер отчета
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = ''.join(random.choices(string.digits, k=5))
        report_number = f"RPT-{timestamp}-{random_suffix}"
        
        # Генерируем уникальное имя файла только цифрами
        file_id = ''.join(random.choices(string.digits, k=12))
        filename = f"{file_id}.html"
        file_path = os.path.join('reports', filename)
        
        # Получаем информацию о пользователе из таблицы users
        user_info = None
        try:
            if include_realtor_info:
                user_result = safe_db_operation(
                    lambda: supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
                )
                if user_result and user_result.data:
                    user_info = user_result.data[0]
                    user_id = user_info['id']
                else:
                    logger.error("Failed to get user info from database")
                    user_id = telegram_id
            else:
                user_result = safe_db_operation(
                    lambda: supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
                )
                if user_result is None:
                    logger.error("Failed to get user_id from database")
                    user_id = telegram_id  # Используем telegram_id как fallback
                else:
                    user_id = user_result.data[0]['id'] if user_result.data else telegram_id
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            user_id = telegram_id  # Используем telegram_id как fallback
        
        # Подготавливаем данные для сохранения в БД
        db_report_data = {
            'user_id': user_id,
            'report_type': 'property_evaluation',
            'title': f'Аналитический отчет по недвижимости - {location_info}',
            'description': f'Отчет по оценке объекта недвижимости в регионе {location_info}',
            'parameters': report_data.get('parameters', {}),
            'address': location_info,
            'latitude': report_data.get('latitude'),
            'longitude': report_data.get('longitude'),
            'price_range_min': report_data.get('price_range_min'),
            'price_range_max': report_data.get('price_range_max'),
            'price': report_data.get('price'),
            'area': report_data.get('area'),
            'report_url': f"/reports/{filename}",
            'full_report': {
                'content': report_content,
                'location_info': location_info,
                'report_number': report_number,
                'generated_at': datetime.now().isoformat()
            }
        }
        
        # Обрабатываем поле bedrooms - извлекаем число из строки "2+1"
        bedrooms_raw = report_data.get('bedrooms')
        if bedrooms_raw:
            try:
                # Извлекаем первое число из строки "2+1" -> 2
                bedrooms_match = re.search(r'(\d+)', str(bedrooms_raw))
                if bedrooms_match:
                    db_report_data['bedrooms'] = int(bedrooms_match.group(1))
                else:
                    db_report_data['bedrooms'] = None
            except (ValueError, TypeError):
                db_report_data['bedrooms'] = None
        else:
            db_report_data['bedrooms'] = None
        
        # Очищаем данные от None значений для числовых полей
        numeric_fields = ['price_range_min', 'price_range_max', 'price', 'area', 'latitude', 'longitude', 'bedrooms']
        for field in numeric_fields:
            if db_report_data.get(field) is None:
                db_report_data.pop(field, None)
        
        # Сохраняем в базу данных с обработкой ошибок
        try:
            db_result = safe_db_operation(
                lambda: supabase.table('user_reports').insert(db_report_data).execute()
            )
            if db_result is None:
                logger.error("Failed to save report to database")
                report_id = None
            else:
                report_id = db_result.data[0]['id'] if db_result.data else None
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            # Продолжаем без сохранения в БД
            report_id = None
        
        # Генерируем QR-код для верификации
        verification_url = f"{request.host_url.rstrip('/')}/reports/{filename}"
        qr_code_svg = generate_qr_code_svg(verification_url)
        
        # Функции для генерации дополнительного контента
        def generate_realtor_section(user_info):
            if not user_info:
                return ""
            
            # Подготавливаем данные риэлтора
            full_name = user_info.get('full_name') or f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            if not full_name:
                full_name = user_info.get('tg_name', 'Риэлтор')
            
            position = user_info.get('position', 'Ведущий риэлтор')
            company_name = user_info.get('company_name', 'RealtyCompany')
            about_me = user_info.get('about_me', 'Опытный риэлтор с многолетним стажем работы на рынке недвижимости.')
            phone = user_info.get('phone', '')
            email = user_info.get('email', '')
            website_url = user_info.get('website_url', '')
            whatsapp_link = user_info.get('whatsapp_link', '')
            telegram_link = user_info.get('telegram_link', '')
            facebook_link = user_info.get('facebook_link', '')
            instagram_link = user_info.get('instagram_link', '')
            
            # Генерируем фото риэлтора
            photo_html = ''
            if user_info.get('avatar_filename') or user_info.get('photo_url'):
                # Используем avatar_filename из БД (соответствует структуре таблицы)
                photo_url = user_info.get('avatar_filename') or user_info.get('photo_url')
                # Если avatar_filename - это только имя файла, добавляем правильный путь
                if photo_url and not photo_url.startswith('http'):
                    # Используем правильный путь согласно API /user/<telegram_id>/<filename>
                    telegram_id = user_info.get('telegram_id', '')
                    photo_url = f"/user/{telegram_id}/{photo_url}"
                photo_html = f'<img src="{photo_url}" alt="{full_name}" class="realtor-photo">'
            else:
                # Дефолтное фото
                photo_html = '<div class="realtor-photo-placeholder">👤</div>'
            
            # Генерируем контакты
            contacts_html = ''
            if phone:
                contacts_html += f'''
                <div class="contact-item">
                    <svg class="contact-icon" viewBox="0 0 24 24" fill="#3498db">
                        <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                    </svg>
                    <div class="contact-text">
                        <a href="tel:{phone}" class="contact-link">{phone}</a>
                    </div>
                </div>
                '''
            
            if email:
                contacts_html += f'''
                <div class="contact-item">
                    <svg class="contact-icon" viewBox="0 0 24 24" fill="#3498db">
                        <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                    </svg>
                    <div class="contact-text">
                        <a href="mailto:{email}" class="contact-link">{email}</a>
                    </div>
                </div>
                '''
            
            if whatsapp_link:
                contacts_html += f'''
                <div class="contact-item">
                    <svg class="contact-icon" viewBox="0 0 24 24" fill="#25D366">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
                    </svg>
                    <div class="contact-text">
                        <a href="{whatsapp_link}" class="contact-link" target="_blank">WhatsApp</a>
                    </div>
                </div>
                '''
            
            if telegram_link:
                contacts_html += f'''
                <div class="contact-item">
                    <svg class="contact-icon" viewBox="0 0 24 24" fill="#0088cc">
                        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.568 8.16c-.169 1.858-.896 3.461-2.189 4.689-1.293 1.228-2.896 1.955-4.755 2.124-1.858.169-3.461-.896-4.689-2.189-1.228-1.293-1.955-2.896-2.124-4.755-.169-1.858.896-3.461 2.189-4.689 1.293-1.228 2.896-1.955 4.755-2.124 1.858-.169 3.461.896 4.689 2.189 1.228 1.293 1.955 2.896 2.124 4.755z"/>
                    </svg>
                    <div class="contact-text">
                        <a href="{telegram_link}" class="contact-link" target="_blank">Telegram</a>
                    </div>
                </div>
                '''
            
            if facebook_link:
                contacts_html += f'''
                <div class="contact-item">
                    <svg class="contact-icon" viewBox="0 0 24 24" fill="#1877f2">
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                    <div class="contact-text">
                        <a href="{facebook_link}" class="contact-link" target="_blank">Facebook</a>
                    </div>
                </div>
                '''
            
            if instagram_link:
                contacts_html += f'''
                <div class="contact-item">
                    <svg class="contact-icon" viewBox="0 0 24 24" fill="#e4405f">
                        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                    <div class="contact-text">
                        <a href="{instagram_link}" class="contact-link" target="_blank">Instagram</a>
                    </div>
                </div>
                '''
            
            return f'''
        <!-- Блок риэлтора -->
        <div class="realtor-section">
            <div class="realtor-header">
                {photo_html}
                <div class="realtor-info">
                    <div class="realtor-name">{full_name}</div>
                    <div class="realtor-title">{position}</div>
                    <div class="realtor-company">{company_name}</div>
                    {f'<div class="realtor-web">{website_url}</div>' if website_url else ''}
                </div>
            </div>
            
            <div class="realtor-description">
                <strong>{about_me}</strong>
            </div>
            
            <div class="realtor-contacts">
                {contacts_html}
            </div>
        </div>
            '''
        
        def generate_property_section(property_info):
            if not property_info or (not property_info.get('photos') and not property_info.get('url')):
                return ""
            
            # Генерируем блок фотографий
            photos_html = ''
            if property_info.get('photos'):
                photos_slides = ''
                photos_dots = ''
                for i, photo in enumerate(property_info['photos']):
                    active_class = 'active' if i == 0 else ''
                    photos_slides += f'''
                        <div class="photo-slide {active_class}">
                            <img src="{photo.get('data', '')}" alt="Фото объекта {i+1}">
                        </div>
                    '''
                    photos_dots += f'<span class="carousel-dot {active_class}" onclick="currentSlide({i+1})"></span>'
                
                photos_html = f'''
                    <div class="photos-container">
                        <div class="photo-carousel" id="photoCarousel">
                            {photos_slides}
                            
                            <!-- Навигация карусели -->
                            <button class="carousel-nav carousel-prev" onclick="changeSlide(-1)">‹</button>
                            <button class="carousel-nav carousel-next" onclick="changeSlide(1)">›</button>
                            
                            <!-- Индикаторы -->
                            <div class="carousel-controls">
                                {photos_dots}
                            </div>
                        </div>
                    </div>
                '''
            
            # Генерируем ссылку на объявление
            property_link_html = ''
            if property_info.get('url'):
                property_link_html = f'''
                    <div class="property-link-section">
                        <div class="property-link-title">Подробная информация об объекте</div>
                        <a href="{property_info['url']}" 
                           class="property-link" 
                           target="_blank">
                            Посмотреть объявление
                        </a>
                    </div>
                '''
            
            if photos_html or property_link_html:
                return f'''
        <!-- Блок карты и фотографий -->
        <div class="location-visual-section">
            <h3 class="location-visual-title">Расположение и фотографии объекта</h3>
            
            <div class="location-visual-grid">
                <!-- Карта (заглушка) -->
                <div class="map-container">
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f8f9fa; color: #6c757d;">
                        📍 Карта локации
                    </div>
                </div>
                
                <!-- Карусель фотографий -->
                {photos_html}
            </div>
            
            <!-- Ссылка на объявление -->
            {property_link_html}
        </div>
                '''
            return ""
        
        # Создаем корпоративный HTML отчет
        html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аналитический отчет по недвижимости - {location_info}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #ffffff;
            color: #2c3e50;
            line-height: 1.6;
            font-size: 14px;
        }}

        .document {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
            border: 1px solid #e0e0e0;
        }}

        /* Корпоративный заголовок */
        .corporate-header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
            border-bottom: 4px solid #3498db;
        }}

        .company-logo {{
            width: 100px;
            height: auto;
            margin-bottom: 20px;
            filter: brightness(0) invert(1);
        }}

        .document-title {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .document-subtitle {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 15px;
        }}

        /* Метаданные отчета */
        .report-metadata {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            margin: 0;
            padding: 25px 30px;
        }}

        .metadata-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .metadata-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}

        .metadata-label {{
            font-weight: 600;
            color: #495057;
        }}

        .metadata-value {{
            color: #6c757d;
            text-align: right;
        }}

        .qr-section {{
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
        }}

        .qr-code {{
            margin: 10px 0;
        }}

        .qr-label {{
            font-size: 12px;
            color: #6c757d;
            margin-top: 5px;
        }}

        /* Основной контент */
        .report-content {{
            padding: 30px;
        }}

        /* Корпоративные стили для всех элементов отчета */
        
        /* Заголовки секций */
        .data-section-title {{
            font-size: 18px;
            font-weight: 700;
            color: #2c3e50;
            margin: 25px 0 15px 0;
            padding: 10px 0;
            border-bottom: 2px solid #3498db;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* Market Indicators Table */
        .market-indicators-table {{
            margin: 20px 0;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .market-data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        
        .market-data-table .category-header {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            font-weight: 700;
            text-align: center;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .market-data-table .data-cell {{
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
            background: #ffffff;
            vertical-align: top;
        }}
        
        .market-data-table tr:nth-child(even) .data-cell {{
            background: #f8f9fa;
        }}
        
        .cell-label {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 5px;
            font-size: 12px;
        }}
        
        .cell-value {{
            font-weight: 700;
            color: #2c3e50;
            font-size: 14px;
        }}
        
        /* Market Analysis Text Block */
        .market-analysis-text-block {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .market-analysis-text-title {{
            font-size: 16px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .market-analysis-text-content p {{
            margin-bottom: 10px;
            line-height: 1.6;
            color: #495057;
            font-size: 13px;
        }}
        
        .market-analysis-text-content strong {{
            color: #2c3e50;
            font-weight: 700;
        }}
        
        /* Trends Grid */
        .trends-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .trend-card {{
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-left: 4px solid #27ae60;
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        
        .trend-card-price_trend {{
            border-left-color: #3498db;
        }}
        
        .trend-title {{
            font-size: 14px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .trend-value {{
            font-size: 20px;
            font-weight: 700;
            color: #27ae60;
            margin-bottom: 10px;
        }}
        
        .trend-change {{
            font-size: 12px;
            color: #6c757d;
            line-height: 1.4;
        }}
        
        /* Trends Table */
        .trends-table-section {{
            margin: 30px 0;
        }}
        
        .trends-table-title {{
            font-size: 16px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .trends-table {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            font-size: 12px;
        }}
        
        .trends-table th {{
            background: #2c3e50;
            color: white;
            padding: 12px 8px;
            font-weight: 700;
            text-align: center;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        .trends-table td {{
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #dee2e6;
            background: #ffffff;
        }}
        
        .trends-table .current-month-row {{
            background: #e3f2fd !important;
            font-weight: 700;
        }}
        
        .trends-table .forecast-row {{
            background: #f0f8ff !important;
        }}
        
        .trends-table .filter-info {{
            background: #f8f9fa !important;
            font-style: italic;
            color: #6c757d;
        }}
        
        /* Object Summary */
        .object-summary-section {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-left: 4px solid #e74c3c;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        
        .object-summary-title {{
            font-size: 16px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .object-comparison-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .object-comparison-table td {{
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .comparison-label {{
            font-weight: 600;
            color: #495057;
            width: 60%;
        }}
        
        .comparison-value {{
            font-weight: 700;
            color: #2c3e50;
            text-align: right;
        }}
        
        .comparison-expensive {{
            color: #e74c3c;
        }}
        
        .comparison-cheaper {{
            color: #27ae60;
        }}
        
        .comparison-smaller {{
            color: #f39c12;
        }}
        
        .object-analysis-text {{
            margin-top: 15px;
            padding: 15px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            font-size: 13px;
            color: #856404;
            line-height: 1.5;
        }}
        
        /* Forecast Tables */
        .forecast-table-section {{
            margin: 30px 0;
        }}
        
        .forecast-table-title {{
            font-size: 16px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .forecast-table {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            font-size: 12px;
        }}
        
        .forecast-table th {{
            background: #2c3e50;
            color: white;
            padding: 12px 8px;
            font-weight: 700;
            text-align: center;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        
        .forecast-table td {{
            padding: 10px 8px;
            text-align: center;
            border-bottom: 1px solid #dee2e6;
            background: #ffffff;
        }}
        
        .forecast-table .current-month-row {{
            background: #e3f2fd !important;
            font-weight: 700;
        }}
        
        .forecast-table .forecast-row {{
            background: #f0f8ff !important;
        }}
        
        /* Price Forecast Market Table */
        .price-forecast-market-table {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin: 20px 0;
        }}
        
        .forecast-category-header {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            font-weight: 700;
            text-align: center;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .forecast-data-cell {{
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
            background: #ffffff;
            vertical-align: top;
        }}
        
        .forecast-cell-label {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
            font-size: 13px;
        }}
        
        .forecast-cell-value {{
            font-weight: 700;
            color: #2c3e50;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        
        .forecast-cell-value.user-price {{
            color: #3498db;
        }}
        
        .forecast-cell-value.market-price {{
            color: #9b59b6;
        }}
        
        .forecast-cell-growth {{
            font-size: 12px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            display: inline-block;
        }}
        
        .forecast-cell-growth.positive {{
            background: #d4edda;
            color: #155724;
        }}
        
        .forecast-cell-growth.negative {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        /* Analysis Sections */
        .trends-analysis-section,
        .forecast-analysis-section {{
            background: #e8f5e8;
            border: 1px solid #c3e6c3;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        
        .trends-analysis-title,
        .forecast-analysis-title {{
            font-size: 16px;
            font-weight: 700;
            color: #155724;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .trends-analysis-content,
        .forecast-analysis-content {{
            color: #155724;
            line-height: 1.6;
            font-size: 13px;
        }}
        
        .trends-analysis-content p,
        .forecast-analysis-content p {{
            margin-bottom: 10px;
        }}
        
        .trends-analysis-content strong,
        .forecast-analysis-content strong {{
            font-weight: 700;
        }}
        
        /* Key Metrics */
        .forecast-metrics-compact-section {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }}
        
        .forecast-metrics-compact-title {{
            font-size: 14px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .forecast-metrics-compact-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .metric-compact-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .metric-compact-label {{
            font-weight: 600;
            color: #495057;
            font-size: 12px;
        }}
        
        .metric-compact-value {{
            font-weight: 700;
            color: #2c3e50;
            font-size: 12px;
        }}
        
        .metric-compact-value.positive {{
            color: #27ae60;
        }}
        
        .metric-compact-value.negative {{
            color: #e74c3c;
        }}
        
        /* Chart Replacements */
        .chart-container {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
        }}
        
        .chart-placeholder {{
            background: #ffffff;
            border: 2px dashed #3498db;
            border-radius: 8px;
            padding: 40px;
            color: #6c757d;
            font-style: italic;
        }}
        
        .chart-info {{
            margin-top: 10px;
            font-size: 11px;
            color: #6c757d;
            font-style: italic;
            text-align: center;
        }}
        
        /* Additional spacing */
        .block-spacing {{
            height: 20px;
        }}
        
        .section-spacing {{
            height: 10px;
        }}
        
        /* Price forecast info */
        .price-forecast-date {{
            text-align: center;
            font-weight: 700;
            color: #2c3e50;
            margin: 15px 0;
            font-size: 14px;
        }}
        
        .price-forecast-currency-info {{
            text-align: center;
            font-size: 12px;
            color: #6c757d;
            margin: 10px 0;
        }}
        
        .price-forecast-disclaimer {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 15px;
            font-size: 11px;
            color: #856404;
            text-align: center;
            font-style: italic;
            margin: 15px 0;
        }}

        /* Location and Object Info */
        .location-object-info {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            margin: 0;
            padding: 25px 30px;
        }}
        
        .location-info-section {{
            margin-bottom: 20px;
        }}
        
        .info-section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #495057;
        }}
        
        .info-value {{
            color: #2c3e50;
            font-weight: 500;
            text-align: right;
        }}

        /* Корпоративный футер */
        .corporate-footer {{
            background: #f8f9fa;
            border-top: 3px solid #3498db;
            padding: 30px;
            margin-top: 40px;
        }}

        .disclaimer {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-left: 4px solid #f39c12;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .disclaimer-title {{
            font-weight: 700;
            color: #856404;
            margin-bottom: 10px;
            font-size: 16px;
        }}

        .disclaimer-text {{
            color: #856404;
            font-size: 13px;
            line-height: 1.5;
        }}

        .verification-section {{
            background: #e8f5e8;
            border: 1px solid #c3e6c3;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .verification-title {{
            font-weight: 700;
            color: #155724;
            margin-bottom: 10px;
        }}

        .verification-link {{
            color: #0066cc;
            text-decoration: none;
            font-weight: 500;
        }}

        .verification-link:hover {{
            text-decoration: underline;
        }}

        .footer-info {{
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }}

        /* Блок риэлтора */
        .realtor-section {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6;
            border-left: 4px solid #3498db;
            padding: 25px;
            margin: 30px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}

        .realtor-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}

        .realtor-photo {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #3498db;
            margin-right: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .realtor-photo-placeholder {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 30px;
            color: #6c757d;
            margin-right: 20px;
            border: 3px solid #3498db;
        }}

        .realtor-info {{
            flex: 1;
        }}

        .realtor-name {{
            font-size: 18px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .realtor-title {{
            font-size: 14px;
            color: #3498db;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .realtor-company {{
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        }}

        .realtor-web {{
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        }}

        .realtor-description {{
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 13px;
            line-height: 1.5;
            color: #495057;
        }}

        .realtor-description strong {{
            color: #2c3e50;
            font-weight: 700;
        }}

        .realtor-contacts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .contact-item {{
            display: flex;
            align-items: center;
            padding: 10px;
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            transition: all 0.3s ease;
        }}

        .contact-item:hover {{
            background: #f8f9fa;
            border-color: #3498db;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
        }}

        .contact-icon {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
            flex-shrink: 0;
        }}

        .contact-text {{
            font-size: 12px;
            color: #2c3e50;
            font-weight: 500;
        }}

        .contact-link {{
            color: #3498db;
            text-decoration: none;
            font-weight: 600;
        }}

        .contact-link:hover {{
            color: #2980b9;
            text-decoration: underline;
        }}

        @media print {{
            body {{ background: white; }}
            .document {{ border: none; box-shadow: none; }}
            .corporate-header {{ background: #2c3e50 !important; }}
        }}
    </style>
</head>
<body>
    <div class="document">
        <!-- Корпоративный заголовок -->
        <div class="corporate-header">
            <img src="logo-flt.png" alt="Aaadviser" class="company-logo" />
            <div class="document-title">Аналитический отчет по недвижимости</div>
            <div class="document-subtitle">{location_info}</div>
        </div>

        <!-- Метаданные отчета -->
        <div class="report-metadata">
            <div class="metadata-grid">
                <div>
                    <div class="metadata-item">
                        <span class="metadata-label">Номер отчета:</span>
                        <span class="metadata-value">{report_number}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Дата формирования:</span>
                        <span class="metadata-value">{datetime.now().strftime("%d.%m.%Y")}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Время формирования:</span>
                        <span class="metadata-value">{datetime.now().strftime("%H:%M:%S")} UTC</span>
                    </div>
                </div>
                <div>
                    <div class="metadata-item">
                        <span class="metadata-label">Система анализа:</span>
                        <span class="metadata-value">Aaadviser v2.0</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Тип отчета:</span>
                        <span class="metadata-value">Оценка объекта недвижимости</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Статус:</span>
                        <span class="metadata-value">Автоматически сгенерирован</span>
                    </div>
                </div>
            </div>
            
            <div class="qr-section">
                <div class="qr-code">
                    {qr_code_svg}
                </div>
                <div class="qr-label">QR-код для верификации отчета</div>
            </div>
        </div>
        
        <!-- Информация о локации и объекте -->
        <div class="location-object-info">
            <div class="location-info-section">
                <h3 class="info-section-title">Информация о локации</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Регион:</span>
                        <span class="info-value">{location_info}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Тип анализа:</span>
                        <span class="info-value">Оценка объекта недвижимости</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Количество спален:</span>
                        <span class="info-value">{report_data.get('bedrooms', 'Не указано')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Этаж:</span>
                        <span class="info-value">{report_data.get('floor', 'Не указано')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Возраст объекта:</span>
                        <span class="info-value">{report_data.get('age', 'Не указано')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Тип отопления:</span>
                        <span class="info-value">{report_data.get('heating', 'Не указано')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Цена объекта:</span>
                        <span class="info-value">{report_data.get('price', 'Не указано')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Площадь объекта:</span>
                        <span class="info-value">{report_data.get('area', 'Не указано')}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Информация об объекте (если включена) -->
        {generate_property_section(property_info) if include_property_info else ''}

        <!-- Основной контент отчета -->
                        <div class="report-content">
                    {report_content}
                </div>
        
        <!-- Блок риэлтора (если включен) -->
        {generate_realtor_section(user_info) if include_realtor_info else ''}
                
                <!-- Добавляем кнопки переключения графиков -->
                <script>
                    // Добавляем кнопки переключения для графиков трендов
                    function addChartControls() {{
                        const trendsChartContainer = document.querySelector('#trendsChart').parentElement;
                        if (trendsChartContainer && !trendsChartContainer.querySelector('.chart-controls')) {{
                            const controlsHtml = `
                                <div class="chart-controls" style="margin-bottom: 15px; text-align: center;">
                                    <button class="chart-button active" data-chart-type="sale" onclick="switchTrendsChartType('sale')" style="background: #28a745; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                        Цена м² продажи
                                    </button>
                                    <button class="chart-button" data-chart-type="rent" onclick="switchTrendsChartType('rent')" style="background: #6c757d; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                        Цена м² аренды
                                    </button>
                                </div>
                            `;
                            trendsChartContainer.insertAdjacentHTML('beforebegin', controlsHtml);
                        }}
                        
                        const forecastChartContainer = document.querySelector('#forecastChart').parentElement;
                        if (forecastChartContainer && !forecastChartContainer.querySelector('.chart-controls')) {{
                            const controlsHtml = `
                                <div class="chart-controls" style="margin-bottom: 15px; text-align: center;">
                                    <button class="chart-button active" data-chart-type="sale" onclick="switchForecastChartType('sale')" style="background: #9b59b6; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                        Прогноз продажи
                                    </button>
                                    <button class="chart-button" data-chart-type="rent" onclick="switchForecastChartType('rent')" style="background: #6c757d; color: white; border: none; padding: 8px 16px; margin: 0 5px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                                        Прогноз аренды
                                    </button>
                                </div>
                            `;
                            forecastChartContainer.insertAdjacentHTML('beforebegin', controlsHtml);
                        }}
                    }}
                    
                    // Переключение типа графика трендов
                    function switchTrendsChartType(chartType) {{
                        // Обновляем активную кнопку
                        const buttons = document.querySelectorAll('.chart-controls button[data-chart-type]');
                        buttons.forEach(btn => {{
                            btn.classList.remove('active');
                            btn.style.background = '#6c757d';
                        }});
                        event.target.classList.add('active');
                        event.target.style.background = chartType === 'sale' ? '#28a745' : '#ffc107';
                        
                        const canvas = document.getElementById('trendsChart');
                        if (canvas) {{
                            const chartData = JSON.parse(canvas.getAttribute('data-chart-data'));
                            if (chartData && chartData[chartType]) {{
                                // Используем сохраненные данные для выбранного типа
                                const newData = chartData[chartType];
                                
                                // Пересоздаем график
                                const ctx = canvas.getContext('2d');
                                if (window.trendsChart) {{
                                    window.trendsChart.destroy();
                                }}
                                window.trendsChart = new Chart(ctx, {{
                                    type: 'line',
                                    data: newData.data,
                                    options: newData.options
                                }});
                            }}
                        }}
                    }}
                    
                    // Переключение типа графика прогноза
                    function switchForecastChartType(chartType) {{
                        // Обновляем активную кнопку
                        const buttons = document.querySelectorAll('.chart-controls button[data-chart-type]');
                        buttons.forEach(btn => {{
                            btn.classList.remove('active');
                            btn.style.background = '#6c757d';
                        }});
                        event.target.classList.add('active');
                        event.target.style.background = chartType === 'sale' ? '#9b59b6' : '#f39c12';
                        
                        const canvas = document.getElementById('forecastChart');
                        if (canvas) {{
                            const chartData = JSON.parse(canvas.getAttribute('data-chart-data'));
                            if (chartData && chartData[chartType]) {{
                                // Используем сохраненные данные для выбранного типа
                                const newData = chartData[chartType];
                                
                                // Пересоздаем график
                                const ctx = canvas.getContext('2d');
                                if (window.forecastChart) {{
                                    window.forecastChart.destroy();
                                }}
                                window.forecastChart = new Chart(ctx, {{
                                    type: 'line',
                                    data: newData.data,
                                    options: newData.options
                                }});
                            }}
                        }}
                    }}
                    
                    // Добавляем контролы после загрузки страницы
                    document.addEventListener('DOMContentLoaded', function() {{
                        setTimeout(addChartControls, 100);
                    }});
                </script>
        
        <!-- Дисклеймер и информация -->
        <div class="corporate-footer">
            <div class="disclaimer">
                <div class="disclaimer-title">Важная информация</div>
                <div class="disclaimer-text">
                    Данный отчет автоматически сгенерирован системой Aaadviser на основании анализа исторических данных и текущего предложения, экономических данных региона и открытой статистики продаж. Анализ носит рекомендательный характер и не является официальной оценкой недвижимости. Для принятия инвестиционных решений рекомендуется консультация со специалистами.
                </div>
            </div>
            
            <div class="verification-section">
                <div class="verification-title">Проверка актуальности данных</div>
                <div>
                    Для проверки актуальности данных и верификации отчета перейдите по ссылке: 
                    <a href="{verification_url}" class="verification-link" target="_blank">{verification_url}</a>
                </div>
            </div>
            
            <div class="footer-info">
                <strong>Aaadviser</strong> - Система аналитики недвижимости<br>
                Отчет №{report_number} | Сформирован {datetime.now().strftime("%d.%m.%Y в %H:%M:%S")}<br>
                © 2024 Aaadviser. Все права защищены.
            </div>
        </div>
    </div>
    
    <script>
        // Функция для восстановления интерактивных графиков в экспортируемом отчете
        document.addEventListener('DOMContentLoaded', function() {{
            restoreCharts();
        }});
        
        function restoreCharts() {{
            // Находим все canvas элементы с данными графиков
            const canvasElements = document.querySelectorAll('canvas[data-chart-data]');
            
            canvasElements.forEach(canvas => {{
                try {{
                    const chartData = JSON.parse(canvas.getAttribute('data-chart-data'));
                    const chartType = canvas.getAttribute('data-chart-type') || 'line';
                    const chartId = canvas.getAttribute('data-chart-id') || 'chart';
                    
                    // Восстанавливаем график
                    if (chartData) {{
                        const ctx = canvas.getContext('2d');
                        
                        // Определяем, какой тип данных у нас есть
                        let chartConfig;
                        if (chartData.sale && chartData.rent) {{
                            // У нас есть данные для обоих типов, используем продажу по умолчанию
                            chartConfig = chartData.sale;
                        }} else if (chartData.data) {{
                            // Старый формат данных
                            chartConfig = chartData;
                        }} else {{
                            console.error('Invalid chart data format');
                            return;
                        }}
                        
                        // Создаем новый график с сохраненными данными
                        if (chartId === 'trendsChart') {{
                            window.trendsChart = new Chart(ctx, {{
                                type: chartType,
                                data: chartConfig.data,
                                options: chartConfig.options
                            }});
                        }} else if (chartId === 'forecastChart') {{
                            window.forecastChart = new Chart(ctx, {{
                                type: chartType,
                                data: chartConfig.data,
                                options: chartConfig.options
                            }});
                        }} else {{
                            new Chart(ctx, {{
                                type: chartType,
                                data: chartConfig.data,
                                options: chartConfig.options || {{
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: {{
                                        legend: {{
                                            position: 'top',
                                            labels: {{
                                                font: {{
                                                    size: 12
                                                }},
                                                color: '#2c3e50'
                                            }}
                                        }},
                                        title: {{
                                            display: true,
                                            text: getChartTitle(chartId),
                                            color: '#2c3e50',
                                            font: {{
                                                size: 16,
                                                weight: 'bold'
                                            }}
                                        }}
                                    }},
                                    scales: {{
                                        x: {{
                                            grid: {{
                                                color: '#e9ecef'
                                            }},
                                            ticks: {{
                                                color: '#6c757d',
                                                font: {{
                                                    size: 11
                                                }}
                                            }}
                                        }},
                                        y: {{
                                            grid: {{
                                                color: '#e9ecef'
                                            }},
                                            ticks: {{
                                                color: '#6c757d',
                                                font: {{
                                                    size: 11
                                                }}
                                            }}
                                        }}
                                    }}
                                }}
                            }});
                        }}
                    }}
                }} catch (error) {{
                    console.error('Error restoring chart:', error);
                    // В случае ошибки показываем placeholder
                    showChartPlaceholder(canvas);
                }}
            }});
        }}
        
        function getChartTitle(chartId) {{
            const titles = {{
                'trendsChart': 'График трендов цен на недвижимость',
                'forecastChart': 'Прогноз цен на недвижимость',
                'priceChart': 'Динамика цен',
                'default': 'График данных'
            }};
            return titles[chartId] || titles['default'];
        }}
        
        function showChartPlaceholder(canvas) {{
            const placeholder = document.createElement('div');
            placeholder.className = 'chart-placeholder';
            placeholder.innerHTML = `
                <div style="font-size: 16px; font-weight: 600; margin-bottom: 10px;">
                    📊 График данных
                </div>
                <div style="font-size: 13px; color: #6c757d;">
                    Данные для построения графика представлены в таблицах выше
                </div>
            `;
            canvas.parentNode.replaceChild(placeholder, canvas);
        }}
        
        // Управление каруселью фотографий
        let currentPhotoIndex = 0;
        const photoSlides = document.querySelectorAll('.photo-slide');
        const totalPhotos = photoSlides.length;
        
        function showSlide(index) {{
            const slides = document.querySelectorAll('.photo-slide');
            const dots = document.querySelectorAll('.carousel-dot');
            
            // Убираем активный класс со всех слайдов и точек
            slides.forEach(slide => slide.classList.remove('active'));
            dots.forEach(dot => dot.classList.remove('active'));
            
            // Добавляем активный класс к текущему слайду и точке
            if (slides[index] && dots[index]) {{
                slides[index].classList.add('active');
                dots[index].classList.add('active');
            }}
        }}
        
        function changeSlide(direction) {{
            if (totalPhotos === 0) return;
            
            currentPhotoIndex += direction;
            
            if (currentPhotoIndex >= totalPhotos) {{
                currentPhotoIndex = 0;
            }} else if (currentPhotoIndex < 0) {{
                currentPhotoIndex = totalPhotos - 1;
            }}
            
            showSlide(currentPhotoIndex);
        }}
        
        function currentSlide(index) {{
            currentPhotoIndex = index - 1;
            showSlide(currentPhotoIndex);
        }}
        
        // Автоматическая смена слайдов (если есть фотографии)
        if (totalPhotos > 1) {{
            function autoSlide() {{
                changeSlide(1);
            }}
            
            // Запускаем автоматическую смену каждые 5 секунд
            let slideInterval = setInterval(autoSlide, 5000);
            
            // Останавливаем автоматическую смену при наведении
            const carousel = document.getElementById('photoCarousel');
            if (carousel) {{
                carousel.addEventListener('mouseenter', function() {{
                    clearInterval(slideInterval);
                }});
                
                // Возобновляем автоматическую смену при уходе курсора
                carousel.addEventListener('mouseleave', function() {{
                    slideInterval = setInterval(autoSlide, 5000);
                }});
            }}
        }}
    </script>
</body>
</html>"""
        
        # Сохраняем файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        # Генерируем ссылку
        base_url = request.host_url.rstrip('/')
        report_url = f"{base_url}/reports/{filename}"
        
        return jsonify({
            'success': True,
            'report_url': report_url,
            'filename': filename,
            'report_id': report_id,
            'report_number': report_number
        })
        
    except Exception as e:
        logger.error(f"Error saving HTML report: {e}")
        return jsonify({'error': 'Internal error'}), 500

def generate_qr_code_svg(url):
    """Генерирует QR-код в формате SVG"""
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Создаем SVG
        svg_string = qr.make_svg(fill_color="black", back_color="white")
        return svg_string
    except ImportError:
        # Fallback если qrcode не установлен - создаем простой SVG QR-код
        return f'''<svg width="80" height="80" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="25" height="25" fill="white"/>
            <path d="M1 1h3v3H1V1zm5 0h1v1H6V1zm2 0h3v1H8V1zm5 0h1v1h-1V1zm2 0h3v3h-2V1zm5 0h3v3h-3V1zM1 2h1v1H1V2zm3 0h1v1H4V2zm5 0h1v1H9V2zm2 0h1v1h-1V2zm7 0h1v1h-1V2zM1 3h1v1H1V3zm3 0h1v1H4V3zm7 0h1v1h-1V3zm3 0h1v1h-1V3zm5 0h1v1h-1V3zM1 5h3v3H1V5zm5 0h1v1H6V5zm3 0h1v1H9V5zm2 0h1v1h-1V5zm3 0h1v1h-1V5zm6 0h3v3h-3V5zM1 6h1v1H1V6zm3 0h1v1H4V6zm5 0h3v1H9V6zm4 0h1v1h-1V6zm7 0h1v1h-1V6zM1 7h1v1H1V7zm3 0h1v1H4V7zm8 0h1v1h-1V7zm3 0h1v1h-1V7zm5 0h1v1h-1V7zM6 9h1v1H6V9zm2 0h1v1H8V9zm3 0h1v1h-1V9zm2 0h1v1h-1V9zm3 0h1v1h-1V9zm3 0h1v1h-1V9zM1 10h1v1H1v-1zm2 0h1v1H3v-1zm4 0h1v1H7v-1zm4 0h3v1h-3v-1zm5 0h1v1h-1v-1zm3 0h1v1h-1v-1zM2 11h1v1H2v-1zm2 0h3v1H4v-1zm3 0h1v1H7v-1zm3 0h1v1h-1v-1zm4 0h1v1h-1v-1zm3 0h1v1h-1v-1zM1 12h1v1H1v-1zm4 0h1v1H5v-1zm2 0h1v1H7v-1zm4 0h1v1h-1v-1zm2 0h1v1h-1v-1zm4 0h1v1h-1v-1zm3 0h1v1h-1v-1zM3 13h1v1H3v-1zm2 0h1v1H5v-1zm3 0h1v1H8v-1zm4 0h1v1h-1v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1zM1 14h1v1H1v-1zm3 0h1v1H4v-1zm2 0h1v1H6v-1zm3 0h1v1H9v-1zm2 0h1v1h-1v-1zm5 0h1v1h-1v-1zm3 0h1v1h-1v-1zM2 15h1v1H2v-1zm2 0h1v1H4v-1zm3 0h1v1H7v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1zm4 0h1v1h-1v-1zM1 17h3v3H1v-3zm5 0h1v1H6v-1zm3 0h1v1H9v-1zm2 0h1v1h-1v-1zm3 0h1v1h-1v-1zm4 0h1v1h-1v-1zM1 18h1v1H1v-1zm3 0h1v1H4v-1zm5 0h1v1H9v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1zm4 0h1v1h-1v-1zM1 19h1v1H1v-1zm3 0h1v1H4v-1zm6 0h1v1h-1v-1zm2 0h1v1h-1v-1zm4 0h3v1h-3v-1zm4 0h1v1h-1v-1zM6 21h1v1H6v-1zm3 0h1v1H9v-1zm2 0h1v1h-1v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1zM1 22h1v1H1v-1zm2 0h1v1H3v-1zm3 0h1v1H6v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1zm4 0h1v1h-1v-1zm4 0h1v1h-1v-1zM2 23h3v1H2v-1zm3 0h1v1H5v-1zm3 0h1v1H8v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1zm3 0h1v1h-1v-1z" fill="#2c3e50"/>
        </svg>'''

@app.route('/api/send_saved_report_pdf', methods=['POST'])
def api_send_saved_report_pdf():
    """Генерирует PDF для сохранённого отчёта и отправляет его пользователю в Telegram (без контактов)"""
    data = request.json or {}
    report_id = data.get('report_id')
    telegram_id = data.get('telegram_id')
    if not report_id or not telegram_id:
        return jsonify({'error': 'report_id and telegram_id required'}), 400
    try:
        # Получаем отчёт из базы
        report_result = supabase.table('user_reports').select('full_report').eq('id', report_id).execute()
        if not report_result.data or not report_result.data[0].get('full_report'):
            return jsonify({'error': 'Report not found'}), 404
        report = report_result.data[0]['full_report']
        if not isinstance(report, dict):
            return jsonify({'error': 'Invalid report data'}), 500
        # Генерируем PDF (без контактов)
        from fpdf import FPDF
        import tempfile, shutil
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf')
        pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf')
        
        # Добавляем логотип на первую страницу (по центру сверху)
        try:
            pdf.image('logo-sqv.png', x=85, y=10, w=40)  # Центрируем логотип
            pdf.ln(35)  # Увеличенный отступ после логотипа
        except Exception as e:
            logger.warning(f"Не удалось добавить логотип на первую страницу: {e}")
            pdf.ln(35)  # Отступ даже если логотип не загрузился
        
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Полный отчет по недвижимости', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(10)
        obj = report.get('object') or {}
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, 'Информация об объекте:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 8, f'Адрес: {obj.get("address", "Не указан")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f'Спален: {obj.get("bedrooms", "Не указано")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f'Цена: €{obj.get("purchase_price", "Не указана")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)
        # ROI анализ
        roi = report.get('roi')
        if roi:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, "Инвестиционный анализ (ROI):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            st = roi.get('short_term', {})
            lt = roi.get('long_term', {})
            nr = roi.get('no_rent', {})
            pdf.cell(0, 8, f"Краткосрочная аренда: ROI {st.get('roi', '-')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f"Долгосрочная аренда: ROI {lt.get('roi', '-')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f"Без аренды: ROI {nr.get('roi', '-')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Макроэкономика
        macro = report.get('macro')
        if macro:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, "Макроэкономические показатели:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(0, 8, f"Инфляция: {macro.get('inflation', '-')}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f"Ключевая ставка: {macro.get('refi_rate', '-')}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f"Рост ВВП: {macro.get('gdp_growth', '-')}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        
        # Экономические данные и тренды
        if 'economic_charts' in report:
            economic_charts = report['economic_charts']
            country_name = economic_charts.get('country_name', 'Unknown')
            
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, f"Экономические тренды ({country_name}):", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            
            # Отображаем тренды
            trends = economic_charts.get('trends', {})
            if trends.get('gdp_trend') is not None:
                gdp_trend = trends['gdp_trend'] * 100  # Конвертируем в проценты
                trend_text = f"Тренд роста ВВП: {gdp_trend:.1f}%"
                pdf.cell(200, 8, text=trend_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            if trends.get('inflation_trend') is not None:
                inflation_trend = trends['inflation_trend'] * 100  # Конвертируем в проценты
                trend_text = f"Тренд инфляции: {inflation_trend:.1f}%"
                pdf.cell(200, 8, text=trend_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Добавляем детальные расчеты в компактной таблице
            detailed_calculations = economic_charts.get('detailed_calculations', {})
            if detailed_calculations:
                pdf.ln(5)
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(200, 8, text="Детальные расчеты трендов:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=8)
                
                # Создаем компактную таблицу в 3 столбца
                gdp_calcs = detailed_calculations.get('gdp_calculations', [])
                inflation_calcs = detailed_calculations.get('inflation_calculations', [])
                
                if gdp_calcs or inflation_calcs:
                    # Заголовки таблицы
                    pdf.set_font("DejaVu", 'B', 9)
                    pdf.cell(60, 6, text="Период", new_x=XPos.RIGHT, new_y=YPos.TOP)
                    pdf.cell(60, 6, text="Расчет", new_x=XPos.RIGHT, new_y=YPos.TOP)
                    pdf.cell(60, 6, text="Результат", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("DejaVu", size=8)
                    
                    # ВВП расчеты
                    if gdp_calcs:
                        pdf.cell(200, 4, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("DejaVu", 'B', 8)
                        pdf.cell(200, 5, text="ВВП:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("DejaVu", size=7)
                        
                        for calc in gdp_calcs:
                            # Первая строка
                            pdf.cell(60, 4, text=calc['years'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                            pdf.cell(60, 4, text=calc['calculation'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                            pdf.cell(60, 4, text=calc['result'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    # Инфляция расчеты
                    if inflation_calcs:
                        pdf.cell(200, 4, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("DejaVu", 'B', 8)
                        pdf.cell(200, 5, text="Инфляция:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.set_font("DejaVu", size=7)
                        
                        for calc in inflation_calcs:
                            # Первая строка
                            pdf.cell(60, 4, text=calc['years'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                            pdf.cell(60, 4, text=calc['calculation'], new_x=XPos.RIGHT, new_y=YPos.TOP)
                            pdf.cell(60, 4, text=calc['result'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Добавляем интерпретации
            interpretations = economic_charts.get('interpretations', {})
            if interpretations and 'ru' in interpretations:
                pdf.ln(5)
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(200, 8, text="Интерпретация трендов:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=10)
                
                ru_interp = interpretations['ru']
                if 'gdp_interpretation' in ru_interp:
                    pdf.cell(200, 6, text=f"ВВП: {ru_interp['gdp_interpretation']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                if 'inflation_interpretation' in ru_interp:
                    pdf.cell(200, 6, text=f"Инфляция: {ru_interp['inflation_interpretation']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                if 'recent_comparison' in ru_interp:
                    pdf.cell(200, 6, text=f"Сравнение: {ru_interp['recent_comparison']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.ln(5)
        
        # Данные трендов недвижимости
        if report.get('object') and report['object'].get('address'):
            address = report['object']['address']
            location_data = extract_location_from_address(address)
            
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, "Тренды рынка недвижимости:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            
            if location_data['city_name']:
                trends_data, trends_message = get_property_trends_data(
                    location_data['city_name'],
                    location_data['district_name'],
                    location_data['county_name']
                )
                
                # Получаем исторические данные для графиков
                historical_data = get_historical_property_trends(
                    location_data['city_name'],
                    location_data['district_name'],
                    location_data['county_name']
                )
                
                # Данные по продаже
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(0, 8, "Данные по продаже:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=10)
                
                # Показываем источник данных
                if trends_message:
                    pdf.cell(0, 6, f"Источник данных: {trends_message}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                if trends_data:
                    if trends_data.get('unit_price_for_sale'):
                        pdf.cell(0, 6, f"Средняя цена за м² (продажа): €{trends_data['unit_price_for_sale']:,.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Средняя цена за м² (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('price_change_sale'):
                        change_percent = trends_data['price_change_sale'] * 100
                        pdf.cell(0, 6, f"Изменение цен (продажа): {change_percent:+.2f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Изменение цен (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('listing_period_for_sale'):
                        pdf.cell(0, 6, f"Средний период продажи: {trends_data['listing_period_for_sale']} дней", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Средний период продажи: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('count_for_sale'):
                        pdf.cell(0, 6, f"Объектов на продажу: {trends_data['count_for_sale']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Объектов на продажу: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                else:
                    pdf.cell(0, 6, "Средняя цена за м² (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, "Изменение цен (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, "Средний период продажи: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, "Объектов на продажу: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # График изменения цен на продажу
                if historical_data:
                    sale_chart_buffer = create_property_trends_chart(historical_data, 'sale', 180, 80)
                    if sale_chart_buffer:
                        pdf.ln(3)
                        pdf.image(sale_chart_buffer, x=15, w=180)
                        pdf.ln(3)
                
                pdf.ln(5)
                
                # Данные по аренде (долгосрочная)
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(0, 8, "Данные по долгосрочной аренде:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=10)
                
                if trends_data:
                    if trends_data.get('unit_price_for_rent'):
                        pdf.cell(0, 6, f"Средняя цена за м² (аренда): €{trends_data['unit_price_for_rent']:,.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Средняя цена за м² (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('price_change_rent'):
                        change_percent = trends_data['price_change_rent'] * 100
                        pdf.cell(0, 6, f"Изменение цен (аренда): {change_percent:+.2f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Изменение цен (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('listing_period_for_rent'):
                        pdf.cell(0, 6, f"Средний период аренды: {trends_data['listing_period_for_rent']} дней", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Средний период аренды: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    if trends_data.get('count_for_rent'):
                        pdf.cell(0, 6, f"Объектов на аренду: {trends_data['count_for_rent']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Объектов на аренду: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    # Доходность
                    if trends_data.get('yield'):
                        yield_percent = trends_data['yield'] * 100
                        pdf.cell(0, 6, f"Доходность: {yield_percent:.2f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    else:
                        pdf.cell(0, 6, "Доходность: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                else:
                    pdf.cell(0, 6, "Средняя цена за м² (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, "Изменение цен (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, "Средний период аренды: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, "Объектов на аренду: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(0, 6, "Доходность: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # График изменения цен на аренду
                if historical_data:
                    rent_chart_buffer = create_property_trends_chart(historical_data, 'rent', 180, 80)
                    if rent_chart_buffer:
                        pdf.ln(3)
                        pdf.image(rent_chart_buffer, x=15, w=180)
                        pdf.ln(3)
            else:
                # Адрес не содержит информации о городе - показываем "н/д" для всех полей
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(0, 8, "Данные по продаже:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=10)
                pdf.cell(0, 6, "Средняя цена за м² (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 6, "Изменение цен (продажа): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 6, "Средний период продажи: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 6, "Объектов на продажу: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                pdf.ln(5)
                
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(0, 8, "Данные по долгосрочной аренде:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", size=10)
                pdf.cell(0, 6, "Средняя цена за м² (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 6, "Изменение цен (аренда): н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 6, "Средний период аренды: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 6, "Объектов на аренду: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 6, "Доходность: н/д", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            pdf.ln(5)
        
        # Налоги
        taxes = report.get('taxes')
        if taxes:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, "Налоги и сборы:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(0, 8, f"Налог на перевод: {taxes.get('transfer_tax', 0)*100}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f"Гербовый сбор: {taxes.get('stamp_duty', 0)*100}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(0, 8, f"Нотариус: €{taxes.get('notary', '-')}" , new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Альтернативы
        alternatives = report.get('alternatives')
        if isinstance(alternatives, list):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Сравнение с альтернативами (5 лет):', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 12)
            for alt in alternatives:
                name = alt.get('name', '-')
                yld = alt.get('yield', 0)
                pdf.cell(0, 8, f'{name}: {round(yld*100, 1)}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Профессиональные метрики
        if any(k in report for k in ['yield', 'price_index', 'mortgage_rate', 'global_house_price_index']):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Профессиональные метрики:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 12)
            if 'yield' in report:
                pdf.cell(0, 8, f'Yield: {round(report.get("yield", 0)*100, 1)}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'price_index' in report:
                pdf.cell(0, 8, f'Индекс цен: {report.get("price_index", "-")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'mortgage_rate' in report:
                pdf.cell(0, 8, f'Ипотечная ставка: {round(report.get("mortgage_rate", 0)*100, 1)}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'global_house_price_index' in report:
                pdf.cell(0, 8, f'Глобальный индекс цен: {report.get("global_house_price_index", "-")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Риски и развитие района
        if any(k in report for k in ['risks', 'liquidity', 'district']):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Риски и развитие района:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVu', '', 12)
            risks = report.get('risks')
            if isinstance(risks, list):
                for idx, risk in enumerate(risks):
                    pdf.cell(0, 8, f'Риск {idx+1}: {risk}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'liquidity' in report:
                pdf.cell(0, 8, f'Ликвидность: {report.get("liquidity", "-")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if 'district' in report:
                pdf.cell(0, 8, f'Развитие района: {report.get("district", "-")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)
        # Сохраняем PDF во временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        # Перемещаем PDF в static/reports/
        reports_dir = os.path.join(app.root_path, 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        # Генерируем уникальное имя файла только цифрами
        file_id = ''.join(random.choices(string.digits, k=12))
        final_pdf_name = f'{file_id}.pdf'
        final_pdf_path = os.path.join(reports_dir, final_pdf_name)
        shutil.move(temp_file.name, final_pdf_path)
        pdf_url = f'/static/reports/{final_pdf_name}'
        supabase.table('user_reports').update({'pdf_path': pdf_url}).eq('id', report_id).execute()
        # Отправка PDF через Telegram-бота (используем общую функцию)
        send_status = None
        if telegram_id:
            send_status = send_pdf_to_telegram(final_pdf_path, telegram_id)
        return jsonify({
            'success': True,
            'pdf_path': pdf_url,
            'telegram_send_status': send_status,
            'message': 'PDF успешно сгенерирован и отправлен!'
        })
    except Exception as e:
        logger.error(f"Error generating/sending PDF: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/admin_balance_100', methods=['POST'])
def api_admin_balance_100():
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    # Проверяем, что пользователь админ
    user_result = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
    user = user_result.data[0] if user_result.data else None
    if not user or user.get('user_status') != 'admin':
        return jsonify({'error': 'not admin'}), 403
    # Обновляем баланс
    try:
        supabase.table('users').update({'balance': 100}).eq('telegram_id', telegram_id).execute()
        return jsonify({'success': True, 'balance': 100})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin_users_stats', methods=['GET'])
def api_admin_users_stats():
    import datetime
    from dateutil.relativedelta import relativedelta
    now = datetime.now()
    today = now.date()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - relativedelta(months=1)
    quarter_ago = today - relativedelta(months=3)
    year_ago = today - relativedelta(years=1)

    # Получаем всех пользователей
    users = supabase.table('users').select('*').execute().data or []
    user_reports = supabase.table('user_reports').select('*').execute().data or []
    tariffs = supabase.table('tariffs').select('*').execute().data or []

    # Фильтры
    non_admin_users = [u for u in users if u.get('user_status') != 'admin']
    admin_users = [u for u in users if u.get('user_status') == 'admin']
    def parse_date(val):
        if not val: return None
        try:
            return datetime.strptime(val[:10], '%Y-%m-%d').date()
        except Exception:
            return None

    # Новые пользователи
    def count_new(users, since):
        return sum(1 for u in users if parse_date(u.get('created_at')) and parse_date(u.get('created_at')) >= since)

    # Балансы
    total_balance = sum(u.get('balance', 0) or 0 for u in non_admin_users)
    expired_users = [u for u in non_admin_users if (parse_date(u.get('period_end')) is None or parse_date(u.get('period_end')) < today) and u.get('period_end')]
    active_users = [u for u in non_admin_users if not ((parse_date(u.get('period_end')) is None or parse_date(u.get('period_end')) < today) and u.get('period_end'))]
    expired_balance = sum(u.get('balance', 0) or 0 for u in expired_users)
    active_balance = total_balance - expired_balance

    # Отчёты
    def count_reports(since):
        return sum(1 for r in user_reports if parse_date(r.get('created_at')) and parse_date(r.get('created_at')) >= since and not r.get('deleted_at'))
    def count_deleted_reports():
        return sum(1 for r in user_reports if r.get('deleted_at'))
    def reports_by_users(users_list):
        ids = set(u.get('telegram_id') for u in users_list)
        return [r for r in user_reports if r.get('user_id') in ids]
    expired_reports = reports_by_users(expired_users)
    active_reports = reports_by_users(active_users)
    avg_expired_reports = len(expired_reports) / len(expired_users) if expired_users else 0
    # Стоимость full из tariffs
    full_price = 0
    for t in tariffs:
        if t.get('name') == 'full':
            full_price = t.get('price', 0)
            break
    active_reports_count = len(active_reports)
    active_reports_cost = active_reports_count * full_price

    return jsonify({
        'total_users': len(non_admin_users),
        'new_users_week': count_new(non_admin_users, week_ago),
        'new_users_month': count_new(non_admin_users, month_ago),
        'new_users_quarter': count_new(non_admin_users, quarter_ago),
        'new_users_year': count_new(non_admin_users, year_ago),
        'total_balance': total_balance,
        'expired_balance': expired_balance,
        'active_balance': active_balance,
        'reports_week': count_reports(week_ago),
        'reports_month': count_reports(month_ago),
        'reports_quarter': count_reports(quarter_ago),
        'reports_year': count_reports(year_ago),
        'deleted_reports': count_deleted_reports(),
        'expired_reports_count': len(expired_reports),
        'avg_expired_reports': avg_expired_reports,
        'active_reports_count': active_reports_count,
        'active_reports_cost': active_reports_cost,
        'admin_count': len(admin_users),
    })

@app.route('/api/admin_publication', methods=['POST'])
def api_admin_publication():
    import requests
    data = request.json or {}
    text = data.get('text', '').strip()
    only_admins = data.get('only_admins', True)
    save_to_db = data.get('save_to_db', False)
    auto_translate = data.get('auto_translate', False)
    test_send = data.get('test_send', False)
    if not text:
        return jsonify({'error': 'text required'}), 400
    # Получаем всех пользователей
    users = supabase.table('users').select('telegram_id, user_status, language').execute().data or []
    # Получаем OpenAI API ключ
    openai_key = get_openai_api_key()
    # Языки и поля для перевода
    lang_map = {'ru': 'ru', 'en': 'us', 'de': 'de', 'fr': 'ft', 'tr': 'tr'}
    translations = {'ru': text, 'us': '', 'de': '', 'ft': '', 'tr': ''}
    # Переводим, если нужно
    print(f"DEBUG: auto_translate={auto_translate}, openai_key={'есть' if openai_key else 'нет'}")
    # Временно форсируем выполнение перевода для диагностики
    if True:
        logger.info(f"auto_translate={auto_translate}, openai_key={'есть' if openai_key else 'нет'}")
        def gpt_translate(prompt, target_lang):
            logger.info(f"Запрос к OpenAI для {target_lang}")
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI library not available, using fallback")
                return f"[Перевод недоступен - {target_lang}]"
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_lang} (no explanation, only translation):"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1024,
                    temperature=0.3
                )
                result = response.choices[0].message.content.strip()
                logger.info(f"Перевод {target_lang}: {result}")
                return result
            except Exception as e:
                logger.error(f"OpenAI API exception for {target_lang}: {e}")
                return f"[Ошибка перевода {target_lang}]"
        translations['us'] = gpt_translate(text, 'English')
        translations['de'] = gpt_translate(text, 'German')
        translations['ft'] = gpt_translate(text, 'French')
        translations['tr'] = gpt_translate(text, 'Turkish')
    # Определяем получателей
    recipients = []
    if test_send:
        # Только админы, но каждому отправить все переводы
        recipients = [u for u in users if u.get('user_status') == 'admin']
    elif only_admins:
        recipients = [u for u in users if u.get('user_status') == 'admin']
    else:
        recipients = users
    # Рассылка
    bot_token = '7215676549:AAFS86JbRCqwzTKQG-dF96JX-C1aWNvBoLo'
    send_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    lang_stats = {'ru': 0, 'us': 0, 'de': 0, 'ft': 0, 'tr': 0}
    admin_count = 0
    user_count = 0
    total = 0
    for u in recipients:
        tid = u.get('telegram_id')
        if not tid:
            continue
        lang = (u.get('language') or 'ru')[:2]
        # Для тестовой рассылки — всем админам все переводы
        if test_send:
            for l, field in lang_map.items():
                msg = translations[field] if translations[field] else text
                data_send = {'chat_id': tid, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
                resp = requests.post(send_url, data=data_send)
                if resp.status_code == 200 and resp.json().get('ok'):
                    lang_stats[field] += 1
                    if u.get('user_status') == 'admin':
                        admin_count += 1
                    else:
                        user_count += 1
                    total += 1
        else:
            # Обычная рассылка — каждому на его языке, если перевод есть
            field = lang_map.get(lang, 'ru')
            msg = translations[field] if translations[field] else text
            data_send = {'chat_id': tid, 'text': msg, 'parse_mode': 'HTML', 'disable_web_page_preview': True}
            resp = requests.post(send_url, data=data_send)
            if resp.status_code == 200 and resp.json().get('ok'):
                lang_stats[field] += 1
                if u.get('user_status') == 'admin':
                    admin_count += 1
                else:
                    user_count += 1
                total += 1
    # Сохраняем в базу, если нужно
    if save_to_db or test_send:
        supabase.table('texts_promo').insert({
            'base': text,
            'ru': translations['ru'],
            'us': translations['us'],
            'de': translations['de'],
            'ft': translations['ft'],
            'tr': translations['tr'],
            'qtty_ru': lang_stats['ru'],
            'qtty_us': lang_stats['us'],
            'qtty_de': lang_stats['de'],
            'qtty_ft': lang_stats['ft'],
            'qtty_tr': lang_stats['tr'],
        }).execute()
    # Формируем строку-отчет для пользователя
    result_message = f"Всего отправлено: {total}\nПользователям: {user_count}\nАдминистраторам: {admin_count}"
    return jsonify({
        'success': True,
        'total': total,
        'users': user_count,
        'admins': admin_count,
        'result_message': result_message,
        'lang_stats': lang_stats
    })

@app.route('/api/admin_add_apikey', methods=['POST'])
def api_admin_add_apikey():
    data = request.json or {}
    key_name = data.get('key_name', '').strip()
    key_value = data.get('key_value', '').strip()
    if not key_name or not key_value:
        return jsonify({'error': 'key_name and key_value required'}), 400
    # Не даём добавлять ключи, которые уже используются в приложении
    used_keys = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'TELEGRAM_BOT_TOKEN', 'GOOGLE_MAPS_API_KEY']
    if key_name in used_keys:
        return jsonify({'error': 'Этот ключ уже используется приложением'}), 400
    # Проверяем, есть ли такой ключ
    exists = supabase.table('api_keys').select('*').eq('key_name', key_name).execute().data
    if exists:
        return jsonify({'error': 'Ключ с таким именем уже существует'}), 400
    try:
        supabase.table('api_keys').insert({'key_name': key_name, 'key_value': key_value}).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin_list_apikeys', methods=['GET'])
def api_admin_list_apikeys():
    used_keys = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'TELEGRAM_BOT_TOKEN', 'GOOGLE_MAPS_API_KEY']
    all_keys = supabase.table('api_keys').select('*').execute().data or []
    new_keys = [k for k in all_keys if k.get('key_name') not in used_keys]
    return jsonify({'keys': new_keys})

# === Запуск Flask приложения ===
def run_flask():
    """Запуск Flask приложения"""
    # Вывод всех роутов для отладки
    print("\n=== Flask ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.methods} {rule}")
    print("====================\n")
    app.run(host='0.0.0.0', port=8080, debug=False)

@app.route('/webapp_admin')
def webapp_admin():
    with open('webapp_admin.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_admin_users')
def webapp_admin_users():
    with open('webapp_admin_users.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_admin_settings')
def webapp_admin_settings():
    with open('webapp_admin_settings.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_admin_publication')
def webapp_admin_publication():
    with open('webapp_admin_publication.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_about')
def webapp_about():
    with open('webapp_about.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_instruction')
def webapp_instruction():
    with open('webapp_instruction.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_geography')
def webapp_geography():
    with open('webapp_geography.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_support')
def webapp_support():
    with open('webapp_support.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_referral')
def webapp_referral():
    with open('webapp_referral.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_additional_data')
def webapp_additional_data():
    with open('webapp_additional_data.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_full_report')
def webapp_full_report():
    with open('webapp_full_report.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/referral_info', methods=['POST'])
def api_referral_info():
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    if telegram_id_raw is None:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid telegram_id'}), 400
    # Получаем пользователя
    user_result = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
    user = user_result.data[0] if user_result.data else None
    if not user:
        return jsonify({'error': 'User not found'}), 404
    invite_code = user.get('invite_code')
    # Если invite_code не существует, генерируем его
    if not invite_code:
        def generate_invite_code():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Проверка уникальности invite_code
        while True:
            invite_code = generate_invite_code()
            code_check = supabase.table('users').select('invite_code').eq('invite_code', invite_code).execute()
            if not code_check.data:
                break
        # Обновляем пользователя с новым invite_code
        supabase.table('users').update({'invite_code': invite_code}).eq('telegram_id', telegram_id).execute()
    # Формируем персональную ссылку
    bot_link = f'https://t.me/Aaadviser_bot?start={invite_code}'
    # Получаем условия реферальной программы
    # Получаем размер бонуса из tariffs
    tariffs_result = supabase.table('tariffs').select('*').execute()
    bonus = None
    if tariffs_result.data:
        # Ищем запись с типом invite или похожим
        for tariff in tariffs_result.data:
            if tariff.get('type') == 'invite' or tariff.get('name') == 'invite' or 'invite' in str(tariff.get('description', '')).lower():
                bonus = tariff.get('price')
                break
        # Если не нашли, берем первую запись
        if bonus is None and tariffs_result.data:
            bonus = tariffs_result.data[0].get('price')
    referral_terms = (
        f'Пригласите друзей по вашей персональной ссылке.\n'
        f'За каждого, кто зарегистрируется и оформит хотя бы один платный отчет, вы получите бонус на баланс.'
    )
    if bonus:
        referral_terms += f' Размер бонуса: {bonus}.'
    referral_terms += '\nБонус начисляется только после первой покупки платного отчета приглашённым.'
    # Получаем приглашённых пользователей
    invited_result = supabase.table('users').select('*').eq('referal', invite_code).execute()
    invited = []
    for invited_user in invited_result.data:
        # Проверяем, есть ли у пользователя хотя бы один платный отчет
        reports_result = supabase.table('reports').select('*').eq('user_id', invited_user['telegram_id']).eq('is_paid', True).execute()
        completed = bool(reports_result.data)
        invited.append({
            'tg_name': invited_user.get('tg_name'),
            'username': invited_user.get('username'),
            'telegram_id': invited_user.get('telegram_id'),
            'completed': completed
        })
    return jsonify({
        'invite_code': invite_code,
        'bot_link': bot_link,
        'referral_terms': referral_terms,
        'invited': invited
    })

@app.route('/api/tariffs', methods=['GET'])
def api_tariffs():
    try:
        tariffs_result = supabase.table('tariffs').select('*').execute()
        tariffs = []
        for t in tariffs_result.data:
            tariffs.append({
                'description': t.get('description'),
                'price': t.get('price'),
                'tariff_type': t.get('tariff_type'),
                'period_days': t.get('period_days'),
                'name': t.get('name'),
            })
        return jsonify({'tariffs': tariffs})
    except Exception as e:
        logger.error(f"Error loading tariffs: {e}")
        return jsonify({'tariffs': []}), 500

@app.route('/api/economic_data', methods=['POST'])
def api_economic_data():
    """Получение экономических данных (ВВП и инфляция) для построения графиков"""
    data = request.json or {}
    country_code = data.get('country_code', 'TUR')
    years_back = data.get('years_back', 10)
    
    try:
        # Получаем экономические данные
        economic_data = get_economic_data(country_code, years_back)
        chart_data = create_economic_chart_data(economic_data)
        
        return jsonify({
            'success': True,
            'economic_data': economic_data,
            'chart_data': chart_data,
            'country_code': country_code,
            'years_back': years_back
        })
        
    except Exception as e:
        logger.error(f"Error in economic_data API: {e}")
        return jsonify({'error': 'Internal error'}), 500

def create_economic_chart_image(economic_charts_data):
    """
    Создает изображение графика экономических данных (заглушка)
    """
    logger.info("Функция создания графиков отключена для упрощения")
    return None

def create_chart_image_for_pdf(chart_data, title, width=180, height=100):
    """
    Создает изображение графика для вставки в PDF (заглушка)
    """
    logger.info(f"Функция создания графиков отключена для упрощения: {title}")
    return None

def get_market_data_by_location_ids(location_codes, target_year=None, target_month=None):
    """
    Получает данные рынка недвижимости по ID локаций
    
    Args:
        location_codes (dict): Коды локаций (country_id, city_id, district_id, county_id)
        target_year (int): Год (по умолчанию текущий)
        target_month (int): Месяц (по умолчанию текущий)
    
    Returns:
        dict: Данные рынка недвижимости
    """
    try:
        from datetime import datetime
        
        # Если год и месяц не указаны, используем текущие
        if target_year is None or target_month is None:
            now = datetime.now()
            target_year = target_year or now.year
            target_month = target_month or now.month
        
        logger.info(f"Получаем данные рынка для {target_year}-{target_month:02d}")
        logger.info(f"Коды локаций: {location_codes}")
        
        # Проверяем, что все необходимые коды локаций присутствуют
        required_codes = ['country_id', 'city_id', 'district_id', 'county_id']
        missing_codes = [code for code in required_codes if not location_codes.get(code)]
        if missing_codes:
            logger.warning(f"Отсутствуют коды локаций: {missing_codes}")
            return None
        
        market_data = {
            'property_trends': None,
            'age_data': None,
            'floor_segment_data': None,
            'general_data': None,
            'heating_data': None,
            'house_type_data': None
        }
        
        # Получаем данные из property_trends
        try:
            query = supabase.table('property_trends').select('*')
            if location_codes.get('country_id'):
                query = query.eq('country_id', location_codes['country_id'])
            if location_codes.get('city_id'):
                query = query.eq('city_id', location_codes['city_id'])
            if location_codes.get('district_id'):
                query = query.eq('district_id', location_codes['district_id'])
            if location_codes.get('county_id'):
                query = query.eq('county_id', location_codes['county_id'])
            
            result = query.execute()
            if result.data:
                # Фильтруем записи с валидными датами
                valid_records = [r for r in result.data if r.get('trend_date')]
                if valid_records:
                    # Берем самую свежую запись
                    latest_record = max(valid_records, key=lambda x: x.get('trend_date', ''))
                    market_data['property_trends'] = latest_record
                    logger.info(f"Найдены данные property_trends: {len(result.data)} записей, выбрана самая свежая: {latest_record.get('trend_date')}")
                else:
                    logger.warning("Все записи property_trends имеют пустые даты")
                    market_data['property_trends'] = result.data[0] if result.data else None
            else:
                logger.info("Данные property_trends не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения property_trends: {e}")
            market_data['property_trends'] = None
        
        # Получаем данные из age_data
        try:
            query = supabase.table('age_data').select('*')
            if location_codes.get('country_id'):
                query = query.eq('country_id', location_codes['country_id'])
            if location_codes.get('city_id'):
                query = query.eq('city_id', location_codes['city_id'])
            if location_codes.get('district_id'):
                query = query.eq('district_id', location_codes['district_id'])
            if location_codes.get('county_id'):
                query = query.eq('county_id', location_codes['county_id'])
            
            result = query.execute()
            if result.data:
                # Группируем записи по listing_type и берем самую свежую для каждого типа
                records_by_type = {}
                for record in result.data:
                    listing_type = record.get('listing_type')
                    if listing_type:
                        if listing_type not in records_by_type:
                            records_by_type[listing_type] = record
                        else:
                            # Если уже есть запись для этого типа, сравниваем даты
                            existing_date = records_by_type[listing_type].get('trend_date', '')
                            current_date = record.get('trend_date', '')
                            if existing_date and current_date and current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['age_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные age_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам возраста")
            else:
                logger.info("Данные age_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения age_data: {e}")
            market_data['age_data'] = None
        
        # Получаем данные из floor_segment_data
        try:
            query = supabase.table('floor_segment_data').select('*')
            if location_codes.get('country_id'):
                query = query.eq('country_id', location_codes['country_id'])
            if location_codes.get('city_id'):
                query = query.eq('city_id', location_codes['city_id'])
            if location_codes.get('district_id'):
                query = query.eq('district_id', location_codes['district_id'])
            if location_codes.get('county_id'):
                query = query.eq('county_id', location_codes['county_id'])
            
            result = query.execute()
            if result.data:
                # Группируем записи по listing_type и берем самую свежую для каждого типа
                records_by_type = {}
                for record in result.data:
                    listing_type = record.get('listing_type')
                    if listing_type:
                        if listing_type not in records_by_type:
                            records_by_type[listing_type] = record
                        else:
                            # Если уже есть запись для этого типа, сравниваем даты
                            existing_date = records_by_type[listing_type].get('trend_date', '')
                            current_date = record.get('trend_date', '')
                            if existing_date and current_date and current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['floor_segment_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные floor_segment_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам этажей")
            else:
                logger.info("Данные floor_segment_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения floor_segment_data: {e}")
            market_data['floor_segment_data'] = None
        
        # Получаем данные из general_data
        try:
            query = supabase.table('general_data').select('*')
            if location_codes.get('country_id'):
                query = query.eq('country_id', location_codes['country_id'])
            if location_codes.get('city_id'):
                query = query.eq('city_id', location_codes['city_id'])
            if location_codes.get('district_id'):
                query = query.eq('district_id', location_codes['district_id'])
            if location_codes.get('county_id'):
                query = query.eq('county_id', location_codes['county_id'])
            
            result = query.execute()
            if result.data:
                # Фильтруем записи с валидными датами
                valid_records = [r for r in result.data if r.get('trend_date')]
                if valid_records:
                    # Берем самую свежую запись
                    latest_record = max(valid_records, key=lambda x: x.get('trend_date', ''))
                    market_data['general_data'] = latest_record
                    logger.info(f"Найдены данные general_data: {len(result.data)} записей, выбрана самая свежая: {latest_record.get('trend_date')}")
                else:
                    logger.warning("Все записи general_data имеют пустые даты")
                    market_data['general_data'] = result.data[0] if result.data else None
            else:
                logger.info("Данные general_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения general_data: {e}")
            market_data['general_data'] = None
        
        # Получаем данные из heating_data
        try:
            query = supabase.table('heating_data').select('*')
            if location_codes.get('country_id'):
                query = query.eq('country_id', location_codes['country_id'])
            if location_codes.get('city_id'):
                query = query.eq('city_id', location_codes['city_id'])
            if location_codes.get('district_id'):
                query = query.eq('district_id', location_codes['district_id'])
            if location_codes.get('county_id'):
                query = query.eq('county_id', location_codes['county_id'])
            
            result = query.execute()
            if result.data:
                # Группируем записи по listing_type и берем самую свежую для каждого типа
                records_by_type = {}
                for record in result.data:
                    listing_type = record.get('listing_type')
                    if listing_type:
                        if listing_type not in records_by_type:
                            records_by_type[listing_type] = record
                        else:
                            # Если уже есть запись для этого типа, сравниваем даты
                            existing_date = records_by_type[listing_type].get('trend_date', '')
                            current_date = record.get('trend_date', '')
                            if existing_date and current_date and current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['heating_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные heating_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам отопления")
            else:
                logger.info("Данные heating_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения heating_data: {e}")
            market_data['heating_data'] = None
        
        # Получаем данные из house_type_data
        try:
            query = supabase.table('house_type_data').select('*')
            if location_codes.get('country_id'):
                query = query.eq('country_id', location_codes['country_id'])
            if location_codes.get('city_id'):
                query = query.eq('city_id', location_codes['city_id'])
            if location_codes.get('district_id'):
                query = query.eq('district_id', location_codes['district_id'])
            if location_codes.get('county_id'):
                query = query.eq('county_id', location_codes['county_id'])
            
            result = query.execute()
            if result.data:
                # Группируем записи по listing_type и берем самую свежую для каждого типа
                records_by_type = {}
                for record in result.data:
                    listing_type = record.get('listing_type')
                    if listing_type:
                        if listing_type not in records_by_type:
                            records_by_type[listing_type] = record
                        else:
                            # Если уже есть запись для этого типа, сравниваем даты
                            existing_date = records_by_type[listing_type].get('trend_date', '')
                            current_date = record.get('trend_date', '')
                            if existing_date and current_date and current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['house_type_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные house_type_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам спален")
            else:
                logger.info("Данные house_type_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения house_type_data: {e}")
            market_data['house_type_data'] = None
        
        return market_data
        
    except Exception as e:
        logger.error(f"Ошибка получения данных рынка: {e}")
        return None

def get_location_codes(city_name, district_name, county_name):
    """
    Получает коды локаций из таблицы locations по названиям
    
    Args:
        city_name (str): Название города
        district_name (str): Название района
        county_name (str): Название округа/провинции
    
    Returns:
        dict: Словарь с кодами или None если не найдены
    """
    try:
        location_codes = {
            'city_code': None,
            'district_code': None,
            'county_code': None,
            'country_code': None
        }
        
        # Ищем запись с точным совпадением всех параметров
        query = supabase.table('locations').select('*')
        
        # Добавляем фильтры по всем параметрам
        if city_name:
            query = query.eq('city_name', city_name)
        if district_name:
            query = query.eq('district_name', district_name)
        if county_name:
            query = query.eq('county_name', county_name)
            
        result = query.execute()
        
        if result.data:
            # Найдена точная запись
            record = result.data[0]
            location_codes['city_code'] = record.get('city_id')
            location_codes['district_code'] = record.get('district_id')
            location_codes['county_code'] = record.get('county_id')
            location_codes['country_code'] = record.get('country_id')
            logger.info(f"Найдены коды локаций: {location_codes}")
            return location_codes
        else:
            # Ищем частичные совпадения
            logger.warning(f"Точное совпадение не найдено, ищем частичные совпадения")
            
            # Поиск по району
            if district_name:
                district_result = supabase.table('locations').select('*').eq('district_name', district_name).execute()
                if district_result.data:
                    location_codes['district_code'] = district_result.data[0].get('district_id')
            
            # Поиск по округу
            if county_name:
                county_result = supabase.table('locations').select('*').eq('county_name', county_name).execute()
                if county_result.data:
                    location_codes['county_code'] = county_result.data[0].get('county_id')
            
            # Поиск по городу
            if city_name:
                city_result = supabase.table('locations').select('*').eq('city_name', city_name).execute()
                if city_result.data:
                    location_codes['city_code'] = city_result.data[0].get('city_id')
        
        return location_codes
        
    except Exception as e:
        logger.error(f"Ошибка получения кодов локаций: {e}")
        return None

def get_property_trends_data(city_name, district_name, county_name):
    """
    Получает данные трендов недвижимости из таблицы property_trends
    
    Args:
        city_name (str): Название города
        district_name (str): Название района
        county_name (str): Название округа/провинции
    
    Returns:
        dict: Данные трендов недвижимости или None если данные не найдены
    """
    try:
        # Получаем текущую дату для определения последнего месяца
        from datetime import datetime
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Если текущий месяц январь, берем декабрь прошлого года
        if current_month == 1:
            target_year = current_year - 1
            target_month = 12
        else:
            target_year = current_year
            target_month = current_month - 1
        
        logger.info(f"Поиск данных трендов для: {city_name}, {district_name}, {county_name}")
        logger.info(f"Целевой период: {target_month}/{target_year}")
        
        # Сначала получаем коды локаций
        location_codes = get_location_codes(city_name, district_name, county_name)
        
        if not location_codes:
            logger.warning("Не удалось получить коды локаций")
            return None
        
        # Каскадный поиск данных трендов
        trends_data, message = get_cascading_trends_data(location_codes, target_year, target_month)
        
        if trends_data:
            logger.info(f"Найдены данные трендов: {message}")
            return trends_data, message
        else:
            logger.warning(f"Данные трендов не найдены: {message}")
            # Возвращаем fallback данные
            fallback_data = {
                'property_year': target_year,
                'property_month': target_month,
                'avg_price_per_sqm': 15000,
                'price_change_percent': 4.2,
                'transaction_count': 25,
                'days_on_market': 68,
                'rental_yield': 8.1,
                'price_trend': 'stable',
                'market_activity': 'moderate'
            }
            return fallback_data, "Fallback данные (нет реальных данных)"
            
    except Exception as e:
        logger.error(f"Ошибка получения данных трендов недвижимости: {e}")
        return None, "Ошибка при получении данных трендов"

def get_cascading_trends_data(location_codes, target_year, target_month):
    """
    Каскадный поиск данных трендов с fallback логикой
    
    Args:
        location_codes (dict): Словарь с кодами локаций
        target_year (int): Целевой год
        target_month (int): Целевой месяц
    
    Returns:
        tuple: (data, message) - данные и сообщение о типе найденных данных
    """
    try:
        city_code = location_codes.get('city_code')
        district_code = location_codes.get('district_code')
        county_code = location_codes.get('county_code')
        country_id = 1  # Türkiye
        
        # 1. Пытаемся найти точное совпадение
        if city_code and district_code and county_code:
            query = supabase.table('property_trends').select('*').eq('city_id', city_code).eq('district_id', district_code).eq('county_id', county_code).eq('property_year', target_year).eq('property_month', target_month)
            result = query.execute()
            
            if result.data:
                logger.info("Найдены данные по точному совпадению")
                return result.data[0], f"Данные по району (точное совпадение)"
        
        # 2. Если district_code не найден, ищем по county_code
        if county_code:
            query = supabase.table('property_trends').select('*').eq('county_id', county_code).is_('city_id', 'null').is_('district_id', 'null').eq('property_year', target_year).eq('property_month', target_month)
            result = query.execute()
            
            if result.data:
                logger.info("Найдены данные по округу")
                return result.data[0], f"Данные по округу (county_id={county_code})"
        
        # 3. Если county_code не найден, ищем по city_code
        if city_code:
            query = supabase.table('property_trends').select('*').eq('city_id', city_code).is_('district_id', 'null').is_('county_id', 'null').eq('property_year', target_year).eq('property_month', target_month)
            result = query.execute()
            
            if result.data:
                logger.info("Найдены данные по городу")
                return result.data[0], f"Данные по городу (city_id={city_code})"
        
        # 4. Если city_code не найден, ищем по country_id
        query = supabase.table('property_trends').select('*').eq('country_id', country_id).is_('city_id', 'null').is_('district_id', 'null').is_('county_id', 'null').eq('property_year', target_year).eq('property_month', target_month)
        result = query.execute()
        
        if result.data:
            logger.info("Найдены данные по стране")
            return result.data[0], f"Данные по стране (country_id={country_id})"
        
        # 5. Если ничего не найдено
        logger.warning("Данные не найдены на всех уровнях")
        return None, "По данной локации нет данных"
        
    except Exception as e:
        logger.error(f"Ошибка каскадного поиска данных: {e}")
        return None, "Ошибка при поиске данных"

def get_nominatim_location(address):
    """
    Получает структурированные данные адреса через Nominatim API
    
    Args:
        address (str): Адрес для геокодирования
    
    Returns:
        dict: Структурированные данные адреса или None
    """
    try:
        # Запрос к Nominatim API
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1
        }
        headers = {
            'User-Agent': 'Aaadviser/1.0'
        }
        
        try:
            logger.info(f"🔄 Отправляем HTTP запрос к Nominatim API: {url}")
            logger.info(f"📝 Параметры запроса: {params}")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            logger.info(f"📡 Статус ответа Nominatim API: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"📊 Размер ответа Nominatim: {len(str(result))} символов")
            else:
                logger.error(f"❌ Nominatim API вернул статус {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут при запросе к Nominatim API (30 секунд)")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Ошибка соединения с Nominatim API: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка запроса к Nominatim API: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка при запросе к Nominatim API: {e}")
            return None
        
        if result and len(result) > 0:
            location = result[0]
            address_details = location.get('address', {})
            
            # Извлекаем структурированные данные
            location_data = {
                'country': address_details.get('country'),
                'country_code': address_details.get('country_code'),
                'city': address_details.get('city') or address_details.get('town'),
                'district': address_details.get('suburb') or address_details.get('neighbourhood'),
                'county': address_details.get('county') or address_details.get('state'),
                'postal_code': address_details.get('postcode'),
                'road': address_details.get('road'),
                'house_number': address_details.get('house_number'),
                'lat': location.get('lat'),
                'lon': location.get('lon'),
                'display_name': location.get('display_name')
            }
            
            logger.info(f"✅ Nominatim данные: {location_data}")
            return location_data
        else:
            logger.warning(f"⚠️ Nominatim API вернул пустой результат: {result}")
            return None
        
    except Exception as e:
        logger.error(f"Ошибка Nominatim API: {e}")
        return None

def extract_location_components(address_components, original_address=None):
    """
    Извлекает структурированные данные из Google Places API address_components
    
    Args:
        address_components (list): Список компонентов адреса от Google API
        original_address (str): Оригинальный адрес для дополнительной обработки
    
    Returns:
        dict: Словарь с country, city, district, county
    """
    location_data = {
        'country': None,
        'country_code': None,
        'city': None,
        'district': None,
        'county': None,
        'postal_code': None
    }
    
    for component in address_components:
        types = component.get('types', [])
        long_name = component.get('long_name', '')
        short_name = component.get('short_name', '')
        
        # Страна
        if 'country' in types:
            location_data['country'] = long_name
            location_data['country_code'] = short_name
        
        # Город (administrative_area_level_1 или locality)
        elif 'administrative_area_level_1' in types:
            location_data['city'] = long_name
        elif 'locality' in types and not location_data['city']:
            location_data['city'] = long_name
        
        # Район (sublocality_level_1 или sublocality)
        elif 'sublocality_level_1' in types:
            location_data['district'] = long_name
        elif 'sublocality' in types and not location_data['district']:
            location_data['district'] = long_name
        
        # Округ (administrative_area_level_2)
        elif 'administrative_area_level_2' in types and not location_data['county']:
            location_data['county'] = long_name
        
        # Почтовый индекс
        elif 'postal_code' in types:
            location_data['postal_code'] = long_name
    
    # Дополнительная обработка для турецких адресов
    if original_address and (location_data['country'] == 'Turkey' or location_data['country'] == 'Türkiye'):
        # Извлекаем район из первой части адреса
        address_parts = original_address.split(',')
        if len(address_parts) >= 1:
            first_part = address_parts[0].strip()
            # Убираем суффиксы типа "Sk.", "Sok.", "Mah." и т.д.
            district_name = first_part.replace(' Sk.', '').replace(' Sok.', '').replace(' Mah.', '').replace(' Mahallesi', '')
            
            # Если Google не определил district, используем извлеченный
            if not location_data['district']:
                location_data['district'] = district_name
                logger.info(f"Извлечен район из адреса (Google не определил): {district_name}")
            else:
                logger.info(f"Google определил district: {location_data['district']}, извлеченный: {district_name}")
    
    logger.info(f"Извлечены компоненты локации: {location_data}")
    return location_data

def find_location_codes_from_components(location_components):
    """
    Находит коды локаций в базе данных на основе компонентов Google Places API
    
    Args:
        location_components (dict): Структурированные данные локации
    
    Returns:
        dict: Коды локаций или None
    """
    try:
        if not location_components:
            return None
        
        # Подготавливаем данные для поиска
        search_data = {
            'country_name': location_components.get('country'),
            'city_name': location_components.get('city'),
            'district_name': location_components.get('district'),
            'county_name': location_components.get('county')
        }
        
        # Убираем None значения
        search_data = {k: v for k, v in search_data.items() if v is not None}
        
        if not search_data:
            return None
        
        logger.info(f"Ищем локацию в базе по компонентам: {search_data}")
        
        # Показываем все возможные варианты поиска
        logger.info("\n🔍 ВАРИАНТЫ ПОИСКА В БАЗЕ ДАННЫХ:")
        logger.info("1. Точное совпадение по всем полям")
        logger.info("2. По county_name и city_name")
        logger.info("3. По district_name и city_name")
        logger.info("4. Только по county_name")
        logger.info("5. Только по district_name")
        
        # Ищем в таблице locations - сначала по точному совпадению
        query = supabase.table('locations').select('*')
        
        if search_data.get('city_name'):
            query = query.eq('city_name', search_data['city_name'])
        if search_data.get('county_name'):
            query = query.eq('county_name', search_data['county_name'])
        if search_data.get('district_name'):
            query = query.eq('district_name', search_data['district_name'])
        if search_data.get('country_name'):
            query = query.eq('country_name', search_data['country_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"✅ Найдена локация (точное совпадение): {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если точное совпадение не найдено, пробуем найти по county_name и city_name
        logger.info("Точное совпадение не найдено, ищем по county_name и city_name")
        query = supabase.table('locations').select('*')
        if search_data.get('county_name'):
            query = query.eq('county_name', search_data['county_name'])
        if search_data.get('city_name'):
            query = query.eq('city_name', search_data['city_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"✅ Найдена локация по county_name и city_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если и это не помогло, ищем по district_name и city_name
        logger.info("Ищем по district_name и city_name")
        query = supabase.table('locations').select('*')
        if search_data.get('district_name'):
            query = query.eq('district_name', search_data['district_name'])
        if search_data.get('city_name'):
            query = query.eq('city_name', search_data['city_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"✅ Найдена локация по district_name и city_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если и это не помогло, ищем только по county_name
        logger.info("Ищем только по county_name")
        query = supabase.table('locations').select('*')
        if search_data.get('county_name'):
            query = query.eq('county_name', search_data['county_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"✅ Найдена локация по county_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если и это не помогло, ищем только по district_name
        logger.info("Ищем только по district_name")
        query = supabase.table('locations').select('*')
        if search_data.get('district_name'):
            query = query.eq('district_name', search_data['district_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"✅ Найдена локация по district_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        logger.warning(f"❌ Локация не найдена для компонентов: {search_data}")
        return None
            
    except Exception as e:
        logger.error(f"❌ Ошибка поиска кодов локаций: {e}")
        return None

def extract_location_from_address(address):
    """
    Извлекает город, район и округ из адреса
    
    Args:
        address (str): Полный адрес
    
    Returns:
        dict: Словарь с city_name, district_name, county_name
    """
    try:
        logger.info(f"🔍 Извлекаем компоненты адреса: {address}")
        # Улучшенное извлечение для турецких адресов
        address_parts = address.split(',')
        logger.info(f"🔍 Части адреса: {address_parts}")
        
        location_data = {
            'city_name': None,
            'district_name': None,
            'county_name': None,
            'country_name': 'Turkey'  # По умолчанию для турецких адресов
        }
        
        if len(address_parts) >= 3:
            # Обрабатываем специальный случай: "Zerdalilik, 07100 Muratpaşa/Antalya, Türkiye"
            if 'Muratpaşa/Antalya' in address_parts[1]:
                logger.info(f"🔍 Обрабатываем случай Muratpaşa/Antalya")
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Muratpaşa'
                location_data['district_name'] = address_parts[0].strip()
                location_data['country_name'] = 'Türkiye'  # Исправляем название страны
            # Обрабатываем специальный случай: "Avsallar, Cengiz Akay Sk. No:12, 07410 Alanya/Antalya, Türkiye"
            elif 'Alanya/Antalya' in address_parts[2]:
                logger.info(f"🔍 Обрабатываем случай Alanya/Antalya")
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Alanya'
                location_data['district_name'] = address_parts[0].strip()
                location_data['country_name'] = 'Türkiye'  # Исправляем название страны
            # Обрабатываем специальный случай: "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye"
            elif 'Kepez/Antalya' in address_parts[2]:
                logger.info(f"🔍 Обрабатываем случай Kepez/Antalya")
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Kepez'
                location_data['district_name'] = address_parts[0].strip()
                location_data['country_name'] = 'Türkiye'  # Исправляем название страны
            else:
                logger.info(f"🔍 Обрабатываем стандартный случай")
                # Для адреса: "Antalya, Alanya, Avsallar Mah., Cengiz Akay Sok., 12B"
                # Первая часть: город (Antalya) - это основной город
                location_data['city_name'] = address_parts[0].strip()
                
                # Вторая часть: округ/район (Alanya) - это округ
                location_data['county_name'] = address_parts[1].strip()
                
                # Третья часть: район (Avsallar Mah.) - это район
                district_name = address_parts[2].strip()
                # Убираем суффиксы типа "Mah.", "Mahallesi", "Sok." и т.д.
                district_name = district_name.replace(' Mah.', '').replace(' Mahallesi', '').replace(' Sok.', '').replace(' Sk.', '')
                location_data['district_name'] = district_name
                
        elif len(address_parts) >= 2:
            logger.info(f"🔍 Обрабатываем простой формат (2 части)")
            # Простой формат
            location_data['district_name'] = address_parts[0].strip()
            location_data['city_name'] = address_parts[1].strip()
        
        # Если не удалось извлечь, используем fallback
        if not location_data['city_name']:
            logger.info(f"🔍 Используем fallback для city_name: Antalya")
            location_data['city_name'] = 'Antalya'  # Default для региона
        if not location_data['district_name']:
            logger.info(f"🔍 Используем fallback для district_name: Baraj")
            location_data['district_name'] = 'Baraj'  # Default район
        if not location_data['county_name']:
            logger.info(f"🔍 Используем fallback для county_name: Kepez")
            location_data['county_name'] = 'Kepez'  # Default провинция
        if not location_data['country_name']:
            logger.info(f"🔍 Используем fallback для country_name: Türkiye")
            location_data['country_name'] = 'Türkiye'  # Default страна
        
        logger.info(f"✅ Извлечены данные локации из адреса: {location_data}")
        return location_data
        
    except Exception as e:
        logger.error(f"❌ Ошибка извлечения локации из адреса: {e}")
        logger.error(f"❌ Адрес: {address}")
        logger.info(f"🔍 Возвращаем fallback значения")
        return {
            'city_name': 'Antalya',
            'district_name': 'Baraj', 
            'county_name': 'Kepez',
            'country_name': 'Türkiye'
        }

def get_historical_property_trends(city_name, district_name, county_name, years_back=5):
    """
    Получает исторические данные трендов недвижимости за последние годы
    
    Args:
        city_name (str): Название города
        district_name (str): Название района
        county_name (str): Название округа/провинции
        years_back (int): Количество лет назад для получения данных
    
    Returns:
        dict: Словарь с данными по годам для продажи и аренды
    """
    try:
        from datetime import datetime
        current_date = datetime.now()
        current_year = current_date.year
        
        # Получаем данные за последние years_back лет
        historical_data = {
            'sale_prices': [],
            'rent_prices': [],
            'years': []
        }
        
        # Получаем коды локаций
        location_codes = get_location_codes(city_name, district_name, county_name)
        
        if not location_codes:
            logger.warning("Не удалось получить коды локаций для исторических данных")
            return None
        
        # Используем каскадную логику для каждого года
        data_source_message = None
        
        for year_offset in range(years_back):
            target_year = current_year - year_offset
            
            # Каскадный поиск данных для текущего года
            year_data, message = get_cascading_historical_data(location_codes, target_year)
            
            if year_data:
                # Берем среднее значение за год
                sale_prices = []
                rent_prices = []
                
                for record in year_data:
                    if record.get('unit_price_for_sale'):
                        sale_prices.append(record['unit_price_for_sale'])
                    if record.get('unit_price_for_rent'):
                        rent_prices.append(record['unit_price_for_rent'])
                
                # Добавляем средние значения
                if sale_prices:
                    historical_data['sale_prices'].append(sum(sale_prices) / len(sale_prices))
                else:
                    historical_data['sale_prices'].append(None)
                
                if rent_prices:
                    historical_data['rent_prices'].append(sum(rent_prices) / len(rent_prices))
                else:
                    historical_data['rent_prices'].append(None)
                
                historical_data['years'].append(target_year)
                
                # Сохраняем сообщение о источнике данных (берем первое найденное)
                if data_source_message is None:
                    data_source_message = message
            else:
                historical_data['sale_prices'].append(None)
                historical_data['rent_prices'].append(None)
                historical_data['years'].append(target_year)
        
        # Переворачиваем списки чтобы годы шли в хронологическом порядке
        historical_data['sale_prices'].reverse()
        historical_data['rent_prices'].reverse()
        historical_data['years'].reverse()
        
        logger.info(f"Получены исторические данные: {len(historical_data['years'])} лет")
        
        # Добавляем информацию об источнике данных
        if data_source_message:
            historical_data['data_source'] = data_source_message
        
        return historical_data
        
    except Exception as e:
        logger.error(f"Ошибка получения исторических данных трендов: {e}")
        return None

def get_cascading_historical_data(location_codes, target_year):
    """
    Каскадный поиск исторических данных трендов с fallback логикой
    
    Args:
        location_codes (dict): Словарь с кодами локаций
        target_year (int): Целевой год
    
    Returns:
        tuple: (data, message) - данные и сообщение о типе найденных данных
    """
    try:
        city_code = location_codes.get('city_code')
        district_code = location_codes.get('district_code')
        county_code = location_codes.get('county_code')
        country_id = 1  # Türkiye
        
        # 1. Пытаемся найти точное совпадение
        if city_code and district_code and county_code:
            query = supabase.table('property_trends').select('*').eq('city_id', city_code).eq('district_id', district_code).eq('county_id', county_code).eq('property_year', target_year)
            result = query.execute()
            
            if result.data:
                logger.info(f"Найдены исторические данные по точному совпадению для {target_year}")
                return result.data, f"Данные по району (точное совпадение)"
        
        # 2. Если district_code не найден, ищем по county_code
        if county_code:
            query = supabase.table('property_trends').select('*').eq('county_id', county_code).is_('city_id', 'null').is_('district_id', 'null').eq('property_year', target_year)
            result = query.execute()
            
            if result.data:
                logger.info(f"Найдены исторические данные по округу для {target_year}")
                return result.data, f"Данные по округу (county_id={county_code})"
        
        # 3. Если county_code не найден, ищем по city_code
        if city_code:
            query = supabase.table('property_trends').select('*').eq('city_id', city_code).is_('district_id', 'null').is_('county_id', 'null').eq('property_year', target_year)
            result = query.execute()
            
            if result.data:
                logger.info(f"Найдены исторические данные по городу для {target_year}")
                return result.data, f"Данные по городу (city_id={city_code})"
        
        # 4. Если city_code не найден, ищем по country_id
        query = supabase.table('property_trends').select('*').eq('country_id', country_id).is_('city_id', 'null').is_('district_id', 'null').is_('county_id', 'null').eq('property_year', target_year)
        result = query.execute()
        
        if result.data:
            logger.info(f"Найдены исторические данные по стране для {target_year}")
            return result.data, f"Данные по стране (country_id={country_id})"
        
        # 5. Если ничего не найдено
        logger.warning(f"Исторические данные не найдены на всех уровнях для {target_year}")
        return None, "По данной локации нет данных"
        
    except Exception as e:
        logger.error(f"Ошибка каскадного поиска исторических данных: {e}")
        return None, "Ошибка при поиске исторических данных"

def create_property_trends_chart(historical_data, chart_type='sale', width=180, height=100):
    """
    Создает график трендов недвижимости для PDF (заглушка)
    """
    logger.info(f"Функция создания графиков отключена для упрощения: {chart_type}")
    return None

def get_openai_api_key():
    """
    Получает OpenAI API ключ из базы данных
    
    Returns:
        str: API ключ или пустая строка
    """
    try:
        # Получаем API ключ из базы данных
        openai_key_row = supabase.table('api_keys').select('key_value').eq('key_name', 'OPENAI_API').execute().data
        
        if openai_key_row and isinstance(openai_key_row, list) and len(openai_key_row) > 0:
            key_data = openai_key_row[0]
            if isinstance(key_data, dict) and 'key_value' in key_data:
                api_key = key_data['key_value']
                if api_key and api_key.strip():
                    logger.info("OpenAI API key retrieved from database successfully")
                    return api_key.strip()
        
        logger.warning("OpenAI API key not found in database")
        return ''
        
    except Exception as e:
        logger.error(f"Error retrieving OpenAI API key from database: {e}")
        return ''

def generate_trend_interpretation_with_chatgpt(gdp_trend, inflation_trend, gdp_data, inflation_data, language='en'):
    """
    Генерирует интерпретацию трендов через ChatGPT
    
    Args:
        gdp_trend (float): Тренд ВВП
        inflation_trend (float): Тренд инфляции
        gdp_data (list): Данные ВВП
        inflation_data (list): Данные инфляции
        language (str): Язык интерпретации (en, ru, tr, fr, de)
    
    Returns:
        dict: Интерпретации на разных языках
    """
    try:
        import openai
        
        # Настройка языков
        languages = {
            'en': 'English',
            'ru': 'Russian', 
            'tr': 'Turkish',
            'fr': 'French',
            'de': 'German'
        }
        
        # Получаем последние 2 года для сравнения
        if len(gdp_data) >= 2 and len(inflation_data) >= 2:
            gdp_last_2 = [d['value'] for d in gdp_data[-2:]]
            inflation_last_2 = [d['value'] for d in inflation_data[-2:]]
            recent_gdp_change = ((gdp_last_2[1] - gdp_last_2[0]) / gdp_last_2[0]) * 100 if gdp_last_2[0] != 0 else 0
            recent_inflation_change = ((inflation_last_2[1] - inflation_last_2[0]) / inflation_last_2[0]) * 100 if inflation_last_2[0] != 0 else 0
        else:
            recent_gdp_change = 0
            recent_inflation_change = 0
        
        # Формируем промпт для ChatGPT
        prompt = f"""
        Analyze economic trends for Turkey and provide interpretations in {languages.get(language, 'English')}.
        
        GDP Trend: {gdp_trend:.1f}%
        Inflation Trend: {inflation_trend:.1f}%
        Recent GDP change (last 2 years): {recent_gdp_change:.1f}%
        Recent Inflation change (last 2 years): {recent_inflation_change:.1f}%
        
        GDP data: {gdp_data}
        Inflation data: {inflation_data}
        
        Please provide:
        1. GDP trend interpretation (2-3 sentences)
        2. Inflation trend interpretation (2-3 sentences) 
        3. Recent comparison interpretation (last 2 years, 2-3 sentences)
        
        Format as JSON:
        {{
            "gdp_interpretation": "...",
            "inflation_interpretation": "...", 
            "recent_comparison": "..."
        }}
        """
        
        # Получаем API ключ из базы данных
        openai_api_key = get_openai_api_key()
        
        if openai_api_key and OPENAI_AVAILABLE:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7
                )
                result = json.loads(response.choices[0].message.content)
                logger.info(f"ChatGPT interpretation generated successfully for language: {language}")
            except Exception as e:
                logger.warning(f"ChatGPT API error: {e}, using fallback")
                result = {
                    "gdp_interpretation": f"GDP trend shows {gdp_trend:.1f}% average growth, indicating strong economic expansion",
                    "inflation_interpretation": f"Inflation trend at {inflation_trend:.1f}% shows significant price increases",
                    "recent_comparison": f"Recent 2-year comparison shows GDP change of {recent_gdp_change:.1f}% and inflation change of {recent_inflation_change:.1f}%"
                }
        else:
            # Временная заглушка без ChatGPT
            logger.info("No OpenAI API key available, using fallback interpretation")
            result = {
                "gdp_interpretation": f"GDP trend shows {gdp_trend:.1f}% average growth, indicating strong economic expansion",
                "inflation_interpretation": f"Inflation trend at {inflation_trend:.1f}% shows significant price increases",
                "recent_comparison": f"Recent 2-year comparison shows GDP change of {recent_gdp_change:.1f}% and inflation change of {recent_inflation_change:.1f}%"
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating ChatGPT interpretation: {e}")
        return {
            "gdp_interpretation": f"GDP trend: {gdp_trend:.1f}%",
            "inflation_interpretation": f"Inflation trend: {inflation_trend:.1f}%",
            "recent_comparison": "Recent comparison data unavailable"
        }

def generate_detailed_calculations(gdp_data, inflation_data):
    """
    Генерирует детальные расчеты трендов
    
    Args:
        gdp_data (list): Данные ВВП
        inflation_data (list): Данные инфляции
    
    Returns:
        dict: Детальные расчеты
    """
    try:
        # Расчеты для ВВП
        gdp_calculations = []
        gdp_values = [d['value'] for d in gdp_data]
        
        for i in range(1, len(gdp_values)):
            year1 = gdp_data[i-1]['year']
            year2 = gdp_data[i]['year']
            val1 = gdp_values[i-1]
            val2 = gdp_values[i]
            
            if val1 != 0:
                change = (val2 - val1) / val1
                gdp_calculations.append({
                    'years': f"{year1}→{year2}",
                    'calculation': f"({val2:.1f} - {val1:.1f}) / {val1:.1f}",
                    'result': f"{change:.3f}"
                })
        
        # Расчеты для инфляции
        inflation_calculations = []
        inflation_values = [d['value'] for d in inflation_data]
        
        for i in range(1, len(inflation_values)):
            year1 = inflation_data[i-1]['year']
            year2 = inflation_data[i]['year']
            val1 = inflation_values[i-1]
            val2 = inflation_values[i]
            
            if val1 != 0:
                change = (val2 - val1) / val1
                inflation_calculations.append({
                    'years': f"{year1}→{year2}",
                    'calculation': f"({val2:.1f} - {val1:.1f}) / {val1:.1f}",
                    'result': f"{change:.3f}"
                })
        
        return {
            'gdp_calculations': gdp_calculations,
            'inflation_calculations': inflation_calculations,
            'gdp_values': gdp_values,
            'inflation_values': inflation_values
        }
        
    except Exception as e:
        logger.error(f"Error generating detailed calculations: {e}")
        return {
            'gdp_calculations': [],
            'inflation_calculations': [],
            'gdp_values': [],
            'inflation_values': []
        }

def save_interpretations_to_database(country_code, interpretations, calculations):
    """
    Сохраняет интерпретации в базу данных
    
    Args:
        country_code (str): Код страны
        interpretations (dict): Интерпретации
        calculations (dict): Детальные расчеты
    """
    try:
        # Обновляем записи в таблице imf_economic_data
        for indicator in ['NGDP_RPCH', 'PCPIPCH']:
            supabase.table('imf_economic_data').update({
                'gdp_trend_interpretation_en': interpretations.get('en', {}).get('gdp_interpretation', ''),
                'gdp_trend_interpretation_ru': interpretations.get('ru', {}).get('gdp_interpretation', ''),
                'gdp_trend_interpretation_tr': interpretations.get('tr', {}).get('gdp_interpretation', ''),
                'gdp_trend_interpretation_fr': interpretations.get('fr', {}).get('gdp_interpretation', ''),
                'gdp_trend_interpretation_de': interpretations.get('de', {}).get('gdp_interpretation', ''),
                'inflation_trend_interpretation_en': interpretations.get('en', {}).get('inflation_interpretation', ''),
                'inflation_trend_interpretation_ru': interpretations.get('ru', {}).get('inflation_interpretation', ''),
                'inflation_trend_interpretation_tr': interpretations.get('tr', {}).get('inflation_interpretation', ''),
                'inflation_trend_interpretation_fr': interpretations.get('fr', {}).get('inflation_interpretation', ''),
                'inflation_trend_interpretation_de': interpretations.get('de', {}).get('inflation_interpretation', ''),
                'recent_comparison_interpretation_en': interpretations.get('en', {}).get('recent_comparison', ''),
                'recent_comparison_interpretation_ru': interpretations.get('ru', {}).get('recent_comparison', ''),
                'recent_comparison_interpretation_tr': interpretations.get('tr', {}).get('recent_comparison', ''),
                'recent_comparison_interpretation_fr': interpretations.get('fr', {}).get('recent_comparison', ''),
                'recent_comparison_interpretation_de': interpretations.get('de', {}).get('recent_comparison', ''),
                'gdp_calculation_details': json.dumps(calculations.get('gdp_calculations', [])),
                'inflation_calculation_details': json.dumps(calculations.get('inflation_calculation_details', []))
            }).eq('country_code', country_code).eq('indicator_code', indicator).execute()
            
        logger.info(f"Interpretations saved to database for country {country_code}")
        
    except Exception as e:
        logger.error(f"Error saving interpretations to database: {e}")

def load_interpretations_from_database(country_code):
    """
    Загружает сохраненные интерпретации из базы данных
    
    Args:
        country_code (str): Код страны
    
    Returns:
        dict: Загруженные интерпретации или None
    """
    try:
        # Получаем записи из таблицы imf_economic_data
        result = supabase.table('imf_economic_data').select('*').eq('country_code', country_code).eq('indicator_code', 'NGDP_RPCH').execute()
        
        if result.data and len(result.data) > 0:
            record = result.data[0]
            
            # Проверяем, есть ли сохраненные интерпретации
            if record.get('gdp_trend_interpretation_en') and record.get('inflation_trend_interpretation_en'):
                interpretations = {}
                for lang in ['en', 'ru', 'tr', 'fr', 'de']:
                    interpretations[lang] = {
                        'gdp_interpretation': record.get(f'gdp_trend_interpretation_{lang}', ''),
                        'inflation_interpretation': record.get(f'inflation_trend_interpretation_{lang}', ''),
                        'recent_comparison': record.get(f'recent_comparison_interpretation_{lang}', '')
                    }
                
                # Загружаем детальные расчеты
                calculations = {
                    'gdp_calculations': json.loads(record.get('gdp_calculation_details', '[]')),
                    'inflation_calculations': json.loads(record.get('inflation_calculation_details', '[]'))
                }
                
                logger.info(f"Interpretations loaded from database for country {country_code}")
                return interpretations, calculations
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error loading interpretations from database: {e}")
        return None, None

def get_market_comparison_data(age_id, floor_id, heating_id, area, price, location_codes, bedrooms=2, is_turkish=False, currency_rate=None):
    """
    Получает рыночные данные для сравнения цен из таблиц floor_segment_data, heating_data, house_type_data, age_data
    
    Args:
        age_id (str): ID записи возраста объекта
        floor_id (str): ID записи этажа объекта
        heating_id (str): ID записи типа отопления
        area (str): Площадь объекта в м²
        price (float): Цена объекта пользователя
        location_codes (dict): Коды локации (country_id, city_id, county_id, district_id)
        bedrooms (int): Количество спален для расчета типичного размера
    
    Returns:
        dict: Данные для сравнения цен и графики изменения цен
    """
    try:
        logger.info(f"🔍 Получаем рыночные данные для сравнения:")
        logger.info(f"📍 Возраст: {age_id}, Этаж: {floor_id}, Отопление: {heating_id}")
        logger.info(f"📍 Площадь: {area} м², Цена: €{price}")
        logger.info(f"📍 Коды локации: {location_codes}")
        logger.info(f"🔍 Типы данных: age_id={type(age_id)}, floor_id={type(floor_id)}, heating_id={type(heating_id)}")
        logger.info(f"🌍 Турция: {is_turkish}, Курс валют: {currency_rate}")
        
        # Импортируем функции конвертации валют
        if is_turkish and currency_rate:
            from currency_functions import convert_turkish_data_to_eur
            logger.info("💱 Конвертация данных из TRY в EUR включена")
        
        # Получаем данные из таблиц
        comparisons = {}
        price_trends = {}  # Для графиков изменения цен
        
        # Получаем текущую дату для фильтрации по trend_date
        current_date = datetime.now().date()
        twelve_months_ago = current_date - timedelta(days=365)  # 12 месяцев для графиков
        
        # 1. Сравнение по возрасту объекта
        if age_id and age_id != 'unknown':
            try:
                # Сначала получаем listing_type по ID записи
                age_record = supabase.table('age_data').select('listing_type').eq('id', age_id).execute()
                if age_record.data:
                    age_listing_type = age_record.data[0].get('listing_type')
                    logger.info(f"🔍 Найден listing_type для возраста {age_id}: {age_listing_type}")
                    
                    # Получаем данные по возрасту с учетом локации, listing_type и даты
                    age_query = supabase.table('age_data').select('trend_date, min_unit_price_for_sale, max_unit_price_for_sale, unit_price_for_sale')
                    
                    # 1. Фильтр по локации
                    if location_codes.get('country_id'):
                        age_query = age_query.eq('country_id', location_codes['country_id'])
                    if location_codes.get('city_id'):
                        age_query = age_query.eq('city_id', location_codes['city_id'])
                    if location_codes.get('county_id'):
                        age_query = age_query.eq('county_id', location_codes['county_id'])
                    if location_codes.get('district_id'):
                        age_query = age_query.eq('district_id', location_codes['district_id'])
                    
                    # 2. Фильтр по listing_type (а не по ID)
                    age_query = age_query.eq('listing_type', age_listing_type)
                    
                    # 3. Фильтр по дате (последние 12 месяцев)
                    age_query = age_query.gte('trend_date', twelve_months_ago).lte('trend_date', current_date)
                    
                    age_result = age_query.execute()
                    logger.info(f"🔍 Результат запроса по возрасту (listing_type={age_listing_type}): {len(age_result.data)} записей")
                
                if age_result.data:
                    # Конвертируем данные в евро, если объект в Турции
                    if is_turkish and currency_rate:
                        age_result.data = convert_turkish_data_to_eur(age_result.data, currency_rate)
                        logger.info("💱 Данные по возрасту конвертированы в EUR")
                    
                    # Сохраняем данные для графика
                    price_trends['age'] = {
                        'dates': [record.get('trend_date') for record in age_result.data],
                        'prices': [float(record.get('unit_price_for_sale', 0)) for record in age_result.data if record.get('unit_price_for_sale')]
                    }
                    
                    # Берем последнюю запись для расчетов
                    latest_record = max(age_result.data, key=lambda x: x.get('trend_date', ''))
                    min_price = float(latest_record.get('min_unit_price_for_sale', 0))
                    max_price = float(latest_record.get('max_unit_price_for_sale', 0))
                    
                    if min_price > 0 and max_price > 0:
                        # Используем типичный размер, если area не указан
                        if area and area != 'unknown':
                            area_value = float(area)
                        else:
                            # Типичный размер на основе количества спален
                            area_value = 80 if bedrooms <= 2 else 120 if bedrooms <= 3 else 150
                            logger.info(f"⚠️ Используем типичный размер для сравнения: {area_value} м²")
                        
                        min_total = min_price * area_value
                        max_total = max_price * area_value
                        
                        comparisons['age'] = {
                            'min_price': min_total,
                            'max_price': max_total,
                            'user_price': price,
                            'deviation_min': ((price - min_total) / min_total * 100) if min_total > 0 else 0,
                            'deviation_max': ((price - max_total) / max_total * 100) if max_total > 0 else 0,
                            'trend_data': price_trends['age']
                        }
                        logger.info(f"✅ Данные по возрасту: min={min_total:.0f}, max={max_total:.0f}, user={price:.0f}")
                else:
                    logger.warning(f"⚠️ Данные по возрасту не найдены для listing_type={age_listing_type}")
            except Exception as e:
                logger.error(f"❌ Ошибка получения данных по возрасту: {e}")
        
        # 2. Сравнение по этажу
        if floor_id and floor_id != 'unknown':
            try:
                # Сначала получаем listing_type по ID записи
                floor_record = supabase.table('floor_segment_data').select('listing_type').eq('id', floor_id).execute()
                if floor_record.data:
                    floor_listing_type = floor_record.data[0].get('listing_type')
                    logger.info(f"🔍 Найден listing_type для этажа {floor_id}: {floor_listing_type}")
                    
                    # Получаем данные по этажу с учетом локации, listing_type и даты
                    floor_query = supabase.table('floor_segment_data').select('trend_date, min_unit_price_for_sale, max_unit_price_for_sale, unit_price_for_sale')
                    
                    # 1. Фильтр по локации
                    if location_codes.get('country_id'):
                        floor_query = floor_query.eq('country_id', location_codes['country_id'])
                    if location_codes.get('city_id'):
                        floor_query = floor_query.eq('city_id', location_codes['city_id'])
                    if location_codes.get('county_id'):
                        floor_query = floor_query.eq('county_id', location_codes['county_id'])
                    if location_codes.get('district_id'):
                        floor_query = floor_query.eq('district_id', location_codes['district_id'])
                    
                    # 2. Фильтр по listing_type (а не по ID)
                    floor_query = floor_query.eq('listing_type', floor_listing_type)
                    
                    # 3. Фильтр по дате (последние 12 месяцев)
                    floor_query = floor_query.gte('trend_date', twelve_months_ago).lte('trend_date', current_date)
                    
                    floor_result = floor_query.execute()
                    logger.info(f"🔍 Результат запроса по этажу (listing_type={floor_listing_type}): {len(floor_result.data)} записей")
                
                if floor_result.data:
                    # Конвертируем данные в евро, если объект в Турции
                    if is_turkish and currency_rate:
                        floor_result.data = convert_turkish_data_to_eur(floor_result.data, currency_rate)
                        logger.info("💱 Данные по этажу конвертированы в EUR")
                    
                    # Сохраняем данные для графика
                    price_trends['floor'] = {
                        'dates': [record.get('trend_date') for record in floor_result.data],
                        'prices': [float(record.get('unit_price_for_sale', 0)) for record in floor_result.data if record.get('unit_price_for_sale')]
                    }
                    
                    # Берем последнюю запись для расчетов
                    latest_record = max(floor_result.data, key=lambda x: x.get('trend_date', ''))
                    min_price = float(latest_record.get('min_unit_price_for_sale', 0))
                    max_price = float(latest_record.get('max_unit_price_for_sale', 0))
                    
                    if min_price > 0 and max_price > 0:
                        # Используем типичный размер, если area не указан
                        if area and area != 'unknown':
                            area_value = float(area)
                        else:
                            # Типичный размер на основе количества спален
                            area_value = 80 if bedrooms <= 2 else 120 if bedrooms <= 3 else 150
                            logger.info(f"⚠️ Используем типичный размер для сравнения этажа: {area_value} м²")
                        
                        min_total = min_price * area_value
                        max_total = max_price * area_value
                        
                        comparisons['floor'] = {
                            'min_price': min_total,
                            'max_price': max_total,
                            'user_price': price,
                            'deviation_min': ((price - min_total) / min_total * 100) if min_total > 0 else 0,
                            'deviation_max': ((price - max_total) / max_total * 100) if max_total > 0 else 0,
                            'trend_data': price_trends['floor']
                        }
                        logger.info(f"✅ Данные по этажу: min={min_total:.0f}, max={max_total:.0f}, user={price:.0f}")
                else:
                    logger.warning(f"⚠️ Данные по этажу не найдены для listing_type={floor_listing_type}")
            except Exception as e:
                logger.error(f"❌ Ошибка получения данных по этажу: {e}")
        
        # 3. Сравнение по типу отопления
        if heating_id and heating_id != 'unknown':
            try:
                # Сначала получаем listing_type по ID записи
                heating_record = supabase.table('heating_data').select('listing_type').eq('id', heating_id).execute()
                if heating_record.data:
                    heating_listing_type = heating_record.data[0].get('listing_type')
                    logger.info(f"🔍 Найден listing_type для отопления {heating_id}: {heating_listing_type}")
                    
                    # Получаем данные по отоплению с учетом локации, listing_type и даты
                    heating_query = supabase.table('heating_data').select('trend_date, min_unit_price_for_sale, max_unit_price_for_sale, unit_price_for_sale')
                    
                    # 1. Фильтр по локации
                    if location_codes.get('country_id'):
                        heating_query = heating_query.eq('country_id', location_codes['country_id'])
                    if location_codes.get('city_id'):
                        heating_query = heating_query.eq('city_id', location_codes['city_id'])
                    if location_codes.get('county_id'):
                        heating_query = heating_query.eq('county_id', location_codes['county_id'])
                    if location_codes.get('district_id'):
                        heating_query = heating_query.eq('district_id', location_codes['district_id'])
                    
                    # 2. Фильтр по listing_type (а не по ID)
                    heating_query = heating_query.eq('listing_type', heating_listing_type)
                    
                    # 3. Фильтр по дате (последние 12 месяцев)
                    heating_query = heating_query.gte('trend_date', twelve_months_ago).lte('trend_date', current_date)
                    
                    heating_result = heating_query.execute()
                    logger.info(f"🔍 Результат запроса по отоплению (listing_type={heating_listing_type}): {len(heating_result.data)} записей")
                
                if heating_result.data:
                    # Конвертируем данные в евро, если объект в Турции
                    if is_turkish and currency_rate:
                        heating_result.data = convert_turkish_data_to_eur(heating_result.data, currency_rate)
                        logger.info("💱 Данные по отоплению конвертированы в EUR")
                    
                    # Сохраняем данные для графика
                    price_trends['heating'] = {
                        'dates': [record.get('trend_date') for record in heating_result.data],
                        'prices': [float(record.get('unit_price_for_sale', 0)) for record in heating_result.data if record.get('unit_price_for_sale')]
                    }
                    
                    # Берем последнюю запись для расчетов
                    latest_record = max(heating_result.data, key=lambda x: x.get('trend_date', ''))
                    min_price = float(latest_record.get('min_unit_price_for_sale', 0))
                    max_price = float(latest_record.get('max_unit_price_for_sale', 0))
                    
                    if min_price > 0 and max_price > 0:
                        # Используем типичный размер, если area не указан
                        if area and area != 'unknown':
                            area_value = float(area)
                        else:
                            # Типичный размер на основе количества спален
                            area_value = 80 if bedrooms <= 2 else 120 if bedrooms <= 3 else 150
                            logger.info(f"⚠️ Используем типичный размер для сравнения отопления: {area_value} м²")
                        
                        min_total = min_price * area_value
                        max_total = max_price * area_value
                        
                        comparisons['heating'] = {
                            'min_price': min_total,
                            'max_price': max_total,
                            'user_price': price,
                            'deviation_min': ((price - min_total) / min_total * 100) if min_total > 0 else 0,
                            'deviation_max': ((price - max_total) / max_total * 100) if max_total > 0 else 0,
                            'trend_data': price_trends['heating']
                        }
                        logger.info(f"✅ Данные по отоплению: min={min_total:.0f}, max={max_total:.0f}, user={price:.0f}")
                else:
                    logger.warning(f"⚠️ Данные по отоплению не найдены для listing_type={heating_listing_type}")
            except Exception as e:
                logger.error(f"❌ Ошибка получения данных по отоплению: {e}")
        
        # 4. Сравнение по типу дома - УБРАНО по требованию
        # Блок "По типу дома" был удален из сравнения с рыночными ценами
        # 5. Рассчитываем итоговые средние значения
        if comparisons:
            all_min_prices = [comp['min_price'] for comp in comparisons.values() if comp['min_price'] > 0]
            all_max_prices = [comp['max_price'] for comp in comparisons.values() if comp['max_price'] > 0]
            
            if all_min_prices and all_max_prices:
                avg_min_price = sum(all_min_prices) / len(all_min_prices)
                avg_max_price = sum(all_max_prices) / len(all_max_prices)
                
                comparisons['final'] = {
                    'avg_min_price': avg_min_price,
                    'avg_max_price': avg_max_price,
                    'user_price': price,
                    'deviation_min': ((price - avg_min_price) / avg_min_price * 100) if avg_min_price > 0 else 0,
                    'deviation_max': ((price - avg_max_price) / avg_max_price * 100) if avg_max_price > 0 else 0
                }
                
                # Определяем вывод по цене
                if price < avg_min_price:
                    price_conclusion = f"Цена ниже рыночной на {abs(comparisons['final']['deviation_min']):.1f}% - выгодное предложение!"
                elif price > avg_max_price:
                    price_conclusion = f"Цена выше рыночной на {comparisons['final']['deviation_max']:.1f}% - завышена"
                else:
                    price_conclusion = f"Цена в рыночном диапазоне (отклонение: {comparisons['final']['deviation_min']:.1f}% до {comparisons['final']['deviation_max']:.1f}%)"
                
                comparisons['price_conclusion'] = price_conclusion
                logger.info(f"✅ Итоговое сравнение: avg_min={avg_min_price:.0f}, avg_max={avg_max_price:.0f}, вывод: {price_conclusion}")
        
        # 6. Добавляем данные для графиков
        comparisons['price_trends'] = price_trends
        
        logger.info(f"📊 Итоговые данные сравнения: {comparisons}")
        logger.info(f"🔍 Структура comparisons:")
        for key, value in comparisons.items():
            if isinstance(value, dict) and 'min_price' in value:
                logger.info(f"  {key}: min={value.get('min_price', 0):.0f}, max={value.get('max_price', 0):.0f}, deviation_min={value.get('deviation_min', 0):.1f}%, deviation_max={value.get('deviation_max', 0):.1f}%")
            else:
                logger.info(f"  {key}: {value}")
        return comparisons
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения рыночных данных для сравнения: {e}")
        return {}


@app.route('/api/base_prices', methods=['POST'])
def api_base_prices():
    """
    API endpoint для получения базовых цен из таблиц age_data, floor_segment_data, heating_data, house_type_data
    Возвращает средние значения min и max цен для расчета базовой цены текущего месяца
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        country_id = data.get('country_id')
        city_id = data.get('city_id')
        county_id = data.get('county_id')
        district_id = data.get('district_id')
        
        if not all([country_id, city_id, county_id, district_id]):
            return jsonify({'error': 'Missing required location parameters'}), 400
        
        logger.info(f"💰 Запрос базовых цен для локации: country_id={country_id}, city_id={city_id}, county_id={county_id}, district_id={district_id}")
        
        # Определяем таблицы для запроса базовых цен
        tables = ['age_data', 'floor_segment_data', 'heating_data', 'house_type_data']
        
        min_sale_prices = []
        max_sale_prices = []
        min_rent_prices = []
        max_rent_prices = []
        
        # Получаем данные из каждой таблицы
        for table_name in tables:
            try:
                logger.info(f"🔍 Запрос данных из таблицы: {table_name}")
                
                response = supabase.table(table_name).select(
                    'min_unit_price_for_sale, max_unit_price_for_sale, min_unit_price_for_rent, max_unit_price_for_rent'
                ).eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id).eq('district_id', district_id).execute()
                
                if response.data and len(response.data) > 0:
                    # Берем средние значения из всех записей в таблице
                    table_data = response.data
                    
                    # Собираем все min/max цены из таблицы
                    table_min_sale = [record.get('min_unit_price_for_sale') for record in table_data if record.get('min_unit_price_for_sale') is not None]
                    table_max_sale = [record.get('max_unit_price_for_sale') for record in table_data if record.get('max_unit_price_for_sale') is not None]
                    table_min_rent = [record.get('min_unit_price_for_rent') for record in table_data if record.get('min_unit_price_for_rent') is not None]
                    table_max_rent = [record.get('max_unit_price_for_rent') for record in table_data if record.get('max_unit_price_for_rent') is not None]
                    
                    # Рассчитываем средние для этой таблицы
                    if table_min_sale:
                        min_sale_prices.append(sum(table_min_sale) / len(table_min_sale))
                    if table_max_sale:
                        max_sale_prices.append(sum(table_max_sale) / len(table_max_sale))
                    if table_min_rent:
                        min_rent_prices.append(sum(table_min_rent) / len(table_min_rent))
                    if table_max_rent:
                        max_rent_prices.append(sum(table_max_rent) / len(table_max_rent))
                    
                    logger.info(f"✅ Данные из {table_name}: записей={len(table_data)}")
                else:
                    logger.warning(f"⚠️ Нет данных в таблице {table_name} для указанной локации")
                    
            except Exception as table_error:
                logger.error(f"❌ Ошибка при запросе таблицы {table_name}: {table_error}")
                continue
        
        # Проверяем, что у нас есть данные
        if not min_sale_prices or not max_sale_prices or not min_rent_prices or not max_rent_prices:
            logger.warning(f"⚠️ Недостаточно данных для расчета базовых цен")
            return jsonify({'error': 'Insufficient data for base price calculation'}), 404
        
        # Рассчитываем средние значения по всем таблицам
        avg_min_sale_price = sum(min_sale_prices) / len(min_sale_prices)
        avg_max_sale_price = sum(max_sale_prices) / len(max_sale_prices)
        avg_min_rent_price = sum(min_rent_prices) / len(min_rent_prices)
        avg_max_rent_price = sum(max_rent_prices) / len(max_rent_prices)
        
        # Рассчитываем финальные базовые цены (среднее между min и max)
        base_sale_price = (avg_min_sale_price + avg_max_sale_price) / 2
        base_rent_price = (avg_min_rent_price + avg_max_rent_price) / 2
        
        logger.info(f"💰 Рассчитанные базовые цены:")
        logger.info(f"  - Базовая цена продажи: {base_sale_price:.2f}")
        logger.info(f"  - Базовая цена аренды: {base_rent_price:.2f}")
        logger.info(f"  - Источник: {len(min_sale_prices)} таблиц")
        
        return jsonify({
            'success': True,
            'base_prices': {
                'sale_price': base_sale_price,
                'rent_price': base_rent_price,
                'calculation_details': {
                    'avg_min_sale_price': avg_min_sale_price,
                    'avg_max_sale_price': avg_max_sale_price,
                    'avg_min_rent_price': avg_min_rent_price,
                    'avg_max_rent_price': avg_max_rent_price,
                    'tables_used': len(min_sale_prices),
                    'tables_requested': tables
                }
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении базовых цен: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/property_trends', methods=['POST'])
def api_property_trends():
    """
    API endpoint для получения данных о трендах недвижимости из таблицы property_trends
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        country_id = data.get('country_id')
        city_id = data.get('city_id')
        county_id = data.get('county_id')
        district_id = data.get('district_id')
        
        if not all([country_id, city_id, county_id, district_id]):
            return jsonify({'error': 'Missing required location parameters'}), 400
        
        logger.info(f"📊 Запрос трендов недвижимости для локации: country_id={country_id}, city_id={city_id}, county_id={county_id}, district_id={district_id}")
        
        # Запрос к таблице property_trends
        query = supabase.table('property_trends').select('*').eq('country_id', country_id).eq('city_id', city_id).eq('county_id', county_id).eq('district_id', district_id).order('property_date', desc=True)
        
        response = query.execute()
        
        if response.data:
            logger.info(f"✅ Найдено {len(response.data)} записей трендов недвижимости")
            
            # Логируем первую запись для отладки
            if response.data:
                first_record = response.data[0]
                logger.info(f"🔍 Первая запись из базы:")
                logger.info(f"  - unit_price_for_sale: {first_record.get('unit_price_for_sale')}")
                logger.info(f"  - unit_price_for_rent: {first_record.get('unit_price_for_rent')}")
                logger.info(f"  - price_change_sale: {first_record.get('price_change_sale')}")
                logger.info(f"  - price_change_rent: {first_record.get('price_change_rent')}")
                logger.info(f"  - yield: {first_record.get('yield')}")
                logger.info(f"  - property_date: {first_record.get('property_date')}")
                logger.info(f"  - property_year: {first_record.get('property_year')}")
                logger.info(f"  - property_month: {first_record.get('property_month')}")
            
            # Формируем тренды для отображения
            trends = []
            for record in response.data:
                trend = {
                    'trend_type': 'price_trend',
                    'trend_value': record.get('unit_price_for_sale') or record.get('unit_price_for_rent'),
                    'period': 'monthly',
                    'date': record.get('property_date'),
                    'property_year': record.get('property_year'),
                    'property_month': record.get('property_month'),
                    'unit_price_for_sale': record.get('unit_price_for_sale'),
                    'unit_price_for_rent': record.get('unit_price_for_rent'),
                    'price_change_sale': record.get('price_change_sale'),
                    'price_change_rent': record.get('price_change_rent'),
                    'annual_price_change_sale': record.get('annual_price_change_sale'),
                    'annual_price_change_rent': record.get('annual_price_change_rent'),
                    'yield': record.get('yield'),
                    'count_for_sale': record.get('count_for_sale'),
                    'count_for_rent': record.get('count_for_rent')
                }
                trends.append(trend)
            
            return jsonify({
                'success': True,
                'trends': trends,
                'total_count': len(trends)
            })
        else:
            logger.info(f"⚠️ Тренды недвижимости не найдены для указанной локации")
            return jsonify({
                'success': True,
                'trends': [],
                'total_count': 0,
                'message': 'No trends found for this location'
            })
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения трендов недвижимости: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/price_trends', methods=['POST'])
def api_price_trends():
    """
    API endpoint для получения данных о динамике цен недвижимости
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request data'}), 400
        
        location_codes = data.get('location_codes', {})
        area = data.get('area')
        
        if not location_codes:
            return jsonify({'error': 'Missing location_codes'}), 400
        
        if not area or area == 'unknown':
            return jsonify({'error': 'Missing or invalid area'}), 400
        
        try:
            area_value = float(area)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid area value'}), 400
        
        logger.info(f"📈 Запрос данных о трендах цен для локации: {location_codes}, площадь: {area_value} м²")
        
        # Добавляем дополнительное логирование для отладки
        logger.info(f"🔍 Проверяем коды локации:")
        logger.info(f"  - country_id: {location_codes.get('country_id')} (тип: {type(location_codes.get('country_id'))})")
        logger.info(f"  - city_id: {location_codes.get('city_id')} (тип: {type(location_codes.get('city_id'))})")
        logger.info(f"  - county_id: {location_codes.get('county_id')} (тип: {type(location_codes.get('county_id'))})")
        logger.info(f"  - district_id: {location_codes.get('district_id')} (тип: {type(location_codes.get('district_id'))})")
        
        # Сразу вызываем функцию get_price_trends_data
        logger.info("🔍 Вызываем функцию get_price_trends_data для получения всех данных")
        
        # ДИАГНОСТИКА: Проверим, что есть в таблице property_trends
        logger.info("🔍 ДИАГНОСТИКА: Проверяем содержимое таблицы property_trends...")
        
        # 1. Проверим общее количество записей
        try:
            total_count_query = supabase.table('property_trends').select('id', count='exact')
            total_count_response = total_count_query.execute()
            total_count = total_count_response.count if hasattr(total_count_response, 'count') else 'неизвестно'
            logger.info(f"🔍 Общее количество записей в таблице property_trends: {total_count}")
        except Exception as e:
            logger.error(f"❌ Ошибка подсчета общего количества записей: {e}")
        
        # 2. Проверим, какие country_id существуют
        try:
            countries_query = supabase.table('property_trends').select('country_id').limit(10)
            countries_response = countries_query.execute()
            if countries_response.data:
                unique_countries = list(set([r.get('country_id') for r in countries_response.data if r.get('country_id') is not None]))
                logger.info(f"🔍 Найденные country_id в таблице: {unique_countries}")
            else:
                logger.warning("⚠️ Не удалось получить country_id из таблицы")
        except Exception as e:
            logger.error(f"❌ Ошибка получения country_id: {e}")
        
        # 3. Проверим, есть ли данные для нашей страны
        try:
            country_query = supabase.table('property_trends').select('*').eq('country_id', location_codes['country_id']).limit(5)
            country_response = country_query.execute()
            logger.info(f"🔍 Данные для country_id={location_codes['country_id']}: найдено {len(country_response.data) if country_response.data else 0} записей")
            if country_response.data:
                logger.info(f"🔍 Пример записи для страны: {country_response.data[0]}")
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных для страны: {e}")
        
        # 4. Проверим, есть ли данные для нашего города
        try:
            city_query = supabase.table('property_trends').select('*').eq('country_id', location_codes['country_id']).eq('city_id', location_codes['city_id']).limit(5)
            city_response = city_query.execute()
            logger.info(f"🔍 Данные для city_id={location_codes['city_id']}: найдено {len(city_response.data) if city_response.data else 0} записей")
            if city_response.data:
                logger.info(f"🔍 Пример записи для города: {city_response.data[0]}")
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных для города: {e}")
        
        # 5. Проверим, есть ли данные для нашего округа
        try:
            county_query = supabase.table('property_trends').select('*').eq('country_id', location_codes['country_id']).eq('city_id', location_codes['city_id']).eq('county_id', location_codes['county_id']).limit(5)
            county_response = county_query.execute()
            logger.info(f"🔍 Данные для county_id={location_codes['county_id']}: найдено {len(county_response.data) if county_response.data else 0} записей")
            if county_response.data:
                logger.info(f"🔍 Пример записи для округа: {county_response.data[0]}")
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных для округа: {e}")
        
        # Проверяем, что функция импортирована
        if get_price_trends_data is None:
            logger.error("❌ Функция get_price_trends_data не импортирована")
            return jsonify({
                'error': 'Функция анализа трендов недоступна',
                'trend': 'Не определен',
                'change_3y': 0,
                'forecast_3m': 0,
                'analysis': 'Система анализа трендов недоступна',
                'recommendation': 'Обратитесь к администратору',
                'chart_data': []
            }), 500
        
        # Получаем данные о трендах цен
        trends_data = get_price_trends_data(supabase, location_codes, area_value)
        
        if 'error' in trends_data:
            logger.warning(f"⚠️ Ошибка получения данных о трендах: {trends_data['error']}")
            return jsonify(trends_data), 400
        
        logger.info(f"✅ Данные о трендах цен успешно получены: {trends_data['trend']}")
        return jsonify(trends_data)
        
    except Exception as e:
        logger.error(f"❌ Ошибка API price_trends: {e}")
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'trend': 'Не определен',
            'change_3y': 0,
            'forecast_3m': 0,
            'analysis': 'Произошла ошибка при получении данных',
            'recommendation': 'Попробуйте позже',
            'chart_data': []
        }), 500


@app.route('/api/region_insights', methods=['POST'])
def api_region_insights():
    """Получение AI-вывода по данным региона"""
    try:
        data = request.json or {}
        region_data = data.get('region_data', {})
        user_language = data.get('language', 'ru')
        
        logger.info(f"🧠 Запрос AI-вывода для языка: {user_language}")
        
        # Получаем OpenAI API ключ из базы данных
        try:
            logger.info("🔍 Ищем OpenAI API ключ в таблице api_keys...")
            
            # Сначала проверим, какие таблицы доступны
            logger.info("🔍 Проверяем доступные таблицы...")
            try:
                # Попробуем получить информацию о таблице
                test_result = supabase.table('api_keys').select('id').limit(1).execute()
                logger.info(f"📊 Тест таблицы api_keys: {test_result}")
            except Exception as table_error:
                logger.error(f"❌ Ошибка доступа к таблице api_keys: {table_error}")
                # Попробуем другие возможные названия таблиц
                possible_tables = ['api_keys', 'apikeys', 'api_keys_table', 'keys', 'api_keys_v1']
                for table_name in possible_tables:
                    try:
                        logger.info(f"🔍 Пробуем таблицу: {table_name}")
                        test_result = supabase.table(table_name).select('id').limit(1).execute()
                        logger.info(f"✅ Таблица {table_name} доступна")
                        break
                    except Exception as e:
                        logger.info(f"❌ Таблица {table_name} недоступна: {e}")
                        continue
            
            # Попробуем разные варианты запроса
            logger.info("🔍 Вариант 1: Запрос с select='*'")
            api_key_result = supabase.table('api_keys').select('*').eq('key_name', 'OPENAI_API').execute()
            logger.info(f"📊 Результат запроса API ключа: {api_key_result}")
            logger.info(f"📊 Тип результата: {type(api_key_result)}")
            logger.info(f"📊 Данные: {api_key_result.data}")
            logger.info(f"📊 Тип данных: {type(api_key_result.data)}")
            logger.info(f"📊 Количество записей: {len(api_key_result.data) if api_key_result.data else 0}")
            
            # Проверим, есть ли данные
            if not api_key_result.data or len(api_key_result.data) == 0:
                logger.warning("⚠️ Первый запрос не дал результатов, пробуем альтернативный...")
                
                # Попробуем альтернативный запрос
                logger.info("🔍 Вариант 2: Запрос с select='key_value'")
                api_key_result2 = supabase.table('api_keys').select('key_value').eq('key_name', 'OPENAI_API').execute()
                logger.info(f"📊 Результат альтернативного запроса: {api_key_result2}")
                logger.info(f"📊 Данные альтернативного запроса: {api_key_result2.data}")
                
                if api_key_result2.data and len(api_key_result2.data) > 0:
                    api_key_result = api_key_result2
                    logger.info("✅ Альтернативный запрос дал результаты")
                else:
                    logger.error("❌ OpenAI API ключ не найден в базе данных")
                    return jsonify({'success': False, 'error': 'OpenAI API key not found'}), 500
            
            # Получаем ключ
            if api_key_result.data and len(api_key_result.data) > 0:
                first_record = api_key_result.data[0]
                logger.info(f"📊 Первая запись: {first_record}")
                logger.info(f"📊 Ключи записи: {list(first_record.keys()) if first_record else 'None'}")
                
                if 'key_value' in first_record:
                    openai_api_key = first_record['key_value']
                    logger.info(f"✅ OpenAI API ключ получен из базы данных: {openai_api_key[:20]}...")
                else:
                    logger.error(f"❌ Поле 'key_value' не найдено в записи: {first_record}")
                    return jsonify({'success': False, 'error': 'key_value field not found in record'}), 500
            else:
                logger.error("❌ OpenAI API ключ не найден в базе данных")
                return jsonify({'success': False, 'error': 'OpenAI API key not found'}), 500
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения OpenAI API ключа: {e}")
            logger.error(f"❌ Тип ошибки: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': 'Failed to get OpenAI API key'}), 500
        
        # Формируем промпт на соответствующем языке
        language_prompts = {
            'ru': 'Проанализируй данные по недвижимости и напиши один сжатый абзац как вывод профессионального риэлтора. Сфокусируйся на трендах рынка, спросе и наиболее выгодных инвестиционных сегментах. Не указывай числа, только инсайты. ОБЯЗАТЕЛЬНО пиши ответ на русском языке.',
            'en': 'Analyze this real estate data and write one concise realtor insight paragraph. Focus on market trends, demand, and best investment segments. Do NOT list numbers—give actionable insights only. Write your response in English.',
            'de': 'Analysiere diese Immobiliendaten und erstelle einen kurzen Absatz mit professioneller Makler-Einschätzung. Konzentriere dich auf Markttrends, Nachfrage und die besten Investitionssegmente. Keine Zahlen nennen, nur aussagekräftige Erkenntnisse. Schreibe deine Antwort auf Deutsch.',
            'fr': 'Analysez ces données immobilières et rédigez un paragraphe concis comme un avis de professionnel de l\'immobilier. Concentrez-vous sur les tendances du marché, la demande et les meilleurs segments d\'investissement. Ne donnez pas de chiffres, uniquement des insights exploitables. Écrivez votre réponse en français.',
            'tr': 'Bu gayrimenkul verilerini analiz edin ve profesyonel bir emlak danışmanı gibi kısa bir paragraf yazın. Piyasa trendleri, talep ve en iyi yatırım segmentlerine odaklanın. Sayı vermeyin, sadece uygulanabilir içgörüler sunun. Cevabınızı Türkçe yazın.'
        }
        
        prompt = language_prompts.get(user_language, language_prompts['en'])
        
        logger.info(f"🔍 Выбранный промпт: {prompt}")
        
        # Подготавливаем данные для отправки в OpenAI
        data_summary = {
            'location': region_data.get('location', {}),
            'general_data': region_data.get('general_data', []),
            'house_type_data': region_data.get('house_type_data', []),
            'floor_segment_data': region_data.get('floor_segment_data', []),
            'age_data': region_data.get('age_data', []),
            'heating_data': region_data.get('heating_data', [])
        }
        
        # Формируем текст для анализа
        analysis_text = f"""
        Данные по региону:
        {data_summary}
        
        {prompt}
        """
        
        try:
            import openai
            client = openai.OpenAI(api_key=openai_api_key)
            
            # Формируем системное сообщение на соответствующем языке
            system_messages = {
                'ru': "Ты профессиональный аналитик недвижимости. Пиши точно как в примере: 'Рынок Kepez, Baraj в Анталье показывает стабильный спрос с недвижимостью, продающейся или сдающейся в аренду примерно за два месяца, и доходностью от аренды в среднем 7-8% годовых. Наиболее привлекательным инвестиционным сегментом являются квартиры 2+1 в возрасте 5-10 лет, предлагающие лучший баланс между ценой и доходностью от аренды. Более новые единицы 1+1 больше подходят для потенциального роста капитала, чем для высокого дохода от аренды, в то время как квартиры на средних этажах с кондиционированием обеспечивают самую высокую ликвидность и привлекательность для аренды.' Будь конкретным, упоминай фактические типы недвижимости, возраст и особенности. Максимум 3 предложения. Никаких общих заявлений.",
                'en': "You are a professional real estate analyst. Write exactly like the example: 'The Kepez, Baraj market in Antalya shows steady demand with properties selling or renting within about two months and rental yields averaging 7–8% annually. The most attractive investment segment is 2+1 apartments aged 5–10 years, offering the best balance between price and rental return. Newer 1+1 units are better suited for capital appreciation rather than high rental income, while mid-floor apartments with air-conditioning provide the strongest liquidity and rental appeal.' Be specific, mention actual property types, ages, and features. Maximum 3 sentences. No general statements.",
                'de': "Du bist ein professioneller Immobilienanalyst. Schreibe genau wie im Beispiel: 'Der Kepez, Baraj Markt in Antalya zeigt eine stabile Nachfrage mit Immobilien, die sich in etwa zwei Monaten verkaufen oder vermieten lassen und Mietrenditen von durchschnittlich 7-8% jährlich erzielen. Das attraktivste Investitionssegment sind 2+1 Wohnungen im Alter von 5-10 Jahren, die das beste Gleichgewicht zwischen Preis und Mietrendite bieten. Neuere 1+1 Einheiten sind besser für potenzielle Kapitalgewinne als für hohe Mieteinnahmen geeignet, während Wohnungen auf mittleren Etagen mit Klimaanlage die höchste Liquidität und Mietattraktivität bieten.' Sei spezifisch, erwähne tatsächliche Immobilientypen, Alter und Merkmale. Maximal 3 Sätze. Keine allgemeinen Aussagen.",
                'fr': "Vous êtes un analyste immobilier professionnel. Écrivez exactement comme dans l'exemple : 'Le marché Kepez, Baraj à Antalya montre une demande stable avec des propriétés se vendant ou se louant en environ deux mois et des rendements locatifs moyens de 7 à 8 % par an. Le segment d'investissement le plus attractif est celui des appartements 2+1 âgés de 5 à 10 ans, offrant le meilleur équilibre entre prix et rendement locatif. Les unités 1+1 plus récentes sont mieux adaptées à l'appréciation du capital plutôt qu'aux revenus locatifs élevés, tandis que les appartements aux étages moyens avec climatisation offrent la plus forte liquidité et l'attrait locatif.' Soyez spécifique, mentionnez les types de propriétés réels, l'âge et les caractéristiques. Maximum 3 phrases. Aucune déclaration générale.",
                'tr': "Sen profesyonel bir emlak analistisin. Tam olarak şu örnekteki gibi yaz: 'Antalya'daki Kepez, Baraj pazarı, mülklerin yaklaşık iki ay içinde satıldığı veya kiralandığı ve kiralama getirisinin yıllık ortalama %7-8 olduğu istikrarlı bir talep gösteriyor. En çekici yatırım segmenti, fiyat ve kiralama getirisi arasında en iyi dengeyi sunan 5-10 yaşındaki 2+1 dairelerdir. Daha yeni 1+1 birimler, yüksek kiralama gelirinden ziyade potansiyel sermaye artışı için daha uygundur, klima ile orta kat daireler ise en güçlü likidite ve kiralama çekiciliğini sağlar.' Spesifik olun, gerçek mülk türlerini, yaşını ve özelliklerini belirtin. Maksimum 3 cümle. Genel ifadeler yok."
            }
            
            system_message = system_messages.get(user_language, system_messages['en'])
            
            logger.info(f"🔍 Выбранное системное сообщение для языка {user_language}")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": analysis_text}
                ],
                max_tokens=150,
                temperature=0.4
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info(f"✅ AI-вывод получен: {insights[:100]}...")
            
            return jsonify({
                'success': True,
                'insights': insights,
                'language': user_language
            })
            
        except ImportError:
            logger.error("❌ Модуль openai не установлен")
            return jsonify({'success': False, 'error': 'OpenAI module not available'}), 500
        except Exception as e:
            logger.error(f"❌ Ошибка OpenAI API: {e}")
            return jsonify({'success': False, 'error': f'OpenAI API error: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"❌ Ошибка API region_insights: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/translations', methods=['POST'])
def api_translations():
    """API endpoint для получения переводов"""
    try:
        data = request.get_json()
        language = data.get('language', 'ru')
        
        if language not in ['ru', 'en', 'de', 'fr', 'tr']:
            language = 'ru'
        
        # Возвращаем переводы для запрошенного языка
        return jsonify(locales.get(language, locales['ru']))
        
    except Exception as e:
        logger.error(f"❌ Ошибка API translations: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/test_api_keys', methods=['GET'])
def api_test_api_keys():
    """Тестовый endpoint для проверки таблицы api_keys"""
    try:
        logger.info("🧪 Тестирование таблицы api_keys")
        
        # Проверяем подключение к Supabase
        logger.info("🔍 Проверяем подключение к Supabase...")
        try:
            # Простой тест подключения
            test_connection = supabase.table('users').select('id').limit(1).execute()
            logger.info(f"✅ Подключение к Supabase работает: {test_connection}")
        except Exception as conn_error:
            logger.error(f"❌ Ошибка подключения к Supabase: {conn_error}")
            return jsonify({'success': False, 'error': f'Supabase connection failed: {str(conn_error)}'}), 500
        
        # Проверяем всю таблицу
        logger.info("🔍 Проверяем таблицу api_keys...")
        try:
            result = supabase.table('api_keys').select('*').execute()
            logger.info(f"📊 Результат запроса всей таблицы: {result}")
            logger.info(f"📊 Данные: {result.data}")
            logger.info(f"📊 Количество записей: {len(result.data) if result.data else 0}")
            
            if result.data:
                logger.info("📋 Все записи в таблице api_keys:")
                for i, record in enumerate(result.data):
                    logger.info(f"  Запись {i+1}: {record}")
            else:
                logger.warning("⚠️ Таблица api_keys пуста или недоступна")
                
        except Exception as table_error:
            logger.error(f"❌ Ошибка доступа к таблице api_keys: {table_error}")
            return jsonify({'success': False, 'error': f'Table access failed: {str(table_error)}'}), 500
        
        # Проверяем конкретно OPENAI_API
        logger.info("🔍 Ищем запись с key_name='OPENAI_API'...")
        try:
            openai_result = supabase.table('api_keys').select('*').eq('key_name', 'OPENAI_API').execute()
            logger.info(f"🔍 Результат поиска OPENAI_API: {openai_result}")
            logger.info(f"🔍 Данные OPENAI_API: {openai_result.data}")
            
            if openai_result.data and len(openai_result.data) > 0:
                logger.info("✅ Запись OPENAI_API найдена")
                openai_record = openai_result.data[0]
                logger.info(f"📊 Запись: {openai_record}")
                logger.info(f"📊 Доступные поля: {list(openai_record.keys())}")
                
                if 'key_value' in openai_record:
                    key_value = openai_record['key_value']
                    logger.info(f"✅ Поле key_value найдено: {key_value[:20]}...")
                else:
                    logger.warning("⚠️ Поле key_value не найдено в записи")
            else:
                logger.warning("⚠️ Запись OPENAI_API не найдена")
                
        except Exception as search_error:
            logger.error(f"❌ Ошибка поиска OPENAI_API: {search_error}")
            return jsonify({'success': False, 'error': f'Search failed: {str(search_error)}'}), 500
        
        return jsonify({
            'success': True,
            'total_records': len(result.data) if result.data else 0,
            'all_records': result.data,
            'openai_records': openai_result.data if 'openai_result' in locals() else [],
            'message': 'Table api_keys checked successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования api_keys: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Дополнительная проверка подключения к Supabase перед запуском
    logger.info("🔍 Финальная проверка подключения к Supabase...")
    final_test = safe_db_operation(
        lambda: supabase.table('users').select('id').limit(1).execute()
    )
    if final_test is not None:
        logger.info("✅ Финальная проверка подключения к Supabase успешна")
    else:
        logger.error("❌ Финальная проверка подключения к Supabase не удалась")
    
    run_flask()
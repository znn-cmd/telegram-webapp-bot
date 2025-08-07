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
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Используем неинтерактивный бэкенд
import io
import base64
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

# Условный импорт openai
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. ChatGPT features will use fallback mode.")

# Инициализация Flask приложения
app = Flask(__name__)

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
supabase: Client = create_client(supabase_url, supabase_key)

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN должен быть задан в переменных окружения!")

# URL вашего WebApp (замените на ваш домен после деплоя)
WEBAPP_URL = "https://aaadvisor-zaicevn.amvera.io/webapp"

# Google Maps API ключ
GOOGLE_MAPS_API_KEY = "AIzaSyBrDkDpNKNAIyY147MQ78hchBkeyCAxhEw"

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

# Flask маршруты для WebApp
@app.route('/webapp')
def webapp():
    """Главное меню WebApp"""
    with open('webapp_main.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_report')
def webapp_report():
    """Страница создания отчета"""
    with open('webapp_real_data.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_saved')
def webapp_saved():
    """Страница сохраненных отчетов"""
    with open('webapp_saved.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_help')
def webapp_help():
    with open('webapp_help.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_profile')
def webapp_profile():
    with open('webapp_profile.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_stats')
def webapp_stats():
    with open('webapp_stats.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_profile_data')
def webapp_profile_data():
    with open('webapp_profile_data.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/webapp_balance')
def webapp_balance():
    with open('webapp_balance.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья приложения"""
    return jsonify({"status": "ok", "message": "Telegram WebApp Bot is running"})

@app.route('/logo-sqv.png')
def serve_logo():
    return send_from_directory('.', 'logo-sqv.png')

@app.route('/logo-flt.png')
def serve_logo_flt():
    return send_from_directory('.', 'logo-flt.png')

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
    user_result = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
    user = user_result.data[0] if user_result.data else None
    if user is not None:
        lang = user.get('language') or (language_code[:2] if language_code[:2] in locales else 'en')
        return jsonify({
            'exists': True,
            'is_new_user': False,
            'language': user.get('language') or lang,
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
        })
    else:
        # Новый пользователь
        lang = language_code[:2] if language_code[:2] in locales else 'en'
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
            'language': lang,
            'balance': 0,
            'invite_code': invite_code
        }
        if referal:
            user_data['referal'] = referal
        supabase.table('users').insert(user_data).execute()
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
            'invite_code': invite_code
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
    for field in ['first_name', 'last_name', 'phone', 'email', 'website', 'company', 'position', 'about_me']:
        if field in data:
            update_data[field] = data[field]
    
    try:
        if update_data:
            # Обновляем данные пользователя
            supabase.table('users').update(update_data).eq('telegram_id', telegram_id).execute()
        
        # Получаем обновленные данные
        result = supabase.table('users').select('first_name, last_name, photo_url, phone, email, website, company, position, about_me').eq('telegram_id', telegram_id).execute()
        if result.data and len(result.data) > 0:
            return jsonify({'success': True, 'profile': result.data[0]})
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error updating/fetching user profile: {e}")
        return jsonify({'error': 'Internal error'}), 500

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
    # Обновляем язык пользователя
    supabase.table('users').update({'language': language}).eq('telegram_id', telegram_id).execute()
    return jsonify({'ok': True})

@app.route('/api/menu', methods=['POST'])
def api_menu():
    data = request.json or {}
    language = data.get('language', 'en')
    if language not in locales:
        language = 'en'
    return jsonify({'menu': locales[language]['menu']})

@app.route('/api/check_admin_status', methods=['POST'])
def api_check_admin_status():
    """Проверка статуса администратора пользователя"""
    data = request.json or {}
    telegram_id_raw = data.get('telegram_id')
    logger.info(f"🔍 Проверка статуса админа для telegram_id: {telegram_id_raw}")
    
    if telegram_id_raw is None:
        logger.error("❌ telegram_id не предоставлен")
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        telegram_id = int(telegram_id_raw)
    except (TypeError, ValueError):
        logger.error(f"❌ Неверный формат telegram_id: {telegram_id_raw}")
        return jsonify({'error': 'Invalid telegram_id'}), 400
    
    try:
        # Проверяем пользователя в базе
        logger.info(f"🔍 Поиск пользователя в базе для telegram_id: {telegram_id}")
        user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
        
        logger.info(f"📊 Результат поиска: {len(user_result.data) if user_result.data else 0} записей")
        
        if user_result.data and len(user_result.data) > 0:
            user_status = user_result.data[0].get('user_status')
            is_admin = user_status == 'admin' if user_status else False
            logger.info(f"👤 Пользователь найден: user_status={user_status}, is_admin={is_admin}")
            logger.info(f"📋 Проверяем user_status='{user_status}' == 'admin' = {user_status == 'admin'}")
            return jsonify({
                'success': True,
                'is_admin': is_admin,
                'user_status': user_status
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
    if not address:
        logger.error("❌ Адрес не предоставлен в запросе")
        return jsonify({'error': 'Address required'}), 400
    
    logger.info(f"🔍 Начинаем геокодинг адреса: {address}")
    
    try:
        # Запрос к Google Maps Geocoding API
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY
        }
        
        logger.info(f"🌐 Отправляем запрос к Google Maps API")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"❌ Google Maps API вернул код {response.status_code}: {response.text}")
            return jsonify({'error': 'Google Maps API error'}), 500
        
        result = response.json()
        logger.info(f"📊 Google Maps API статус: {result.get('status')}")
        
        if result['status'] == 'OK' and result['results']:
            location = result['results'][0]['geometry']['location']
            formatted_address = result['results'][0]['formatted_address']
            
            logger.info(f"✅ Адрес найден: {formatted_address}")
            logger.info(f"📍 Координаты: {location['lat']}, {location['lng']}")
            
            # Извлекаем структурированные данные из Google Places API
            logger.info("🔍 Извлекаем компоненты адреса...")
            location_components = extract_location_components(result['results'][0]['address_components'], address)
            
            # Дополнительно получаем данные через Nominatim
            logger.info("🌐 Получаем дополнительные данные через Nominatim...")
            nominatim_data = get_nominatim_location(address)
            
            # Объединяем данные Google и Nominatim
            if nominatim_data:
                logger.info("✅ Данные Nominatim получены")
                # Если Google не определил district, используем данные Nominatim
                if not location_components.get('district') and nominatim_data.get('district'):
                    location_components['district'] = nominatim_data['district']
                    logger.info(f"Добавлен district из Nominatim: {nominatim_data['district']}")
                
                # Если Google не определил county, используем данные Nominatim
                if not location_components.get('county') and nominatim_data.get('county'):
                    location_components['county'] = nominatim_data['county']
                    logger.info(f"Добавлен county из Nominatim: {nominatim_data['county']}")
                
                # Сохраняем данные Nominatim для отображения
                location_components['nominatim_data'] = nominatim_data
            else:
                logger.warning("⚠️ Данные Nominatim не получены")
            
            # Пытаемся найти коды локаций в базе данных
            logger.info("🔍 Ищем коды локаций в базе данных...")
            location_codes = find_location_codes_from_components(location_components)
            
            if location_codes:
                logger.info(f"✅ Найдены коды локаций: {location_codes}")
            else:
                logger.warning("⚠️ Коды локаций не найдены")
            
            logger.info("✅ Геокодинг завершен успешно")
            return jsonify({
                'success': True,
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': formatted_address,
                'location_components': location_components,
                'location_codes': location_codes
            })
        else:
            logger.error(f"❌ Google Maps API не нашел адрес. Статус: {result.get('status')}")
            return jsonify({
                'success': False,
                'error': f"Address not found. Google status: {result.get('status')}"
            })
    except requests.exceptions.Timeout:
        logger.error("❌ Таймаут при запросе к Google Maps API")
        return jsonify({'error': 'Google Maps API timeout'}), 500
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка сети при запросе к Google Maps API: {e}")
        return jsonify({'error': 'Network error'}), 500
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка в геокодинге: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Geocoding service error'}), 500

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
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        logger.info(f"🔍 Генерация отчета для адреса: {address}")
        logger.info(f"📋 Полученные коды локаций: {location_codes}")
        
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
        
        # Проверяем статус администратора
        is_admin = False
        if telegram_id:
            try:
                user_result = supabase.table('users').select('user_status').eq('telegram_id', telegram_id).execute()
                if user_result.data and len(user_result.data) > 0:
                    user_status = user_result.data[0].get('user_status')
                    is_admin = user_status == 'admin' if user_status else False
            except Exception as e:
                logger.error(f"Error checking admin status: {e}")
        
        # Импортируем функции для работы с валютой
        from currency_functions import get_currency_rate_for_date, convert_turkish_data_to_eur, is_turkish_location
        
        # Проверяем, является ли локация турецкой и конвертируем данные если нужно
        is_turkish = is_turkish_location(location_components) if location_components else False
        currency_rate = None
        
        if is_turkish:
            logger.info(f"🇹🇷 Турецкая локация обнаружена, получаем курс валюты")
            currency_rate = get_currency_rate_for_date()
            if currency_rate and market_data:
                logger.info(f"💱 Конвертируем турецкие данные в EUR")
                market_data = convert_turkish_data_to_eur(market_data, currency_rate)
        
        # Формируем отчёт в текстовом формате для отображения
        report_text = format_simple_report(address, bedrooms, price, location_codes, language, market_data, is_admin, currency_rate, is_turkish)
        
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
                'market_data': market_data,
                'is_turkish': is_turkish,
                'currency_rate': currency_rate,
                'report_text': report_text
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации отчета: {e}")
        return jsonify({'error': str(e)}), 500

def get_location_codes_from_address(address):
    """Получает коды локаций из таблицы locations по адресу"""
    try:
        # Извлекаем компоненты адреса
        location_info = extract_location_from_address(address)
        if not location_info:
            return None
        
        # Исправляем названия для соответствия с базой данных
        if location_info.get('country_name') == 'Turkey':
            location_info['country_name'] = 'Türkiye'
        
        logger.info(f"Ищем локацию в базе: {location_info}")
        
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
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            logger.info(f"Найдена локация: {location}")
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
        logger.warning(f"Локация не найдена для: {location_info}")
        return None
            
    except Exception as e:
        logger.error(f"Error getting location codes: {e}")
        return None

def format_simple_report(address, bedrooms, price, location_codes, language='en', market_data=None, is_admin=False, currency_rate=None, is_turkish=False):
    """Форматирование простого отчёта с кодами локаций и данными рынка"""
    
    # Форматируем цену
    def format_price(price):
        return f"€{price:.2f}".replace('.00', '').replace('.', ',')
    
    # Получаем текущую дату
    from datetime import datetime
    current_date = datetime.now().strftime('%d.%m.%Y')
    
    # Формируем отчёт
    report_lines = [
        f"Анализ рынка в радиусе 5 км:",
        "",
    ]
    
    # Добавляем информацию о дате формирования отчета и курсе валюты для турецких локаций
    if is_turkish and currency_rate:
        try_rate = currency_rate.get('try', 0)
        report_lines.extend([
            f"📅 Дата формирования отчета: {current_date}",
            f"💱 Курс валюты (EUR/TRY): 1 EUR = {try_rate:.6f} TRY",
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
    
    report_lines.append("")
    
    # Добавляем новые разделы отчета
    if market_data:
        # Общий тренд (из таблицы general_data)
        if market_data.get('general_data'):
            general = market_data['general_data']
            report_lines.extend([
                "=== ОБЩИЙ ТРЕНД ===",
                "",
                f"Средняя цена продажи, м²: €{general.get('unit_price_for_sale', 'н/д')}",
                f"Минимальная цена продажи, м²: €{general.get('min_unit_price_for_sale', 'н/д')}",
                f"Максимальная цена продажи: €{general.get('max_unit_price_for_sale', 'н/д')}",
                f"Средняя площадь продажи: {general.get('comparable_area_for_sale', 'н/д')} м²",
                f"Количество объектов на продажу: {general.get('count_for_sale', 'н/д')}",
                "",
                f"Средняя цена аренды, м²: €{general.get('unit_price_for_rent', 'н/д')}",
                f"Минимальная цена аренды, м²: €{general.get('min_unit_price_for_rent', 'н/д')}",
                f"Максимальная цена аренды, м²: €{general.get('max_unit_price_for_rent', 'н/д')}",
                f"Средняя площадь аренды: {general.get('comparable_area_for_rent', 'н/д')} м²",
                f"Количество объектов в аренду: {general.get('count_for_rent', 'н/д')}",
                "",
                f"Цена для продажи, средняя: €{general.get('price_for_sale', 'н/д')}",
                f"Цена для аренды, средняя: €{general.get('price_for_rent', 'н/д')}",
                f"Средний возраст объекта для продажи: {general.get('average_age_for_sale', 'н/д')} лет",
                f"Средний возраст объекта для аренды: {general.get('average_age_for_rent', 'н/д')} лет",
                f"Период листинга для продажи: {general.get('listing_period_for_sale', 'н/д')} дней",
                f"Период листинга для аренды: {general.get('listing_period_for_rent', 'н/д')} дней",
                f"Доходность: {general.get('yield', 'н/д')}%",
                "",
            ])
            
            # Добавляем дату тренда только для администраторов
            if is_admin:
                report_lines.append(f"Дата тренда: {general.get('trend_date', 'н/д')}")
                report_lines.append("")
    
        # Тренд по количеству спален (из таблицы house_type_data)
        if market_data.get('house_type_data'):
            house_type_data = market_data['house_type_data']
            report_lines.extend([
                "=== ТРЕНД ПО КОЛИЧЕСТВУ СПАЛЕН ===",
            ])
            
            # Если house_type_data это список (несколько записей с разными listing_type)
            if isinstance(house_type_data, list):
                for record in house_type_data:
                    listing_type = record.get('listing_type', 'н/д')
                    report_lines.extend([
                        f"--- Количество спален: {listing_type} ---",
                        f"Средняя цена продажи: €{record.get('unit_price_for_sale', 'н/д')}",
                        f"Минимальная цена продажи: €{record.get('min_unit_price_for_sale', 'н/д')}",
                        f"Максимальная цена продажи: €{record.get('max_unit_price_for_sale', 'н/д')}",
                        f"Сопоставимая площадь для продажи: {record.get('comparable_area_for_sale', 'н/д')} м²",
                        f"Количество объектов на продажу: {record.get('count_for_sale', 'н/д')}",
                        f"Средняя цена аренды: €{record.get('unit_price_for_rent', 'н/д')}",
                        f"Минимальная цена аренды: €{record.get('min_unit_price_for_rent', 'н/д')}",
                        f"Максимальная цена аренды: €{record.get('max_unit_price_for_rent', 'н/д')}",
                        f"Сопоставимая площадь для аренды: {record.get('comparable_area_for_rent', 'н/д')} м²",
                        f"Количество объектов в аренду: {record.get('count_for_rent', 'н/д')}",
                        f"Цена для продажи: €{record.get('price_for_sale', 'н/д')}",
                        f"Цена для аренды: €{record.get('price_for_rent', 'н/д')}",
                        f"Средний возраст объекта для продажи: {record.get('average_age_for_sale', 'н/д')} лет",
                        f"Средний возраст объекта для аренды: {record.get('average_age_for_rent', 'н/д')} лет",
                        f"Период листинга для продажи: {record.get('listing_period_for_sale', 'н/д')} дней",
                        f"Период листинга для аренды: {record.get('listing_period_for_rent', 'н/д')} дней",
                        f"Доходность: {record.get('yield', 'н/д')}%",
                        "",
                    ])
            else:
                # Если это одна запись
                listing_type = house_type_data.get('listing_type', 'н/д')
                report_lines.extend([
                    f"--- Количество спален: {listing_type} ---",
                    f"Средняя цена продажи: €{house_type_data.get('unit_price_for_sale', 'н/д')}",
                    f"Минимальная цена продажи: €{house_type_data.get('min_unit_price_for_sale', 'н/д')}",
                    f"Максимальная цена продажи: €{house_type_data.get('max_unit_price_for_sale', 'н/д')}",
                    f"Сопоставимая площадь для продажи: {house_type_data.get('comparable_area_for_sale', 'н/д')} м²",
                    f"Количество объектов на продажу: {house_type_data.get('count_for_sale', 'н/д')}",
                    f"Средняя цена аренды: €{house_type_data.get('unit_price_for_rent', 'н/д')}",
                    f"Минимальная цена аренды: €{house_type_data.get('min_unit_price_for_rent', 'н/д')}",
                    f"Максимальная цена аренды: €{house_type_data.get('max_unit_price_for_rent', 'н/д')}",
                    f"Сопоставимая площадь для аренды: {house_type_data.get('comparable_area_for_rent', 'н/д')} м²",
                    f"Количество объектов в аренду: {house_type_data.get('count_for_rent', 'н/д')}",
                    f"Цена для продажи: €{house_type_data.get('price_for_sale', 'н/д')}",
                    f"Цена для аренды: €{house_type_data.get('price_for_rent', 'н/d')}",
                    f"Средний возраст объекта для продажи: {house_type_data.get('average_age_for_sale', 'н/д')} лет",
                    f"Средний возраст объекта для аренды: {house_type_data.get('average_age_for_rent', 'н/d')} лет",
                    f"Период листинга для продажи: {house_type_data.get('listing_period_for_sale', 'н/d')} дней",
                    f"Период листинга для аренды: {house_type_data.get('listing_period_for_rent', 'н/d')} дней",
                    f"Доходность: {house_type_data.get('yield', 'н/d')}%",
                    "",
                ])
        
        # Тренд по возрасту объекта (из таблицы age_data)
        if market_data.get('age_data'):
            age_data = market_data['age_data']
            report_lines.extend([
                "=== ТРЕНД ПО ВОЗРАСТУ ОБЪЕКТА ===",
            ])
            
            # Если age_data это список (несколько записей с разными listing_type)
            if isinstance(age_data, list):
                for record in age_data:
                    listing_type = record.get('listing_type', 'н/д')
                    report_lines.extend([
                        f"--- Возраст здания: {listing_type} ---",
                        f"Средний возраст объектов на продажу: {record.get('average_age_for_sale', 'н/д')} лет",
                        f"Средний возраст объектов в аренду: {record.get('average_age_for_rent', 'н/д')} лет",
                        f"Средняя цена продажи: €{record.get('unit_price_for_sale', 'н/д')}",
                        f"Минимальная цена продажи: €{record.get('min_unit_price_for_sale', 'н/д')}",
                        f"Максимальная цена продажи: €{record.get('max_unit_price_for_sale', 'н/д')}",
                        f"Сопоставимая площадь для продажи: {record.get('comparable_area_for_sale', 'н/д')} м²",
                        f"Количество объектов на продажу: {record.get('count_for_sale', 'н/д')}",
                        f"Средняя цена аренды: €{record.get('unit_price_for_rent', 'н/д')}",
                        f"Минимальная цена аренды: €{record.get('min_unit_price_for_rent', 'н/д')}",
                        f"Максимальная цена аренды: €{record.get('max_unit_price_for_rent', 'н/д')}",
                        f"Сопоставимая площадь для аренды: {record.get('comparable_area_for_rent', 'н/д')} м²",
                        f"Количество объектов в аренду: {record.get('count_for_rent', 'н/d')}",
                        f"Цена для продажи: €{record.get('price_for_sale', 'н/d')}",
                        f"Цена для аренды: €{record.get('price_for_rent', 'н/d')}",
                        f"Период листинга для продажи: {record.get('listing_period_for_sale', 'н/d')} дней",
                        f"Период листинга для аренды: {record.get('listing_period_for_rent', 'н/d')} дней",
                        f"Доходность: {record.get('yield', 'н/d')}%",
                        "",
                    ])
            else:
                # Если это одна запись
                listing_type = age_data.get('listing_type', 'н/д')
                report_lines.extend([
                    f"--- Возраст здания: {listing_type} ---",
                    f"Средний возраст объектов на продажу: {age_data.get('average_age_for_sale', 'н/д')} лет",
                    f"Средний возраст объектов в аренду: {age_data.get('average_age_for_rent', 'н/д')} лет",
                    f"Средняя цена продажи: €{age_data.get('unit_price_for_sale', 'н/д')}",
                    f"Минимальная цена продажи: €{age_data.get('min_unit_price_for_sale', 'н/д')}",
                    f"Максимальная цена продажи: €{age_data.get('max_unit_price_for_sale', 'н/д')}",
                    f"Сопоставимая площадь для продажи: {age_data.get('comparable_area_for_sale', 'н/д')} м²",
                    f"Количество объектов на продажу: {age_data.get('count_for_sale', 'н/d')}",
                    f"Средняя цена аренды: €{age_data.get('unit_price_for_rent', 'н/d')}",
                    f"Минимальная цена аренды: €{age_data.get('min_unit_price_for_rent', 'н/d')}",
                    f"Максимальная цена аренды: €{age_data.get('max_unit_price_for_rent', 'н/d')}",
                    f"Сопоставимая площадь для аренды: {age_data.get('comparable_area_for_rent', 'н/d')} м²",
                    f"Количество объектов в аренду: {age_data.get('count_for_rent', 'н/d')}",
                    f"Цена для продажи: €{age_data.get('price_for_sale', 'н/d')}",
                    f"Цена для аренды: €{age_data.get('price_for_rent', 'н/d')}",
                    f"Период листинга для продажи: {age_data.get('listing_period_for_sale', 'н/d')} дней",
                    f"Период листинга для аренды: {age_data.get('listing_period_for_rent', 'н/d')} дней",
                    f"Доходность: {age_data.get('yield', 'н/d')}%",
                    "",
                ])
        
        # Тренд по этажу объекта (из таблицы floor_segment_data)
        if market_data.get('floor_segment_data'):
            floor_data = market_data['floor_segment_data']
            report_lines.extend([
                "=== ТРЕНД ПО ЭТАЖУ ОБЪЕКТА ===",
            ])
            
            # Если floor_data это список (несколько записей с разными listing_type)
            if isinstance(floor_data, list):
                for record in floor_data:
                    listing_type = record.get('listing_type', 'н/д')
                    report_lines.extend([
                        f"--- Этаж объекта: {listing_type} ---",
                        f"Средняя цена продажи: €{record.get('unit_price_for_sale', 'н/д')}",
                        f"Минимальная цена продажи: €{record.get('min_unit_price_for_sale', 'н/д')}",
                        f"Максимальная цена продажи: €{record.get('max_unit_price_for_sale', 'н/д')}",
                        f"Сопоставимая площадь для продажи: {record.get('comparable_area_for_sale', 'н/д')} м²",
                        f"Количество объектов на продажу: {record.get('count_for_sale', 'н/д')}",
                        f"Средняя цена аренды: €{record.get('unit_price_for_rent', 'н/д')}",
                        f"Минимальная цена аренды: €{record.get('min_unit_price_for_rent', 'н/д')}",
                        f"Максимальная цена аренды: €{record.get('max_unit_price_for_rent', 'н/д')}",
                        f"Сопоставимая площадь для аренды: {record.get('comparable_area_for_rent', 'н/d')} м²",
                        f"Количество объектов в аренду: {record.get('count_for_rent', 'н/d')}",
                        f"Цена для продажи: €{record.get('price_for_sale', 'н/d')}",
                        f"Цена для аренды: €{record.get('price_for_rent', 'н/d')}",
                        f"Средний возраст объекта для продажи: {record.get('average_age_for_sale', 'н/d')} лет",
                        f"Средний возраст объекта для аренды: {record.get('average_age_for_rent', 'н/d')} лет",
                        f"Период листинга для продажи: {record.get('listing_period_for_sale', 'н/d')} дней",
                        f"Период листинга для аренды: {record.get('listing_period_for_rent', 'н/d')} дней",
                        f"Доходность: {record.get('yield', 'н/d')}%",
                        "",
                    ])
            else:
                # Если это одна запись
                listing_type = floor_data.get('listing_type', 'н/д')
                report_lines.extend([
                    f"--- Этаж объекта: {listing_type} ---",
                    f"Средняя цена продажи: €{floor_data.get('unit_price_for_sale', 'н/d')}",
                    f"Минимальная цена продажи: €{floor_data.get('min_unit_price_for_sale', 'н/d')}",
                    f"Максимальная цена продажи: €{floor_data.get('max_unit_price_for_sale', 'н/d')}",
                    f"Сопоставимая площадь для продажи: {floor_data.get('comparable_area_for_sale', 'н/d')} м²",
                    f"Количество объектов на продажу: {floor_data.get('count_for_sale', 'н/d')}",
                    f"Средняя цена аренды: €{floor_data.get('unit_price_for_rent', 'н/d')}",
                    f"Минимальная цена аренды: €{floor_data.get('min_unit_price_for_rent', 'н/d')}",
                    f"Максимальная цена аренды: €{floor_data.get('max_unit_price_for_rent', 'н/d')}",
                    f"Сопоставимая площадь для аренды: {floor_data.get('comparable_area_for_rent', 'н/d')} м²",
                    f"Количество объектов в аренду: {floor_data.get('count_for_rent', 'н/d')}",
                    f"Цена для продажи: €{floor_data.get('price_for_sale', 'н/d')}",
                    f"Цена для аренды: €{floor_data.get('price_for_rent', 'н/d')}",
                    f"Средний возраст объекта для продажи: {floor_data.get('average_age_for_sale', 'н/d')} лет",
                    f"Средний возраст объекта для аренды: {floor_data.get('average_age_for_rent', 'н/d')} лет",
                    f"Период листинга для продажи: {floor_data.get('listing_period_for_sale', 'н/d')} дней",
                    f"Период листинга для аренды: {floor_data.get('listing_period_for_rent', 'н/d')} дней",
                    f"Доходность: {floor_data.get('yield', 'н/d')}%",
                    "",
                ])
        
        # Тренд по типу отопления (из таблицы heating_data)
        if market_data.get('heating_data'):
            heating_data = market_data['heating_data']
            report_lines.extend([
                "=== ТРЕНД ПО ТИПУ ОТОПЛЕНИЯ ===",
            ])
            
            # Если heating_data это список (несколько записей с разными listing_type)
            if isinstance(heating_data, list):
                for record in heating_data:
                    listing_type = record.get('listing_type', 'н/д')
                    report_lines.extend([
                        f"--- Система отопления: {listing_type} ---",
                        f"Средняя цена продажи: €{record.get('unit_price_for_sale', 'н/д')}",
                        f"Минимальная цена продажи: €{record.get('min_unit_price_for_sale', 'н/д')}",
                        f"Максимальная цена продажи: €{record.get('max_unit_price_for_sale', 'н/д')}",
                        f"Сопоставимая площадь для продажи: {record.get('comparable_area_for_sale', 'н/д')} м²",
                        f"Количество объектов на продажу: {record.get('count_for_sale', 'н/d')}",
                        f"Средняя цена аренды: €{record.get('unit_price_for_rent', 'н/d')}",
                        f"Минимальная цена аренды: €{record.get('min_unit_price_for_rent', 'н/d')}",
                        f"Максимальная цена аренды: €{record.get('max_unit_price_for_rent', 'н/d')}",
                        f"Сопоставимая площадь для аренды: {record.get('comparable_area_for_rent', 'н/d')} м²",
                        f"Количество объектов в аренду: {record.get('count_for_rent', 'н/d')}",
                        f"Цена для продажи: €{record.get('price_for_sale', 'н/d')}",
                        f"Цена для аренды: €{record.get('price_for_rent', 'н/d')}",
                        f"Средний возраст объекта для продажи: {record.get('average_age_for_sale', 'н/d')} лет",
                        f"Средний возраст объекта для аренды: {record.get('average_age_for_rent', 'н/d')} лет",
                        f"Период листинга для продажи: {record.get('listing_period_for_sale', 'н/d')} дней",
                        f"Период листинга для аренды: {record.get('listing_period_for_rent', 'н/d')} дней",
                        f"Доходность: {record.get('yield', 'н/d')}%",
                        "",
                    ])
            else:
                # Если это одна запись
                listing_type = heating_data.get('listing_type', 'н/д')
                report_lines.extend([
                    f"--- Система отопления: {listing_type} ---",
                    f"Средняя цена продажи: €{heating_data.get('unit_price_for_sale', 'н/d')}",
                    f"Минимальная цена продажи: €{heating_data.get('min_unit_price_for_sale', 'н/d')}",
                    f"Максимальная цена продажи: €{heating_data.get('max_unit_price_for_sale', 'н/d')}",
                    f"Сопоставимая площадь для продажи: {heating_data.get('comparable_area_for_sale', 'н/d')} м²",
                    f"Количество объектов на продажу: {heating_data.get('count_for_sale', 'н/d')}",
                    f"Средняя цена аренды: €{heating_data.get('unit_price_for_rent', 'н/d')}",
                    f"Минимальная цена аренды: €{heating_data.get('min_unit_price_for_rent', 'н/d')}",
                    f"Максимальная цена аренды: €{heating_data.get('max_unit_price_for_rent', 'н/d')}",
                    f"Сопоставимая площадь для аренды: {heating_data.get('comparable_area_for_rent', 'н/d')} м²",
                    f"Количество объектов в аренду: {heating_data.get('count_for_rent', 'н/d')}",
                    f"Цена для продажи: €{heating_data.get('price_for_sale', 'н/d')}",
                    f"Цена для аренды: €{heating_data.get('price_for_rent', 'н/d')}",
                    f"Средний возраст объекта для продажи: {heating_data.get('average_age_for_sale', 'н/d')} лет",
                    f"Средний возраст объекта для аренды: {heating_data.get('average_age_for_rent', 'н/d')} лет",
                    f"Период листинга для продажи: {heating_data.get('listing_period_for_sale', 'н/d')} дней",
                    f"Период листинга для аренды: {heating_data.get('listing_period_for_rent', 'н/d')} дней",
                    f"Доходность: {heating_data.get('yield', 'н/d')}%",
                    "",
                ])

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
    Создает изображение графика экономических данных
    """
    try:
        # Настройка для русского языка
        plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
        
        # Создаем фигуру
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Получаем данные
        gdp_chart = economic_charts_data.get('gdp_chart', {})
        inflation_chart = economic_charts_data.get('inflation_chart', {})
        
        if not gdp_chart.get('labels') or not inflation_chart.get('labels'):
            return None
        
        # Данные для графиков
        years = gdp_chart['labels']
        # Конвертируем годы в целые числа для правильного отображения
        years = [int(year) for year in years]
        gdp_data = gdp_chart['datasets'][0]['data']
        inflation_data = inflation_chart['datasets'][0]['data']
        
        # Создаем график
        ax.plot(years, gdp_data, 'o-', color='#00bcd4', linewidth=2, 
                markersize=6, label='Рост ВВП (%)', alpha=0.8)
        ax.plot(years, inflation_data, 's-', color='#dc3545', linewidth=2, 
                markersize=6, label='Инфляция (%)', alpha=0.8)
        
        # Настройка графика с явным указанием шрифта
        ax.set_xlabel('Год', fontsize=12, fontname='DejaVu Sans')
        ax.set_ylabel('Процент (%)', fontsize=12, fontname='DejaVu Sans')
        ax.set_title('Динамика экономических показателей', fontsize=14, fontweight='bold', fontname='DejaVu Sans')
        ax.grid(True, alpha=0.3)
        
        # Настройка легенды с явным указанием шрифта
        legend = ax.legend(fontsize=10)
        for text in legend.get_texts():
            text.set_fontname('DejaVu Sans')
        
        # Поворот подписей оси X для лучшей читаемости
        plt.xticks(rotation=45)
        # Устанавливаем шрифт для меток осей
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname('DejaVu Sans')
        
        # Настройка отступов
        plt.tight_layout()
        
        # Сохраняем в буфер
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        
        # Закрываем фигуру для освобождения памяти
        plt.close()
        
        return buffer
        
    except Exception as e:
        logger.error(f"Ошибка создания графика: {e}")
        return None

def create_chart_image_for_pdf(chart_data, title, width=180, height=100):
    """
    Создает изображение графика для вставки в PDF
    """
    try:
        logger.info(f"Создание графика для PDF: {title}")
        
        # Настройка для русского языка
        plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
        plt.rcParams['font.size'] = 8
        
        # Создаем фигуру с заданными размерами (в дюймах)
        fig, ax = plt.subplots(figsize=(width/25.4, height/25.4))  # Конвертируем мм в дюймы
        
        # Получаем данные
        years = chart_data.get('labels', [])
        # Конвертируем годы в целые числа для правильного отображения
        years = [int(year) for year in years if year.isdigit()]
        gdp_data = chart_data.get('gdp_chart', {}).get('datasets', [{}])[0].get('data', [])
        inflation_data = chart_data.get('inflation_chart', {}).get('datasets', [{}])[0].get('data', [])
        
        logger.info(f"Данные для графика: {len(years)} лет, ВВП: {len(gdp_data)} точек, Инфляция: {len(inflation_data)} точек")
        
        # Проверяем минимальное количество данных
        if len(years) < 2 or len(gdp_data) < 2 or len(inflation_data) < 2:
            logger.warning("Недостаточно данных для создания графика")
            # Создаем placeholder график с сообщением
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=10, fontname='DejaVu Sans')
            ax.set_title(title, fontsize=8, fontname='DejaVu Sans', pad=10)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Сохраняем в буфер
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
        
        # Создаем график
        ax.plot(years, gdp_data, 'o-', color='#00bcd4', linewidth=1.5, 
                markersize=3, label='ВВП', alpha=0.8)
        ax.plot(years, inflation_data, 's-', color='#dc3545', linewidth=1.5, 
                markersize=3, label='Инфляция', alpha=0.8)
        
        # Настройка графика с явным указанием шрифта
        ax.set_xlabel('Год', fontsize=6, fontname='DejaVu Sans')
        ax.set_ylabel('%', fontsize=6, fontname='DejaVu Sans')
        ax.set_title(title, fontsize=8, fontweight='bold', fontname='DejaVu Sans')
        ax.grid(True, alpha=0.2)
        
        # Настройка легенды с явным указанием шрифта
        legend = ax.legend(fontsize=6, loc='upper right')
        for text in legend.get_texts():
            text.set_fontname('DejaVu Sans')
        
        # Поворот подписей оси X
        plt.xticks(rotation=45, fontsize=6)
        plt.yticks(fontsize=6)
        
        # Устанавливаем шрифт для меток осей
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname('DejaVu Sans')
        
        # Настройка отступов
        plt.tight_layout()
        
        # Сохраняем в буфер
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
        buffer.seek(0)
        
        # Закрываем фигуру
        plt.close()
        
        return buffer
        
    except Exception as e:
        logger.error(f"Ошибка создания графика для PDF: {e}")
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
                # Берем самую свежую запись
                latest_record = max(result.data, key=lambda x: x.get('trend_date', ''))
                market_data['property_trends'] = latest_record
                logger.info(f"Найдены данные property_trends: {len(result.data)} записей, выбрана самая свежая: {latest_record.get('trend_date')}")
            else:
                logger.info("Данные property_trends не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения property_trends: {e}")
        
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
                            if current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['age_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные age_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам возраста")
            else:
                logger.info("Данные age_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения age_data: {e}")
        
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
                            if current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['floor_segment_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные floor_segment_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам этажей")
            else:
                logger.info("Данные floor_segment_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения floor_segment_data: {e}")
        
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
                # Берем самую свежую запись
                latest_record = max(result.data, key=lambda x: x.get('trend_date', ''))
                market_data['general_data'] = latest_record
                logger.info(f"Найдены данные general_data: {len(result.data)} записей, выбрана самая свежая: {latest_record.get('trend_date')}")
            else:
                logger.info("Данные general_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения general_data: {e}")
        
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
                            if current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['heating_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные heating_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам отопления")
            else:
                logger.info("Данные heating_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения heating_data: {e}")
        
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
                            if current_date > existing_date:
                                records_by_type[listing_type] = record
                
                # Сохраняем все записи (сгруппированные по listing_type)
                market_data['house_type_data'] = list(records_by_type.values())
                logger.info(f"Найдены данные house_type_data: {len(result.data)} записей, сгруппированы по {len(records_by_type)} типам спален")
            else:
                logger.info("Данные house_type_data не найдены")
        except Exception as e:
            logger.error(f"Ошибка получения house_type_data: {e}")
        
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
        
        response = requests.get(url, params=params, headers=headers)
        result = response.json()
        
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
            
            logger.info(f"Nominatim данные: {location_data}")
            return location_data
        
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
        # Улучшенное извлечение для турецких адресов
        address_parts = address.split(',')
        
        location_data = {
            'city_name': None,
            'district_name': None,
            'county_name': None,
            'country_name': 'Turkey'  # По умолчанию для турецких адресов
        }
        
        if len(address_parts) >= 3:
            # Обрабатываем специальный случай: "Zerdalilik, 07100 Muratpaşa/Antalya, Türkiye"
            if 'Muratpaşa/Antalya' in address_parts[1]:
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Muratpaşa'
                location_data['district_name'] = address_parts[0].strip()
            # Обрабатываем специальный случай: "Avsallar, Cengiz Akay Sk. No:12, 07410 Alanya/Antalya, Türkiye"
            elif 'Alanya/Antalya' in address_parts[2]:
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Alanya'
                location_data['district_name'] = address_parts[0].strip()
            # Обрабатываем специальный случай: "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye"
            elif 'Kepez/Antalya' in address_parts[2]:
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Kepez'
                location_data['district_name'] = address_parts[0].strip()
            else:
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
            # Простой формат
            location_data['district_name'] = address_parts[0].strip()
            location_data['city_name'] = address_parts[1].strip()
        
        # Если не удалось извлечь, используем fallback
        if not location_data['city_name']:
            location_data['city_name'] = 'Alanya'  # Default для региона
        if not location_data['district_name']:
            location_data['district_name'] = 'Avsallar'  # Default район
        if not location_data['county_name']:
            location_data['county_name'] = 'Antalya'  # Default провинция
        
        logger.info(f"Извлечены данные локации из адреса: {location_data}")
        return location_data
        
    except Exception as e:
        logger.error(f"Ошибка извлечения локации из адреса: {e}")
        return {
            'city_name': 'Alanya',
            'district_name': 'Avsallar', 
            'county_name': 'Antalya'
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
    Создает график трендов недвижимости для PDF
    
    Args:
        historical_data (dict): Исторические данные трендов
        chart_type (str): Тип графика ('sale' или 'rent')
        width (int): Ширина графика в мм
        height (int): Высота графика в мм
    
    Returns:
        BytesIO: Буфер с изображением графика или None при ошибке
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        from io import BytesIO
        
        # Настройка шрифта для русского языка
        plt.rcParams['font.family'] = 'DejaVu Sans'
        
        # Создаем фигуру
        fig, ax = plt.subplots(figsize=(width/25.4, height/25.4), dpi=200)
        
        years = historical_data['years']
        if chart_type == 'sale':
            prices = historical_data['sale_prices']
            title = 'Динамика цен на продажу (€/м²)'
            color = '#667eea'
        else:
            prices = historical_data['rent_prices']
            title = 'Динамика цен на аренду (€/м²)'
            color = '#dc3545'
        
        # Фильтруем None значения
        valid_data = [(year, price) for year, price in zip(years, prices) if price is not None]
        
        if valid_data:
            valid_years, valid_prices = zip(*valid_data)
            
            # Создаем график
            ax.plot(valid_years, valid_prices, marker='o', linewidth=2, markersize=4, 
                   color=color, alpha=0.8)
            
            # Настройка осей
            ax.set_title(title, fontsize=10, fontname='DejaVu Sans', pad=10)
            ax.set_xlabel('Год', fontsize=8, fontname='DejaVu Sans')
            ax.set_ylabel('Цена (€/м²)', fontsize=8, fontname='DejaVu Sans')
            
            # Настройка сетки
            ax.grid(True, alpha=0.3)
            
            # Настройка тиков
            ax.tick_params(axis='both', which='major', labelsize=7)
            
            # Поворот подписей оси X для лучшей читаемости
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Убираем лишние отступы
            plt.tight_layout()
        else:
            # Если нет данных, показываем пустой график с сообщением
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=10, fontname='DejaVu Sans')
            ax.set_title(title, fontsize=10, fontname='DejaVu Sans', pad=10)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Сохраняем в буфер
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        logger.info(f"Создан график трендов {chart_type}: {len(valid_data) if valid_data else 0} точек данных")
        return buffer
        
    except Exception as e:
        logger.error(f"Ошибка создания графика трендов {chart_type}: {e}")
        # Создаем placeholder график при ошибке
        try:
            fig, ax = plt.subplots(figsize=(width/25.4, height/25.4), dpi=200)
            ax.text(0.5, 0.5, 'Ошибка графика', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=8, fontname='DejaVu Sans')
            ax.set_title(f'Тренды {chart_type}', fontsize=8, fontname='DejaVu Sans', pad=10)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
        except:
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

if __name__ == '__main__':
    run_flask()
import os
import logging
from flask import Flask, request, jsonify, send_file, send_from_directory
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv
import threading
import asyncio
from locales import locales
import requests
import datetime
from fpdf import FPDF
import tempfile
import os
from dateutil.relativedelta import relativedelta
import random
import string

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

@app.route('/api/geocode', methods=['POST'])
def api_geocode():
    """Геокодинг адреса через Google Maps API"""
    data = request.json or {}
    address = data.get('address')
    if not address:
        return jsonify({'error': 'Address required'}), 400
    
    try:
        # Запрос к Google Maps Geocoding API
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': GOOGLE_MAPS_API_KEY
        }
        response = requests.get(url, params=params)
        result = response.json()
        
        if result['status'] == 'OK' and result['results']:
            location = result['results'][0]['geometry']['location']
            formatted_address = result['results'][0]['formatted_address']
            return jsonify({
                'success': True,
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': formatted_address
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Address not found'
            })
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
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
    
    if not all([address, bedrooms, price]):
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        # Анализируем рынок в радиусе 5 км
        market_analysis = analyze_market_around_location(lat, lng, bedrooms, price)
        
        # Формируем отчёт в текстовом формате для отображения
        report_text = format_market_report(market_analysis, address, language)
        
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
                        'lng': lng
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
            'report': market_analysis,
            'report_text': report_text
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': 'Internal error'}), 500

def format_market_report(market_analysis, address, language='en'):
    """Форматирование отчёта в текстовый вид"""
    
    # Получаем данные из анализа
    short_term = market_analysis['market_analysis']['radius_5km']['short_term_rentals']
    long_term = market_analysis['market_analysis']['radius_5km']['long_term_rentals']
    sales = market_analysis['market_analysis']['radius_5km']['sales']
    
    # Форматируем цены
    def format_price(price):
        return f"€{price:.2f}".replace('.00', '').replace('.', ',')
    
    def format_price_range(min_price, max_price):
        return f"€{min_price:.0f} - €{max_price:.0f}"
    
    # Формируем отчёт
    report_lines = [
        f"Анализ рынка в радиусе 5 км:",
        "",
        f"Краткосрочная аренда ({short_term['count']} объектов)",
        f"Средняя цена за ночь: {format_price(short_term['avg_price_per_night'])}",
        "",
        f"Диапазон цен: {format_price_range(short_term['price_range'][0], short_term['price_range'][1])}",
        "",
        f"Долгосрочная аренда ({long_term['count']} объектов)",
        f"Средняя месячная аренда: {format_price(long_term['avg_monthly_rent'])}",
        "",
        f"Диапазон цен: {format_price_range(long_term['price_range'][0], long_term['price_range'][1])}",
        "",
        f"Продажи недвижимости ({sales['count']} объектов)",
        f"Средняя цена продажи: {format_price(sales['avg_sale_price'])}",
        "",
        f"Диапазон цен: {format_price_range(sales['price_range'][0], sales['price_range'][1])}",
        "",
        f"Средняя цена за кв.м: €{market_analysis['market_analysis']['radius_5km']['avg_price_per_sqm']:.2f}"
    ]
    
    return "\n".join(report_lines)

def analyze_market_around_location(lat, lng, bedrooms, target_price):
    try:
        radius = 0.05  # ~5.5 км
        # Краткосрочная аренда
        short_term_query = supabase.table('short_term_rentals') \
            .select('property_id, price_per_night, bedrooms, latitude, longitude') \
            .gte('latitude', lat - radius).lte('latitude', lat + radius) \
            .gte('longitude', lng - radius).lte('longitude', lng + radius)
        if bedrooms:
            short_term_query = short_term_query.eq('bedrooms', bedrooms)
        short_term_rentals = short_term_query.execute().data or []

        # Долгосрочная аренда
        long_term_query = supabase.table('long_term_rentals') \
            .select('property_id, monthly_rent, bedrooms, latitude, longitude') \
            .gte('latitude', lat - radius).lte('latitude', lat + radius) \
            .gte('longitude', lng - radius).lte('longitude', lng + radius)
        if bedrooms:
            long_term_query = long_term_query.eq('bedrooms', bedrooms)
        long_term_rentals = long_term_query.execute().data or []

        # Продажи (используем asking_price, price_per_sqm)
        sales_query = supabase.table('property_sales') \
            .select('property_id, asking_price, bedrooms, latitude, longitude, price_per_sqm') \
            .gte('latitude', lat - radius).lte('latitude', lat + radius) \
            .gte('longitude', lng - radius).lte('longitude', lng + radius)
        if bedrooms:
            sales_query = sales_query.eq('bedrooms', bedrooms)
        sales = sales_query.execute().data or []

        def summarize(props, price_key):
            prices = [p[price_key] for p in props if p.get(price_key) is not None and p[price_key] != 0]
            total_count = len(props)
            count = len(prices)
            if not prices:
                return {'avg_price': 0, 'count': count, 'total_count': total_count, 'price_range': [0, 0]}
            return {
                'avg_price': sum(prices) / len(prices),
                'count': count,
                'total_count': total_count,
                'price_range': [min(prices), max(prices)]
            }

        short_term_stats = summarize(short_term_rentals, 'price_per_night')
        long_term_stats = summarize(long_term_rentals, 'monthly_rent')
        sales_stats = summarize(sales, 'asking_price')

        # Средняя цена за кв.м. (только по price_per_sqm)
        sqm_prices = [x for x in (s['price_per_sqm'] for s in sales) if isinstance(x, (int, float))]
        avg_price_per_sqm = sum(sqm_prices) / len(sqm_prices) if sqm_prices else 0

        report = {
            'market_analysis': {
                'radius_5km': {
                    'short_term_rentals': {
                        'count': short_term_stats['count'],
                        'total_count': short_term_stats['total_count'],
                        'avg_price_per_night': short_term_stats['avg_price'],
                        'price_range': short_term_stats['price_range']
                    },
                    'long_term_rentals': {
                        'count': long_term_stats['count'],
                        'total_count': long_term_stats['total_count'],
                        'avg_monthly_rent': long_term_stats['avg_price'],
                        'price_range': long_term_stats['price_range']
                    },
                    'sales': {
                        'count': sales_stats['count'],
                        'total_count': sales_stats['total_count'],
                        'avg_sale_price': sales_stats['avg_price'],
                        'price_range': sales_stats['price_range']
                    },
                    'avg_price_per_sqm': avg_price_per_sqm
                }
            },
            'property_details': {
                'address': f'Адрес объекта',
                'bedrooms': bedrooms,
                'target_price': target_price,
                'coordinates': {'lat': lat, 'lng': lng}
            },
            'summary': {
                'total_properties_analyzed': short_term_stats['total_count'] + long_term_stats['total_count'] + sales_stats['total_count'],
                'market_activity': 'high' if sales_stats['count'] > 5 else 'medium',
                'price_trend': 'up' if sales_stats['avg_price'] > 1100000 else 'stable'
            }
        }
        return report
    except Exception as e:
        logger.error(f"Error analyzing market data: {e}")
        # Возвращаем пустой отчёт в случае ошибки
        return {
            'market_analysis': {
                'radius_5km': {
                    'short_term_rentals': {'count': 0, 'avg_price_per_night': 0, 'price_range': [0, 0]},
                    'long_term_rentals': {'count': 0, 'avg_monthly_rent': 0, 'price_range': [0, 0]},
                    'sales': {'count': 0, 'avg_sale_price': 0, 'price_range': [0, 0]},
                    'avg_price_per_sqm': 0
                }
            },
            'property_details': {'address': 'Адрес объекта', 'bedrooms': bedrooms, 'target_price': target_price, 'coordinates': {'lat': lat, 'lng': lng}},
            'summary': {'total_properties_analyzed': 0, 'market_activity': 'none', 'price_trend': 'stable'}
        }

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
    try:
        price = float(price) if price is not None else 0
    except (ValueError, TypeError):
        price = 0
    try:
        # --- MOCK/DEMO DATA ---
        avg_sqm = 15451.29
        price_growth = 0.042
        short_term_income = 1950
        short_term_net = 1560
        long_term_income = 43000
        long_term_net = 34400
        five_year_growth = 0.23
        alt_deposit = 0.128
        alt_bonds = 0.245
        alt_stocks = 0.382
        alt_reits = 0.427
        inflation = 64.8
        eur_try = 35.2
        eur_try_growth = 0.14
        refi_rate = 45
        gdp_growth = 4.1
        taxes = {
            'transfer_tax': 0.04,
            'stamp_duty': 0.015,
            'notary': 1200,
            'annual_property_tax': 0.001,
            'annual_property_tax_max': 0.006,
            'rental_income_tax': '15-35%',
            'capital_gains_tax': '15-40%'
        }
        risks = [
            'Валютный: TRY/EUR ▲23% за 3 года',
            'Политический: Выборы 2028',
            'Экологический: Карта наводнений (NASA Earth Data)'
        ]
        liquidity = 'Среднее время продажи: 68 дней'
        district = 'Новый трамвай до пляжа (2026), Строительство школы (2027)'
        # --- Формируем структуру полного отчёта ---
        full_report_data = {
            'object': {
                'address': address,
                'bedrooms': bedrooms,
                'purchase_price': price,
                'avg_price_per_sqm': avg_sqm
            },
            'roi': {
                'short_term': {
                    'monthly_income': short_term_income,
                    'net_income': short_term_net,
                    'five_year_income': 93600,
                    'final_value': price * (1 + five_year_growth),
                    'roi': 81.5
                },
                'long_term': {
                    'annual_income': long_term_income,
                    'net_income': long_term_net,
                    'five_year_income': 172000,
                    'final_value': price * (1 + five_year_growth),
                    'roi': 130.5
                },
                'no_rent': {
                    'final_value': price * (1 + five_year_growth),
                    'roi': 23
                },
                'price_growth': price_growth
            },
            'alternatives': [
                {'name': 'Банковский депозит', 'yield': alt_deposit, 'source': 'TCMB API'},
                {'name': 'Облигации Турции', 'yield': alt_bonds, 'source': 'Investing.com API'},
                {'name': 'Акции (BIST30)', 'yield': alt_stocks, 'source': 'Alpha Vantage API'},
                {'name': 'REITs (фонды)', 'yield': alt_reits, 'source': 'Financial Modeling Prep'},
                {'name': 'Недвижимость', 'yield': 0.815, 'source': 'Ваш объект'}
            ],
            'macro': {
                'inflation': inflation,
                'eur_try': eur_try,
                'eur_try_growth': eur_try_growth,
                'refi_rate': refi_rate,
                'gdp_growth': gdp_growth
            },
            'taxes': taxes,
            'risks': risks,
            'liquidity': liquidity,
            'district': district,
            'yield': 0.081,
            'price_index': 1.23,
            'mortgage_rate': 0.32,
            'global_house_price_index': 1.12,
            'summary': 'Полный отчёт с реальными/мок-данными. Для реальных данных используйте таблицы Supabase.'
        }
        # Получаем user_id из базы данных по telegram_id
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        user_id = user_result.data[0]['id'] if user_result.data else telegram_id
        
        created_at = datetime.datetime.now().isoformat()
        
        report_data = {
            'user_id': user_id,
            'report_type': 'full',
            'title': f'Полный отчет: {address}',
            'description': f'Полный отчет по адресу {address}, {bedrooms} спален, цена {price}',
            'parameters': {
                'address': address,
                'bedrooms': bedrooms,
                'price': price,
                'lat': lat,
                'lng': lng
            },
            'address': address,
            'latitude': lat,
            'longitude': lng,
            'bedrooms': bedrooms,
            'price': price,
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
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        if not user_result.data:
            return jsonify({'error': 'User not found'}), 404
        user_id = user_result.data[0]['id']
        # Возвращаем только неотвязанные отчеты
        result = supabase.table('user_reports').select('*').eq('user_id', user_id).is_('deleted_at', None).order('created_at', desc=True).execute()
        reports = result.data if hasattr(result, 'data') else result
        return jsonify({'success': True, 'reports': reports})
    except Exception as e:
        logger.error(f"Error fetching user reports: {e}")
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
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        if not user_result.data:
            logger.error(f"User with telegram_id {telegram_id} not found for report deletion")
            return jsonify({'error': 'User not found'}), 404
        user_id = user_result.data[0]['id']
        # Проверяем, что отчет принадлежит пользователю и не удалён
        report_result = supabase.table('user_reports').select('id').eq('id', report_id).eq('user_id', user_id).is_('deleted_at', None).execute()
        if not report_result.data:
            logger.error(f"Report {report_id} not found or not owned by user_id {user_id} or already deleted")
            return jsonify({'error': 'Report not found or not owned by user'}), 404
        # Soft delete: выставляем deleted_at
        now = datetime.datetime.utcnow().isoformat()
        supabase.table('user_reports').update({'deleted_at': now}).eq('id', report_id).execute()
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
            'saved_at': datetime.datetime.now().isoformat()
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
        pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        pdf.set_font('DejaVu', 'B', 16)
        if client_name:
            pdf.cell(0, 10, f'Клиент: {client_name}', ln=True, align='C')
            pdf.ln(2)
        pdf.cell(0, 10, 'Полный отчет по недвижимости', ln=True, align='C')
        pdf.ln(10)
        if report.get('object'):
            pdf.set_font('DejaVu', 'B', 12)
            pdf.cell(0, 10, 'Информация об объекте:', ln=True)
            pdf.set_font('DejaVu', '', 10)
            obj = report['object']
            pdf.cell(0, 8, f'Адрес: {obj.get("address", "Не указан")}', ln=True)
            pdf.cell(0, 8, f'Спален: {obj.get("bedrooms", "Не указано")}', ln=True)
            pdf.cell(0, 8, f'Цена: €{obj.get("purchase_price", "Не указана")}', ln=True)
            pdf.ln(5)
        # Печатаем остальные блоки отчёта (без вложенности)
        # ROI анализ
        if 'roi' in report:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(200, 10, txt="Инвестиционный анализ (ROI):", ln=True)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(200, 8, txt=f"Краткосрочная аренда: ROI {report['roi']['short_term']['roi']}%", ln=True)
            pdf.cell(200, 8, txt=f"Долгосрочная аренда: ROI {report['roi']['long_term']['roi']}%", ln=True)
            pdf.cell(200, 8, txt=f"Без аренды: ROI {report['roi']['no_rent']['roi']}%", ln=True)
            pdf.ln(5)
        # Макроэкономика
        if 'macro' in report:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(200, 10, txt="Макроэкономические показатели:", ln=True)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(200, 8, txt=f"Инфляция: {report['macro']['inflation']}%", ln=True)
            pdf.cell(200, 8, txt=f"Ключевая ставка: {report['macro']['refi_rate']}%", ln=True)
            pdf.cell(200, 8, txt=f"Рост ВВП: {report['macro']['gdp_growth']}%", ln=True)
            pdf.ln(5)
        # Налоги
        if 'taxes' in report:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(200, 10, txt="Налоги и сборы:", ln=True)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(200, 8, txt=f"Налог на перевод: {report['taxes']['transfer_tax']*100}%", ln=True)
            pdf.cell(200, 8, txt=f"Гербовый сбор: {report['taxes']['stamp_duty']*100}%", ln=True)
            pdf.cell(200, 8, txt=f"Нотариус: €{report['taxes']['notary']}", ln=True)
            pdf.ln(5)
        # Блок: Альтернативы
        if 'alternatives' in report and isinstance(report['alternatives'], list):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Сравнение с альтернативами (5 лет):', ln=True)
            pdf.set_font('DejaVu', '', 12)
            for alt in report['alternatives']:
                name = alt.get('name', '-')
                yld = alt.get('yield', 0)
                pdf.cell(0, 8, f'{name}: {round(yld*100, 1)}%', ln=True)
            pdf.ln(5)
        # Блок: Профессиональные метрики
        if 'yield' in report or 'price_index' in report or 'mortgage_rate' in report or 'global_house_price_index' in report:
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Профессиональные метрики:', ln=True)
            pdf.set_font('DejaVu', '', 12)
            if 'yield' in report:
                pdf.cell(0, 8, f'Yield: {round(report["yield"]*100, 1)}%', ln=True)
            if 'price_index' in report:
                pdf.cell(0, 8, f'Индекс цен: {report["price_index"]}', ln=True)
            if 'mortgage_rate' in report:
                pdf.cell(0, 8, f'Ипотечная ставка: {round(report["mortgage_rate"]*100, 1)}%', ln=True)
            if 'global_house_price_index' in report:
                pdf.cell(0, 8, f'Глобальный индекс цен: {report["global_house_price_index"]}', ln=True)
            pdf.ln(5)
        # Блок: Риски и развитие района
        if 'risks' in report or 'liquidity' in report or 'district' in report:
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Риски и развитие района:', ln=True)
            pdf.set_font('DejaVu', '', 12)
            if 'risks' in report and isinstance(report['risks'], list):
                for idx, risk in enumerate(report['risks']):
                    pdf.cell(0, 8, f'Риск {idx+1}: {risk}', ln=True)
            if 'liquidity' in report:
                pdf.cell(0, 8, f'Ликвидность: {report["liquidity"]}', ln=True)
            if 'district' in report:
                pdf.cell(0, 8, f'Развитие района: {report["district"]}', ln=True)
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
            pdf.cell(0, 8, 'Контактные данные риелтора:', ln=True)
            pdf.set_font('DejaVu', '', 10)
            if profile.get('tg_name') or profile.get('last_name'):
                pdf.cell(0, 8, f"Имя: {profile.get('tg_name','')} {profile.get('last_name','')}", ln=True)
            if profile.get('company'):
                pdf.cell(0, 8, f"Компания: {profile.get('company')}", ln=True)
            if profile.get('position'):
                pdf.cell(0, 8, f"Должность: {profile.get('position')}", ln=True)
            if profile.get('phone'):
                pdf.cell(0, 8, f"Телефон: {profile.get('phone')}", ln=True)
            if profile.get('email'):
                pdf.cell(0, 8, f"Email: {profile.get('email')}", ln=True)
            if profile.get('website'):
                pdf.cell(0, 8, f"Сайт: {profile.get('website')}", ln=True)
            if profile.get('about_me'):
                pdf.multi_cell(0, 8, f"О себе: {profile.get('about_me')}")
        # Сохраняем PDF во временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        # Перемещаем PDF в static/reports/
        reports_dir = os.path.join(app.root_path, 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        final_pdf_name = f'report_{report_id}.pdf'
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
            'updated_at': datetime.datetime.now().isoformat()
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
        user_result = supabase.table('users').select('id').eq('telegram_id', telegram_id).execute()
        user_id = user_result.data[0]['id'] if user_result.data else telegram_id
        # Сохраняем отчет
        report_data = {
            'user_id': user_id,
            'report_type': report_type,
            'address': address,
            'full_report': full_report,
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }
        result = supabase.table('user_reports').insert(report_data).execute()
        new_id = result.data[0]['id'] if hasattr(result, 'data') and result.data else None
        return jsonify({'success': True, 'report_id': new_id})
    except Exception as e:
        logger.error(f"Error saving user report: {e}")
        return jsonify({'error': 'Internal error'}), 500

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
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, 'Полный отчет по недвижимости', ln=1, align='C')
        pdf.ln(10)
        obj = report.get('object') or {}
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, 'Информация об объекте:', ln=1)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 8, f'Адрес: {obj.get("address", "Не указан")}', ln=1)
        pdf.cell(0, 8, f'Спален: {obj.get("bedrooms", "Не указано")}', ln=1)
        pdf.cell(0, 8, f'Цена: €{obj.get("purchase_price", "Не указана")}', ln=1)
        pdf.ln(5)
        # ROI анализ
        roi = report.get('roi')
        if roi:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, "Инвестиционный анализ (ROI):", ln=1)
            pdf.set_font("DejaVu", size=12)
            st = roi.get('short_term', {})
            lt = roi.get('long_term', {})
            nr = roi.get('no_rent', {})
            pdf.cell(0, 8, f"Краткосрочная аренда: ROI {st.get('roi', '-')}", ln=1)
            pdf.cell(0, 8, f"Долгосрочная аренда: ROI {lt.get('roi', '-')}", ln=1)
            pdf.cell(0, 8, f"Без аренды: ROI {nr.get('roi', '-')}", ln=1)
            pdf.ln(5)
        # Макроэкономика
        macro = report.get('macro')
        if macro:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, "Макроэкономические показатели:", ln=1)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(0, 8, f"Инфляция: {macro.get('inflation', '-')}%", ln=1)
            pdf.cell(0, 8, f"Ключевая ставка: {macro.get('refi_rate', '-')}%", ln=1)
            pdf.cell(0, 8, f"Рост ВВП: {macro.get('gdp_growth', '-')}%", ln=1)
            pdf.ln(5)
        # Налоги
        taxes = report.get('taxes')
        if taxes:
            pdf.set_font("DejaVu", 'B', 14)
            pdf.cell(0, 10, "Налоги и сборы:", ln=1)
            pdf.set_font("DejaVu", size=12)
            pdf.cell(0, 8, f"Налог на перевод: {taxes.get('transfer_tax', 0)*100}%", ln=1)
            pdf.cell(0, 8, f"Гербовый сбор: {taxes.get('stamp_duty', 0)*100}%", ln=1)
            pdf.cell(0, 8, f"Нотариус: €{taxes.get('notary', '-')}" , ln=1)
            pdf.ln(5)
        # Альтернативы
        alternatives = report.get('alternatives')
        if isinstance(alternatives, list):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Сравнение с альтернативами (5 лет):', ln=1)
            pdf.set_font('DejaVu', '', 12)
            for alt in alternatives:
                name = alt.get('name', '-')
                yld = alt.get('yield', 0)
                pdf.cell(0, 8, f'{name}: {round(yld*100, 1)}%', ln=1)
            pdf.ln(5)
        # Профессиональные метрики
        if any(k in report for k in ['yield', 'price_index', 'mortgage_rate', 'global_house_price_index']):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Профессиональные метрики:', ln=1)
            pdf.set_font('DejaVu', '', 12)
            if 'yield' in report:
                pdf.cell(0, 8, f'Yield: {round(report.get("yield", 0)*100, 1)}%', ln=1)
            if 'price_index' in report:
                pdf.cell(0, 8, f'Индекс цен: {report.get("price_index", "-")}', ln=1)
            if 'mortgage_rate' in report:
                pdf.cell(0, 8, f'Ипотечная ставка: {round(report.get("mortgage_rate", 0)*100, 1)}%', ln=1)
            if 'global_house_price_index' in report:
                pdf.cell(0, 8, f'Глобальный индекс цен: {report.get("global_house_price_index", "-")}', ln=1)
            pdf.ln(5)
        # Риски и развитие района
        if any(k in report for k in ['risks', 'liquidity', 'district']):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.cell(0, 10, 'Риски и развитие района:', ln=1)
            pdf.set_font('DejaVu', '', 12)
            risks = report.get('risks')
            if isinstance(risks, list):
                for idx, risk in enumerate(risks):
                    pdf.cell(0, 8, f'Риск {idx+1}: {risk}', ln=1)
            if 'liquidity' in report:
                pdf.cell(0, 8, f'Ликвидность: {report.get("liquidity", "-")}', ln=1)
            if 'district' in report:
                pdf.cell(0, 8, f'Развитие района: {report.get("district", "-")}', ln=1)
            pdf.ln(5)
        # Сохраняем PDF во временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        # Перемещаем PDF в static/reports/
        reports_dir = os.path.join(app.root_path, 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        final_pdf_name = f'report_{report_id}.pdf'
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
    now = datetime.datetime.now()
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
            return datetime.datetime.strptime(val[:10], '%Y-%m-%d').date()
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
    openai_key_row = supabase.table('api_keys').select('key_value').eq('key_name', 'OPENAI_API').execute().data
    if openai_key_row and isinstance(openai_key_row, list) and len(openai_key_row) > 0 and openai_key_row[0] and isinstance(openai_key_row[0], dict) and 'key_value' in openai_key_row[0]:
        openai_key = openai_key_row[0]['key_value']
    else:
        openai_key = ''
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
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_lang} (no explanation, only translation):"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1024,
                "temperature": 0.3
            }
            try:
                resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30)
                if resp.status_code == 200:
                    result = resp.json()['choices'][0]['message']['content'].strip()
                    logger.info(f"Перевод {target_lang}: {result}")
                    return result
                else:
                    logger.error(f"OpenAI API error for {target_lang}: {resp.status_code} {resp.text}")
                    return f"[Ошибка перевода {target_lang}]"
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

if __name__ == '__main__':
    run_flask()
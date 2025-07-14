import os
import logging
from flask import Flask, request, jsonify, send_file
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, Bot
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
supabase: Client = create_client(supabase_url, supabase_key)

# Токен бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

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
#                 'first_name': getattr(user, 'first_name', None),
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

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья приложения"""
    return jsonify({"status": "ok", "message": "Telegram WebApp Bot is running"})

@app.route('/api/user', methods=['POST'])
def api_user():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    username = data.get('username')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    language_code = data.get('language_code', 'en')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400

    # Проверяем пользователя в базе
    user_result = supabase.table('users').select('*').eq('telegram_id', telegram_id).execute()
    user = user_result.data if hasattr(user_result, 'data') else user_result
    if user:
        user = user[0]
        lang = user.get('language') or (language_code[:2] if language_code[:2] in locales else 'en')
        return jsonify({
            'exists': True,
            'is_new_user': False,
            'language': user.get('language'),
            'welcome': locales[lang]['welcome_back'],
            'menu': locales[lang]['menu']
        })
    else:
        # Новый пользователь
        supabase.table('users').insert({
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language': None
        }).execute()
        # Приветствие на языке Telegram
        lang = language_code[:2] if language_code[:2] in locales else 'en'
        return jsonify({
            'exists': False,
            'is_new_user': True,
            'language': None,
            'welcome': locales[lang]['welcome_new'],
            'choose_language': locales[lang]['choose_language'],
            'languages': locales[lang]['language_names']
        })

@app.route('/api/user_profile', methods=['POST'])
def api_user_profile():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    try:
        result = supabase.table('users').select('first_name, last_name, photo_url, phone, email, website, company, position, about_me').eq('telegram_id', telegram_id).execute()
        if result.data and len(result.data) > 0:
            return jsonify({'success': True, 'profile': result.data[0]})
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/set_language', methods=['POST'])
def api_set_language():
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    language = data.get('language')
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
                    'price_range_min': float(price) * 0.8,
                    'price_range_max': float(price) * 1.2
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
        sqm_prices = [s['price_per_sqm'] for s in sales if s.get('price_per_sqm') and s['price_per_sqm'] > 0]
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
    """Получение статистики рынка"""
    data = request.json or {}
    city = data.get('city')
    district = data.get('district')
    
    try:
        # Здесь должна быть логика получения статистики
        # Пока возвращаем демо-данные
        
        stats = {
            'avg_price_per_sqm': 3500,
            'price_growth_yoy': 12.5,
            'total_properties': 1250,
            'avg_days_on_market': 68,
            'rental_yield': 8.5,
            'price_trend': 'up',
            'market_activity': 'high'
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
    """Калькулятор ROI"""
    data = request.json or {}
    property_type = data.get('property_type')
    purchase_price = data.get('purchase_price')
    purchase_costs = data.get('purchase_costs', 0)
    
    if property_type == 'short_term':
        avg_nightly_rate = data.get('avg_nightly_rate')
        occupancy_rate = data.get('occupancy_rate', 75)
        
        # Расчет ROI для краткосрочной аренды
        monthly_income = avg_nightly_rate * (occupancy_rate / 100) * 30
        annual_income = monthly_income * 12
        total_investment = purchase_price + purchase_costs
        roi = (annual_income / total_investment) * 100
        
    elif property_type == 'long_term':
        monthly_rent = data.get('monthly_rent')
        
        # Расчет ROI для долгосрочной аренды
        annual_income = monthly_rent * 12
        total_investment = purchase_price + purchase_costs
        roi = (annual_income / total_investment) * 100
        
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
    telegram_id = data.get('telegram_id')
    address = data.get('address')
    lat = data.get('lat')
    lng = data.get('lng')
    bedrooms = data.get('bedrooms')
    price = data.get('price')
    try:
        price = float(price) if price is not None else 0
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
        report_id = result.data[0]['id'] if result.data else None
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
    telegram_id = data.get('telegram_id')
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
def api_delete_user_report():
    """Soft delete отчета: выставляет deleted_at"""
    data = request.json or {}
    telegram_id = data.get('telegram_id')
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
    telegram_id = data.get('telegram_id')
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

@app.route('/api/generate_pdf_report', methods=['POST'])
def api_generate_pdf_report():
    """Генерация PDF отчета с поддержкой Unicode (DejaVu)"""
    data = request.json or {}
    logger.info(f"PDF request data: {data}")
    report = data.get('report')
    profile = data.get('profile') or {}
    client_name = data.get('client_name')
    report_id = data.get('report_id')
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
            if profile.get('first_name') or profile.get('last_name'):
                pdf.cell(0, 8, f"Имя: {profile.get('first_name','')} {profile.get('last_name','')}", ln=True)
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
        # Сохраняем путь к PDF в user_reports
        if not report_id:
            return jsonify({'error': 'report_id required'}), 400
        supabase.table('user_reports').update({'pdf_path': temp_file.name}).eq('id', report_id).execute()
        return jsonify({
            'success': True,
            'pdf_path': temp_file.name,
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
    telegram_id = data.get('telegram_id')
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

@app.route('/api/send_pdf_to_client', methods=['POST'])
def api_send_pdf_to_client():
    """Отправка PDF клиенту и запись в client_contacts (всегда новая запись)"""
    data = request.json or {}
    realtor_telegram_id = data.get('realtor_telegram_id')
    client_name = data.get('client_name')
    client_telegram = data.get('client_telegram')
    pdf_path = data.get('pdf_path')
    pdf_url = data.get('pdf_url')  # если уже загружено в облако
    now = datetime.datetime.now().isoformat()
    if not all([realtor_telegram_id, client_telegram, pdf_path or pdf_url]):
        return jsonify({'error': 'Missing required data'}), 400
    try:
        # Здесь должна быть логика отправки PDF через Telegram Bot API (или просто сохраняем ссылку)
        # Сохраняем информацию о клиенте (всегда новая запись)
        client_data = {
            'realtor_telegram_id': realtor_telegram_id,
            'client_name': client_name,
            'client_telegram': client_telegram,
            'created_at': now,
            'last_report_pdf_url': pdf_url or pdf_path
        }
        supabase.table('client_contacts').insert(client_data).execute()
        return jsonify({
            'success': True,
            'sent': True
        })
    except Exception as e:
        logger.error(f"Error sending PDF to client: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/send_report_to_client', methods=['POST'])
def api_send_report_to_client():
    """Отправка отчета клиенту через Telegram"""
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    client_name = data.get('client_name')
    client_username = data.get('client_username')
    report_data = data.get('report_data')
    
    if not all([telegram_id, client_name, client_username, report_data]):
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        # Получаем данные пользователя (риелтора)
        user_result = supabase.table('users').select('first_name, last_name').eq('telegram_id', telegram_id).execute()
        if not user_result.data:
            return jsonify({'error': 'User not found'}), 404
        
        realtor_name = f"{user_result.data[0].get('first_name', '')} {user_result.data[0].get('last_name', '')}".strip()
        
        # Генерируем PDF отчет
        pdf_path = generate_client_report_pdf(report_data, realtor_name)
        
        # Отправляем через Telegram Bot API
        success = send_pdf_via_telegram(client_username, pdf_path, client_name, realtor_name)
        
        if success:
            # Сохраняем информацию о клиенте
            try:
                supabase.table('client_contacts').insert({
                    'user_id': telegram_id,
                    'client_name': client_name,
                    'client_username': client_username,
                    'report_address': report_data.get('address'),
                    'sent_at': datetime.datetime.now().isoformat()
                }).execute()
            except Exception as e:
                logger.error(f"Error saving client contact: {e}")
                # Продолжаем выполнение даже если сохранение не удалось
            
            # Удаляем временный файл
            try:
                os.remove(pdf_path)
            except:
                pass
            
            return jsonify({'success': True, 'message': 'Report sent successfully'})
        else:
            return jsonify({'error': 'Failed to send report via Telegram'}), 500
            
    except Exception as e:
        logger.error(f"Error sending report to client: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def generate_client_report_pdf(report_data, realtor_name):
    """Генерация PDF отчета для клиента"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("DejaVu", size=12)
    
    # Заголовок
    pdf.set_font("DejaVu", 'B', 16)
    pdf.cell(200, 10, txt="Анализ недвижимости", ln=True, align='C')
    pdf.ln(5)
    
    # Информация об объекте
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(200, 10, txt="Информация об объекте:", ln=True)
    pdf.set_font("DejaVu", size=12)
    pdf.cell(200, 8, txt=f"Адрес: {report_data.get('address', 'N/A')}", ln=True)
    pdf.cell(200, 8, txt=f"Спален: {report_data.get('bedrooms', 'N/A')}", ln=True)
    pdf.cell(200, 8, txt=f"Цена: €{report_data.get('price', 0):,.0f}", ln=True)
    pdf.ln(5)
    
    # Если есть полный отчет
    if 'report' in report_data:
        report = report_data['report']
        
        # ROI анализ
        pdf.set_font("DejaVu", 'B', 14)
        pdf.cell(200, 10, txt="Инвестиционный анализ (ROI):", ln=True)
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 8, txt=f"Краткосрочная аренда: ROI {report['roi']['short_term']['roi']}%", ln=True)
        pdf.cell(200, 8, txt=f"Долгосрочная аренда: ROI {report['roi']['long_term']['roi']}%", ln=True)
        pdf.cell(200, 8, txt=f"Без аренды: ROI {report['roi']['no_rent']['roi']}%", ln=True)
        pdf.ln(5)
        
        # Макроэкономика
        pdf.set_font("DejaVu", 'B', 14)
        pdf.cell(200, 10, txt="Макроэкономические показатели:", ln=True)
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 8, txt=f"Инфляция: {report['macro']['inflation']}%", ln=True)
        pdf.cell(200, 8, txt=f"Ключевая ставка: {report['macro']['refi_rate']}%", ln=True)
        pdf.cell(200, 8, txt=f"Рост ВВП: {report['macro']['gdp_growth']}%", ln=True)
        pdf.ln(5)
        
        # Налоги
        pdf.set_font("DejaVu", 'B', 14)
        pdf.cell(200, 10, txt="Налоги и сборы:", ln=True)
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 8, txt=f"Налог на перевод: {report['taxes']['transfer_tax']*100}%", ln=True)
        pdf.cell(200, 8, txt=f"Гербовый сбор: {report['taxes']['stamp_duty']*100}%", ln=True)
        pdf.cell(200, 8, txt=f"Нотариус: €{report['taxes']['notary']}", ln=True)
        pdf.ln(5)
        
        # Итог
        pdf.set_font("DejaVu", 'B', 14)
        pdf.cell(200, 10, txt="Заключение:", ln=True)
        pdf.set_font("DejaVu", size=12)
        pdf.multi_cell(200, 8, txt=report.get('summary', 'Анализ завершен'))
    
    # Контактная информация риелтора
    pdf.ln(10)
    pdf.set_font("DejaVu", 'B', 12)
    pdf.cell(200, 8, txt=f"Риелтор: {realtor_name}", ln=True)
    pdf.cell(200, 8, txt="Свяжитесь для получения дополнительной информации", ln=True)
    
    # Сохраняем во временный файл
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

def send_pdf_via_telegram(client_username, pdf_path, client_name, realtor_name):
    """Отправка PDF через Telegram Bot API"""
    try:
        # Убираем @ если есть
        username = client_username.lstrip('@')
        
        # Формируем сообщение
        message = f"Здравствуйте, {client_name}! 👋\n\n"
        message += f"Риелтор {realtor_name} подготовил для вас анализ недвижимости.\n\n"
        message += "В прикрепленном файле вы найдете:\n"
        message += "• Детальный анализ объекта\n"
        message += "• Инвестиционные расчеты (ROI)\n"
        message += "• Макроэкономические показатели\n"
        message += "• Информацию о налогах и сборах\n\n"
        message += "Для получения дополнительной информации свяжитесь с риелтором."
        
        # Отправляем через Telegram Bot API
        bot = Bot(token=TOKEN)
        
        # Сначала отправляем текстовое сообщение
        try:
            bot.send_message(chat_id=f"@{username}", text=message)
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            return False
        
        # Затем отправляем PDF файл
        try:
            with open(pdf_path, 'rb') as pdf_file:
                bot.send_document(
                    chat_id=f"@{username}",
                    document=pdf_file,
                    caption="Анализ недвижимости"
                )
            return True
        except Exception as e:
            logger.error(f"Error sending PDF: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in send_pdf_via_telegram: {e}")
        return False

def run_flask():
    """Запуск Flask приложения"""
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Для WebApp запускаем только Flask
    run_flask() 

@app.route('/api/update_user_report', methods=['POST'])
def api_update_user_report():
    """Обновление отчета пользователя (списание $1, перегенерация)"""
    data = request.json or {}
    telegram_id = data.get('telegram_id')
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
    telegram_id = data.get('telegram_id')
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
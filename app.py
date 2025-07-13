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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    if not user or not hasattr(user, 'id'):
        await update.message.reply_text("Ошибка: не удалось определить пользователя.")
        return
    
    # Проверяем, есть ли пользователь в базе данных
    try:
        result = supabase.table('users').select('*').eq('telegram_id', user.id).execute()
        
        if result.data:
            # Пользователь уже существует
            welcome_message = f"С возвращением, {getattr(user, 'first_name', 'Пользователь')}! 👋"
        else:
            # Новый пользователь
            welcome_message = f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Добро пожаловать! 🎉"
            
            # Сохраняем пользователя в базу данных
            supabase.table('users').insert({
                'telegram_id': user.id,
                'username': getattr(user, 'username', None),
                'first_name': getattr(user, 'first_name', None),
                'last_name': getattr(user, 'last_name', None)
            }).execute()
            
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
        welcome_message = f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Добро пожаловать! 🎉"
    
    # Создаем кнопку для запуска WebApp
    keyboard = [
        [KeyboardButton("🚀 Запустить WebApp", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup
    )

async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик данных от WebApp"""
    data = update.message.web_app_data.data
    user = update.effective_user
    
    await update.message.reply_text(
        f"Получены данные от WebApp: {data}\n"
        f"Пользователь: {getattr(user, 'first_name', 'Пользователь')}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик обычных сообщений"""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {getattr(user, 'first_name', 'Пользователь')}! Используйте кнопку WebApp для тестирования."
    )

def main() -> None:
    """Запуск бота"""
    logger.info("Запуск Telegram-бота...")
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

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
            'language': lang,
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
            'language': lang,
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

        # Продажи (используем asking_price вместо sale_price)
        sales_query = supabase.table('property_sales') \
            .select('property_id, asking_price, bedrooms, latitude, longitude, price_per_sqm, area, avg_price_per_sqm') \
            .gte('latitude', lat - radius).lte('latitude', lat + radius) \
            .gte('longitude', lng - radius).lte('longitude', lng + radius)
        if bedrooms:
            sales_query = sales_query.eq('bedrooms', bedrooms)
        sales = sales_query.execute().data or []

        def summarize(props, price_key):
            prices = [p[price_key] for p in props if p.get(price_key)]
            if not prices:
                return {'avg_price': 0, 'count': 0, 'price_range': [0, 0]}
            return {
                'avg_price': sum(prices) / len(prices),
                'count': len(prices),
                'price_range': [min(prices), max(prices)]
            }

        short_term_stats = summarize(short_term_rentals, 'price_per_night')
        long_term_stats = summarize(long_term_rentals, 'monthly_rent')
        sales_stats = summarize(sales, 'asking_price')

        # Средняя цена за кв.м.
        sqm_prices = []
        for s in sales:
            if s.get('price_per_sqm') and s['price_per_sqm'] > 0:
                sqm_prices.append(s['price_per_sqm'])
            elif s.get('avg_price_per_sqm') and s['avg_price_per_sqm'] > 0:
                sqm_prices.append(s['avg_price_per_sqm'])
            elif s.get('asking_price') and s.get('area') and s['area']:
                try:
                    sqm = float(s['asking_price']) / float(s['area'])
                    if sqm > 0:
                        sqm_prices.append(sqm)
                except Exception:
                    pass
        avg_price_per_sqm = sum(sqm_prices) / len(sqm_prices) if sqm_prices else 0

        report = {
            'market_analysis': {
                'radius_5km': {
                    'short_term_rentals': {
                        'count': short_term_stats['count'],
                        'avg_price_per_night': short_term_stats['avg_price'],
                        'price_range': short_term_stats['price_range']
                    },
                    'long_term_rentals': {
                        'count': long_term_stats['count'],
                        'avg_monthly_rent': long_term_stats['avg_price'],
                        'price_range': long_term_stats['price_range']
                    },
                    'sales': {
                        'count': sales_stats['count'],
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
                'total_properties_analyzed': short_term_stats['count'] + long_term_stats['count'] + sales_stats['count'],
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
    """Получение полного отчета (платный)"""
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    object_data = data.get('object_data')
    client_name = data.get('client_name')
    add_realtor_contacts = data.get('add_realtor_contacts', False)
    add_client_name = data.get('add_client_name', False)
    
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    
    try:
        # Проверяем баланс пользователя
        balance_result = supabase.table('users').select('balance').eq('telegram_id', telegram_id).execute()
        if balance_result.data:
            balance = balance_result.data[0].get('balance', 0)
        else:
            balance = 0
        
        report_cost = 1.0
        
        if balance < report_cost:
            return jsonify({
                'success': False,
                'insufficient_balance': True,
                'message': 'Недостаточно средств на балансе',
                'required': report_cost,
                'current': balance
            })
        
        # Списываем средства
        new_balance = balance - report_cost
        supabase.table('users').update({'balance': new_balance}).eq('telegram_id', telegram_id).execute()
        
        # Генерируем полный отчет
        full_report = generate_full_report(object_data, client_name, add_realtor_contacts, add_client_name)
        
        return jsonify({
            'success': True,
            'report': full_report,
            'balance_after': new_balance
        })
        
    except Exception as e:
        logger.error(f"Error generating full report: {e}")
        return jsonify({'error': 'Internal error'}), 500

def generate_full_report(object_data, client_name=None, add_realtor_contacts=False, add_client_name=False):
    """Генерация полного отчета"""
    
    report = {
        'object': object_data,
        'macro': {
            'inflation_rate': 2.5,
            'interest_rate': 4.2,
            'gdp_growth': 3.1,
            'unemployment_rate': 5.2
        },
        'investments': [
            {'type': 'Краткосрочная аренда', 'roi': '12-18%', 'risk': 'Средний'},
            {'type': 'Долгосрочная аренда', 'roi': '6-10%', 'risk': 'Низкий'},
            {'type': 'Перепродажа', 'roi': '15-25%', 'risk': 'Высокий'}
        ],
        'region': {
            'population_growth': 2.1,
            'infrastructure_development': 'Высокий',
            'tourism_growth': 8.5
        },
        'taxes': {
            'property_tax': 0.5,
            'income_tax': 15.0,
            'capital_gains_tax': 20.0
        },
        'risks': [
            'Риск изменения законодательства',
            'Риск изменения курса валют',
            'Риск природных катаклизмов'
        ]
    }
    
    if add_client_name and client_name:
        report['client_name'] = client_name
    
    if add_realtor_contacts:
        report['realtor_contacts'] = {
            'name': 'Иван Петров',
            'phone': '+90 555 123 4567',
            'email': 'ivan@aaadvisor.com',
            'company': 'Aaadvisor Real Estate'
        }
    
    return report

@app.route('/api/save_object', methods=['POST'])
def api_save_object():
    """Сохранение объекта в избранное"""
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    object_data = data.get('object_data')
    
    if not telegram_id or not object_data:
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        # Сохраняем объект в базу данных
        saved_object = {
            'user_id': telegram_id,
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
    """Генерация PDF отчета"""
    data = request.json or {}
    report = data.get('report')
    add_realtor_contacts = data.get('add_realtor_contacts', False)
    add_client_name = data.get('add_client_name', False)
    
    try:
        # Создаем PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Заголовок
        pdf.cell(0, 10, 'Полный отчет по недвижимости', ln=True, align='C')
        pdf.ln(10)
        
        # Информация об объекте
        if report.get('object'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Информация об объекте:', ln=True)
            pdf.set_font('Arial', '', 10)
            obj = report['object']
            pdf.cell(0, 8, f'Адрес: {obj.get("address", "Не указан")}', ln=True)
            pdf.cell(0, 8, f'Спален: {obj.get("bedrooms", "Не указано")}', ln=True)
            pdf.cell(0, 8, f'Цена: €{obj.get("purchase_price", "Не указана")}', ln=True)
            pdf.ln(5)
        
        # Макроэкономика
        if report.get('macro'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Макроэкономические показатели:', ln=True)
            pdf.set_font('Arial', '', 10)
            macro = report['macro']
            pdf.cell(0, 8, f'Инфляция: {macro.get("inflation_rate", 0)}%', ln=True)
            pdf.cell(0, 8, f'Ставка рефинансирования: {macro.get("interest_rate", 0)}%', ln=True)
            pdf.cell(0, 8, f'Рост ВВП: {macro.get("gdp_growth", 0)}%', ln=True)
            pdf.ln(5)
        
        # Сохраняем PDF во временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        temp_file.close()
        
        return jsonify({
            'success': True,
            'pdf_path': temp_file.name
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
    """Получение баланса пользователя"""
    data = request.json or {}
    telegram_id = data.get('telegram_id')
    
    if not telegram_id:
        return jsonify({'error': 'telegram_id required'}), 400
    
    try:
        result = supabase.table('users').select('balance').eq('telegram_id', telegram_id).execute()
        if result.data:
            balance = result.data[0].get('balance', 0)
        else:
            balance = 0
        
        return jsonify({'balance': balance})
        
    except Exception as e:
        logger.error(f"Error getting user balance: {e}")
        return jsonify({'error': 'Internal error'}), 500

@app.route('/api/send_pdf_to_client', methods=['POST'])
def api_send_pdf_to_client():
    """Отправка PDF клиенту"""
    data = request.json or {}
    realtor_telegram_id = data.get('realtor_telegram_id')
    client_name = data.get('client_name')
    client_telegram = data.get('client_telegram')
    pdf_path = data.get('pdf_path')
    
    if not all([realtor_telegram_id, client_telegram, pdf_path]):
        return jsonify({'error': 'Missing required data'}), 400
    
    try:
        # Здесь должна быть логика отправки PDF через Telegram Bot API
        # Пока возвращаем успех
        
        # Сохраняем информацию о клиенте
        client_data = {
            'realtor_telegram_id': realtor_telegram_id,
            'client_name': client_name,
            'client_telegram': client_telegram,
            'pdf_sent_at': datetime.datetime.now().isoformat()
        }
        
        supabase.table('client_communications').insert(client_data).execute()
        
        return jsonify({
            'success': True,
            'sent': True
        })
        
    except Exception as e:
        logger.error(f"Error sending PDF to client: {e}")
        return jsonify({'error': 'Internal error'}), 500

def run_flask():
    """Запуск Flask приложения"""
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Запускаем Telegram бота
    main() 
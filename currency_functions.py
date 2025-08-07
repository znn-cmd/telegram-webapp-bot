import os
import logging
import requests
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
supabase: Client = create_client(supabase_url, supabase_key)

# CurrencyLayer API ключ
CURRENCYLAYER_API_KEY = "c61dddb55d93e77ce5a2c8b91fb22694"

def get_currency_rates():
    """
    Получает курсы валют на сегодняшнюю дату.
    Сначала проверяет базу данных, если нет записи на сегодня - получает с API и сохраняет.
    """
    today = datetime.now().date()
    
    try:
        # Проверяем, есть ли курсы валют на сегодня в базе данных
        result = supabase.table('currency').select('*').eq('created_at', today.isoformat()).execute()
        
        if result.data and len(result.data) > 0:
            logger.info(f"✅ Курсы валют на {today} найдены в базе данных")
            return result.data[0]
        else:
            logger.info(f"📊 Курсы валют на {today} не найдены в базе данных, получаем с API")
            return fetch_and_save_currency_rates()
            
    except Exception as e:
        logger.error(f"❌ Ошибка при получении курсов валют: {e}")
        return None

def fetch_and_save_currency_rates():
    """
    Получает курсы валют с currencylayer.com API и сохраняет в базу данных
    """
    try:
        # Формируем URL для API запроса
        url = "http://api.currencylayer.com/live"
        params = {
            'access_key': CURRENCYLAYER_API_KEY,
            'source': 'EUR',  # Базовая валюта - евро
            'currencies': 'RUB,USD,TRY,AED,THB'  # Нужные валюты
        }
        
        logger.info(f"🌐 Запрос к currencylayer.com API: {url}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success'):
            quotes = data.get('quotes', {})
            
            # Формируем данные для сохранения
            currency_data = {
                'created_at': datetime.now().isoformat(),
                'euro': 1.0,  # Базовая валюта всегда 1.0
                'rub': quotes.get('EURRUB', 0),
                'usd': quotes.get('EURUSD', 0),
                'try': quotes.get('EURTRY', 0),
                'aed': quotes.get('EURAED', 0),
                'thb': quotes.get('EURTHB', 0)
            }
            
            # Сохраняем в базу данных
            result = supabase.table('currency').insert(currency_data).execute()
            
            if result.data:
                logger.info(f"✅ Курсы валют успешно сохранены в базу данных: {currency_data}")
                return currency_data
            else:
                logger.error("❌ Ошибка при сохранении курсов валют в базу данных")
                return None
                
        else:
            logger.error(f"❌ Ошибка API currencylayer.com: {data.get('error', {}).get('info', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка сетевого запроса к currencylayer.com: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка при получении курсов валют: {e}")
        return None

def format_currency_rates_for_report(currency_data):
    """
    Форматирует курсы валют для отображения в отчете
    """
    if not currency_data:
        return "Курсы валют: недоступны"
    
    try:
        rates = []
        if currency_data.get('rub'):
            rates.append(f"RUB: {currency_data['rub']:.4f}")
        if currency_data.get('usd'):
            rates.append(f"USD: {currency_data['usd']:.4f}")
        if currency_data.get('try'):
            rates.append(f"TRY: {currency_data['try']:.4f}")
        if currency_data.get('aed'):
            rates.append(f"AED: {currency_data['aed']:.4f}")
        if currency_data.get('thb'):
            rates.append(f"THB: {currency_data['thb']:.4f}")
        
        return f"Курсы валют (EUR): {' | '.join(rates)}"
    except Exception as e:
        logger.error(f"❌ Ошибка форматирования курсов валют: {e}")
        return "Курсы валют: ошибка форматирования"

def convert_to_euro(value, currency_code, currency_rates):
    """
    Конвертирует значение в евро по курсу валют
    
    Args:
        value: Значение для конвертации
        currency_code: Код валюты (TRY, USD, RUB, AED, THB)
        currency_rates: Курсы валют из базы данных
    
    Returns:
        float: Значение в евро
    """
    if not value or not currency_rates:
        return value
    
    try:
        # Получаем курс для нужной валюты
        rate_key = currency_code.lower()
        rate = currency_rates.get(rate_key, 0)
        
        if rate and rate > 0:
            # Конвертируем в евро (делим на курс, так как курс показывает EUR/валюта)
            return float(value) / rate
        else:
            logger.warning(f"⚠️ Курс для {currency_code} не найден или равен 0")
            return value
            
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Ошибка конвертации {value} {currency_code} в евро: {e}")
        return value

def convert_market_data_to_euro(market_data, currency_rates):
    """
    Конвертирует все цены в market_data в евро
    
    Args:
        market_data: Данные рынка недвижимости
        currency_rates: Курсы валют
    
    Returns:
        dict: Данные с конвертированными ценами
    """
    if not currency_rates:
        return market_data
    
    converted_data = {}
    
    # Конвертируем общие данные
    if market_data.get('general_data'):
        general = market_data['general_data'].copy()
        for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                   'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                   'price_for_sale', 'price_for_rent']:
            if general.get(key) and general[key] != 'н/д':
                general[key] = convert_to_euro(general[key], 'TRY', currency_rates)
        converted_data['general_data'] = general
    
    # Конвертируем данные по типам домов
    if market_data.get('house_type_data'):
        if isinstance(market_data['house_type_data'], list):
            converted_data['house_type_data'] = []
            for record in market_data['house_type_data']:
                converted_record = record.copy()
                for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                           'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                           'price_for_sale', 'price_for_rent']:
                    if converted_record.get(key) and converted_record[key] != 'н/д':
                        converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
                converted_data['house_type_data'].append(converted_record)
        else:
            converted_record = market_data['house_type_data'].copy()
            for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                       'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                       'price_for_sale', 'price_for_rent']:
                if converted_record.get(key) and converted_record[key] != 'н/д':
                    converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
            converted_data['house_type_data'] = converted_record
    
    # Конвертируем данные по возрасту
    if market_data.get('age_data'):
        if isinstance(market_data['age_data'], list):
            converted_data['age_data'] = []
            for record in market_data['age_data']:
                converted_record = record.copy()
                for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                           'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                           'price_for_sale', 'price_for_rent']:
                    if converted_record.get(key) and converted_record[key] != 'н/д':
                        converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
                converted_data['age_data'].append(converted_record)
        else:
            converted_record = market_data['age_data'].copy()
            for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                       'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                       'price_for_sale', 'price_for_rent']:
                if converted_record.get(key) and converted_record[key] != 'н/д':
                    converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
            converted_data['age_data'] = converted_record
    
    # Конвертируем данные по этажам
    if market_data.get('floor_segment_data'):
        if isinstance(market_data['floor_segment_data'], list):
            converted_data['floor_segment_data'] = []
            for record in market_data['floor_segment_data']:
                converted_record = record.copy()
                for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                           'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                           'price_for_sale', 'price_for_rent']:
                    if converted_record.get(key) and converted_record[key] != 'н/д':
                        converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
                converted_data['floor_segment_data'].append(converted_record)
        else:
            converted_record = market_data['floor_segment_data'].copy()
            for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                       'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                       'price_for_sale', 'price_for_rent']:
                if converted_record.get(key) and converted_record[key] != 'н/д':
                    converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
            converted_data['floor_segment_data'] = converted_record
    
    # Конвертируем данные по отоплению
    if market_data.get('heating_data'):
        if isinstance(market_data['heating_data'], list):
            converted_data['heating_data'] = []
            for record in market_data['heating_data']:
                converted_record = record.copy()
                for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                           'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                           'price_for_sale', 'price_for_rent']:
                    if converted_record.get(key) and converted_record[key] != 'н/д':
                        converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
                converted_data['heating_data'].append(converted_record)
        else:
            converted_record = market_data['heating_data'].copy()
            for key in ['unit_price_for_sale', 'min_unit_price_for_sale', 'max_unit_price_for_sale',
                       'unit_price_for_rent', 'min_unit_price_for_rent', 'max_unit_price_for_rent',
                       'price_for_sale', 'price_for_rent']:
                if converted_record.get(key) and converted_record[key] != 'н/д':
                    converted_record[key] = convert_to_euro(converted_record[key], 'TRY', currency_rates)
            converted_data['heating_data'] = converted_record
    
    return converted_data

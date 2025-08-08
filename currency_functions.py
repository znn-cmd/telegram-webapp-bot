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

def get_currency_rate_for_date(target_date=None):
    """
    Получает курс валюты для указанной даты из таблицы currency.
    Если записи нет, получает с currencylayer.com и сохраняет в базу.
    
    Args:
        target_date (datetime): Дата для получения курса (по умолчанию сегодня)
    
    Returns:
        dict: Словарь с курсами валют или None если ошибка
    """
    try:
        if target_date is None:
            target_date = datetime.now()
        
        # Форматируем дату для поиска в базе
        date_str = target_date.strftime('%Y-%m-%d')
        
        # Ищем запись в таблице currency для указанной даты
        currency_query = supabase.table('currency').select('*').gte('created_at', f'{date_str} 00:00:00').lt('created_at', f'{date_str} 23:59:59').order('created_at', desc=True).limit(1)
        currency_result = currency_query.execute()
        
        if currency_result.data and len(currency_result.data) > 0:
            logger.info(f"✅ Найдена запись курса валют для {date_str}: {currency_result.data[0]}")
            return currency_result.data[0]
        
        # Если записи нет, получаем с currencylayer.com
        logger.info(f"❌ Запись курса валют для {date_str} не найдена, получаем с currencylayer.com")
        return fetch_and_save_currency_rates(target_date)
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения курса валют: {e}")
        return None

def fetch_and_save_currency_rates(target_date=None):
    """
    Получает курсы валют с currencylayer.com и сохраняет в базу данных.
    
    Args:
        target_date (datetime): Дата для получения курсов (по умолчанию сегодня)
    
    Returns:
        dict: Словарь с курсами валют или None если ошибка
    """
    try:
        if target_date is None:
            target_date = datetime.now()
        
        # Форматируем дату для API запроса
        date_str = target_date.strftime('%Y-%m-%d')
        
        # Запрос к currencylayer.com API
        url = "http://api.currencylayer.com/historical"
        params = {
            'access_key': CURRENCYLAYER_API_KEY,
            'date': date_str,
            'base': 'EUR',
            'currencies': 'RUB,USD,TRY,AED,THB'
        }
        
        logger.info(f"🔍 Запрос курсов валют с currencylayer.com для {date_str}")
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"❌ Ошибка API currencylayer.com: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        if not data.get('success'):
            logger.error(f"❌ Ошибка currencylayer.com API: {data.get('error', {}).get('info', 'Unknown error')}")
            return None
        
        # Извлекаем курсы валют
        quotes = data.get('quotes', {})
        
        # Формируем данные для сохранения в базу
        currency_data = {
            'created_at': target_date.isoformat(),
            'rub': quotes.get('EURRUB', 1.0),
            'usd': quotes.get('EURUSD', 1.0),
            'euro': 1.0,  # Базовая валюта
            'try': quotes.get('EURTRY', 1.0),
            'aed': quotes.get('EURAED', 1.0),
            'thb': quotes.get('EURTHB', 1.0)
        }
        
        # Сохраняем в базу данных
        logger.info(f"💾 Сохраняем курсы валют в базу: {currency_data}")
        supabase.table('currency').insert(currency_data).execute()
        
        logger.info(f"✅ Курсы валют успешно получены и сохранены для {date_str}")
        return currency_data
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения курсов валют с currencylayer.com: {e}")
        return None

def convert_turkish_data_to_eur(data, currency_rate):
    """
    Конвертирует турецкие данные в евро используя курс валюты.
    
    Args:
        data (dict): Данные для конвертации
        currency_rate (dict): Курс валюты (TRY/EUR)
    
    Returns:
        dict: Конвертированные данные в евро
    """
    if not currency_rate or 'try' not in currency_rate:
        logger.warning("❌ Курс валюты не найден, возвращаем исходные данные")
        return data
    
    try_rate = currency_rate['try']
    logger.info(f"💱 Конвертируем данные в EUR используя курс TRY/EUR: {try_rate}")
    
    def convert_price(price):
        """Конвертирует цену из TRY в EUR"""
        if price is None or price == 'н/д':
            return price
        try:
            return float(price) / try_rate
        except (ValueError, TypeError):
            return price
    
    def convert_data_recursive(obj):
        """Рекурсивно конвертирует все числовые значения в объекте"""
        if isinstance(obj, dict):
            converted = {}
            for key, value in obj.items():
                if isinstance(value, (int, float)) and key in ['unit_price_for_sale', 'min_unit_price_for_sale', 
                                                             'max_unit_price_for_sale', 'unit_price_for_rent', 
                                                             'min_unit_price_for_rent', 'max_unit_price_for_rent',
                                                             'price_for_sale', 'price_for_rent']:
                    converted[key] = convert_price(value)
                elif isinstance(value, dict):
                    converted[key] = convert_data_recursive(value)
                elif isinstance(value, list):
                    converted[key] = [convert_data_recursive(item) for item in value]
                else:
                    converted[key] = value
            return converted
        elif isinstance(obj, list):
            return [convert_data_recursive(item) for item in obj]
        else:
            return obj
    
    return convert_data_recursive(data)

def is_turkish_location(location_components):
    """
    Проверяет, находится ли локация в Турции.
    
    Args:
        location_components (dict): Компоненты локации
    
    Returns:
        bool: True если локация в Турции
    """
    if not location_components:
        return False
    
    # Проверяем по стране
    country = location_components.get('country', '').lower()
    country_code = location_components.get('country_code', '').lower()
    
    turkish_indicators = ['turkey', 'türkiye', 'tr', 'tur']
    
    return country in turkish_indicators or country_code in turkish_indicators

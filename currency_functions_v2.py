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

def get_latest_currency_rate():
    """
    Получает последнюю доступную запись курса валют из базы данных.
    
    Returns:
        dict: Последняя запись курса валют или None если нет записей
    """
    try:
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(1).execute()
        if result.data and len(result.data) > 0:
            latest_record = result.data[0]
            
            # Проверяем, что все обязательные поля присутствуют
            required_fields = ['rub', 'usd', 'euro', 'try', 'aed', 'thb']
            missing_fields = [field for field in required_fields if field not in latest_record or latest_record[field] is None]
            
            if missing_fields:
                logger.warning(f"⚠️ В последней записи отсутствуют поля: {missing_fields}")
                # Возвращаем None, чтобы использовать значения по умолчанию
                return None
            
            # Проверяем, что все значения числовые и положительные
            for field in required_fields:
                if not isinstance(latest_record[field], (int, float)) or latest_record[field] <= 0:
                    logger.warning(f"⚠️ Некорректное значение в последней записи для {field}: {latest_record[field]}")
                    return None
            
            logger.info(f"✅ Используем последнюю доступную запись курса валют: {latest_record}")
            return latest_record
        else:
            logger.warning("⚠️ Нет доступных записей курса валют в базе данных")
            return None
    except Exception as e:
        logger.error(f"❌ Ошибка получения последней записи курса валют: {e}")
        return None

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
        return get_latest_currency_rate()

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
            # Если API недоступен, используем последнюю доступную запись
            return get_latest_currency_rate()
        
        data = response.json()
        
        if not data.get('success'):
            logger.error(f"❌ Ошибка currencylayer.com API: {data.get('error', {}).get('info', 'Unknown error')}")
            # Если API недоступен, используем последнюю доступную запись
            return get_latest_currency_rate()
        
        # Извлекаем курсы валют
        quotes = data.get('quotes', {})
        
        # Проверяем, что все необходимые курсы валют получены
        required_currencies = {
            'EURRUB': 'rub',
            'EURUSD': 'usd', 
            'EURTRY': 'try',
            'EURAED': 'aed',
            'EURTHB': 'thb'
        }
        
        # Формируем данные для сохранения в базу с проверкой
        currency_data = {
            'created_at': target_date.isoformat(),
            'euro': 1.0  # Базовая валюта всегда = 1.0
        }
        
        # Заполняем курсы валют с проверкой
        for api_key, db_key in required_currencies.items():
            if api_key in quotes and quotes[api_key] is not None:
                currency_data[db_key] = quotes[api_key]
            else:
                logger.warning(f"⚠️ Курс {api_key} не получен от API, используем значение по умолчанию")
                # Используем последнюю доступную запись или значение по умолчанию
                latest_rate = get_latest_currency_rate()
                if latest_rate and db_key in latest_rate:
                    currency_data[db_key] = latest_rate[db_key]
                else:
                    # Если нет последней записи, используем разумные значения по умолчанию
                    default_rates = {
                        'rub': 90.0,  # Примерный курс RUB/EUR
                        'usd': 1.16,  # Примерный курс USD/EUR
                        'try': 46.0,  # Примерный курс TRY/EUR
                        'aed': 4.26,  # Примерный курс AED/EUR
                        'thb': 37.6   # Примерный курс THB/EUR
                    }
                    currency_data[db_key] = default_rates.get(db_key, 1.0)
        
        # Проверяем, что все поля заполнены
        required_fields = ['rub', 'usd', 'euro', 'try', 'aed', 'thb']
        missing_fields = [field for field in required_fields if field not in currency_data or currency_data[field] is None]
        
        if missing_fields:
            logger.error(f"❌ Отсутствуют обязательные поля: {missing_fields}")
            # Используем последнюю доступную запись
            return get_latest_currency_rate()
        
        # Валидация данных - проверяем, что все значения числовые и положительные
        for field in required_fields:
            if not isinstance(currency_data[field], (int, float)) or currency_data[field] <= 0:
                logger.error(f"❌ Некорректное значение для {field}: {currency_data[field]}")
                # Используем последнюю доступную запись
                return get_latest_currency_rate()
        
        # Сохраняем в базу данных
        logger.info(f"💾 Сохраняем курсы валют в базу: {currency_data}")
        try:
            supabase.table('currency').insert(currency_data).execute()
            logger.info(f"✅ Курсы валют успешно получены и сохранены для {date_str}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось сохранить в базу: {e}")
            # Возвращаем данные даже если сохранение не удалось
            return currency_data
        
        return currency_data
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения курсов валют с currencylayer.com: {e}")
        # Используем последнюю доступную запись
        return get_latest_currency_rate()

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

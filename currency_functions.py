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
        
        # Сначала проверяем, есть ли уже запись для этой даты
        existing_query = supabase.table('currency').select('*').gte('created_at', f'{date_str} 00:00:00').lt('created_at', f'{date_str} 23:59:59').order('created_at', desc=True).limit(1)
        existing_result = existing_query.execute()
        
        if existing_result.data and len(existing_result.data) > 0:
            logger.info(f"✅ Запись курса валют для {date_str} уже существует: {existing_result.data[0]}")
            return existing_result.data[0]
        
        # Запрос к currencylayer.com API (используем USD как базовую валюту)
        url = "http://api.currencylayer.com/historical"
        params = {
            'access_key': CURRENCYLAYER_API_KEY,
            'date': date_str,
            'source': 'USD',
            'currencies': 'RUB,TRY,AED,THB,EUR'
        }
        
        logger.info(f"🔍 Запрос курсов валют с currencylayer.com для {date_str}")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"❌ Ошибка API currencylayer.com: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        logger.info(f"🔍 Ответ API: {data}")
        
        if not data.get('success'):
            logger.error(f"❌ Ошибка currencylayer.com API: {data.get('error', {}).get('info', 'Unknown error')}")
            return None
        
        # Извлекаем курсы валют
        quotes = data.get('quotes', {})
        logger.info(f"🔍 Полученные курсы: {quotes}")
        
        # Конвертируем курсы из USD в EUR
        # Сначала получаем курс EUR/USD
        eur_usd_rate = quotes.get('USDEUR')
        if not eur_usd_rate:
            logger.error("❌ Не удалось получить курс EUR/USD")
            return None
        
        # Конвертируем все курсы в EUR
        currency_data = {
            'created_at': target_date.isoformat(),
            'rub': quotes.get('USDRUB', 1.0) / eur_usd_rate if quotes.get('USDRUB') else 1.0,
            'usd': 1.0 / eur_usd_rate,  # USD к EUR
            'euro': 1.0,  # Базовая валюта
            'try': quotes.get('USDTRY', 1.0) / eur_usd_rate if quotes.get('USDTRY') else 1.0,
            'aed': quotes.get('USDAED', 1.0) / eur_usd_rate if quotes.get('USDAED') else 1.0,
            'thb': quotes.get('USDTHB', 1.0) / eur_usd_rate if quotes.get('USDTHB') else 1.0
        }
        
        # Проверяем, что все курсы получены корректно
        required_currencies = ['rub', 'usd', 'try', 'aed', 'thb']
        missing_currencies = [curr for curr in required_currencies if currency_data.get(curr) == 1.0]
        
        if missing_currencies:
            logger.warning(f"⚠️ Не удалось получить курсы для валют: {missing_currencies}")
            # Если не удалось получить курсы, возвращаем None
            return None
        
        # Сохраняем в базу данных
        logger.info(f"💾 Сохраняем курсы валют в базу: {currency_data}")
        
        # Создаем копию данных для вставки
        insert_data = currency_data.copy()
        
        try:
            # Убираем поле id из данных, чтобы Supabase сам сгенерировал его
            if 'id' in insert_data:
                del insert_data['id']
            
            # Дополнительная проверка перед вставкой
            check_query = supabase.table('currency').select('*').gte('created_at', f'{date_str} 00:00:00').lt('created_at', f'{date_str} 23:59:59').order('created_at', desc=True).limit(1)
            check_result = check_query.execute()
            if check_result.data and len(check_result.data) > 0:
                logger.info(f"✅ Запись уже существует, возвращаем её: {check_result.data[0]}")
                return check_result.data[0]
            
            # Пытаемся вставить новую запись
            insert_result = supabase.table('currency').insert(insert_data).execute()
            logger.info(f"✅ Курсы валют успешно получены и сохранены для {date_str}")
            
            # Если вставка прошла успешно, возвращаем вставленные данные
            if insert_result.data and len(insert_result.data) > 0:
                return insert_result.data[0]
            else:
                return currency_data
                
        except Exception as insert_error:
            logger.warning(f"⚠️ Ошибка при сохранении курсов валют: {insert_error}")
            
            # Проверяем, является ли это ошибкой RLS
            if 'row-level security policy' in str(insert_error) or '42501' in str(insert_error):
                logger.warning("🔒 Обнаружена ошибка RLS политики. Пытаемся получить существующую запись...")
                
                # Пытаемся получить существующую запись
                existing_query = supabase.table('currency').select('*').gte('created_at', f'{date_str} 00:00:00').lt('created_at', f'{date_str} 23:59:59').order('created_at', desc=True).limit(1)
                existing_result = existing_query.execute()
                if existing_result.data and len(existing_result.data) > 0:
                    logger.info(f"✅ Используем существующую запись курса валют для {date_str}")
                    return existing_result.data[0]
                else:
                    logger.warning("⚠️ RLS политика блокирует вставку, но существующая запись не найдена. Возвращаем данные без сохранения.")
                    # Возвращаем данные без сохранения в базу
                    return currency_data
            elif 'duplicate key' in str(insert_error) or '23505' in str(insert_error):
                logger.warning("🔑 Обнаружена ошибка дублирования ключа. Пытаемся получить существующую запись...")
                
                # Пытаемся получить существующую запись
                existing_query = supabase.table('currency').select('*').gte('created_at', f'{date_str} 00:00:00').lt('created_at', f'{date_str} 23:59:59').order('created_at', desc=True).limit(1)
                existing_result = existing_query.execute()
                if existing_result.data and len(existing_result.data) > 0:
                    logger.info(f"✅ Используем существующую запись курса валют для {date_str}")
                    return existing_result.data[0]
                else:
                    logger.warning("⚠️ Ошибка дублирования ключа, но существующая запись не найдена. Возвращаем данные без сохранения.")
                    # Возвращаем данные без сохранения в базу
                    return currency_data
            else:
                logger.warning(f"⚠️ Неизвестная ошибка при сохранении: {insert_error}. Возвращаем данные без сохранения.")
                # Возвращаем данные без сохранения в базу
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
    logger.info(f"📊 Пример: 1000 TRY = {1000/try_rate:.2f} EUR")
    
    def convert_price(price):
        """Конвертирует цену из TRY в EUR"""
        if price is None or price == 'н/д':
            return price
        try:
            # try_rate уже представлен как TRY/EUR, поэтому делим на него
            converted_price = float(price) / try_rate
            logger.debug(f"💱 Конвертация: {price} TRY / {try_rate} = {converted_price:.2f} EUR")
            return converted_price
        except (ValueError, TypeError):
            logger.warning(f"⚠️ Не удалось конвертировать цену: {price}")
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

def get_current_currency_rate():
    """
    Получает текущий курс валют для сегодняшней даты.
    
    Returns:
        dict: Словарь с курсами валют или None если ошибка
    """
    return get_currency_rate_for_date(datetime.now())

def format_currency_info(currency_rate, language='en'):
    """
    Форматирует информацию о курсе валют для отображения в отчете.
    
    Args:
        currency_rate (dict): Курс валюты
        language (str): Язык отчета
    
    Returns:
        str: Отформатированная информация о курсе валют
    """
    if not currency_rate:
        return ""
    
    try:
        # Форматируем дату
        created_at = currency_rate.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                date_obj = created_at
            date_str = date_obj.strftime('%d.%m.%Y')
        else:
            date_str = datetime.now().strftime('%d.%m.%Y')
        
        # Форматируем курсы
        try_rate = currency_rate.get('try', 0)
        usd_rate = currency_rate.get('usd', 0)
        rub_rate = currency_rate.get('rub', 0)
        
        currency_info = f"Курс валют на {date_str}: 1 EUR = {try_rate:.4f} TRY, {usd_rate:.4f} USD, {rub_rate:.4f} RUB"
        
        return currency_info
    except Exception as e:
        logger.error(f"Ошибка форматирования информации о курсе валют: {e}")
        return ""

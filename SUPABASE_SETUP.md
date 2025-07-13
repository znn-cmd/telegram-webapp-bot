# Настройка Supabase для бота недвижимости

## 1. Создание проекта в Supabase

1. Перейдите на [supabase.com](https://supabase.com)
2. Создайте новый проект
3. Выберите регион (рекомендуется ближайший к вам)
4. Дождитесь завершения создания проекта

## 2. Получение ключей доступа

1. В Dashboard вашего проекта перейдите в **Settings** → **API**
2. Скопируйте:
   - **Project URL** (например: `https://your-project.supabase.co`)
   - **anon public** ключ

## 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```

Или установите переменные окружения:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your_anon_key_here"
```

## 4. Создание таблиц в Supabase

### Способ 1: Через SQL Editor

1. В Dashboard перейдите в **SQL Editor**
2. Создайте новый запрос
3. Скопируйте содержимое файла `supabase_schema.sql`
4. Выполните запрос

### Способ 2: Через командную строку

```bash
# Установите Supabase CLI
npm install -g supabase

# Войдите в аккаунт
supabase login

# Инициализируйте проект
supabase init

# Создайте миграцию
supabase migration new create_real_estate_tables

# Скопируйте содержимое supabase_schema.sql в созданный файл миграции
# Затем выполните:
supabase db push
```

## 5. Проверка создания таблиц

В Dashboard перейдите в **Table Editor** и убедитесь, что созданы таблицы:

- `short_term_rentals`
- `long_term_rentals`
- `property_sales`
- `historical_prices`
- `market_statistics`

## 6. Настройка Row Level Security (RLS)

Таблицы уже настроены с RLS и политиками для публичного чтения. Если нужно изменить:

1. Перейдите в **Authentication** → **Policies**
2. Для каждой таблицы создайте политику:
   - **Policy Name**: `Allow public read access`
   - **Target roles**: `public`
   - **Using expression**: `true`
   - **Operation**: `SELECT`

## 7. Установка зависимостей Python

```bash
pip install requests
```

## 8. Загрузка тестовых данных

```bash
python load_test_data_supabase.py
```

## 9. Проверка данных

В Dashboard перейдите в **Table Editor** и проверьте, что данные загружены:

```sql
-- Проверка количества записей
SELECT 'short_term_rentals' as table_name, COUNT(*) as count FROM short_term_rentals
UNION ALL
SELECT 'long_term_rentals', COUNT(*) FROM long_term_rentals
UNION ALL
SELECT 'property_sales', COUNT(*) FROM property_sales
UNION ALL
SELECT 'historical_prices', COUNT(*) FROM historical_prices
UNION ALL
SELECT 'market_statistics', COUNT(*) FROM market_statistics;
```

## 10. Настройка API для бота

### Обновление app.py для работы с Supabase

```python
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def make_supabase_request(endpoint, method='GET', data=None):
    """Выполнение запроса к Supabase API"""
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=data)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

@app.route('/api/properties/short-term', methods=['GET'])
def get_short_term_properties():
    """Получение краткосрочной аренды"""
    params = request.args.to_dict()
    
    # Построение запроса к Supabase
    query_params = {}
    if 'district' in params:
        query_params['district'] = f"eq.{params['district']}"
    if 'min_price' in params:
        query_params['price_per_night'] = f"gte.{params['min_price']}"
    if 'max_price' in params:
        query_params['price_per_night'] = f"lte.{params['max_price']}"
    if 'bedrooms' in params:
        query_params['bedrooms'] = f"eq.{params['bedrooms']}"
    
    result = make_supabase_request('short_term_rentals', data=query_params)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/api/properties/long-term', methods=['GET'])
def get_long_term_properties():
    """Получение долгосрочной аренды"""
    params = request.args.to_dict()
    
    query_params = {}
    if 'district' in params:
        query_params['district'] = f"eq.{params['district']}"
    if 'min_price' in params:
        query_params['monthly_rent'] = f"gte.{params['min_price']}"
    if 'max_price' in params:
        query_params['monthly_rent'] = f"lte.{params['max_price']}"
    
    result = make_supabase_request('long_term_rentals', data=query_params)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/api/properties/sales', methods=['GET'])
def get_property_sales():
    """Получение продажи недвижимости"""
    params = request.args.to_dict()
    
    query_params = {}
    if 'district' in params:
        query_params['district'] = f"eq.{params['district']}"
    if 'min_price' in params:
        query_params['asking_price'] = f"gte.{params['min_price']}"
    if 'max_price' in params:
        query_params['asking_price'] = f"lte.{params['max_price']}"
    
    result = make_supabase_request('property_sales', data=query_params)
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/api/market/stats/<district>', methods=['GET'])
def get_market_stats(district):
    """Получение рыночной статистики по району"""
    query_params = {
        'district': f"eq.{district}",
        'order': 'date.desc',
        'limit': '1'
    }
    
    result = make_supabase_request('market_statistics', data=query_params)
    
    if result and len(result) > 0:
        return jsonify(result[0])
    else:
        return jsonify({'error': 'No data found'}), 404

@app.route('/api/roi/calculate', methods=['POST'])
def calculate_roi():
    """Расчет ROI"""
    data = request.json
    
    # Вызов функции Supabase для расчета ROI
    result = make_supabase_request(
        'rpc/calculate_roi',
        method='POST',
        data=data
    )
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Failed to calculate ROI'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## 11. Полезные SQL запросы для тестирования

### Поиск недвижимости по району
```sql
SELECT * FROM short_term_rentals 
WHERE district = 'Lara' 
AND price_per_night BETWEEN 100 AND 200
ORDER BY price_per_night;
```

### Анализ цен по районам
```sql
SELECT 
    district,
    AVG(price_per_night) as avg_price,
    COUNT(*) as property_count
FROM short_term_rentals 
GROUP BY district 
ORDER BY avg_price DESC;
```

### Исторические данные цен
```sql
SELECT 
    property_id,
    date,
    price,
    price_type
FROM historical_prices 
WHERE property_id = 'airbnb_001'
ORDER BY date;
```

### Рыночная статистика
```sql
SELECT * FROM market_statistics 
WHERE district = 'Lara' 
ORDER BY date DESC 
LIMIT 5;
```

## 12. Мониторинг и логи

В Dashboard Supabase вы можете:

1. **Monitor** → **Logs** - просмотр логов запросов
2. **Database** → **Logs** - просмотр SQL логов
3. **Table Editor** - просмотр и редактирование данных
4. **SQL Editor** - выполнение SQL запросов

## 13. Безопасность

- RLS включен для всех таблиц
- Публичный доступ только для чтения
- Для записи данных используйте сервисный ключ (Service Role Key)
- Храните ключи в переменных окружения
- Не коммитьте `.env` файл в Git

## 14. Масштабирование

Supabase автоматически масштабируется:
- До 500MB базы данных бесплатно
- До 2GB в платном плане
- Автоматические бэкапы
- Репликация для высокой доступности

## Поддержка

При возникновении проблем:

1. Проверьте правильность URL и ключей
2. Убедитесь, что таблицы созданы
3. Проверьте политики RLS
4. Посмотрите логи в Dashboard
5. Проверьте формат данных в CSV файлах 
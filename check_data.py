import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def check_table_count(table_name):
    """Проверка количества записей в таблице"""
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=count"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return len(data)
        else:
            print(f"❌ Ошибка при проверке таблицы {table_name}: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Ошибка запроса к {table_name}: {e}")
        return 0

def check_table_content(table_name, limit=5):
    """Просмотр содержимого таблицы"""
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit={limit}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Содержимое таблицы {table_name}:")
            for i, record in enumerate(data, 1):
                print(f"  {i}. {record}")
            return data
        else:
            print(f"❌ Ошибка при получении данных из {table_name}: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка запроса к {table_name}: {e}")
        return []

def main():
    print("🔍 Проверка данных в Supabase...")
    
    tables = [
        'short_term_rentals',
        'long_term_rentals', 
        'property_sales',
        'historical_prices',
        'market_statistics'
    ]
    
    total_records = 0
    
    for table in tables:
        count = check_table_count(table)
        print(f"📊 {table}: {count} записей")
        total_records += count
        
        # Показываем содержимое таблицы
        if count > 0:
            check_table_content(table)
    
    print(f"\n✅ Всего записей в базе данных: {total_records}")
    
    if total_records > 0:
        print("🎉 Данные успешно загружены! Ошибки 409 означали, что данные уже существовали.")
    else:
        print("⚠️ Данные не найдены. Возможно, есть проблемы с правами доступа.")

if __name__ == "__main__":
    main() 
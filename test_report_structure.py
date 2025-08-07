#!/usr/bin/env python3
"""
Тест структуры отчета
"""

import requests
import json

def test_report_structure():
    """Тест структуры отчета"""
    url = "http://localhost:8080/api/generate_report"
    
    data = {
        "address": "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye",
        "bedrooms": 3,
        "price": 111000,
        "lat": 36.8969,
        "lng": 30.7133,
        "language": "ru",
        "telegram_id": 1952374904
    }
    
    try:
        print(f"🔍 Тестируем структуру отчета")
        
        response = requests.post(url, json=data)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            report_text = result.get('report_text', '')
            
            print(f"✅ Отчет сгенерирован успешно")
            print(f"📊 Размер отчета: {len(report_text)} символов")
            
            # Проверяем структуру отчета
            lines = report_text.split('\n')
            
            print(f"\n📄 Структура отчета:")
            print("=" * 50)
            
            # Ищем ключевые секции
            sections = {
                'Коды локаций': False,
                'Google Places API': False,
                'Nominatim': False,
                'Общий тренд': False,
                'Тренд по количеству спален': False,
                'Тренд по возрасту объекта': False,
                'Тренд по этажу объекта': False,
                'Тренд по типу отопления': False
            }
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                if '=== КОДЫ ЛОКАЦИЙ (только для администраторов) ===' in line:
                    sections['Коды локаций'] = True
                    print(f"✅ Найдены коды локаций (строка {i+1})")
                    
                elif '=== ДАННЫЕ GOOGLE PLACES API (только для администраторов) ===' in line:
                    sections['Google Places API'] = True
                    print(f"✅ Найдены данные Google Places API (только для админов) (строка {i+1})")
                    
                elif '=== ДАННЫЕ NOMINATIM (OpenStreetMap) (только для администраторов) ===' in line:
                    sections['Nominatim'] = True
                    print(f"✅ Найдены данные Nominatim (только для админов) (строка {i+1})")
                    
                elif '=== ОБЩИЙ ТРЕНД ===' in line:
                    sections['Общий тренд'] = True
                    print(f"✅ Найден общий тренд (строка {i+1})")
                    
                elif '=== ТРЕНД ПО КОЛИЧЕСТВУ СПАЛЕН ===' in line:
                    sections['Тренд по количеству спален'] = True
                    print(f"✅ Найден тренд по количеству спален (строка {i+1})")
                    
                elif '=== ТРЕНД ПО ВОЗРАСТУ ОБЪЕКТА ===' in line:
                    sections['Тренд по возрасту объекта'] = True
                    print(f"✅ Найден тренд по возрасту объекта (строка {i+1})")
                    
                elif '=== ТРЕНД ПО ЭТАЖУ ОБЪЕКТА ===' in line:
                    sections['Тренд по этажу объекта'] = True
                    print(f"✅ Найден тренд по этажу объекта (строка {i+1})")
                    
                elif '=== ТРЕНД ПО ТИПУ ОТОПЛЕНИЯ ===' in line:
                    sections['Тренд по типу отопления'] = True
                    print(f"✅ Найден тренд по типу отопления (строка {i+1})")
                    
                elif 'Данные объекта:' in line:
                    print(f"❌ НАЙДЕН ДУБЛИРУЮЩИЙСЯ БЛОК 'Данные объекта' (строка {i+1})")
                    
            print(f"\n📋 Результаты проверки:")
            for section, found in sections.items():
                status = "✅" if found else "❌"
                print(f"  {status} {section}: {'Найден' if found else 'НЕ найден'}")
                
            # Проверяем коды локаций
            location_lines = [line for line in lines if 'ID:' in line]
            if location_lines:
                print(f"\n📋 Коды локаций:")
                for line in location_lines:
                    print(f"  - {line.strip()}")
            else:
                print(f"\n❌ Коды локаций не найдены")
                
        else:
            print(f"❌ Ошибка: {response.json()}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🔧 Тестирование структуры отчета")
    print("=" * 50)
    
    test_report_structure()
    
    print("\n📝 Ожидаемые изменения:")
    print("1. ✅ Убран дублирующийся блок 'Данные объекта'")
    print("2. ✅ Коды локаций отображаются только для администраторов")
    print("3. ✅ Восстановлены данные Google Places API и Nominatim")
    print("4. ✅ Структура отчета стала чище") 
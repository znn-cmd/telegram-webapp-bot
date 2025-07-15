#!/usr/bin/env python3
"""
Тест для проверки работы отправки сохраненных отчетов
"""

import requests
import json

def test_saved_report_sending():
    """Тестирует отправку сохраненных отчетов"""
    
    # URL для тестирования
    base_url = "http://localhost:5000"
    
    print("🧪 Тест отправки сохраненных отчетов:")
    print("-" * 50)
    
    # Тестовые данные
    test_data = {
        "report_id": 1,  # ID существующего отчета
        "telegram_id": 123456789  # Тестовый Telegram ID
    }
    
    try:
        # Отправляем запрос на генерацию PDF
        response = requests.post(
            f"{base_url}/api/send_saved_report_pdf",
            headers={'Content-Type': 'application/json'},
            json=test_data
        )
        
        print(f"📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успех: {data.get('success')}")
            print(f"📄 PDF путь: {data.get('pdf_path')}")
            print(f"📱 Статус отправки в Telegram: {data.get('telegram_send_status')}")
            print(f"💬 Сообщение: {data.get('message')}")
            
            if data.get('telegram_send_status') == 'sent':
                print("🎉 Отчет успешно отправлен в Telegram!")
            else:
                print("⚠️  Ошибка отправки в Telegram")
                
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        print("   Убедитесь, что сервер запущен на http://localhost:5000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("-" * 50)
    print("✅ Тест завершен!")

if __name__ == "__main__":
    test_saved_report_sending() 
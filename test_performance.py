#!/usr/bin/env python3
"""
Тестовый скрипт для проверки оптимизаций производительности
"""

import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Конфигурация
BASE_URL = "https://aaadvisor-zaicevn.amvera.io"  # Замените на ваш домен
TEST_ENDPOINTS = [
    "/api/locations/countries",
    "/api/currency/rates", 
    "/api/user",
    "/api/performance/stats"
]

def test_endpoint(endpoint, method="GET", data=None):
    """Тестирование отдельного endpoint"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        execution_time = time.time() - start_time
        
        return {
            'endpoint': endpoint,
            'method': method,
            'status_code': response.status_code,
            'execution_time': execution_time,
            'response_size': len(response.content),
            'success': response.status_code == 200
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'endpoint': endpoint,
            'method': method,
            'status_code': 0,
            'execution_time': execution_time,
            'response_size': 0,
            'success': False,
            'error': str(e)
        }

def test_concurrent_requests(endpoint, num_requests=10):
    """Тестирование параллельных запросов"""
    print(f"🔍 Тестирование {num_requests} параллельных запросов к {endpoint}")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_endpoint, endpoint) for _ in range(num_requests)]
        
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    
    return results

def test_cache_performance():
    """Тестирование производительности кэша"""
    print("🧪 Тестирование производительности кэша")
    
    # Первый запрос (должен быть медленным)
    print("📊 Первый запрос (кэш MISS)...")
    result1 = test_endpoint("/api/locations/countries")
    
    # Второй запрос (должен быть быстрым)
    print("📊 Второй запрос (кэш HIT)...")
    result2 = test_endpoint("/api/locations/countries")
    
    # Третий запрос (должен быть быстрым)
    print("📊 Третий запрос (кэш HIT)...")
    result3 = test_endpoint("/api/locations/countries")
    
    return {
        'first_request': result1,
        'second_request': result2,
        'third_request': result3,
        'cache_improvement': result1['execution_time'] / result2['execution_time'] if result2['execution_time'] > 0 else 0
    }

def test_performance_stats():
    """Получение статистики производительности"""
    print("📈 Получение статистики производительности")
    
    try:
        response = requests.get(f"{BASE_URL}/api/performance/stats", timeout=30)
        if response.status_code == 200:
            stats = response.json()
            return stats
        else:
            return {'error': f'Status code: {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов производительности Aaadviser")
    print("=" * 60)
    
    # Тест 1: Базовые endpoints
    print("\n1️⃣ Тестирование базовых endpoints:")
    for endpoint in TEST_ENDPOINTS:
        result = test_endpoint(endpoint)
        status = "✅" if result['success'] else "❌"
        print(f"{status} {endpoint}: {result['execution_time']:.3f}s ({result['status_code']})")
    
    # Тест 2: Производительность кэша
    print("\n2️⃣ Тестирование производительности кэша:")
    cache_results = test_cache_performance()
    
    print(f"📊 Первый запрос: {cache_results['first_request']['execution_time']:.3f}s")
    print(f"📊 Второй запрос: {cache_results['second_request']['execution_time']:.3f}s")
    print(f"📊 Третий запрос: {cache_results['third_request']['execution_time']:.3f}s")
    print(f"🚀 Улучшение производительности: {cache_results['cache_improvement']:.1f}x")
    
    # Тест 3: Параллельные запросы
    print("\n3️⃣ Тестирование параллельных запросов:")
    concurrent_results = test_concurrent_requests("/api/locations/countries", 5)
    
    successful_requests = [r for r in concurrent_results if r['success']]
    avg_time = sum(r['execution_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0
    
    print(f"📊 Успешных запросов: {len(successful_requests)}/{len(concurrent_results)}")
    print(f"📊 Среднее время выполнения: {avg_time:.3f}s")
    
    # Тест 4: Статистика производительности
    print("\n4️⃣ Статистика производительности:")
    stats = test_performance_stats()
    
    if 'error' not in stats:
        print("✅ Статистика получена успешно")
        if 'overall_stats' in stats:
            overall = stats['overall_stats']
            print(f"📊 Время работы: {overall.get('uptime_seconds', 0):.0f} секунд")
            print(f"📊 Всего метрик: {overall.get('total_metrics_recorded', 0)}")
            print(f"📊 Всего ошибок: {overall.get('total_errors', 0)}")
    else:
        print(f"❌ Ошибка получения статистики: {stats['error']}")
    
    # Тест 5: Очистка кэша
    print("\n5️⃣ Тестирование очистки кэша:")
    try:
        response = requests.post(f"{BASE_URL}/api/performance/cache/clear", timeout=30)
        if response.status_code == 200:
            print("✅ Кэш очищен успешно")
        else:
            print(f"❌ Ошибка очистки кэша: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка очистки кэша: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Тестирование завершено!")
    
    # Рекомендации
    print("\n📋 Рекомендации:")
    if cache_results['cache_improvement'] > 2:
        print("✅ Кэширование работает эффективно")
    else:
        print("⚠️ Кэширование может быть настроено лучше")
    
    print("📊 Обновленные TTL кэшей:")
    print("   - Локации: 1 неделя")
    print("   - Курсы валют: 1 день") 
    print("   - Рыночные данные: 1 неделя")
    print("   - Пользователи: 1 неделя")
    
    if avg_time < 1.0:
        print("✅ Производительность API хорошая")
    else:
        print("⚠️ Производительность API может быть улучшена")
    
    if len(successful_requests) == len(concurrent_results):
        print("✅ Параллельная обработка работает стабильно")
    else:
        print("⚠️ Есть проблемы с параллельной обработкой")

if __name__ == "__main__":
    main()

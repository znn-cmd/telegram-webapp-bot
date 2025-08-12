#!/usr/bin/env python3
"""
Тестовый скрипт для проверки настроек геокодинга
"""

import os

def test_environment_variables():
    """Тестирует переменные окружения"""
    print("🧪 Проверяем переменные окружения геокодинга...")
    print("=" * 50)
    
    # Google Maps API настройки
    enable_google_maps = os.getenv('ENABLE_GOOGLE_MAPS', 'false').lower() == 'true'  # По умолчанию отключен
    google_maps_timeout = int(os.getenv('GOOGLE_MAPS_TIMEOUT', '5'))  # Минимальный таймаут
    
    # Nominatim API настройки
    enable_nominatim = os.getenv('ENABLE_NOMINATIM', 'true').lower() == 'true'
    nominatim_timeout = int(os.getenv('NOMINATIM_TIMEOUT', '15'))
    
    print(f"🌐 Google Maps API:")
    print(f"   Включен: {'✅' if enable_google_maps else '🚫'}")
    print(f"   Таймаут: {google_maps_timeout} секунд")
    
    print(f"\n🗺️ Nominatim API:")
    print(f"   Включен: {'✅' if enable_nominatim else '🚫'}")
    print(f"   Таймаут: {nominatim_timeout} секунд")
    
    print(f"\n📊 Конфигурация:")
    if enable_google_maps and enable_nominatim:
        print("   🔄 Оба API включены (Google Maps + Nominatim)")
        print("   📝 Google Maps основной, Nominatim как fallback")
    elif enable_google_maps and not enable_nominatim:
        print("   🌐 Только Google Maps API")
        print("   📝 Nominatim отключен")
    elif not enable_google_maps and enable_nominatim:
        print("   🗺️ Только Nominatim API")
        print("   📝 Google Maps отключен")
    else:
        print("   🚫 Все внешние API отключены")
        print("   📝 Только база данных")
    
    print(f"\n⚡ Скорость:")
    if google_maps_timeout <= 10 and nominatim_timeout <= 10:
        print("   🚀 Быстрые таймауты (≤10с)")
    elif google_maps_timeout <= 20 and nominatim_timeout <= 15:
        print("   🐌 Средние таймауты (≤20с)")
    else:
        print("   🐌 Медленные таймауты (>20с)")

def show_recommendations():
    """Показывает рекомендации по настройке"""
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    print("=" * 50)
    
    enable_google_maps = os.getenv('ENABLE_GOOGLE_MAPS', 'true').lower() == 'true'
    enable_nominatim = os.getenv('ENABLE_NOMINATIM', 'true').lower() == 'true'
    
    if enable_google_maps:
        print("🔧 Если Google Maps API зависает:")
        print("   export ENABLE_GOOGLE_MAPS=false")
        print("")
    
    if enable_nominatim:
        print("🔧 Если Nominatim API работает медленно:")
        print("   export ENABLE_NOMINATIM=false")
        print("")
    
    print("🔧 Для быстрых ответов:")
    print("   export GOOGLE_MAPS_TIMEOUT=5")
    print("   export NOMINATIM_TIMEOUT=3")
    print("")
    
    print("🔧 Для полного отключения внешних API:")
    print("   export ENABLE_GOOGLE_MAPS=false")
    print("   export ENABLE_NOMINATIM=false")

def main():
    """Основная функция"""
    print("🚀 Проверка настроек геокодинга")
    print("=" * 50)
    
    # Проверяем переменные окружения
    test_environment_variables()
    
    # Показываем рекомендации
    show_recommendations()
    
    print(f"\n📋 Следующие шаги:")
    print("1. Перезапустите приложение")
    print("2. Проверьте логи при геокодинге")
    print("3. При необходимости настройте переменные окружения")

if __name__ == "__main__":
    main()

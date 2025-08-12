# 🔧 Исправление зависания геокодинга

## Проблема
Приложение зависает на этапе отправки HTTP запроса к Google Maps API.

## Решение
Добавлены настройки для полного контроля работы с API геокодинга:

### 1. Переменные окружения
```bash
# Отключить Google Maps API полностью
ENABLE_GOOGLE_MAPS=false

# Отключить Nominatim API
ENABLE_NOMINATIM=false

# Установить таймауты (в секундах)
GOOGLE_MAPS_TIMEOUT=10
NOMINATIM_TIMEOUT=5
```

### 2. Настройки по умолчанию
- `ENABLE_GOOGLE_MAPS=true` - Google Maps API включен
- `ENABLE_NOMINATIM=true` - Nominatim API включен
- `GOOGLE_MAPS_TIMEOUT=20` - таймаут Google Maps 20 секунд
- `NOMINATIM_TIMEOUT=15` - таймаут Nominatim 15 секунд

### 3. Что исправлено
- ✅ Возможность отключения Google Maps API
- ✅ Fallback на Nominatim при отключении Google Maps
- ✅ Настраиваемые таймауты для каждого API
- ✅ Graceful fallback при ошибках
- ✅ Детальное логирование всех этапов

### 4. Как использовать

#### Если Google Maps API зависает:
```bash
export ENABLE_GOOGLE_MAPS=false
```

#### Если Nominatim API работает медленно:
```bash
export ENABLE_NOMINATIM=false
```

#### Если нужны быстрые ответы:
```bash
export GOOGLE_MAPS_TIMEOUT=5
export NOMINATIM_TIMEOUT=3
```

#### Полное отключение внешних API (только база данных):
```bash
export ENABLE_GOOGLE_MAPS=false
export ENABLE_NOMINATIM=false
```

### 5. Логирование
Теперь в логах будет видно:
- 🚫 Отключение API
- 🔄 Отправка HTTP запроса
- 📡 Статус ответа
- ⏰ Таймауты
- 🔄 Fallback на альтернативные API

### 6. Приоритеты API
1. **Google Maps API** (если включен)
2. **Nominatim API** (если Google Maps отключен или недоступен)
3. **Только база данных** (если оба API отключены)

## Тестирование
После внесения изменений перезапустите приложение и проверьте логи.

## Рекомендации
- Начните с `ENABLE_GOOGLE_MAPS=false` если Google Maps API нестабилен
- Используйте короткие таймауты (5-10 секунд) для быстрого обнаружения проблем
- При необходимости полностью отключите внешние API и работайте только с базой данных

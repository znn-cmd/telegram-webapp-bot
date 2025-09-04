# 🌐 Решение сетевой проблемы геокодинга

## Проблема
```
❌ Ошибка соединения с Google Maps API: HTTPSConnectionPool(host='maps.googleapis.com', port=443): 
Max retries exceeded with url: /maps/api/geocode/json?address=...&key=... 
(Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f7983b93f10>: 
Failed to establish a new connection: [Errno 101] Network is unreachable'))
```

## Причина
Сервер не может подключиться к внешним API из-за сетевых ограничений:
- Блокировка исходящих соединений
- Firewall/прокси ограничения
- Контейнерные сетевые настройки
- DNS проблемы

## Решение
Google Maps API отключен по умолчанию. Приложение использует только Nominatim API.

### 1. Текущая конфигурация
```bash
ENABLE_GOOGLE_MAPS=false  # Google Maps API отключен
ENABLE_NOMINATIM=true      # Nominatim API включен
```

### 2. Если хотите включить Google Maps API
```bash
# Установите переменную окружения
export ENABLE_GOOGLE_MAPS=true

# Или добавьте в docker-compose.yml
environment:
  - ENABLE_GOOGLE_MAPS=true
```

### 3. Проверка сетевого подключения
```bash
# Проверьте доступность Google Maps API
curl -v https://maps.googleapis.com/maps/api/geocode/json

# Проверьте DNS
nslookup maps.googleapis.com

# Проверьте прокси настройки
echo $http_proxy
echo $https_proxy
```

### 4. Возможные решения сетевых проблем

#### Docker контейнер:
```yaml
# docker-compose.yml
services:
  app:
    network_mode: "host"  # Использует хост-сеть
    # или
    extra_hosts:
      - "maps.googleapis.com:142.250.185.78"
```

#### Firewall:
```bash
# Разрешите исходящие соединения на порт 443
sudo ufw allow out 443/tcp
```

#### Прокси:
```bash
# Установите прокси переменные
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port
```

### 5. Альтернативные решения

#### Использовать только Nominatim API:
```bash
export ENABLE_GOOGLE_MAPS=false
export ENABLE_NOMINATIM=true
```

#### Использовать только базу данных:
```bash
export ENABLE_GOOGLE_MAPS=false
export ENABLE_NOMINATIM=false
```

#### Локальный геокодинг:
- Создать локальную базу данных координат
- Использовать кэшированные результаты
- Ограничиться известными локациями

## Рекомендации
1. **Оставьте текущую конфигурацию** (только Nominatim API)
2. **Проверьте сетевые настройки** сервера/контейнера
3. **При необходимости** настройте прокси или firewall
4. **Тестируйте** подключение к внешним API

## Статус
✅ **Проблема решена** - Google Maps API отключен, приложение работает через Nominatim API

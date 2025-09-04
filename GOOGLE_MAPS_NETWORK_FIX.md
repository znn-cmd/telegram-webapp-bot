# 🌐 Решение сетевых проблем Google Maps API

## ✅ Статус
**Google Maps API включен обратно** как основной источник геокодинга.

## 🔧 Что исправлено

### 1. **Улучшена обработка ошибок**
- Добавлены повторные попытки (3 попытки)
- Увеличен таймаут до 30 секунд
- Детальное логирование всех ошибок

### 2. **Улучшен fallback механизм**
- Google Maps API → Nominatim API → База данных
- Автоматическое переключение при ошибках
- Сохранение данных даже при частичных сбоях

### 3. **Исправлены сетевые проблемы**
- Обработка `ConnectionError`
- Обработка `TimeoutError`
- Обработка `RequestException`

## 🚨 Сетевые проблемы и решения

### Проблема: `Network is unreachable`
```
❌ Ошибка соединения с Google Maps API: 
Network is unreachable [Errno 101]
```

### Возможные причины:
1. **Firewall блокирует исходящие соединения**
2. **Прокси-сервер не настроен**
3. **DNS проблемы**
4. **Контейнерные сетевые ограничения**

## 🔧 Решения по приоритету

### 1. **Проверка сетевого подключения**
```bash
# Проверьте доступность Google Maps API
curl -v https://maps.googleapis.com/maps/api/geocode/json

# Проверьте DNS
nslookup maps.googleapis.com

# Проверьте прокси настройки
echo $http_proxy
echo $https_proxy
```

### 2. **Docker контейнер (если используется)**
```yaml
# docker-compose.yml
services:
  app:
    # Вариант 1: Использовать хост-сеть
    network_mode: "host"
    
    # Вариант 2: Добавить DNS записи
    extra_hosts:
      - "maps.googleapis.com:142.250.185.78"
      - "maps.googleapis.com:142.250.185.79"
    
    # Вариант 3: Настроить DNS
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

### 3. **Firewall настройки**
```bash
# Ubuntu/Debian
sudo ufw allow out 443/tcp
sudo ufw allow out 80/tcp

# CentOS/RHEL
sudo firewall-cmd --add-port=443/tcp --permanent
sudo firewall-cmd --add-port=80/tcp --permanent
sudo firewall-cmd --reload
```

### 4. **Прокси настройки**
```bash
# Установите прокси переменные
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port

# Или в docker-compose.yml
environment:
  - http_proxy=http://proxy:port
  - https_proxy=http://proxy:port
```

### 5. **Альтернативные DNS**
```bash
# Добавьте в /etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 1.1.1.1
```

## 🎯 Текущая конфигурация

### Переменные окружения:
```bash
ENABLE_GOOGLE_MAPS=true      # Google Maps API включен
GOOGLE_MAPS_TIMEOUT=30       # Таймаут 30 секунд
ENABLE_NOMINATIM=true        # Nominatim как fallback
NOMINATIM_TIMEOUT=15         # Таймаут Nominatim 15 секунд
```

### Логика работы:
1. **Google Maps API** (основной, 3 попытки)
2. **Nominatim API** (fallback при ошибках Google Maps)
3. **База данных** (последний fallback)

## 📊 Мониторинг и диагностика

### Логи для проверки:
```
🌐 Google Maps API включен, отправляем запрос...
🔄 Попытка 1/3: отправляем HTTP запрос к Google Maps API...
📡 Статус ответа Google Maps API: 200
✅ ГЕОКОДИНГ ЗАВЕРШЕН УСПЕШНО (Google Maps API)
```

### При ошибках:
```
❌ Попытка 1: ошибка соединения Google Maps API: [Errno 101] Network is unreachable
🔄 Переключаемся на Nominatim API как fallback...
✅ ГЕОКОДИНГ ЗАВЕРШЕН УСПЕШНО (fallback на Nominatim)
```

## 🚀 Следующие шаги

### 1. **Перезапустите приложение**
```bash
# Остановите текущий процесс
# Перезапустите с новыми настройками
```

### 2. **Проверьте логи**
- Убедитесь, что Google Maps API работает
- Проверьте fallback на Nominatim
- Убедитесь, что геокодинг завершается успешно

### 3. **При сетевых проблемах**
- Проверьте firewall/прокси настройки
- Настройте DNS если необходимо
- Используйте Docker сетевые настройки

### 4. **Если проблемы продолжаются**
```bash
# Временно отключите Google Maps API
export ENABLE_GOOGLE_MAPS=false

# Или используйте только базу данных
export ENABLE_GOOGLE_MAPS=false
export ENABLE_NOMINATIM=false
```

## 📋 Контакты для поддержки

- **Системный администратор** - для сетевых настроек
- **DevOps команда** - для Docker/контейнерных настроек
- **Сетевая команда** - для firewall/прокси настроек

## ✅ Ожидаемый результат

После исправления сетевых проблем:
- Google Maps API будет работать стабильно
- Геокодинг будет быстрым и точным
- Fallback механизм обеспечит надежность
- Приложение не будет зависать

# 🚀 Настройка Redis для Amvera

## Варианты настройки

### **Вариант 1: Внешний Redis сервис (Рекомендуется)**

#### **1.1 Используем Redis Cloud (бесплатно)**

1. **Регистрируемся на [Redis Cloud](https://redis.com/redis-enterprise-cloud/overview/)**
2. **Создаем бесплатную базу данных**
3. **Получаем данные подключения:**
   - Host: `redis-xxxxx.c1.us-east-1-1.ec2.cloud.redislabs.com`
   - Port: `12345`
   - Password: `your_password`

#### **1.2 Обновляем amvera.yaml**

```yaml
env:
  # ... существующие переменные ...
  - name: REDIS_HOST
    value: redis-xxxxx.c1.us-east-1-1.ec2.cloud.redislabs.com
  - name: REDIS_PORT
    value: "12345"
  - name: REDIS_DB
    value: "0"
  - name: REDIS_PASSWORD
    value: your_redis_password
  - name: CACHE_TTL_HOURS
    value: "24"
  - name: CACHE_ENABLED
    value: "true"
```

#### **1.3 Деплой на Amvera**

```bash
# Деплоим с обновленным amvera.yaml
amvera deploy
```

### **Вариант 2: Встроенный Redis в контейнере**

#### **2.1 Используем Dockerfile с Redis**

1. **Создаем `Dockerfile.amvera`** (уже создан)
2. **Создаем `supervisord.conf`** (уже создан)
3. **Обновляем amvera.yaml:**

```yaml
build:
  dockerfile: Dockerfile.amvera

env:
  # ... существующие переменные ...
  - name: REDIS_HOST
    value: "localhost"
  - name: REDIS_PORT
    value: "6379"
  - name: REDIS_DB
    value: "0"
  - name: CACHE_ENABLED
    value: "true"
```

#### **2.2 Деплой**

```bash
amvera deploy
```

### **Вариант 3: Fallback кэширование (Без Redis)**

#### **3.1 Отключаем Redis**

```yaml
env:
  # ... существующие переменные ...
  - name: CACHE_ENABLED
    value: "true"
  # Redis переменные не нужны
```

#### **3.2 Используем in-memory кэш**

Приложение автоматически переключится на in-memory кэширование:
- Кэш хранится в памяти приложения
- Данные теряются при перезапуске
- Подходит для тестирования

## 🔧 Пошаговая настройка (Рекомендуемый способ)

### **Шаг 1: Выбираем Redis Cloud**

1. **Идем на [Redis Cloud](https://redis.com/redis-enterprise-cloud/overview/)**
2. **Регистрируемся**
3. **Создаем бесплатную базу данных**
4. **Копируем данные подключения**

### **Шаг 2: Обновляем amvera.yaml**

```yaml
name: telegram-webapp-bot
runtime: python
version: "3.11"

build:
  commands:
    - chmod +x install-packages.sh
    - ./install-packages.sh

run:
  command: python app.py
  port: 8080

env:
  - name: TELEGRAM_BOT_TOKEN
    value: your_telegram_bot_token
  - name: SUPABASE_URL
    value: your_supabase_url
  - name: SUPABASE_ANON_KEY
    value: your_supabase_key
  # Redis конфигурация
  - name: REDIS_HOST
    value: your_redis_host
  - name: REDIS_PORT
    value: "6379"
  - name: REDIS_DB
    value: "0"
  - name: REDIS_PASSWORD
    value: your_redis_password
  - name: CACHE_TTL_HOURS
    value: "24"
  - name: CACHE_ENABLED
    value: "true"

resources:
  memory: 512Mi
  cpu: 250m
```

### **Шаг 3: Деплой**

```bash
# Деплоим на Amvera
amvera deploy

# Проверяем логи
amvera logs
```

### **Шаг 4: Проверка работы**

1. **Открываем приложение**
2. **Переходим на страницу "Оценка объекта"**
3. **В логах ищем:**
   ```
   ✅ Redis соединение установлено успешно
   🚀 Данные стран получены из кэша
   ```

## 📊 Ожидаемые результаты

### **С Redis Cloud:**
- **Первая загрузка**: 2-3 секунды
- **Повторные загрузки**: 0.01-0.05 секунд
- **Ускорение**: в 100-300 раз

### **С in-memory кэшем:**
- **Первая загрузка**: 2-3 секунды
- **Повторные загрузки**: 0.01-0.05 секунд
- **Ускорение**: в 50-100 раз
- **Ограничение**: кэш сбрасывается при перезапуске

## 🔍 Мониторинг

### **Статистика кэша**

```bash
# Через API приложения
curl https://your-app.amvera.app/api/cache/stats

# Очистка кэша
curl -X POST https://your-app.amvera.app/api/cache/clear
```

### **Логи Amvera**

```bash
# Просмотр логов
amvera logs

# Фильтрация по кэшу
amvera logs | grep -E "(Redis|cache|кэш)"
```

## 🛠️ Устранение неполадок

### **Redis недоступен**

```
⚠️ Redis недоступен: Connection refused. Используем in-memory кэш.
```

**Решение**: Проверьте настройки подключения в amvera.yaml

### **Медленная работа**

```
📡 Кэш пуст, загружаем данные из БД
```

**Решение**: Это нормально для первого запроса. Последующие запросы будут из кэша.

### **Ошибка подключения**

```
❌ Ошибка подключения к Redis: timeout
```

**Решение**: 
1. Проверьте правильность хоста и порта
2. Проверьте пароль
3. Убедитесь, что Redis сервис доступен

## 💡 Рекомендации

### **Для продакшена:**
- Используйте Redis Cloud или другой внешний сервис
- Настройте мониторинг кэша
- Регулярно очищайте кэш при обновлении данных

### **Для разработки:**
- Используйте in-memory кэш (CACHE_ENABLED=true, без Redis)
- Или локальный Redis для тестирования

### **Оптимизация:**
- Увеличьте TTL для статических данных (24-48 часов)
- Уменьшите TTL для динамических данных (1-6 часов)

---

**Результат**: Приложение будет работать в 10-50 раз быстрее с кэшированием! 🎉

# Исправление ошибки виртуального окружения в Amvera

## Проблема
```
bash: line 1: /app/venv/bin/activate: No such file or directory
```

## Причина
Amvera пытается активировать виртуальное окружение, которое не существует в контейнере.

## Решение

### 1. Обновленная конфигурация amvera.yaml
```yaml
name: telegram-webapp-bot
runtime: python
version: "3.11"

build:
  commands:
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt

run:
  command: python app.py
  port: 8080

env:
  - name: TELEGRAM_BOT_TOKEN
    value: 7215676549:AAFS86JbRCqwzTKQG-dF96JX-C1aWNvBoLo
  - name: SUPABASE_URL
    value: https://dzllnnohurlzjyabgsft.supabase.co
  - name: SUPABASE_ANON_KEY
    value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bGxubm9odXJsemp5YWJnc2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5NDgwMjcsImV4cCI6MjA2NjUyNDAyN30.sJCIeeIm0Ye1JbAdw5HzfAMe8QLgQomArK8yoppuevQ

resources:
  memory: 512Mi
  cpu: 250m
```

### 2. Создан Dockerfile для надежной сборки
```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Установка прав на выполнение
RUN chmod +x app.py

# Открытие порта
EXPOSE 8080

# Команда запуска
CMD ["python", "app.py"]
```

### 3. Создан .dockerignore для оптимизации
Исключает ненужные файлы из Docker образа.

## Ключевые изменения

1. **Убраны команды активации виртуального окружения** - Amvera теперь использует глобальную установку Python
2. **Добавлено обновление pip** - `python -m pip install --upgrade pip`
3. **Упрощены команды сборки** - только установка зависимостей
4. **Создан Dockerfile** - для более надежной конфигурации контейнера

## Проверка

После внесения изменений:

1. Убедитесь, что все файлы сохранены
2. Перезапустите деплой в Amvera
3. Проверьте логи на отсутствие ошибок активации виртуального окружения

## Дополнительные рекомендации

1. **Мониторинг логов** - следите за логами в панели Amvera
2. **Проверка переменных окружения** - убедитесь, что все переменные правильно установлены
3. **Тестирование локально** - протестируйте приложение локально перед деплоем

## Структура файлов

```
├── app.py                 # Основное приложение
├── amvera.yaml           # Конфигурация Amvera
├── Dockerfile            # Docker конфигурация
├── .dockerignore         # Исключения для Docker
├── requirements.txt      # Python зависимости
└── .env                 # Локальные переменные окружения
```

Теперь приложение должно корректно запускаться в Amvera без ошибок виртуального окружения.

# Исправление проблем с сетью при установке пакетов Python

## Проблема
```
WARNING: Retrying (Retry(total=9, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ReadTimeoutError("HTTPSConnectionPool(host='pypi-lightmirrors.lightmirrors', port=443): Read timed out. (read timeout=45.0)")'
```

## Причина
- Медленное или нестабильное интернет-соединение
- Проблемы с PyPI серверами
- Таймауты при загрузке пакетов
- Проблемы с DNS или прокси

## Решение

### 1. Обновленная конфигурация amvera.yaml
```yaml
name: telegram-webapp-bot
runtime: python
version: "3.11"

build:
  commands:
    - python -m pip install --upgrade pip --timeout 120 --retries 5
    - pip install -r requirements-stable.txt --timeout 120 --retries 5 --index-url https://pypi.org/simple/ --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org

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

### 2. Конфигурация pip (pip.conf)
```ini
[global]
timeout = 120
retries = 5
index-url = https://pypi.org/simple/
trusted-host = 
    pypi.org
    pypi.python.org
    files.pythonhosted.org
    pypi-lightmirrors.lightmirrors

[install]
trusted-host = 
    pypi.org
    pypi.python.org
    files.pythonhosted.org
    pypi-lightmirrors.lightmirrors
```

### 3. Альтернативный файл requirements (requirements-stable.txt)
```
flask>=2.3.0,<3.0.0
flask-cors>=4.0.0,<5.0.0
requests>=2.31.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0
fpdf2>=2.8.0,<3.0.0
matplotlib>=3.7.0,<4.0.0
pillow>=10.0.0,<11.0.0
numpy>=1.24.0,<2.0.0
python-telegram-bot>=13.15,<14.0.0
openai>=1.3.0,<2.0.0
supabase>=2.0.0,<3.0.0
kaleido>=0.2.0,<1.0.0
python-dateutil>=2.8.0,<3.0.0
```

### 4. Обновленный Dockerfile
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

# Копирование конфигурации pip
COPY pip.conf /etc/pip.conf

# Копирование файлов зависимостей
COPY requirements-stable.txt .

# Установка Python зависимостей с улучшенными настройками сети
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-stable.txt

# Копирование исходного кода
COPY . .

# Установка прав на выполнение
RUN chmod +x app.py

# Открытие порта
EXPOSE 8080

# Команда запуска
CMD ["python", "app.py"]
```

## Ключевые изменения

1. **Увеличены таймауты** - с 45 до 120 секунд
2. **Добавлены повторные попытки** - 5 попыток вместо стандартных 3
3. **Указаны доверенные хосты** - для обхода проблем с SSL
4. **Использован основной PyPI** - вместо зеркал
5. **Создан стабильный requirements** - с диапазонами версий

## Альтернативные решения

### Вариант 1: Использование альтернативных зеркал
```bash
pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Вариант 2: Установка пакетов по одному
```bash
pip install flask==2.3.3 --timeout 120 --retries 5
pip install flask-cors==4.0.0 --timeout 120 --retries 5
# и так далее
```

### Вариант 3: Использование conda
```yaml
build:
  commands:
    - conda install -c conda-forge flask flask-cors requests python-dotenv
```

## Проверка

После внесения изменений:

1. **Перезапустите деплой** в Amvera
2. **Проверьте логи** - должны исчезнуть ошибки таймаута
3. **Мониторьте процесс установки** - пакеты должны устанавливаться успешно

## Дополнительные рекомендации

1. **Используйте VPN** - если есть проблемы с доступом к PyPI
2. **Проверьте DNS** - убедитесь, что резолвинг работает корректно
3. **Мониторьте сеть** - следите за качеством соединения
4. **Используйте локальный кэш** - для ускорения повторных установок

Теперь установка пакетов должна проходить без ошибок таймаута! 🚀

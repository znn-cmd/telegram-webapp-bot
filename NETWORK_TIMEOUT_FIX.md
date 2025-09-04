# Решение проблем с таймаутами сети в Amvera

## Проблема
```
WARNING: Retrying (Retry(total=9, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ReadTimeoutError("HTTPSConnectionPool(host='pypi-lightmirrors.lightmirrors', port=443): Read timed out. (read timeout=45.0)")'
```

## Причина
- Проблемы с основным PyPI сервером
- Медленное интернет-соединение
- Проблемы с DNS резолвингом
- Блокировка или ограничения сети

## Решения

### 🔧 Решение 1: Альтернативное зеркало PyPI

**Обновленный amvera.yaml:**
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
    value: 7215676549:AAFS86JbRCqwzTKQG-dF96JX-C1aWNvBoLo
  - name: SUPABASE_URL
    value: https://dzllnnohurlzjyabgsft.supabase.co
  - name: SUPABASE_ANON_KEY
    value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bGxubm9odXJsemp5YWJnc2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5NDgwMjcsImV4cCI6MjA2NjUyNDAyN30.sJCIeeIm0Ye1JbAdw5HzfAMe8QLgQomArK8yoppuevQ

resources:
  memory: 512Mi
  cpu: 250m
```

**Скрипт install-packages.sh:**
```bash
#!/bin/bash

# Устанавливаем пакеты по одному с повторными попытками
packages=(
    "flask>=2.3.0"
    "flask-cors>=4.0.0"
    "requests>=2.31.0"
    "python-dotenv>=1.0.0"
    "fpdf2>=2.8.0"
    "matplotlib>=3.7.0"
    "pillow>=10.0.0"
    "numpy>=1.24.0"
    "python-telegram-bot>=13.15"
    "openai>=1.3.0"
    "supabase>=2.0.0"
    "python-dateutil>=2.8.0"
)

for package in "${packages[@]}"; do
    pip install "$package" --timeout 300 --retries 10 --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn --no-cache-dir
done
```

### 🔧 Решение 2: Использование conda

**amvera-conda.yaml:**
```yaml
name: telegram-webapp-bot
runtime: python
version: "3.11"

build:
  commands:
    - conda install -c conda-forge -c defaults flask flask-cors requests python-dotenv matplotlib pillow numpy python-dateutil -y
    - pip install fpdf2 python-telegram-bot openai supabase --timeout 300 --retries 10 --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

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

### 🔧 Решение 3: Минимальный requirements

**requirements-minimal.txt:**
```
flask>=2.3.0
flask-cors>=4.0.0
requests>=2.31.0
python-dotenv>=1.0.0
fpdf2>=2.8.0
matplotlib>=3.7.0
pillow>=10.0.0
numpy>=1.24.0
python-telegram-bot>=13.15
openai>=1.3.0
supabase>=2.0.0
python-dateutil>=2.8.0
```

## Альтернативные зеркала PyPI

1. **Tsinghua University (Китай):**
   ```
   https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **Alibaba Cloud (Китай):**
   ```
   https://mirrors.aliyun.com/pypi/simple/
   ```

3. **Douban (Китай):**
   ```
   https://pypi.douban.com/simple/
   ```

4. **USTC (Китай):**
   ```
   https://pypi.mirrors.ustc.edu.cn/simple/
   ```

## Ключевые изменения

1. **Увеличены таймауты** - с 45 до 300 секунд
2. **Добавлены повторные попытки** - 10 попыток
3. **Использовано альтернативное зеркало** - Tsinghua University
4. **Установка по одному пакету** - для лучшего контроля
5. **Отключен кэш** - `--no-cache-dir`

## Проверка

После внесения изменений:

1. **Перезапустите деплой** в Amvera
2. **Проверьте логи** - должны исчезнуть ошибки таймаута
3. **Мониторьте процесс** - каждый пакет должен устанавливаться отдельно

## Дополнительные рекомендации

1. **Попробуйте разные зеркала** - если одно не работает
2. **Используйте conda** - для более стабильной установки
3. **Установите пакеты по одному** - для лучшего контроля ошибок
4. **Увеличьте ресурсы** - если нужно больше памяти/CPU

## Структура файлов

```
├── amvera.yaml              # Основная конфигурация
├── amvera-conda.yaml        # Альтернативная конфигурация с conda
├── install-packages.sh      # Скрипт установки пакетов
├── requirements-minimal.txt  # Минимальный requirements
├── pip.conf                 # Конфигурация pip
└── NETWORK_TIMEOUT_FIX.md   # Это руководство
```

Теперь установка пакетов должна проходить стабильно! 🚀

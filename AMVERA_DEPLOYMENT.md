# Инструкция по развертыванию на Amvera

## 🚀 Быстрое развертывание

### Вариант 1: Сверхминимальный Dockerfile (рекомендуется)
```bash
# Используйте сверхминимальный Dockerfile для Amvera
docker build -f Dockerfile.ultra-minimal -t aaadviser .
```

### Вариант 2: Использование обновленного Dockerfile
```bash
# Используйте обновленный Dockerfile (уже исправлен)
docker build -t aaadviser .
```

### Вариант 3: Использование минимального Dockerfile
```bash
# Если основной Dockerfile не работает, используйте минимальный
docker build -f Dockerfile.minimal -t aaadviser .
```

### Вариант 4: Использование альтернативного Dockerfile
```bash
# Альтернативный вариант без GUI зависимостей
docker build -f Dockerfile.amvera -t aaadviser .
```

## 🔧 Настройка для Amvera

### 1. Переменные окружения
Создайте файл `.env` с необходимыми переменными:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
```

### 2. Настройка портов
Приложение использует порт 8080. Убедитесь, что он открыт в настройках Amvera.

### 3. Настройка домена
Настройте домен в панели управления Amvera для доступа к приложению.

## 🐛 Решение проблем

### Проблема: Ошибка с libgl1-mesa-glx
**Решение:** Используйте `Dockerfile.ultra-minimal` (рекомендуется)

### Проблема: Ошибка с libgdk-pixbuf2.0-0
**Решение:** Используйте `Dockerfile.ultra-minimal` или обновленный `Dockerfile`

### Проблема: Ошибки сборки Python пакетов
**Решение:** Добавьте в Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
```

### Проблема: Проблемы с сетью
**Решение:** Используйте российские зеркала:
```dockerfile
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 🎯 Рекомендуемый порядок попыток

1. **Попробуйте сверхминимальный:**
   ```bash
   docker build -f Dockerfile.ultra-minimal -t aaadviser .
   ```

2. **Если не работает, попробуйте обновленный:**
   ```bash
   docker build -t aaadviser .
   ```

3. **Если не работает, попробуйте минимальный:**
   ```bash
   docker build -f Dockerfile.minimal -t aaadviser .
   ```

4. **Если не работает, попробуйте альтернативный:**
   ```bash
   docker build -f Dockerfile.amvera -t aaadviser .
   ```

## 📊 Мониторинг

### Логи приложения
```bash
# Просмотр логов
docker logs aaadviser

# Просмотр логов в реальном времени
docker logs -f aaadviser
```

### Проверка состояния
```bash
# Проверка статуса контейнера
docker ps

# Проверка использования ресурсов
docker stats aaadviser
```

## 🔄 Обновление

### Обновление кода
```bash
# Остановка контейнера
docker stop aaadviser

# Удаление старого образа
docker rmi aaadviser

# Сборка нового образа
docker build -f Dockerfile.ultra-minimal -t aaadviser .

# Запуск нового контейнера
docker run -d --name aaadviser -p 8080:8080 aaadviser
```

### Обновление переменных окружения
```bash
# Перезапуск с новыми переменными
docker run -d --name aaadviser \
  -p 8080:8080 \
  -e TELEGRAM_BOT_TOKEN=new_token \
  -e SUPABASE_URL=new_url \
  aaadviser
```

## 🌍 Мультиязычность

Приложение поддерживает 5 языков:
- 🇷🇺 Русский (ru)
- 🇺🇸 English (en)
- 🇩🇪 Deutsch (de)
- 🇫🇷 Français (fr)
- 🇹🇷 Türkçe (tr)

Система мультиязычности автоматически:
- Определяет язык из Telegram WebApp
- Сохраняет предпочтения пользователя
- Применяет переводы ко всем элементам интерфейса

## 🚀 Автоматическое развертывание

### Для Windows:
```bash
# Сверхминимальный (рекомендуется)
deploy.bat ultra

# Минимальный
deploy.bat minimal

# Альтернативный
deploy.bat amvera
```

### Для Linux/Mac:
```bash
# Сверхминимальный (рекомендуется)
./deploy.sh ultra

# Минимальный
./deploy.sh minimal

# Альтернативный
./deploy.sh amvera
```

## 📞 Поддержка

При возникновении проблем:
1. Попробуйте `Dockerfile.ultra-minimal` (рекомендуется)
2. Проверьте логи контейнера
3. Убедитесь в корректности переменных окружения
4. Проверьте доступность порта 8080
5. Обратитесь к документации в `I18N_README.md`

---

**Версия:** 1.1  
**Дата:** 2024  
**Платформа:** Amvera  
**Рекомендуемый Dockerfile:** `Dockerfile.ultra-minimal`

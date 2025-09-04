# 🚀 Инструкция по обновлению Docker образа на Amvera

## 📋 Предварительные требования

1. **Доступ к Amvera:**
   - Войдите в панель управления Amvera
   - Убедитесь, что у вас есть доступ к проекту

2. **Подготовка файлов:**
   - Убедитесь, что все изменения сохранены локально
   - Проверьте, что `Dockerfile.ultra-minimal` готов к использованию

## 🔧 Шаги обновления

### Шаг 1: Подготовка локального образа
```bash
# Собрать новый образ с исправлениями
docker build -f Dockerfile.ultra-minimal -t aaadviser:latest .

# Проверить, что образ создался
docker images | grep aaadviser
```

### Шаг 2: Тегирование образа для Amvera
```bash
# Добавить тег для Amvera registry (замените на ваш registry)
docker tag aaadviser:latest your-amvera-registry.azurecr.io/aaadviser:latest

# Или если используете Docker Hub
docker tag aaadviser:latest your-username/aaadviser:latest
```

### Шаг 3: Отправка образа в registry
```bash
# Войти в registry (если требуется)
docker login your-amvera-registry.azurecr.io

# Отправить образ
docker push your-amvera-registry.azurecr.io/aaadviser:latest
```

## 🌐 Обновление через Amvera CLI (альтернативный способ)

### Шаг 1: Установка Amvera CLI
```bash
# Установить Amvera CLI
npm install -g @amvera/cli

# Войти в аккаунт
amvera login
```

### Шаг 2: Развертывание
```bash
# Перейти в папку проекта
cd /path/to/your/project

# Развернуть приложение
amvera deploy

# Или указать конкретный образ
amvera deploy --image your-amvera-registry.azurecr.io/aaadviser:latest
```

## 🔄 Автоматическое обновление через GitHub Actions

### Создать файл `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Amvera

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: |
        docker build -f Dockerfile.ultra-minimal -t aaadviser:latest .
    
    - name: Login to Amvera Registry
      run: |
        echo ${{ secrets.AMVERA_REGISTRY_PASSWORD }} | docker login your-amvera-registry.azurecr.io -u ${{ secrets.AMVERA_REGISTRY_USERNAME }} --password-stdin
    
    - name: Push image
      run: |
        docker tag aaadviser:latest your-amvera-registry.azurecr.io/aaadviser:latest
        docker push your-amvera-registry.azurecr.io/aaadviser:latest
    
    - name: Deploy to Amvera
      run: |
        amvera deploy --image your-amvera-registry.azurecr.io/aaadviser:latest
```

## 📝 Проверка обновления

### После развертывания проверьте:

1. **Логи приложения:**
   ```bash
   amvera logs
   ```

2. **Статус развертывания:**
   ```bash
   amvera status
   ```

3. **Тестирование API:**
   ```bash
   curl -X POST https://your-app.amvera.app/api/translations \
   -H "Content-Type: application/json" \
   -d '{"language": "ru"}'
   ```

## 🚨 Возможные проблемы

### Проблема: Ошибка сборки образа
**Решение:**
```bash
# Очистить кэш Docker
docker system prune -a

# Пересобрать образ
docker build --no-cache -f Dockerfile.ultra-minimal -t aaadviser:latest .
```

### Проблема: Ошибка авторизации в registry
**Решение:**
```bash
# Проверить учетные данные
docker login your-amvera-registry.azurecr.io

# Или использовать переменные окружения
export AMVERA_REGISTRY_USERNAME=your-username
export AMVERA_REGISTRY_PASSWORD=your-password
```

### Проблема: Приложение не запускается
**Решение:**
```bash
# Проверить логи
amvera logs --tail 100

# Проверить переменные окружения
amvera env list

# Перезапустить приложение
amvera restart
```

## ✅ Быстрая команда для обновления

Если у вас настроен автоматический деплой, просто выполните:
```bash
# Отправить изменения в Git
git add .
git commit -m "Fix i18n translations - update API endpoint"
git push origin main
```

## 🎯 Проверка результата

После обновления откройте приложение в браузере и убедитесь, что:
- ✅ Все элементы отображаются на правильном языке
- ✅ Нет ключей переводов типа `main.title`
- ✅ Система переключения языков работает
- ✅ API endpoint `/api/translations` возвращает правильные данные

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `amvera logs`
2. Убедитесь, что образ собрался корректно
3. Проверьте настройки registry в Amvera
4. Обратитесь в поддержку Amvera с логами ошибок

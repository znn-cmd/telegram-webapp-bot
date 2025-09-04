#!/bin/bash
# Скрипт для быстрого обновления Docker образа на Amvera

echo "🚀 Начинаем обновление Docker образа для Amvera..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

# Проверяем наличие Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo "❌ Файл Dockerfile не найден!"
    exit 1
fi

echo "📦 Собираем новый Docker образ..."
docker build -t aaadviser:latest .

if [ $? -ne 0 ]; then
    echo "❌ Ошибка сборки Docker образа!"
    exit 1
fi

echo "✅ Образ успешно собран!"

# Запрашиваем информацию о registry
echo "🌐 Введите адрес вашего registry (например: your-registry.azurecr.io):"
read registry_url

echo "🏷️ Тегируем образ для registry..."
docker tag aaadviser:latest $registry_url/aaadviser:latest

echo "📤 Отправляем образ в registry..."
docker push $registry_url/aaadviser:latest

if [ $? -ne 0 ]; then
    echo "❌ Ошибка отправки образа в registry!"
    echo "💡 Убедитесь, что вы вошли в registry: docker login $registry_url"
    exit 1
fi

echo "✅ Образ успешно отправлен в registry!"

echo "🎯 Следующие шаги:"
echo "1. Войдите в панель управления Amvera"
echo "2. Обновите образ в настройках приложения на: $registry_url/aaadviser:latest"
echo "3. Перезапустите приложение"
echo "4. Проверьте логи: amvera logs"

echo "🚀 Обновление завершено!"

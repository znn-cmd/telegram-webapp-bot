@echo off
REM Скрипт для быстрого обновления Docker образа на Amvera (Windows)

echo 🚀 Начинаем обновление Docker образа для Amvera...

REM Проверяем наличие Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен!
    pause
    exit /b 1
)

REM Проверяем наличие Dockerfile
if not exist "Dockerfile" (
    echo ❌ Файл Dockerfile не найден!
    pause
    exit /b 1
)

echo 📦 Собираем новый Docker образ...
docker build -t aaadviser:latest .

if errorlevel 1 (
    echo ❌ Ошибка сборки Docker образа!
    pause
    exit /b 1
)

echo ✅ Образ успешно собран!

REM Запрашиваем информацию о registry
set /p registry_url="🌐 Введите адрес вашего registry (например: your-registry.azurecr.io): "

echo 🏷️ Тегируем образ для registry...
docker tag aaadviser:latest %registry_url%/aaadviser:latest

echo 📤 Отправляем образ в registry...
docker push %registry_url%/aaadviser:latest

if errorlevel 1 (
    echo ❌ Ошибка отправки образа в registry!
    echo 💡 Убедитесь, что вы вошли в registry: docker login %registry_url%
    pause
    exit /b 1
)

echo ✅ Образ успешно отправлен в registry!

echo 🎯 Следующие шаги:
echo 1. Войдите в панель управления Amvera
echo 2. Обновите образ в настройках приложения на: %registry_url%/aaadviser:latest
echo 3. Перезапустите приложение
echo 4. Проверьте логи: amvera logs

echo 🚀 Обновление завершено!
pause

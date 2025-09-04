@echo off
REM Скрипт автоматического развертывания на Amvera для Windows
REM Автор: Aaadviser Team
REM Дата: 2024

echo 🚀 Начинаем развертывание Aaadviser на Amvera...

REM Проверка наличия Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Установите Docker и попробуйте снова.
    pause
    exit /b 1
)

REM Проверка наличия необходимых файлов
if not exist "app.py" (
    echo ❌ Файл app.py не найден. Убедитесь, что вы находитесь в корневой директории проекта.
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ Файл requirements.txt не найден.
    pause
    exit /b 1
)

REM Проверка переменных окружения
if not exist ".env" (
    echo ⚠️ Файл .env не найден. Создайте его с необходимыми переменными окружения.
    echo Пример содержимого .env:
    echo TELEGRAM_BOT_TOKEN=your_bot_token
    echo SUPABASE_URL=your_supabase_url
    echo SUPABASE_KEY=your_supabase_key
    echo OPENAI_API_KEY=your_openai_key
)

REM Остановка существующего контейнера
echo 📦 Останавливаем существующий контейнер...
docker stop aaadviser >nul 2>&1
docker rm aaadviser >nul 2>&1

REM Удаление старого образа
echo 🗑️ Удаляем старый образ...
docker rmi aaadviser >nul 2>&1

REM Выбор Dockerfile
set DOCKERFILE=Dockerfile
if "%1"=="minimal" (
    set DOCKERFILE=Dockerfile.minimal
    echo 📋 Используем минимальный Dockerfile
) else if "%1"=="amvera" (
    set DOCKERFILE=Dockerfile.amvera
    echo 📋 Используем альтернативный Dockerfile для Amvera
) else if "%1"=="ultra" (
    set DOCKERFILE=Dockerfile.ultra-minimal
    echo 📋 Используем сверхминимальный Dockerfile (рекомендуется для Amvera)
)

REM Проверка наличия выбранного Dockerfile
if not exist "%DOCKERFILE%" (
    echo ❌ Файл %DOCKERFILE% не найден.
    pause
    exit /b 1
)

REM Сборка образа
echo 🔨 Собираем Docker образ...
if "%1"=="minimal" (
    docker build -f Dockerfile.minimal -t aaadviser .
) else if "%1"=="amvera" (
    docker build -f Dockerfile.amvera -t aaadviser .
) else if "%1"=="ultra" (
    docker build -f Dockerfile.ultra-minimal -t aaadviser .
) else (
    docker build -t aaadviser .
)

if errorlevel 1 (
    echo ❌ Ошибка при сборке образа. Попробуйте использовать ultra, minimal или amvera
    echo.
    echo Рекомендуемые варианты:
    echo   deploy.bat ultra    - сверхминимальный (рекомендуется)
    echo   deploy.bat minimal  - минимальный
    echo   deploy.bat amvera   - альтернативный
    pause
    exit /b 1
)

echo ✅ Образ успешно собран!

REM Запуск контейнера
echo 🚀 Запускаем контейнер...
docker run -d --name aaadviser -p 8080:8080 --restart unless-stopped --env-file .env aaadviser

if errorlevel 1 (
    echo ❌ Ошибка при запуске контейнера
    pause
    exit /b 1
)

echo ✅ Контейнер успешно запущен!

REM Проверка статуса
timeout /t 5 /nobreak >nul
docker ps | findstr aaadviser >nul
if errorlevel 1 (
    echo ❌ Контейнер не запущен. Проверьте логи: docker logs aaadviser
    pause
    exit /b 1
)

echo ✅ Приложение успешно развернуто!
echo 🌐 Доступно по адресу: http://localhost:8080
echo 📊 Статус контейнера:
docker ps | findstr aaadviser

REM Показ логов
echo 📋 Последние логи приложения:
docker logs --tail 20 aaadviser

echo.
echo 🎉 Развертывание завершено успешно!
echo.
echo Полезные команды:
echo   docker logs aaadviser          - просмотр логов
echo   docker logs -f aaadviser        - просмотр логов в реальном времени
echo   docker stop aaadviser           - остановка приложения
echo   docker restart aaadviser        - перезапуск приложения
echo   docker exec -it aaadviser bash  - доступ к контейнеру
echo.
echo Документация:
echo   AMVERA_DEPLOYMENT.md           - инструкция по развертыванию
echo   I18N_README.md                 - документация мультиязычности
echo.
pause

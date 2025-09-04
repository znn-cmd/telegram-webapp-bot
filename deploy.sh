#!/bin/bash

# Скрипт автоматического развертывания на Amvera
# Автор: Aaadviser Team
# Дата: 2024

set -e

echo "🚀 Начинаем развертывание Aaadviser на Amvera..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    error "Docker не установлен. Установите Docker и попробуйте снова."
fi

# Проверка наличия необходимых файлов
if [ ! -f "app.py" ]; then
    error "Файл app.py не найден. Убедитесь, что вы находитесь в корневой директории проекта."
fi

if [ ! -f "requirements.txt" ]; then
    error "Файл requirements.txt не найден."
fi

# Проверка переменных окружения
if [ ! -f ".env" ]; then
    warn "Файл .env не найден. Создайте его с необходимыми переменными окружения."
    echo "Пример содержимого .env:"
    echo "TELEGRAM_BOT_TOKEN=your_bot_token"
    echo "SUPABASE_URL=your_supabase_url"
    echo "SUPABASE_KEY=your_supabase_key"
    echo "OPENAI_API_KEY=your_openai_key"
fi

# Остановка существующего контейнера
log "Останавливаем существующий контейнер..."
docker stop aaadviser 2>/dev/null || true
docker rm aaadviser 2>/dev/null || true

# Удаление старого образа
log "Удаляем старый образ..."
docker rmi aaadviser 2>/dev/null || true

# Выбор Dockerfile
DOCKERFILE="Dockerfile"
if [ "$1" = "minimal" ]; then
    DOCKERFILE="Dockerfile.minimal"
    log "Используем минимальный Dockerfile"
elif [ "$1" = "amvera" ]; then
    DOCKERFILE="Dockerfile.amvera"
    log "Используем альтернативный Dockerfile для Amvera"
fi

# Проверка наличия выбранного Dockerfile
if [ ! -f "$DOCKERFILE" ]; then
    error "Файл $DOCKERFILE не найден."
fi

# Сборка образа
log "Собираем Docker образ..."
if [ "$1" = "minimal" ]; then
    docker build -f Dockerfile.minimal -t aaadviser .
elif [ "$1" = "amvera" ]; then
    docker build -f Dockerfile.amvera -t aaadviser .
else
    docker build -t aaadviser .
fi

if [ $? -eq 0 ]; then
    log "Образ успешно собран!"
else
    error "Ошибка при сборке образа. Попробуйте использовать --minimal или --amvera"
fi

# Запуск контейнера
log "Запускаем контейнер..."
docker run -d \
    --name aaadviser \
    -p 8080:8080 \
    --restart unless-stopped \
    --env-file .env \
    aaadviser

if [ $? -eq 0 ]; then
    log "Контейнер успешно запущен!"
else
    error "Ошибка при запуске контейнера"
fi

# Проверка статуса
sleep 5
if docker ps | grep -q aaadviser; then
    log "✅ Приложение успешно развернуто!"
    log "🌐 Доступно по адресу: http://localhost:8080"
    log "📊 Статус контейнера:"
    docker ps | grep aaadviser
else
    error "Контейнер не запущен. Проверьте логи: docker logs aaadviser"
fi

# Показ логов
log "📋 Последние логи приложения:"
docker logs --tail 20 aaadviser

echo ""
log "🎉 Развертывание завершено успешно!"
echo ""
echo "Полезные команды:"
echo "  docker logs aaadviser          - просмотр логов"
echo "  docker logs -f aaadviser        - просмотр логов в реальном времени"
echo "  docker stop aaadviser           - остановка приложения"
echo "  docker restart aaadviser        - перезапуск приложения"
echo "  docker exec -it aaadviser bash  - доступ к контейнеру"
echo ""
echo "Документация:"
echo "  AMVERA_DEPLOYMENT.md           - инструкция по развертыванию"
echo "  I18N_README.md                 - документация мультиязычности"
echo ""

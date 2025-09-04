#!/bin/bash

# Скрипт для автоматического обновления Aaadviser
# Использование: ./update.sh "описание изменений"

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    print_error "Необходимо указать описание изменений"
    echo "Использование: ./update.sh \"описание изменений\""
    exit 1
fi

COMMIT_MESSAGE="$1"

print_status "Начинаем процесс обновления Aaadviser..."

# Проверка наличия Git
if ! command -v git &> /dev/null; then
    print_error "Git не установлен"
    exit 1
fi

# Проверка статуса Git
print_status "Проверяем статус Git репозитория..."

if [ ! -d ".git" ]; then
    print_error "Не найден Git репозиторий"
    exit 1
fi

# Проверка изменений
if git diff --quiet && git diff --cached --quiet; then
    print_warning "Нет изменений для коммита"
    read -p "Продолжить? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Обновление отменено"
        exit 0
    fi
fi

# Показываем изменения
print_status "Изменения в файлах:"
git status --short

# Добавление всех файлов
print_status "Добавляем файлы в Git..."
git add .

# Коммит
print_status "Создаем коммит с сообщением: '$COMMIT_MESSAGE'"
git commit -m "Update: $COMMIT_MESSAGE"

# Пуш в репозиторий
print_status "Отправляем изменения в репозиторий..."
git push origin main

print_success "Изменения успешно отправлены в репозиторий!"

# Информация о следующем шаге
print_status "Следующие шаги:"
echo "1. Amvera автоматически обнаружит изменения"
echo "2. Запустится новый деплой"
echo "3. Проверьте статус в панели Amvera"
echo "4. Проверьте логи на предмет ошибок"

# Проверка основных файлов
print_status "Проверяем основные файлы..."

if [ -f "app.py" ]; then
    print_success "✓ app.py найден"
else
    print_error "✗ app.py не найден"
fi

if [ -f "amvera.yaml" ]; then
    print_success "✓ amvera.yaml найден"
else
    print_error "✗ amvera.yaml не найден"
fi

if [ -f "requirements.txt" ]; then
    print_success "✓ requirements.txt найден"
else
    print_error "✗ requirements.txt не найден"
fi

# Проверка переменных окружения
print_status "Проверяем переменные окружения в amvera.yaml..."

if grep -q "TELEGRAM_BOT_TOKEN" amvera.yaml; then
    print_success "✓ TELEGRAM_BOT_TOKEN настроен"
else
    print_warning "⚠ TELEGRAM_BOT_TOKEN не найден в amvera.yaml"
fi

if grep -q "SUPABASE_URL" amvera.yaml; then
    print_success "✓ SUPABASE_URL настроен"
else
    print_warning "⚠ SUPABASE_URL не найден в amvera.yaml"
fi

if grep -q "SUPABASE_KEY" amvera.yaml; then
    print_success "✓ SUPABASE_KEY настроен"
else
    print_warning "⚠ SUPABASE_KEY не найден в amvera.yaml"
fi

print_success "Обновление завершено успешно!"
print_status "Не забудьте проверить логи в Amvera после деплоя" 
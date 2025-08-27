#!/bin/bash

echo "🔧 Скрипт для исправления SSL проблем"
echo "===================================="

# Функция для проверки и установки пакетов
install_if_missing() {
    package=$1
    if ! command -v $package &> /dev/null; then
        echo "📦 Установка $package..."
        apt-get update && apt-get install -y $package
    else
        echo "✅ $package уже установлен"
    fi
}

# 1. Обновляем сертификаты
echo -e "\n1️⃣ Обновление сертификатов..."
apt-get update && apt-get install -y ca-certificates
update-ca-certificates

# 2. Устанавливаем необходимые пакеты
echo -e "\n2️⃣ Проверка и установка необходимых пакетов..."
install_if_missing openssl
install_if_missing curl
install_if_missing wget

# 3. Проверяем версию OpenSSL
echo -e "\n3️⃣ Версия OpenSSL:"
openssl version

# 4. Тестируем подключение к Supabase
echo -e "\n4️⃣ Тестирование подключения к Supabase..."
if [ -f .env ]; then
    source .env
    if [ ! -z "$SUPABASE_URL" ]; then
        # Извлекаем хост из URL
        SUPABASE_HOST=$(echo $SUPABASE_URL | sed -e 's|^[^/]*//||' -e 's|/.*$||')
        echo "Проверяем подключение к $SUPABASE_HOST..."
        
        # Тест с curl
        echo -e "\nТест с curl:"
        curl -I -v --connect-timeout 10 https://$SUPABASE_HOST 2>&1 | grep -E "(HTTP|SSL|certificate)"
        
        # Тест с openssl
        echo -e "\nТест с openssl:"
        echo | openssl s_client -connect $SUPABASE_HOST:443 -servername $SUPABASE_HOST 2>/dev/null | openssl x509 -noout -dates
    else
        echo "⚠️ SUPABASE_URL не найден в .env"
    fi
else
    echo "⚠️ Файл .env не найден"
fi

# 5. Экспортируем переменные для отладки
echo -e "\n5️⃣ Настройка переменных окружения для отладки..."
export PYTHONHTTPSVERIFY=1
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_DIR=/etc/ssl/certs
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

echo -e "\n✅ Настройка завершена!"
echo "Теперь попробуйте запустить приложение снова."
echo ""
echo "Если проблема сохраняется, попробуйте:"
echo "1. Временно отключить SSL проверку: export SUPABASE_SSL_VERIFY=false"
echo "2. Запустить тестовый скрипт: python test_ssl_connection.py"
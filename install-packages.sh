#!/bin/bash

# Скрипт для установки пакетов Python по одному с повторными попытками

echo "Начинаем установку пакетов..."

# Функция для установки пакета с повторными попытками
install_package() {
    local package=$1
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "Попытка $attempt из $max_attempts: установка $package"
        
        if pip install "$package" --timeout 300 --retries 5 --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn --no-cache-dir; then
            echo "✅ Успешно установлен: $package"
            return 0
        else
            echo "❌ Ошибка установки $package (попытка $attempt)"
            if [ $attempt -eq $max_attempts ]; then
                echo "❌ Не удалось установить $package после $max_attempts попыток"
                return 1
            fi
            attempt=$((attempt + 1))
            sleep 10
        fi
    done
}

# Обновляем pip
echo "Обновляем pip..."
pip install --upgrade pip --timeout 300 --retries 10 --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

# Устанавливаем пакеты по одному
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
    if ! install_package "$package"; then
        echo "❌ Критическая ошибка: не удалось установить $package"
        exit 1
    fi
done

echo "✅ Все пакеты успешно установлены!"

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование конфигурации pip
COPY pip.conf /etc/pip.conf

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей с улучшенными настройками сети
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Установка прав на выполнение
RUN chmod +x app.py

# Открытие порта
EXPOSE 8080

# Команда запуска
CMD ["python", "app.py"]

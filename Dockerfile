FROM python:3.11-slim

# Установка системных зависимостей для Amvera (только доступные пакеты)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    libglu1-mesa \
    libglx-mesa0 \
    libx11-6 \
    libxau6 \
    libxcb1 \
    libxdmcp6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libexpat1 \
    libfontconfig1 \
    libfreetype6 \
    libgcc-s1 \
    libgdk-pixbuf-xlib-2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrender1 \
    libxtst6 \
    libx11-xcb1 \
    libxcb-dri3-0 \
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

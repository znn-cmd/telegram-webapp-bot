FROM python:3.11-slim

# Установка системных зависимостей для Amvera (оптимизированный список)
RUN apt-get update && apt-get install -y \
    # Основные графические библиотеки
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # OpenGL библиотеки
    libgl1 \
    libglu1-mesa \
    libglx-mesa0 \
    # X11 библиотеки
    libx11-6 \
    libxau6 \
    libxcb1 \
    libxdmcp6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    # Аудио библиотеки
    libasound2 \
    # GTK библиотеки
    libatk1.0-0 \
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
    # NSS библиотеки
    libnspr4 \
    libnss3 \
    # Pango библиотеки
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    # Дополнительные X11 библиотеки
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxrender1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    # Очистка кэша для уменьшения размера образа
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование конфигурации pip
COPY pip.conf /etc/pip.conf

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей с оптимизированными настройками
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Установка прав на выполнение для основных файлов
RUN chmod +x app.py && \
    chmod +x *.sh && \
    chmod +x *.bat

# Создание пользователя для безопасности (опционально)
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

# Открытие порта
EXPOSE 8080

# Переменные окружения для оптимизации
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Команда запуска с обработкой сигналов
CMD ["python", "app.py"]

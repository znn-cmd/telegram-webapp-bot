# 📁 Структура папок для отчетов

## 🏗️ Новая организованная структура

### Структура папок:
```
reports/
├── {telegram_id}/           # Папка пользователя
│   ├── {report_folder_id}/  # Уникальная папка отчета
│   │   ├── {report_id}.html # HTML файл отчета
│   │   └── photos/          # Папка с фотографиями
│   │       ├── property_1.jpg
│   │       ├── property_2.png
│   │       └── ...
│   └── {другой_report_id}/
│       ├── {report_id}.html
│       └── photos/
└── {другой_telegram_id}/
    └── ...
```

### Пример:
```
reports/
├── 123456789/              # telegram_id пользователя
│   ├── 847392058473/       # ID отчета
│   │   ├── 847392058473.html
│   │   └── photos/
│   │       ├── property_1.jpg
│   │       └── property_2.png
│   └── 592847362849/
│       ├── 592847362849.html
│       └── photos/
└── 987654321/
    └── 384756293847/
        ├── 384756293847.html
        └── photos/
```

## 🔗 API эндпоинты

### 1. Доступ к отчетам
```
GET /reports/{telegram_id}/{report_id}/{filename}
```
**Пример:** `/reports/123456789/847392058473/847392058473.html`

### 2. Доступ к фотографиям отчета
```
GET /reports/{telegram_id}/{report_id}/photos/{photo_filename}
```
**Пример:** `/reports/123456789/847392058473/photos/property_1.jpg`

### 3. Legacy поддержка старых отчетов
```
GET /reports/{filename}
```
**Пример:** `/reports/847392058473.html` (для старых отчетов в корне папки reports)

## ⚙️ Процесс создания отчета

### 1. Генерация ID и создание папок
```python
# Генерируем уникальный ID отчета
report_folder_id = ''.join(random.choices(string.digits, k=12))

# Создаем структуру папок
user_reports_dir = os.path.join('reports', str(telegram_id))
report_dir = os.path.join(user_reports_dir, report_folder_id)
os.makedirs(report_dir, exist_ok=True)

# Путь к файлу отчета
filename = f"{report_folder_id}.html"
file_path = os.path.join(report_dir, filename)

# Папка для фотографий
photos_dir = os.path.join(report_dir, 'photos')
```

### 2. Сохранение фотографий
```python
if property_info.get('photos'):
    # Создаем папку для фотографий
    os.makedirs(photos_dir, exist_ok=True)
    
    for i, photo in enumerate(property_info['photos']):
        # Декодируем base64 и сохраняем файл
        photo_filename = f"property_{i+1}.jpg"
        photo_path = os.path.join(photos_dir, photo_filename)
        # ... сохранение файла
```

### 3. Генерация URL
```python
# URL отчета
report_url = f"/reports/{telegram_id}/{report_folder_id}/{filename}"

# URL верификации
verification_url = f"{host}/reports/{telegram_id}/{report_folder_id}/{filename}"
```

## 🎯 Преимущества новой структуры

### ✅ Организация
- **Изоляция пользователей:** Каждый пользователь имеет свою папку
- **Уникальность отчетов:** Каждый отчет в отдельной папке
- **Группировка файлов:** Фотографии хранятся вместе с отчетом

### ✅ Безопасность
- **Контроль доступа:** Легко проверить права доступа по telegram_id
- **Изоляция данных:** Файлы пользователей не смешиваются

### ✅ Масштабируемость
- **Производительность:** Быстрый доступ к файлам через структурированные папки
- **Управление:** Легко найти и управлять отчетами конкретного пользователя
- **Очистка:** Простое удаление всех данных пользователя

### ✅ Обслуживание
- **Резервное копирование:** Легко создавать бэкапы по пользователям
- **Мониторинг:** Отслеживание использования дискового пространства
- **Архивирование:** Возможность архивировать старые отчеты

## 🔧 Совместимость

- **Legacy поддержка:** Старые отчеты остаются доступными через `/reports/{filename}`
- **Миграция:** Постепенный переход на новую структуру
- **Обратная совместимость:** Существующие ссылки продолжают работать

## 📊 Мониторинг

Для мониторинга использования дискового пространства можно использовать:
```bash
# Размер папки конкретного пользователя
du -sh reports/{telegram_id}/

# Общий размер всех отчетов
du -sh reports/

# Количество отчетов пользователя
find reports/{telegram_id}/ -name "*.html" | wc -l
```

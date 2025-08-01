# Быстрое обновление Aaadviser

## 🚀 Быстрый старт

### 1. Обновление файлов
```bash
# Внесите изменения в файлы
# Сохраните все изменения
```

### 2. Загрузка на GitHub
```bash
git add .
git commit -m "Update: краткое описание изменений"
git push origin main
```

### 3. Автоматический деплой
- Amvera автоматически обнаружит изменения
- Запустится новый деплой
- Проверьте статус в панели Amvera

## 📁 Основные файлы для редактирования

| Файл | Назначение |
|------|------------|
| `app.py` | Основная логика, API endpoints |
| `webapp_*.html` | Интерфейс WebApp |
| `ux-utils.js` | JavaScript утилиты |
| `styles.css` | Стили |
| `locales.py` | Переводы |

## 🔧 Добавление новой страницы

1. Создайте `webapp_newpage.html`
2. Добавьте в `app.py`:
```python
@app.route('/webapp_newpage')
def webapp_newpage():
    with open('webapp_newpage.html', 'r', encoding='utf-8') as f:
        return f.read()
```

## 🔧 Добавление нового API

```python
@app.route('/api/new_endpoint', methods=['POST'])
def api_new_endpoint():
    data = request.json or {}
    # Ваша логика
    return jsonify({'success': True})
```

## 🔍 Проверка после деплоя

1. Откройте панель Amvera
2. Проверьте логи на ошибки
3. Протестируйте основные endpoints:
   - `/health`
   - `/webapp`
   - `/api/user`

## ⚠️ Важные моменты

- **НЕ храните API ключи в коде**
- Используйте переменные окружения в Amvera
- Проверяйте логи после каждого деплоя
- Тестируйте локально перед загрузкой

## 🆘 Устранение проблем

### Ошибка импорта
```bash
pip install -r requirements.txt
```

### Ошибка подключения к БД
- Проверьте переменные окружения в Amvera
- Убедитесь в правильности URL и ключей Supabase

### Ошибка Telegram API
- Проверьте токен бота в Amvera
- Убедитесь в правильности WebApp URL

## 📞 Поддержка

При проблемах:
1. Проверьте логи в Amvera
2. Изучите `DEPLOYMENT_GUIDE.md`
3. Обратитесь к команде разработки 
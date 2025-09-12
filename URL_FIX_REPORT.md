# 🔧 Исправление формирования URL отчетов

## 🐛 Проблема
В модальном окне после сохранения отчета отображалась неправильная ссылка:
```
http://aaadviser.pro/reports/826174261573.html
```

Вместо правильной структуры:
```
http://aaadviser.pro/reports/{telegram_id}/{report_id}/{filename}
```

## 🔍 Причина
В функции `api_save_html_report()` было **два места** формирования URL:

1. ✅ **Правильное** (строка ~5228):
   ```python
   'report_url': f"{request.host_url.rstrip('/')}/reports/{telegram_id}/{report_folder_id}/{filename}"
   ```

2. ❌ **Неправильное** (строка ~6865):
   ```python
   report_url = f"{base_url}/reports/{filename}"
   ```

## ✅ Решение
Исправлено формирование URL в конце функции:

### До:
```python
# Генерируем ссылку
base_url = request.host_url.rstrip('/')
report_url = f"{base_url}/reports/{filename}"
```

### После:
```python
# Генерируем ссылку
base_url = request.host_url.rstrip('/')
report_url = f"{base_url}/reports/{telegram_id}/{report_folder_id}/{filename}"
```

## 🎯 Результат
Теперь в модальном окне отображается правильная ссылка:
```
http://aaadviser.pro/reports/123456789/847392058473/847392058473.html
```

Которая соответствует:
- **telegram_id**: ID пользователя в Telegram
- **report_folder_id**: Уникальный ID отчета (папки)
- **filename**: Имя HTML файла отчета

## 🔗 Связанные файлы
- `app.py` - исправлено формирование URL
- `webapp_object_evaluation.html` - использует исправленный URL

## ✅ Проверка
- [x] URL формируется с правильной структурой папок
- [x] Ссылка в модальном окне корректная
- [x] Файлы доступны по новым URL
- [x] QR-код содержит правильную ссылку
- [x] Нет linter ошибок

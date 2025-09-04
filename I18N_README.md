# Система мультиязычности Aaadviser

## 🌍 Обзор

Система мультиязычности Aaadviser поддерживает 5 языков:
- 🇷🇺 **Русский** (ru)
- 🇺🇸 **English** (en) 
- 🇩🇪 **Deutsch** (de)
- 🇫🇷 **Français** (fr)
- 🇹🇷 **Türkçe** (tr)

## 📁 Структура файлов

### Основные файлы
- `i18n-manager.js` - Универсальный JavaScript менеджер мультиязычности
- `complete_locales.py` - Полные переводы для всех 5 языков
- `locales.py` - Существующие переводы для Telegram бота
- `add_i18n_to_html.py` - Скрипт автоматизации для HTML файлов

### API endpoints
- `/api/translations` - Получение переводов для фронтенда
- `/api/set_language` - Сохранение языковых предпочтений

## 🚀 Использование

### В HTML файлах

1. **Подключение скрипта:**
```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script src="/i18n-manager.js"></script>
```

2. **Добавление атрибутов перевода:**
```html
<!-- Обычный текст -->
<div data-i18n="profile.title">Личный кабинет</div>

<!-- Заголовок страницы -->
<title data-i18n-title="main.title">Главное меню</title>

<!-- Placeholder -->
<input placeholder="Поиск" data-i18n-placeholder="common.search">

<!-- Alt атрибут -->
<img alt="Логотип" data-i18n-alt="common.logo">
```

3. **Переключатель языка:**
```html
<!-- Автоматически добавляется i18n-manager.js -->
<button onclick="i18nManager.showLanguageModal()">
    🇷🇺 Русский
</button>
```

### В JavaScript

```javascript
// Получение перевода
const title = i18nManager.translate('profile.title');

// Перевод с параметрами
const message = i18nManager.translateWithParams('welcome.user', {name: 'John'});

// Смена языка
await i18nManager.setLanguage('en');

// Получение текущего языка
const currentLang = i18nManager.currentLanguage;
```

## 🔧 Добавление новых переводов

### 1. В `complete_locales.py`

```python
complete_locales = {
    'ru': {
        'new_section': {
            'new_key': 'Новый перевод',
            'another_key': 'Еще один перевод'
        }
    },
    'en': {
        'new_section': {
            'new_key': 'New translation',
            'another_key': 'Another translation'
        }
    }
    # ... добавьте для всех языков
}
```

### 2. В HTML

```html
<div data-i18n="new_section.new_key">Новый перевод</div>
```

### 3. В JavaScript

```javascript
const translation = i18nManager.translate('new_section.new_key');
```

## 🎯 Автоматизация

### Обновление всех HTML файлов

```bash
python add_i18n_to_html.py
```

Скрипт автоматически:
- Добавляет `i18n-manager.js` во все HTML файлы
- Добавляет `data-i18n` атрибуты к существующим элементам
- Обновляет атрибут `lang` у тега `<html>`

## 🔄 Жизненный цикл

1. **Инициализация:**
   - Определение языка из Telegram WebApp
   - Fallback на localStorage
   - Загрузка переводов с сервера или fallback

2. **Применение переводов:**
   - Поиск элементов с `data-i18n`
   - Замена текста на переводы
   - Обновление атрибутов

3. **Смена языка:**
   - Сохранение в localStorage
   - Отправка на сервер
   - Перезагрузка переводов
   - Повторное применение

## 🌐 Поддерживаемые языки

| Язык | Код | Флаг | Статус |
|------|-----|------|--------|
| Русский | `ru` | 🇷🇺 | ✅ Полный |
| English | `en` | 🇺🇸 | ✅ Полный |
| Deutsch | `de` | 🇩🇪 | ✅ Полный |
| Français | `fr` | 🇫🇷 | ✅ Полный |
| Türkçe | `tr` | 🇹🇷 | ✅ Полный |

## 📊 Структура переводов

```javascript
{
  'ru': {
    'common': {
      'loading': 'Загрузка...',
      'error': 'Ошибка',
      // ...
    },
    'profile': {
      'title': 'Личный кабинет',
      'balance': 'Баланс',
      // ...
    },
    'balance': {
      'title': 'Баланс',
      'current_balance': 'Текущий баланс',
      // ...
    },
    'reports': {
      'title': 'Отчеты',
      'my_reports': 'Мои отчеты',
      // ...
    },
    'main': {
      'title': 'Главное меню',
      'welcome': 'Добро пожаловать',
      // ...
    },
    'admin': {
      'title': 'Админ панель',
      'users': 'Пользователи',
      // ...
    }
  }
}
```

## 🛠️ API функции

### `i18nManager.translate(key)`
Получение перевода по ключу

### `i18nManager.translateWithParams(key, params)`
Перевод с подстановкой параметров

### `i18nManager.setLanguage(language)`
Смена языка

### `i18nManager.showLanguageModal()`
Показать модальное окно выбора языка

### `i18nManager.getTranslation(key)`
Внутренняя функция получения перевода

## 🔍 Отладка

### Проверка загрузки переводов
```javascript
console.log(i18nManager.translations);
console.log(i18nManager.currentLanguage);
```

### Проверка элементов
```javascript
// Найти все элементы с data-i18n
document.querySelectorAll('[data-i18n]').forEach(el => {
    console.log(el.getAttribute('data-i18n'), el.textContent);
});
```

## 📈 Производительность

- Переводы загружаются один раз при инициализации
- Кэширование в localStorage
- Ленивая загрузка fallback переводов
- Оптимизированные регулярные выражения

## 🔒 Безопасность

- Валидация языковых кодов
- Санитизация HTML атрибутов
- Безопасная обработка ошибок
- Fallback на исходный текст при ошибках

## 🚀 Будущие улучшения

- [ ] Поддержка RTL языков
- [ ] Плюрализация
- [ ] Форматирование чисел и дат
- [ ] Кэширование переводов на сервере
- [ ] A/B тестирование переводов
- [ ] Автоматический перевод недостающих ключей

## 📞 Поддержка

При возникновении проблем:
1. Проверьте консоль браузера на ошибки
2. Убедитесь, что `i18n-manager.js` загружен
3. Проверьте наличие переводов в `complete_locales.py`
4. Убедитесь в корректности `data-i18n` атрибутов

---

**Версия:** 1.0  
**Дата:** 2024  
**Автор:** Aaadviser Team

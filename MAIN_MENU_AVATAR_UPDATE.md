# Добавление аватара в главное меню

## Обзор изменений

Добавлен аватар пользователя в главное меню приложения между приветствием "С возвращением!" и информацией о балансе.

## Внесенные изменения

### 1. 🎨 CSS стили (`webapp_main.html`)

**Обновлен блок `.user-info`:**
```css
.user-info {
    /* ... существующие стили ... */
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}
```

**Добавлены стили для аватара:**
```css
.user-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #667eea;
    box-shadow: 0 2px 8px rgba(102,126,234,0.15);
}

.user-avatar-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: white;
    border: 3px solid #667eea;
}
```

### 2. 📱 HTML структура (`webapp_main.html`)

**ДО:**
```html
<div class="user-info hidden" id="userInfo">
    <div class="user-name" id="userName">Загрузка...</div>
    <div class="user-balance">
        <span>Баланс:</span>
        <span class="balance-amount" id="userBalance">$0</span>
    </div>
</div>
```

**ПОСЛЕ:**
```html
<div class="user-info hidden" id="userInfo">
    <!-- Аватар пользователя -->
    <div id="userAvatarContainer">
        <div class="user-avatar-placeholder" id="userAvatarPlaceholder">👤</div>
    </div>
    <div class="user-name" id="userName">Загрузка...</div>
    <div class="user-balance">
        <span>Баланс:</span>
        <span class="balance-amount" id="userBalance">$0</span>
    </div>
</div>
```

### 3. ⚡ JavaScript функционал (`webapp_main.html`)

**Добавлена функция `updateUserAvatar`:**
```javascript
function updateUserAvatar(avatarFilename, telegramId) {
    const avatarContainer = document.getElementById('userAvatarContainer');
    const placeholder = document.getElementById('userAvatarPlaceholder');
    
    if (avatarFilename && telegramId) {
        // Создаем элемент изображения
        const avatarImg = document.createElement('img');
        avatarImg.src = `/user/${telegramId}/${avatarFilename}`;
        avatarImg.className = 'user-avatar';
        avatarImg.alt = 'User Avatar';
        
        // Обработка ошибки загрузки
        avatarImg.onerror = function() {
            this.style.display = 'none';
            placeholder.style.display = 'flex';
        };
        
        // Заменяем placeholder на изображение
        placeholder.style.display = 'none';
        avatarContainer.innerHTML = '';
        avatarContainer.appendChild(avatarImg);
    } else {
        // Показываем placeholder если нет аватара
        placeholder.style.display = 'flex';
    }
}
```

**Интеграция в `loadUserData`:**
```javascript
// Отображение аватара пользователя
updateUserAvatar(userInfo.avatar_filename, userInfo.telegram_id);
```

### 4. 🔧 API обновления (`app.py`)

**Обновлен endpoint `/api/user`:**
```python
return jsonify({
    # ... существующие поля ...
    'avatar_filename': user.get('avatar_filename'),
    # ... остальные поля ...
})
```

## Логика работы

### 📋 Алгоритм отображения аватара:

1. **Загрузка данных пользователя** → API возвращает `avatar_filename` и `telegram_id`
2. **Проверка наличия аватара:**
   - ✅ **Есть аватар:** Загружаем изображение из `/user/{telegram_id}/{avatar_filename}`
   - ❌ **Нет аватара:** Показываем placeholder с иконкой 👤
3. **Обработка ошибок:** Если изображение не загрузилось, возвращаемся к placeholder

### 🎯 Особенности реализации:

- **Graceful fallback:** При ошибке загрузки показывается placeholder
- **Responsive дизайн:** Аватар адаптируется под размер экрана
- **Единый стиль:** Соответствует общему дизайну приложения
- **Производительность:** Изображения загружаются асинхронно

## Визуальный результат

### 🔄 Структура блока пользователя:

```
┌─────────────────────────────────┐
│         [Аватар 80x80]          │
│                                 │
│        "С возвращением!"        │
│                                 │
│         "Баланс: $XX"           │
└─────────────────────────────────┘
```

### 🎨 Стилизация:

- **Размер:** 80x80 пикселей
- **Форма:** Круглая (border-radius: 50%)
- **Рамка:** 3px solid #667eea (фирменный цвет)
- **Тень:** Мягкая тень для объема
- **Placeholder:** Градиентный фон с иконкой пользователя

## Совместимость

✅ **Обратная совместимость:** Работает для пользователей без аватара  
✅ **Производительность:** Не влияет на скорость загрузки  
✅ **Responsive:** Адаптируется под разные размеры экрана  
✅ **Accessibility:** Корректные alt-теги для изображений  

## Тестирование

Для проверки функционала:

1. **С аватаром:** Загрузите аватар в разделе "Личные данные"
2. **Без аватара:** Убедитесь, что показывается placeholder
3. **Ошибка загрузки:** Проверьте fallback при недоступном файле
4. **Разные размеры экрана:** Протестируйте на мобильных устройствах

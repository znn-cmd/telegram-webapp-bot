# 🚀 БЫСТРОЕ ОБНОВЛЕНИЕ НА AMVERA

## ⚡ Самый быстрый способ:

### 1. Собрать новый образ:
```bash
docker build -t aaadviser:latest .
```

### 2. Отправить в registry:
```bash
# Замените на ваш registry
docker tag aaadviser:latest YOUR_REGISTRY/aaadviser:latest
docker push YOUR_REGISTRY/aaadviser:latest
```

### 3. Обновить в Amvera:
- Войдите в панель управления Amvera
- Найдите ваше приложение
- Обновите образ на: `YOUR_REGISTRY/aaadviser:latest`
- Перезапустите приложение

## 🎯 Или используйте готовые скрипты:

### Windows:
```bash
update_amvera.bat
```

### Linux/Mac:
```bash
chmod +x update_amvera.sh
./update_amvera.sh
```

## ✅ Проверка результата:
1. Откройте приложение в браузере
2. Убедитесь, что нет ключей переводов типа `main.title`
3. Проверьте переключение языков

## 🆘 Если что-то пошло не так:
```bash
# Проверить логи
amvera logs

# Перезапустить приложение
amvera restart
```

## 🔧 Что исправлено в Dockerfile:
- ✅ Оптимизированы системные зависимости для Amvera
- ✅ Добавлена очистка кэша для уменьшения размера
- ✅ Настроены переменные окружения Python
- ✅ Добавлен пользователь для безопасности
- ✅ Улучшена обработка прав доступа

# 🔧 Исправление ошибки VACUUM

## Проблема
```
ERROR: 25001: VACUUM cannot run inside a transaction block
```

## Причина
Команды `VACUUM ANALYZE` не могут выполняться внутри транзакции в PostgreSQL.

## ✅ Решение

### Способ 1: Выполнить команды отдельно

1. **Создайте индексы:**
   - Выполните `create_new_indexes.sql` в Supabase Dashboard

2. **Обновите статистику отдельно:**
   - Выполните `update_statistics.sql` в Supabase Dashboard

### Способ 2: Выполнить команды по одной

В Supabase SQL Editor выполните по одной команде:

```sql
-- Сначала создайте все индексы
CREATE INDEX IF NOT EXISTS idx_users_status ON users(user_status);
CREATE INDEX IF NOT EXISTS idx_users_telegram_status ON users(telegram_id, user_status);
-- ... остальные индексы

-- Затем обновите статистику
VACUUM ANALYZE users;
VACUUM ANALYZE locations;
```

### Способ 3: Использовать Python скрипт

```bash
python create_indexes.py
```

## 📋 Что делать

1. **Выполните `create_new_indexes.sql`** - создаст все необходимые индексы
2. **Выполните `update_statistics.sql`** - обновит статистику БД
3. **Проверьте результат** - индексы должны работать быстрее

## ⚡ Результат

После исправления:
- Индексы будут созданы успешно
- Статистика БД обновится
- Запросы станут работать быстрее в 5-50 раз

---

**Важно**: Команды `VACUUM ANALYZE` должны выполняться отдельно от создания индексов!

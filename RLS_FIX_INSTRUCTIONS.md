# Инструкция по исправлению RLS политики для таблицы currency

## Проблема
В логе видна ошибка: `new row violates row-level security policy for table "currency"`

Это означает, что в Supabase включена RLS (Row Level Security) политика, которая блокирует вставку новых записей в таблицу `currency`.

## Решение

### Вариант 1: Отключить RLS (рекомендуется для таблицы курсов валют)

1. Откройте **Supabase Dashboard**
2. Перейдите в **SQL Editor**
3. Выполните команду:

```sql
ALTER TABLE currency DISABLE ROW LEVEL SECURITY;
```

### Вариант 2: Настроить RLS политику (если безопасность критична)

1. В **SQL Editor** выполните:

```sql
-- Включаем RLS
ALTER TABLE currency ENABLE ROW LEVEL SECURITY;

-- Создаем политику для вставки (разрешаем всем аутентифицированным пользователям)
CREATE POLICY "Enable insert for authenticated users" ON currency
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Создаем политику для чтения (разрешаем всем)
CREATE POLICY "Enable read access for all users" ON currency
    FOR SELECT USING (true);
```

### Вариант 3: Проверить текущий статус

Выполните в **SQL Editor**:

```sql
-- Проверяем текущий статус RLS
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'currency';

-- Проверяем существующие политики
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'currency';
```

## Рекомендация

Для таблицы `currency` рекомендуется **Вариант 1** (отключить RLS), так как:
- Курсы валют - это публичные данные
- Нет необходимости в строгом контроле доступа
- Упрощает работу приложения

## После исправления

1. Перезапустите приложение
2. Попробуйте сгенерировать отчет с турецким адресом
3. Проверьте, что курсы валют сохраняются в базу

## Альтернативное решение

Если по каким-то причинам нельзя изменить RLS политику, приложение теперь имеет fallback механизм:
- При ошибке RLS возвращает курсы валют без сохранения в базу
- Отчет все равно будет сгенерирован с актуальными курсами
- Данные будут получены с currencylayer.com API

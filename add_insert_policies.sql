-- Добавление политик для записи данных в Supabase
-- Выполните этот скрипт в SQL Editor в Supabase Dashboard

-- Политики для записи в short_term_rentals
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'short_term_rentals' AND policyname = 'Allow public insert access') THEN
        CREATE POLICY "Allow public insert access" ON short_term_rentals FOR INSERT WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'short_term_rentals' AND policyname = 'Allow public update access') THEN
        CREATE POLICY "Allow public update access" ON short_term_rentals FOR UPDATE USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Политики для записи в long_term_rentals
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'long_term_rentals' AND policyname = 'Allow public insert access') THEN
        CREATE POLICY "Allow public insert access" ON long_term_rentals FOR INSERT WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'long_term_rentals' AND policyname = 'Allow public update access') THEN
        CREATE POLICY "Allow public update access" ON long_term_rentals FOR UPDATE USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Политики для записи в property_sales
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'property_sales' AND policyname = 'Allow public insert access') THEN
        CREATE POLICY "Allow public insert access" ON property_sales FOR INSERT WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'property_sales' AND policyname = 'Allow public update access') THEN
        CREATE POLICY "Allow public update access" ON property_sales FOR UPDATE USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Политики для записи в historical_prices
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'historical_prices' AND policyname = 'Allow public insert access') THEN
        CREATE POLICY "Allow public insert access" ON historical_prices FOR INSERT WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'historical_prices' AND policyname = 'Allow public update access') THEN
        CREATE POLICY "Allow public update access" ON historical_prices FOR UPDATE USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Политики для записи в market_statistics
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_statistics' AND policyname = 'Allow public insert access') THEN
        CREATE POLICY "Allow public insert access" ON market_statistics FOR INSERT WITH CHECK (true);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'market_statistics' AND policyname = 'Allow public update access') THEN
        CREATE POLICY "Allow public update access" ON market_statistics FOR UPDATE USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Проверка созданных политик
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename IN ('short_term_rentals', 'long_term_rentals', 'property_sales', 'historical_prices', 'market_statistics')
ORDER BY tablename, policyname; 
-- Добавление недостающих колонок во все таблицы

-- 1. Добавляем колонки в long_term_rentals
ALTER TABLE long_term_rentals 
ADD COLUMN IF NOT EXISTS deposit_currency VARCHAR(10),
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER;

-- 2. Добавляем колонки в property_sales
ALTER TABLE property_sales 
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER,
ADD COLUMN IF NOT EXISTS construction_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS ownership_type VARCHAR(50);

-- 3. Добавляем колонки в short_term_rentals
ALTER TABLE short_term_rentals 
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER;

-- 4. Проверяем и добавляем колонки в historical_prices
ALTER TABLE historical_prices 
ADD COLUMN IF NOT EXISTS source VARCHAR(100);

-- 5. Проверяем и добавляем колонки в market_statistics
ALTER TABLE market_statistics 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Обновляем политики RLS для новых колонок
-- Long term rentals
DROP POLICY IF EXISTS "Enable read access for all users" ON long_term_rentals;
CREATE POLICY "Enable read access for all users" ON long_term_rentals FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON long_term_rentals FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON long_term_rentals FOR UPDATE USING (true);

-- Property sales
DROP POLICY IF EXISTS "Enable read access for all users" ON property_sales;
CREATE POLICY "Enable read access for all users" ON property_sales FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON property_sales FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON property_sales FOR UPDATE USING (true);

-- Short term rentals
DROP POLICY IF EXISTS "Enable read access for all users" ON short_term_rentals;
CREATE POLICY "Enable read access for all users" ON short_term_rentals FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON short_term_rentals FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON short_term_rentals FOR UPDATE USING (true);

-- Historical prices
DROP POLICY IF EXISTS "Enable read access for all users" ON historical_prices;
CREATE POLICY "Enable read access for all users" ON historical_prices FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON historical_prices FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON historical_prices FOR UPDATE USING (true);

-- Market statistics
DROP POLICY IF EXISTS "Enable read access for all users" ON market_statistics;
CREATE POLICY "Enable read access for all users" ON market_statistics FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON market_statistics FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for all users" ON market_statistics FOR UPDATE USING (true); 
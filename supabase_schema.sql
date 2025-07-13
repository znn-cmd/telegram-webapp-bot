-- Создание таблиц для бота недвижимости в Supabase
-- Выполните этот скрипт в SQL Editor в Supabase Dashboard

-- 1. Таблица краткосрочной аренды
CREATE TABLE IF NOT EXISTS short_term_rentals (
    id BIGSERIAL PRIMARY KEY,
    property_id VARCHAR(100) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    max_guests INTEGER NOT NULL,
    amenities TEXT,
    description TEXT,
    photos TEXT,
    source VARCHAR(50) NOT NULL,
    source_url TEXT,
    source_id VARCHAR(100),
    price_per_night DECIMAL(10, 2) NOT NULL,
    price_currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    availability_rate DECIMAL(5, 2),
    avg_rating DECIMAL(3, 2),
    review_count INTEGER,
    host_name VARCHAR(200),
    host_rating DECIMAL(3, 2),
    host_review_count INTEGER,
    instant_bookable BOOLEAN DEFAULT false,
    superhost BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- 2. Таблица долгосрочной аренды
CREATE TABLE IF NOT EXISTS long_term_rentals (
    id BIGSERIAL PRIMARY KEY,
    property_id VARCHAR(100) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    floor_area_sqm DECIMAL(8, 2),
    land_area_sqm DECIMAL(8, 2),
    amenities TEXT,
    description TEXT,
    photos TEXT,
    source VARCHAR(50) NOT NULL,
    source_url TEXT,
    source_id VARCHAR(100),
    monthly_rent DECIMAL(12, 2) NOT NULL,
    rent_currency VARCHAR(10) NOT NULL DEFAULT 'TRY',
    deposit_amount DECIMAL(12, 2),
    deposit_currency VARCHAR(10) DEFAULT 'TRY',
    utilities_included BOOLEAN DEFAULT false,
    pet_friendly BOOLEAN DEFAULT false,
    furnished BOOLEAN DEFAULT false,
    available_from DATE,
    lease_term_months INTEGER,
    agent_name VARCHAR(200),
    agent_rating DECIMAL(3, 2),
    agent_review_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- 3. Таблица продажи недвижимости
CREATE TABLE IF NOT EXISTS property_sales (
    id BIGSERIAL PRIMARY KEY,
    property_id VARCHAR(100) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    city VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    floor_area_sqm DECIMAL(8, 2),
    land_area_sqm DECIMAL(8, 2),
    amenities TEXT,
    description TEXT,
    photos TEXT,
    source VARCHAR(50) NOT NULL,
    source_url TEXT,
    source_id VARCHAR(100),
    asking_price DECIMAL(15, 2) NOT NULL,
    price_currency VARCHAR(10) NOT NULL DEFAULT 'TRY',
    price_per_sqm DECIMAL(10, 2),
    property_age_years INTEGER,
    construction_status VARCHAR(50),
    ownership_type VARCHAR(50),
    agent_name VARCHAR(200),
    agent_rating DECIMAL(3, 2),
    agent_review_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- 4. Таблица исторических цен
CREATE TABLE IF NOT EXISTS historical_prices (
    id BIGSERIAL PRIMARY KEY,
    property_id VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    price DECIMAL(15, 2) NOT NULL,
    price_currency VARCHAR(10) NOT NULL,
    price_type VARCHAR(20) NOT NULL, -- 'sale', 'rent', 'short_term'
    source VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(property_id, date, price_type)
);

-- 5. Таблица рыночной статистики
CREATE TABLE IF NOT EXISTS market_statistics (
    id BIGSERIAL PRIMARY KEY,
    district VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    avg_sale_price_per_sqm DECIMAL(10, 2),
    avg_rent_price_per_month DECIMAL(12, 2),
    avg_short_term_price_per_night DECIMAL(8, 2),
    property_count INTEGER,
    avg_property_age DECIMAL(5, 2),
    avg_bedrooms DECIMAL(3, 1),
    avg_bathrooms DECIMAL(3, 1),
    avg_floor_area DECIMAL(8, 2),
    avg_land_area DECIMAL(8, 2),
    price_change_1y DECIMAL(5, 2),
    price_change_3y DECIMAL(5, 2),
    price_change_5y DECIMAL(5, 2),
    rent_yield_avg DECIMAL(5, 2),
    occupancy_rate_short_term DECIMAL(5, 2),
    days_on_market_avg DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(district, date)
);

-- Создание индексов для улучшения производительности
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_district ON short_term_rentals(district);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_price ON short_term_rentals(price_per_night);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_bedrooms ON short_term_rentals(bedrooms);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_location ON short_term_rentals(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_long_term_rentals_district ON long_term_rentals(district);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_price ON long_term_rentals(monthly_rent);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_bedrooms ON long_term_rentals(bedrooms);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_location ON long_term_rentals(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_property_sales_district ON property_sales(district);
CREATE INDEX IF NOT EXISTS idx_property_sales_price ON property_sales(asking_price);
CREATE INDEX IF NOT EXISTS idx_property_sales_bedrooms ON property_sales(bedrooms);
CREATE INDEX IF NOT EXISTS idx_property_sales_location ON property_sales(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_historical_prices_property ON historical_prices(property_id);
CREATE INDEX IF NOT EXISTS idx_historical_prices_date ON historical_prices(date);
CREATE INDEX IF NOT EXISTS idx_historical_prices_type ON historical_prices(price_type);

CREATE INDEX IF NOT EXISTS idx_market_statistics_district ON market_statistics(district);
CREATE INDEX IF NOT EXISTS idx_market_statistics_date ON market_statistics(date);

-- Включение Row Level Security (RLS) для безопасности
ALTER TABLE short_term_rentals ENABLE ROW LEVEL SECURITY;
ALTER TABLE long_term_rentals ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE historical_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_statistics ENABLE ROW LEVEL SECURITY;

-- Создание политик для публичного доступа (только чтение)
CREATE POLICY "Allow public read access" ON short_term_rentals FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON long_term_rentals FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON property_sales FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON historical_prices FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON market_statistics FOR SELECT USING (true);

-- Создание функций для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггеров для автоматического обновления updated_at
CREATE TRIGGER update_short_term_rentals_updated_at 
    BEFORE UPDATE ON short_term_rentals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_long_term_rentals_updated_at 
    BEFORE UPDATE ON long_term_rentals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_property_sales_updated_at 
    BEFORE UPDATE ON property_sales 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Функция для расчета ROI
CREATE OR REPLACE FUNCTION calculate_roi(
    property_id_param VARCHAR(100),
    investment_amount DECIMAL(15, 2),
    monthly_rent_income DECIMAL(12, 2),
    annual_expenses DECIMAL(12, 2) DEFAULT 0
)
RETURNS TABLE(
    roi_percentage DECIMAL(5, 2),
    annual_return DECIMAL(12, 2),
    monthly_cash_flow DECIMAL(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ((monthly_rent_income * 12 - annual_expenses) / investment_amount * 100)::DECIMAL(5, 2) as roi_percentage,
        (monthly_rent_income * 12 - annual_expenses)::DECIMAL(12, 2) as annual_return,
        (monthly_rent_income - annual_expenses / 12)::DECIMAL(12, 2) as monthly_cash_flow;
END;
$$ LANGUAGE plpgsql;

-- Функция для поиска похожих объектов
CREATE OR REPLACE FUNCTION find_similar_properties(
    target_property_id VARCHAR(100),
    property_type_param VARCHAR(50),
    max_distance_km DECIMAL(5, 2) DEFAULT 5.0,
    price_tolerance_percent DECIMAL(5, 2) DEFAULT 20.0
)
RETURNS TABLE(
    property_id VARCHAR(100),
    address TEXT,
    distance_km DECIMAL(5, 2),
    price_difference_percent DECIMAL(5, 2),
    similarity_score DECIMAL(5, 2)
) AS $$
DECLARE
    target_lat DECIMAL(10, 8);
    target_lng DECIMAL(11, 8);
    target_price DECIMAL(10, 2);
BEGIN
    -- Получаем данные целевого объекта
    SELECT latitude, longitude, price_per_night 
    INTO target_lat, target_lng, target_price
    FROM short_term_rentals 
    WHERE property_id = target_property_id;
    
    IF NOT FOUND THEN
        RETURN;
    END IF;
    
    RETURN QUERY
    SELECT 
        str.property_id,
        str.address,
        (6371 * acos(cos(radians(target_lat)) * cos(radians(str.latitude)) * 
         cos(radians(str.longitude) - radians(target_lng)) + 
         sin(radians(target_lat)) * sin(radians(str.latitude))))::DECIMAL(5, 2) as distance_km,
        ABS((str.price_per_night - target_price) / target_price * 100)::DECIMAL(5, 2) as price_difference_percent,
        (100 - ABS((str.price_per_night - target_price) / target_price * 100))::DECIMAL(5, 2) as similarity_score
    FROM short_term_rentals str
    WHERE str.property_id != target_property_id
    AND str.property_type = property_type_param
    AND (6371 * acos(cos(radians(target_lat)) * cos(radians(str.latitude)) * 
         cos(radians(str.longitude) - radians(target_lng)) + 
         sin(radians(target_lat)) * sin(radians(str.latitude)))) <= max_distance_km
    AND ABS((str.price_per_night - target_price) / target_price * 100) <= price_tolerance_percent
    ORDER BY similarity_score DESC, distance_km ASC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения рыночной статистики по району
CREATE OR REPLACE FUNCTION get_market_stats_by_district(
    district_param VARCHAR(100),
    months_back INTEGER DEFAULT 12
)
RETURNS TABLE(
    district VARCHAR(100),
    avg_price_per_sqm DECIMAL(10, 2),
    avg_rent_per_month DECIMAL(12, 2),
    avg_short_term_price DECIMAL(8, 2),
    price_change_1y DECIMAL(5, 2),
    rent_yield DECIMAL(5, 2),
    property_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ms.district,
        ms.avg_sale_price_per_sqm,
        ms.avg_rent_price_per_month,
        ms.avg_short_term_price_per_night,
        ms.price_change_1y,
        ms.rent_yield_avg,
        ms.property_count
    FROM market_statistics ms
    WHERE ms.district = district_param
    AND ms.date >= CURRENT_DATE - INTERVAL '1 month' * months_back
    ORDER BY ms.date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql; 
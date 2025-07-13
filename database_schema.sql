-- =====================================================
-- Схема базы данных для системы недвижимости
-- Поддержка краткосрочной аренды, долгосрочной аренды и продаж
-- =====================================================

-- Создание таблиц для краткосрочной аренды (Airbnb, Booking.com)
-- =====================================================

CREATE TABLE IF NOT EXISTS short_term_rentals (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(100),
    district VARCHAR(100),
    property_type VARCHAR(50),
    bedrooms INTEGER,
    bathrooms INTEGER,
    max_guests INTEGER,
    amenities TEXT[],
    description TEXT,
    photos TEXT[],
    source VARCHAR(50) NOT NULL, -- 'airbnb', 'booking', 'vrbo'
    source_url TEXT,
    source_id VARCHAR(255),
    price_per_night DECIMAL(10, 2),
    price_currency VARCHAR(3) DEFAULT 'USD',
    availability_rate DECIMAL(5, 2), -- процент занятости
    avg_rating DECIMAL(3, 2),
    review_count INTEGER,
    host_name VARCHAR(255),
    host_rating DECIMAL(3, 2),
    host_review_count INTEGER,
    instant_bookable BOOLEAN DEFAULT false,
    superhost BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Индексы для краткосрочной аренды
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_location ON short_term_rentals(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_city ON short_term_rentals(city);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_district ON short_term_rentals(district);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_property_type ON short_term_rentals(property_type);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_bedrooms ON short_term_rentals(bedrooms);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_price ON short_term_rentals(price_per_night);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_source ON short_term_rentals(source);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_source_id ON short_term_rentals(source, source_id);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_rating ON short_term_rentals(avg_rating);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_updated ON short_term_rentals(updated_at);
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_active ON short_term_rentals(is_active);

-- =====================================================
-- Создание таблиц для долгосрочной аренды
-- =====================================================

CREATE TABLE IF NOT EXISTS long_term_rentals (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(100),
    district VARCHAR(100),
    property_type VARCHAR(50),
    bedrooms INTEGER,
    bathrooms INTEGER,
    total_area DECIMAL(8, 2), -- в квадратных метрах
    floor_number INTEGER,
    total_floors INTEGER,
    year_built INTEGER,
    condition_rating VARCHAR(20), -- 'excellent', 'good', 'fair', 'poor'
    amenities TEXT[],
    description TEXT,
    photos TEXT[],
    source VARCHAR(50) NOT NULL, -- 'olx', 'domria', 'realty', 'custom'
    source_url TEXT,
    source_id VARCHAR(255),
    monthly_rent DECIMAL(10, 2),
    rent_currency VARCHAR(3) DEFAULT 'USD',
    deposit_required BOOLEAN DEFAULT false,
    deposit_amount DECIMAL(10, 2),
    utilities_included BOOLEAN DEFAULT false,
    pets_allowed BOOLEAN DEFAULT false,
    furnished BOOLEAN DEFAULT false,
    available_from DATE,
    contact_name VARCHAR(255),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Индексы для долгосрочной аренды
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_location ON long_term_rentals(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_city ON long_term_rentals(city);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_district ON long_term_rentals(district);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_property_type ON long_term_rentals(property_type);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_bedrooms ON long_term_rentals(bedrooms);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_rent ON long_term_rentals(monthly_rent);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_source ON long_term_rentals(source);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_source_id ON long_term_rentals(source, source_id);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_available_from ON long_term_rentals(available_from);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_updated ON long_term_rentals(updated_at);
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_active ON long_term_rentals(is_active);

-- =====================================================
-- Создание таблиц для продаж недвижимости
-- =====================================================

CREATE TABLE IF NOT EXISTS property_sales (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(100),
    district VARCHAR(100),
    property_type VARCHAR(50),
    bedrooms INTEGER,
    bathrooms INTEGER,
    total_area DECIMAL(8, 2), -- в квадратных метрах
    land_area DECIMAL(8, 2), -- площадь участка
    floor_number INTEGER,
    total_floors INTEGER,
    year_built INTEGER,
    condition_rating VARCHAR(20),
    amenities TEXT[],
    description TEXT,
    photos TEXT[],
    source VARCHAR(50) NOT NULL, -- 'olx', 'domria', 'realty', 'custom'
    source_url TEXT,
    source_id VARCHAR(255),
    asking_price DECIMAL(12, 2),
    price_currency VARCHAR(3) DEFAULT 'USD',
    price_per_sqm DECIMAL(10, 2),
    negotiable BOOLEAN DEFAULT true,
    contact_name VARCHAR(255),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- Индексы для продаж недвижимости
CREATE INDEX IF NOT EXISTS idx_property_sales_location ON property_sales(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_property_sales_city ON property_sales(city);
CREATE INDEX IF NOT EXISTS idx_property_sales_district ON property_sales(district);
CREATE INDEX IF NOT EXISTS idx_property_sales_property_type ON property_sales(property_type);
CREATE INDEX IF NOT EXISTS idx_property_sales_bedrooms ON property_sales(bedrooms);
CREATE INDEX IF NOT EXISTS idx_property_sales_price ON property_sales(asking_price);
CREATE INDEX IF NOT EXISTS idx_property_sales_price_per_sqm ON property_sales(price_per_sqm);
CREATE INDEX IF NOT EXISTS idx_property_sales_source ON property_sales(source);
CREATE INDEX IF NOT EXISTS idx_property_sales_source_id ON property_sales(source, source_id);
CREATE INDEX IF NOT EXISTS idx_property_sales_updated ON property_sales(updated_at);
CREATE INDEX IF NOT EXISTS idx_property_sales_active ON property_sales(is_active);

-- =====================================================
-- Создание таблиц для исторических данных
-- =====================================================

-- Исторические данные для краткосрочной аренды
CREATE TABLE IF NOT EXISTS short_term_rental_history (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    price_per_night DECIMAL(10, 2),
    availability_rate DECIMAL(5, 2),
    avg_rating DECIMAL(3, 2),
    review_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (property_id) REFERENCES short_term_rentals(property_id) ON DELETE CASCADE
);

-- Исторические данные для долгосрочной аренды
CREATE TABLE IF NOT EXISTS long_term_rental_history (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    monthly_rent DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (property_id) REFERENCES long_term_rentals(property_id) ON DELETE CASCADE
);

-- Исторические данные для продаж
CREATE TABLE IF NOT EXISTS property_sales_history (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    asking_price DECIMAL(12, 2),
    price_per_sqm DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (property_id) REFERENCES property_sales(property_id) ON DELETE CASCADE
);

-- Индексы для исторических данных
CREATE INDEX IF NOT EXISTS idx_short_term_rental_history_property_date ON short_term_rental_history(property_id, date);
CREATE INDEX IF NOT EXISTS idx_long_term_rental_history_property_date ON long_term_rental_history(property_id, date);
CREATE INDEX IF NOT EXISTS idx_property_sales_history_property_date ON property_sales_history(property_id, date);

-- =====================================================
-- Создание таблиц для метрик и аналитики
-- =====================================================

-- Ежедневные метрики по районам
CREATE TABLE IF NOT EXISTS daily_district_metrics (
    id SERIAL PRIMARY KEY,
    district VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    property_type VARCHAR(50) NOT NULL, -- 'short_term', 'long_term', 'sale'
    
    -- Метрики краткосрочной аренды
    avg_short_term_price DECIMAL(10, 2),
    median_short_term_price DECIMAL(10, 2),
    short_term_listings_count INTEGER,
    avg_short_term_rating DECIMAL(3, 2),
    avg_short_term_availability DECIMAL(5, 2),
    
    -- Метрики долгосрочной аренды
    avg_long_term_rent DECIMAL(10, 2),
    median_long_term_rent DECIMAL(10, 2),
    long_term_listings_count INTEGER,
    
    -- Метрики продаж
    avg_sale_price DECIMAL(12, 2),
    median_sale_price DECIMAL(12, 2),
    sale_listings_count INTEGER,
    avg_price_per_sqm DECIMAL(10, 2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(district, city, date, property_type)
);

-- Индексы для метрик
CREATE INDEX IF NOT EXISTS idx_daily_district_metrics_location ON daily_district_metrics(district, city);
CREATE INDEX IF NOT EXISTS idx_daily_district_metrics_date ON daily_district_metrics(date);
CREATE INDEX IF NOT EXISTS idx_daily_district_metrics_type ON daily_district_metrics(property_type);

-- =====================================================
-- Создание таблиц для пользователей и отчетов
-- =====================================================

-- Пользователи системы
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Отчеты пользователей
CREATE TABLE IF NOT EXISTS user_reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    report_type VARCHAR(50) NOT NULL, -- 'market_analysis', 'roi_analysis', 'comparison'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    parameters JSONB, -- параметры отчета
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    bedrooms INTEGER,
    price_range_min DECIMAL(12, 2),
    price_range_max DECIMAL(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Индексы для пользователей и отчетов
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_type ON user_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_user_reports_created ON user_reports(created_at);

-- =====================================================
-- Создание представлений для удобного доступа к данным
-- =====================================================

-- Представление для активных объявлений краткосрочной аренды
CREATE OR REPLACE VIEW active_short_term_rentals AS
SELECT 
    id, property_id, address, latitude, longitude, city, district,
    property_type, bedrooms, bathrooms, max_guests, amenities,
    price_per_night, price_currency, availability_rate, avg_rating,
    review_count, host_name, host_rating, instant_bookable, superhost,
    source, source_url, updated_at
FROM short_term_rentals 
WHERE is_active = true;

-- Представление для активных объявлений долгосрочной аренды
CREATE OR REPLACE VIEW active_long_term_rentals AS
SELECT 
    id, property_id, address, latitude, longitude, city, district,
    property_type, bedrooms, bathrooms, total_area, floor_number,
    total_floors, year_built, condition_rating, amenities,
    monthly_rent, rent_currency, deposit_amount, utilities_included,
    pets_allowed, furnished, available_from, contact_name,
    source, source_url, updated_at
FROM long_term_rentals 
WHERE is_active = true;

-- Представление для активных объявлений продаж
CREATE OR REPLACE VIEW active_property_sales AS
SELECT 
    id, property_id, address, latitude, longitude, city, district,
    property_type, bedrooms, bathrooms, total_area, land_area,
    floor_number, total_floors, year_built, condition_rating, amenities,
    asking_price, price_currency, price_per_sqm, negotiable,
    contact_name, source, source_url, updated_at
FROM property_sales 
WHERE is_active = true;

-- =====================================================
-- Создание функций для автоматического обновления updated_at
-- =====================================================

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггеры для автоматического обновления updated_at
DROP TRIGGER IF EXISTS update_short_term_rentals_updated_at ON short_term_rentals;
CREATE TRIGGER update_short_term_rentals_updated_at 
    BEFORE UPDATE ON short_term_rentals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_long_term_rentals_updated_at ON long_term_rentals;
CREATE TRIGGER update_long_term_rentals_updated_at 
    BEFORE UPDATE ON long_term_rentals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_property_sales_updated_at ON property_sales;
CREATE TRIGGER update_property_sales_updated_at 
    BEFORE UPDATE ON property_sales 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_reports_updated_at ON user_reports;
CREATE TRIGGER update_user_reports_updated_at 
    BEFORE UPDATE ON user_reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Создание индексов для полнотекстового поиска
-- =====================================================

-- Индексы для поиска по адресу
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_address_gin ON short_term_rentals USING gin(to_tsvector('english', address));
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_address_gin ON long_term_rentals USING gin(to_tsvector('english', address));
CREATE INDEX IF NOT EXISTS idx_property_sales_address_gin ON property_sales USING gin(to_tsvector('english', address));

-- Индексы для поиска по описанию
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_description_gin ON short_term_rentals USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_description_gin ON long_term_rentals USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_property_sales_description_gin ON property_sales USING gin(to_tsvector('english', description));

-- =====================================================
-- Комментарии к таблицам
-- =====================================================

COMMENT ON TABLE short_term_rentals IS 'Объявления краткосрочной аренды (Airbnb, Booking.com)';
COMMENT ON TABLE long_term_rentals IS 'Объявления долгосрочной аренды';
COMMENT ON TABLE property_sales IS 'Объявления продажи недвижимости';
COMMENT ON TABLE short_term_rental_history IS 'Исторические данные краткосрочной аренды';
COMMENT ON TABLE long_term_rental_history IS 'Исторические данные долгосрочной аренды';
COMMENT ON TABLE property_sales_history IS 'Исторические данные продаж недвижимости';
COMMENT ON TABLE daily_district_metrics IS 'Ежедневные метрики по районам';
COMMENT ON TABLE users IS 'Пользователи системы';
COMMENT ON TABLE user_reports IS 'Отчеты пользователей';

-- =====================================================
-- Создание ролей и прав доступа (опционально)
-- =====================================================

-- Создание роли для чтения данных
-- CREATE ROLE readonly_user;
-- GRANT CONNECT ON DATABASE your_database TO readonly_user;
-- GRANT USAGE ON SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly_user;

-- Создание роли для записи данных
-- CREATE ROLE write_user;
-- GRANT CONNECT ON DATABASE your_database TO write_user;
-- GRANT USAGE ON SCHEMA public TO write_user;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO write_user;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO write_user; 
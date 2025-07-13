-- =====================================================
-- Полезные функции для работы с данными недвижимости
-- =====================================================

-- Функция для расчета ROI краткосрочной аренды
CREATE OR REPLACE FUNCTION calculate_short_term_roi(
    purchase_price DECIMAL(12, 2),
    monthly_expenses DECIMAL(10, 2),
    avg_nightly_rate DECIMAL(10, 2),
    occupancy_rate DECIMAL(5, 2)
)
RETURNS DECIMAL(8, 2) AS $$
DECLARE
    annual_revenue DECIMAL(12, 2);
    annual_expenses DECIMAL(12, 2);
    annual_profit DECIMAL(12, 2);
    roi DECIMAL(8, 2);
BEGIN
    -- Годовой доход = средняя цена за ночь * количество ночей * процент занятости
    annual_revenue := avg_nightly_rate * 365 * (occupancy_rate / 100);
    
    -- Годовые расходы
    annual_expenses := monthly_expenses * 12;
    
    -- Годовая прибыль
    annual_profit := annual_revenue - annual_expenses;
    
    -- ROI = (годовая прибыль / цена покупки) * 100
    roi := (annual_profit / purchase_price) * 100;
    
    RETURN roi;
END;
$$ LANGUAGE plpgsql;

-- Функция для расчета ROI долгосрочной аренды
CREATE OR REPLACE FUNCTION calculate_long_term_roi(
    purchase_price DECIMAL(12, 2),
    monthly_expenses DECIMAL(10, 2),
    monthly_rent DECIMAL(10, 2)
)
RETURNS DECIMAL(8, 2) AS $$
DECLARE
    annual_revenue DECIMAL(12, 2);
    annual_expenses DECIMAL(12, 2);
    annual_profit DECIMAL(12, 2);
    roi DECIMAL(8, 2);
BEGIN
    -- Годовой доход
    annual_revenue := monthly_rent * 12;
    
    -- Годовые расходы
    annual_expenses := monthly_expenses * 12;
    
    -- Годовая прибыль
    annual_profit := annual_revenue - annual_expenses;
    
    -- ROI = (годовая прибыль / цена покупки) * 100
    roi := (annual_profit / purchase_price) * 100;
    
    RETURN roi;
END;
$$ LANGUAGE plpgsql;

-- Функция для поиска недвижимости по радиусу
CREATE OR REPLACE FUNCTION find_properties_in_radius(
    center_lat DECIMAL(10, 8),
    center_lng DECIMAL(11, 8),
    radius_km DECIMAL(8, 2),
    property_type_param VARCHAR(50) DEFAULT NULL
)
RETURNS TABLE(
    property_id VARCHAR(255),
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    distance_km DECIMAL(8, 2),
    property_type VARCHAR(50),
    bedrooms INTEGER,
    price DECIMAL(12, 2),
    source VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        str.property_id,
        str.address,
        str.latitude,
        str.longitude,
        (6371 * acos(cos(radians(center_lat)) * cos(radians(str.latitude)) * 
         cos(radians(str.longitude) - radians(center_lng)) + 
         sin(radians(center_lat)) * sin(radians(str.latitude)))) AS distance_km,
        'short_term'::VARCHAR(50) AS property_type,
        str.bedrooms,
        str.price_per_night AS price,
        str.source
    FROM short_term_rentals str
    WHERE str.is_active = true
        AND (property_type_param IS NULL OR property_type_param = 'short_term')
        AND (6371 * acos(cos(radians(center_lat)) * cos(radians(str.latitude)) * 
             cos(radians(str.longitude) - radians(center_lng)) + 
             sin(radians(center_lat)) * sin(radians(str.latitude)))) <= radius_km
    
    UNION ALL
    
    SELECT 
        ltr.property_id,
        ltr.address,
        ltr.latitude,
        ltr.longitude,
        (6371 * acos(cos(radians(center_lat)) * cos(radians(ltr.latitude)) * 
         cos(radians(ltr.longitude) - radians(center_lng)) + 
         sin(radians(center_lat)) * sin(radians(ltr.latitude)))) AS distance_km,
        'long_term'::VARCHAR(50) AS property_type,
        ltr.bedrooms,
        ltr.monthly_rent AS price,
        ltr.source
    FROM long_term_rentals ltr
    WHERE ltr.is_active = true
        AND (property_type_param IS NULL OR property_type_param = 'long_term')
        AND (6371 * acos(cos(radians(center_lat)) * cos(radians(ltr.latitude)) * 
             cos(radians(ltr.longitude) - radians(center_lng)) + 
             sin(radians(center_lat)) * sin(radians(ltr.latitude)))) <= radius_km
    
    UNION ALL
    
    SELECT 
        ps.property_id,
        ps.address,
        ps.latitude,
        ps.longitude,
        (6371 * acos(cos(radians(center_lat)) * cos(radians(ps.latitude)) * 
         cos(radians(ps.longitude) - radians(center_lng)) + 
         sin(radians(center_lat)) * sin(radians(ps.latitude)))) AS distance_km,
        'sale'::VARCHAR(50) AS property_type,
        ps.bedrooms,
        ps.asking_price AS price,
        ps.source
    FROM property_sales ps
    WHERE ps.is_active = true
        AND (property_type_param IS NULL OR property_type_param = 'sale')
        AND (6371 * acos(cos(radians(center_lat)) * cos(radians(ps.latitude)) * 
             cos(radians(ps.longitude) - radians(center_lng)) + 
             sin(radians(center_lat)) * sin(radians(ps.latitude)))) <= radius_km
    
    ORDER BY distance_km;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения статистики по району
CREATE OR REPLACE FUNCTION get_district_statistics(
    district_param VARCHAR(100),
    city_param VARCHAR(100)
)
RETURNS TABLE(
    property_type VARCHAR(50),
    avg_price DECIMAL(12, 2),
    median_price DECIMAL(12, 2),
    min_price DECIMAL(12, 2),
    max_price DECIMAL(12, 2),
    listings_count INTEGER,
    avg_rating DECIMAL(3, 2),
    avg_bedrooms DECIMAL(4, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'short_term'::VARCHAR(50) AS property_type,
        AVG(str.price_per_night) AS avg_price,
        percentile_cont(0.5) WITHIN GROUP (ORDER BY str.price_per_night) AS median_price,
        MIN(str.price_per_night) AS min_price,
        MAX(str.price_per_night) AS max_price,
        COUNT(*)::INTEGER AS listings_count,
        AVG(str.avg_rating) AS avg_rating,
        AVG(str.bedrooms) AS avg_bedrooms
    FROM short_term_rentals str
    WHERE str.district = district_param 
        AND str.city = city_param 
        AND str.is_active = true
    
    UNION ALL
    
    SELECT 
        'long_term'::VARCHAR(50) AS property_type,
        AVG(ltr.monthly_rent) AS avg_price,
        percentile_cont(0.5) WITHIN GROUP (ORDER BY ltr.monthly_rent) AS median_price,
        MIN(ltr.monthly_rent) AS min_price,
        MAX(ltr.monthly_rent) AS max_price,
        COUNT(*)::INTEGER AS listings_count,
        NULL::DECIMAL(3, 2) AS avg_rating,
        AVG(ltr.bedrooms) AS avg_bedrooms
    FROM long_term_rentals ltr
    WHERE ltr.district = district_param 
        AND ltr.city = city_param 
        AND ltr.is_active = true
    
    UNION ALL
    
    SELECT 
        'sale'::VARCHAR(50) AS property_type,
        AVG(ps.asking_price) AS avg_price,
        percentile_cont(0.5) WITHIN GROUP (ORDER BY ps.asking_price) AS median_price,
        MIN(ps.asking_price) AS min_price,
        MAX(ps.asking_price) AS max_price,
        COUNT(*)::INTEGER AS listings_count,
        NULL::DECIMAL(3, 2) AS avg_rating,
        AVG(ps.bedrooms) AS avg_bedrooms
    FROM property_sales ps
    WHERE ps.district = district_param 
        AND ps.city = city_param 
        AND ps.is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения исторических данных по цене
CREATE OR REPLACE FUNCTION get_price_history(
    property_id_param VARCHAR(255),
    days_back INTEGER DEFAULT 30
)
RETURNS TABLE(
    date DATE,
    price DECIMAL(12, 2),
    property_type VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        strh.date,
        strh.price_per_night AS price,
        'short_term'::VARCHAR(50) AS property_type
    FROM short_term_rental_history strh
    WHERE strh.property_id = property_id_param
        AND strh.date >= CURRENT_DATE - INTERVAL '1 day' * days_back
    
    UNION ALL
    
    SELECT 
        ltrh.date,
        ltrh.monthly_rent AS price,
        'long_term'::VARCHAR(50) AS property_type
    FROM long_term_rental_history ltrh
    WHERE ltrh.property_id = property_id_param
        AND ltrh.date >= CURRENT_DATE - INTERVAL '1 day' * days_back
    
    UNION ALL
    
    SELECT 
        psh.date,
        psh.asking_price AS price,
        'sale'::VARCHAR(50) AS property_type
    FROM property_sales_history psh
    WHERE psh.property_id = property_id_param
        AND psh.date >= CURRENT_DATE - INTERVAL '1 day' * days_back
    
    ORDER BY date;
END;
$$ LANGUAGE plpgsql;

-- Процедура для обновления ежедневных метрик
CREATE OR REPLACE PROCEDURE update_daily_metrics(
    target_date DATE DEFAULT CURRENT_DATE
)
LANGUAGE plpgsql
AS $$
DECLARE
    district_record RECORD;
BEGIN
    -- Удаляем существующие метрики за указанную дату
    DELETE FROM daily_district_metrics 
    WHERE date = target_date;
    
    -- Вставляем новые метрики для каждого района
    FOR district_record IN 
        SELECT DISTINCT district, city 
        FROM (
            SELECT district, city FROM short_term_rentals WHERE is_active = true
            UNION
            SELECT district, city FROM long_term_rentals WHERE is_active = true
            UNION
            SELECT district, city FROM property_sales WHERE is_active = true
        ) AS all_districts
        WHERE district IS NOT NULL AND city IS NOT NULL
    LOOP
        -- Метрики краткосрочной аренды
        INSERT INTO daily_district_metrics (
            district, city, date, property_type,
            avg_short_term_price, median_short_term_price, short_term_listings_count,
            avg_short_term_rating, avg_short_term_availability
        )
        SELECT 
            district_record.district,
            district_record.city,
            target_date,
            'short_term',
            AVG(price_per_night),
            percentile_cont(0.5) WITHIN GROUP (ORDER BY price_per_night),
            COUNT(*),
            AVG(avg_rating),
            AVG(availability_rate)
        FROM short_term_rentals
        WHERE district = district_record.district 
            AND city = district_record.city 
            AND is_active = true;
        
        -- Метрики долгосрочной аренды
        INSERT INTO daily_district_metrics (
            district, city, date, property_type,
            avg_long_term_rent, median_long_term_rent, long_term_listings_count
        )
        SELECT 
            district_record.district,
            district_record.city,
            target_date,
            'long_term',
            AVG(monthly_rent),
            percentile_cont(0.5) WITHIN GROUP (ORDER BY monthly_rent),
            COUNT(*)
        FROM long_term_rentals
        WHERE district = district_record.district 
            AND city = district_record.city 
            AND is_active = true;
        
        -- Метрики продаж
        INSERT INTO daily_district_metrics (
            district, city, date, property_type,
            avg_sale_price, median_sale_price, sale_listings_count, avg_price_per_sqm
        )
        SELECT 
            district_record.district,
            district_record.city,
            target_date,
            'sale',
            AVG(asking_price),
            percentile_cont(0.5) WITHIN GROUP (ORDER BY asking_price),
            COUNT(*),
            AVG(price_per_sqm)
        FROM property_sales
        WHERE district = district_record.district 
            AND city = district_record.city 
            AND is_active = true;
    END LOOP;
END;
$$;

-- Функция для поиска похожих объектов
CREATE OR REPLACE FUNCTION find_similar_properties(
    target_bedrooms INTEGER,
    target_price_min DECIMAL(12, 2),
    target_price_max DECIMAL(12, 2),
    target_city VARCHAR(100),
    target_district VARCHAR(100) DEFAULT NULL,
    property_type_param VARCHAR(50) DEFAULT 'short_term'
)
RETURNS TABLE(
    property_id VARCHAR(255),
    address TEXT,
    bedrooms INTEGER,
    price DECIMAL(12, 2),
    similarity_score DECIMAL(5, 2),
    source VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        str.property_id,
        str.address,
        str.bedrooms,
        str.price_per_night AS price,
        CASE 
            WHEN str.district = target_district THEN 100
            WHEN str.city = target_city THEN 80
            ELSE 60
        END AS similarity_score,
        str.source
    FROM short_term_rentals str
    WHERE str.is_active = true
        AND str.bedrooms = target_bedrooms
        AND str.price_per_night BETWEEN target_price_min AND target_price_max
        AND str.city = target_city
        AND (property_type_param = 'short_term' OR property_type_param IS NULL)
    
    UNION ALL
    
    SELECT 
        ltr.property_id,
        ltr.address,
        ltr.bedrooms,
        ltr.monthly_rent AS price,
        CASE 
            WHEN ltr.district = target_district THEN 100
            WHEN ltr.city = target_city THEN 80
            ELSE 60
        END AS similarity_score,
        ltr.source
    FROM long_term_rentals ltr
    WHERE ltr.is_active = true
        AND ltr.bedrooms = target_bedrooms
        AND ltr.monthly_rent BETWEEN target_price_min AND target_price_max
        AND ltr.city = target_city
        AND (property_type_param = 'long_term' OR property_type_param IS NULL)
    
    UNION ALL
    
    SELECT 
        ps.property_id,
        ps.address,
        ps.bedrooms,
        ps.asking_price AS price,
        CASE 
            WHEN ps.district = target_district THEN 100
            WHEN ps.city = target_city THEN 80
            ELSE 60
        END AS similarity_score,
        ps.source
    FROM property_sales ps
    WHERE ps.is_active = true
        AND ps.bedrooms = target_bedrooms
        AND ps.asking_price BETWEEN target_price_min AND target_price_max
        AND ps.city = target_city
        AND (property_type_param = 'sale' OR property_type_param IS NULL)
    
    ORDER BY similarity_score DESC, price;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Создание индексов для функций
-- =====================================================

-- Индексы для геопространственных запросов
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_geo ON short_term_rentals USING gist (
    ll_to_earth(latitude, longitude)
);

CREATE INDEX IF NOT EXISTS idx_long_term_rentals_geo ON long_term_rentals USING gist (
    ll_to_earth(latitude, longitude)
);

CREATE INDEX IF NOT EXISTS idx_property_sales_geo ON property_sales USING gist (
    ll_to_earth(latitude, longitude)
);

-- Индексы для составных запросов
CREATE INDEX IF NOT EXISTS idx_short_term_rentals_composite ON short_term_rentals(city, district, bedrooms, price_per_night) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_long_term_rentals_composite ON long_term_rentals(city, district, bedrooms, monthly_rent) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_property_sales_composite ON property_sales(city, district, bedrooms, asking_price) WHERE is_active = true;

-- =====================================================
-- Комментарии к функциям
-- =====================================================

COMMENT ON FUNCTION calculate_short_term_roi IS 'Рассчитывает ROI для краткосрочной аренды';
COMMENT ON FUNCTION calculate_long_term_roi IS 'Рассчитывает ROI для долгосрочной аренды';
COMMENT ON FUNCTION find_properties_in_radius IS 'Находит недвижимость в заданном радиусе от точки';
COMMENT ON FUNCTION get_district_statistics IS 'Получает статистику по району';
COMMENT ON FUNCTION get_price_history IS 'Получает историю цен для объекта';
COMMENT ON PROCEDURE update_daily_metrics IS 'Обновляет ежедневные метрики';
COMMENT ON FUNCTION find_similar_properties IS 'Находит похожие объекты недвижимости'; 
-- SQL скрипт для создания таблицы imf_economic_data
-- Создает полную структуру таблицы с поддержкой интерпретаций и кэширования

-- Удаляем таблицу если она существует (для пересоздания)
DROP TABLE IF EXISTS imf_economic_data;

-- Создаем таблицу imf_economic_data
CREATE TABLE imf_economic_data (
    -- Основные поля
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    country_name VARCHAR(255) NOT NULL,
    indicator_code VARCHAR(50) NOT NULL,
    indicator_name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    value DECIMAL(10,4) NOT NULL,
    
    -- Поля для интерпретаций ВВП (GDP)
    gdp_trend_interpretation_en TEXT,
    gdp_trend_interpretation_ru TEXT,
    gdp_trend_interpretation_tr TEXT,
    gdp_trend_interpretation_fr TEXT,
    gdp_trend_interpretation_de TEXT,
    
    -- Поля для интерпретаций инфляции (Inflation)
    inflation_trend_interpretation_en TEXT,
    inflation_trend_interpretation_ru TEXT,
    inflation_trend_interpretation_tr TEXT,
    inflation_trend_interpretation_fr TEXT,
    inflation_trend_interpretation_de TEXT,
    
    -- Поля для интерпретаций сравнения (Recent Comparison)
    recent_comparison_interpretation_en TEXT,
    recent_comparison_interpretation_ru TEXT,
    recent_comparison_interpretation_tr TEXT,
    recent_comparison_interpretation_fr TEXT,
    recent_comparison_interpretation_de TEXT,
    
    -- Поля для детальных расчетов
    gdp_calculation_details TEXT, -- JSON строка с детальными расчетами ВВП
    inflation_calculation_details TEXT, -- JSON строка с детальными расчетами инфляции
    
    -- Временные метки
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаем индексы для оптимизации запросов
CREATE INDEX idx_imf_economic_data_country_code ON imf_economic_data(country_code);
CREATE INDEX idx_imf_economic_data_indicator_code ON imf_economic_data(indicator_code);
CREATE INDEX idx_imf_economic_data_year ON imf_economic_data(year);
CREATE INDEX idx_imf_economic_data_country_indicator ON imf_economic_data(country_code, indicator_code);
CREATE INDEX idx_imf_economic_data_country_year ON imf_economic_data(country_code, year);

-- Создаем уникальный индекс для предотвращения дублирования данных
CREATE UNIQUE INDEX idx_imf_economic_data_unique 
ON imf_economic_data(country_code, indicator_code, year);

-- Создаем функцию для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создаем триггер для автоматического обновления updated_at
CREATE TRIGGER update_imf_economic_data_updated_at 
    BEFORE UPDATE ON imf_economic_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Добавляем комментарии к таблице и полям
COMMENT ON TABLE imf_economic_data IS 'Таблица для хранения экономических данных IMF с поддержкой интерпретаций и кэширования';
COMMENT ON COLUMN imf_economic_data.country_code IS 'Код страны (например, TUR для Турции)';
COMMENT ON COLUMN imf_economic_data.country_name IS 'Название страны';
COMMENT ON COLUMN imf_economic_data.indicator_code IS 'Код индикатора (NGDP_RPCH для ВВП, PCPIPCH для инфляции)';
COMMENT ON COLUMN imf_economic_data.indicator_name IS 'Название индикатора';
COMMENT ON COLUMN imf_economic_data.year IS 'Год данных';
COMMENT ON COLUMN imf_economic_data.value IS 'Значение индикатора';
COMMENT ON COLUMN imf_economic_data.gdp_trend_interpretation_en IS 'Интерпретация тренда ВВП на английском языке';
COMMENT ON COLUMN imf_economic_data.gdp_trend_interpretation_ru IS 'Интерпретация тренда ВВП на русском языке';
COMMENT ON COLUMN imf_economic_data.gdp_trend_interpretation_tr IS 'Интерпретация тренда ВВП на турецком языке';
COMMENT ON COLUMN imf_economic_data.gdp_trend_interpretation_fr IS 'Интерпретация тренда ВВП на французском языке';
COMMENT ON COLUMN imf_economic_data.gdp_trend_interpretation_de IS 'Интерпретация тренда ВВП на немецком языке';
COMMENT ON COLUMN imf_economic_data.inflation_trend_interpretation_en IS 'Интерпретация тренда инфляции на английском языке';
COMMENT ON COLUMN imf_economic_data.inflation_trend_interpretation_ru IS 'Интерпретация тренда инфляции на русском языке';
COMMENT ON COLUMN imf_economic_data.inflation_trend_interpretation_tr IS 'Интерпретация тренда инфляции на турецком языке';
COMMENT ON COLUMN imf_economic_data.inflation_trend_interpretation_fr IS 'Интерпретация тренда инфляции на французском языке';
COMMENT ON COLUMN imf_economic_data.inflation_trend_interpretation_de IS 'Интерпретация тренда инфляции на немецком языке';
COMMENT ON COLUMN imf_economic_data.recent_comparison_interpretation_en IS 'Интерпретация сравнения последних лет на английском языке';
COMMENT ON COLUMN imf_economic_data.recent_comparison_interpretation_ru IS 'Интерпретация сравнения последних лет на русском языке';
COMMENT ON COLUMN imf_economic_data.recent_comparison_interpretation_tr IS 'Интерпретация сравнения последних лет на турецком языке';
COMMENT ON COLUMN imf_economic_data.recent_comparison_interpretation_fr IS 'Интерпретация сравнения последних лет на французском языке';
COMMENT ON COLUMN imf_economic_data.recent_comparison_interpretation_de IS 'Интерпретация сравнения последних лет на немецком языке';
COMMENT ON COLUMN imf_economic_data.gdp_calculation_details IS 'JSON строка с детальными расчетами ВВП';
COMMENT ON COLUMN imf_economic_data.inflation_calculation_details IS 'JSON строка с детальными расчетами инфляции';

-- Создаем представление для удобного просмотра данных
CREATE OR REPLACE VIEW v_imf_economic_data_summary AS
SELECT 
    country_code,
    country_name,
    indicator_code,
    indicator_name,
    year,
    value,
    CASE 
        WHEN indicator_code = 'NGDP_RPCH' THEN gdp_trend_interpretation_ru
        WHEN indicator_code = 'PCPIPCH' THEN inflation_trend_interpretation_ru
        ELSE NULL
    END as interpretation_ru,
    created_at,
    updated_at
FROM imf_economic_data
ORDER BY country_code, indicator_code, year DESC;

-- Добавляем пример данных для тестирования
INSERT INTO imf_economic_data (country_code, country_name, indicator_code, indicator_name, year, value) VALUES
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'GDP growth (annual %)', 2025, 2.7),
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'GDP growth (annual %)', 2024, 3.2),
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'GDP growth (annual %)', 2023, 5.1),
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'GDP growth (annual %)', 2022, 5.5),
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'GDP growth (annual %)', 2021, 11.4),
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'GDP growth (annual %)', 2020, 1.9),
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'GDP growth (annual %)', 2019, 0.8),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation (annual %)', 2025, 35.9),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation (annual %)', 2024, 58.5),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation (annual %)', 2023, 53.9),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation (annual %)', 2022, 72.3),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation (annual %)', 2021, 19.6),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation (annual %)', 2020, 12.3),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation (annual %)', 2019, 15.2);

-- Выводим информацию о созданной таблице
SELECT 
    'Table created successfully!' as status,
    COUNT(*) as total_records,
    COUNT(DISTINCT country_code) as countries,
    COUNT(DISTINCT indicator_code) as indicators,
    MIN(year) as min_year,
    MAX(year) as max_year
FROM imf_economic_data; 
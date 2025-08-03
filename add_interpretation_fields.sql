-- SQL скрипт для добавления полей интерпретаций к существующей таблице imf_economic_data
-- Используйте этот скрипт, если таблица уже существует и нужно добавить новые поля

-- Добавляем поля для интерпретаций ВВП (GDP)
ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS gdp_trend_interpretation_en TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS gdp_trend_interpretation_ru TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS gdp_trend_interpretation_tr TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS gdp_trend_interpretation_fr TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS gdp_trend_interpretation_de TEXT;

-- Добавляем поля для интерпретаций инфляции (Inflation)
ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS inflation_trend_interpretation_en TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS inflation_trend_interpretation_ru TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS inflation_trend_interpretation_tr TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS inflation_trend_interpretation_fr TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS inflation_trend_interpretation_de TEXT;

-- Добавляем поля для интерпретаций сравнения (Recent Comparison)
ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS recent_comparison_interpretation_en TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS recent_comparison_interpretation_ru TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS recent_comparison_interpretation_tr TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS recent_comparison_interpretation_fr TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS recent_comparison_interpretation_de TEXT;

-- Добавляем поля для детальных расчетов
ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS gdp_calculation_details TEXT;

ALTER TABLE imf_economic_data 
ADD COLUMN IF NOT EXISTS inflation_calculation_details TEXT;

-- Добавляем комментарии к новым полям
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

-- Проверяем структуру таблицы после добавления полей
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'imf_economic_data' 
ORDER BY ordinal_position;

-- Выводим статистику по добавленным полям
SELECT 
    'Fields added successfully!' as status,
    COUNT(*) as total_columns,
    COUNT(CASE WHEN column_name LIKE '%interpretation%' THEN 1 END) as interpretation_fields,
    COUNT(CASE WHEN column_name LIKE '%calculation%' THEN 1 END) as calculation_fields
FROM information_schema.columns 
WHERE table_name = 'imf_economic_data'; 
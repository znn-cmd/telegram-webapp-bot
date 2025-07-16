-- Исправляем таблицу user_reports

-- 1. Проверяем, существует ли таблица
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_reports') THEN
        -- Создаем таблицу с нуля
        CREATE TABLE user_reports (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            report_type VARCHAR(50) NOT NULL,
            title VARCHAR(255),
            description TEXT,
            parameters JSONB,
            address VARCHAR(500),
            latitude NUMERIC,
            longitude NUMERIC,
            bedrooms INTEGER,
            price_range_min NUMERIC,
            price_range_max NUMERIC,
            full_report JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Создаем индексы
        CREATE INDEX idx_user_reports_user_id ON user_reports(user_id);
        CREATE INDEX idx_user_reports_created_at ON user_reports(created_at);
        CREATE INDEX idx_user_reports_report_type ON user_reports(report_type);
        
        RAISE NOTICE 'Таблица user_reports создана';
    ELSE
        -- Таблица существует, добавляем недостающие колонки
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'user_id') THEN
            ALTER TABLE user_reports ADD COLUMN user_id INTEGER;
            RAISE NOTICE 'Колонка user_id добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'report_type') THEN
            ALTER TABLE user_reports ADD COLUMN report_type VARCHAR(50);
            RAISE NOTICE 'Колонка report_type добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'title') THEN
            ALTER TABLE user_reports ADD COLUMN title VARCHAR(255);
            RAISE NOTICE 'Колонка title добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'description') THEN
            ALTER TABLE user_reports ADD COLUMN description TEXT;
            RAISE NOTICE 'Колонка description добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'parameters') THEN
            ALTER TABLE user_reports ADD COLUMN parameters JSONB;
            RAISE NOTICE 'Колонка parameters добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'address') THEN
            ALTER TABLE user_reports ADD COLUMN address VARCHAR(500);
            RAISE NOTICE 'Колонка address добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'latitude') THEN
            ALTER TABLE user_reports ADD COLUMN latitude NUMERIC;
            RAISE NOTICE 'Колонка latitude добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'longitude') THEN
            ALTER TABLE user_reports ADD COLUMN longitude NUMERIC;
            RAISE NOTICE 'Колонка longitude добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'bedrooms') THEN
            ALTER TABLE user_reports ADD COLUMN bedrooms INTEGER;
            RAISE NOTICE 'Колонка bedrooms добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'price_range_min') THEN
            ALTER TABLE user_reports ADD COLUMN price_range_min NUMERIC;
            RAISE NOTICE 'Колонка price_range_min добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'price_range_max') THEN
            ALTER TABLE user_reports ADD COLUMN price_range_max NUMERIC;
            RAISE NOTICE 'Колонка price_range_max добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'full_report') THEN
            ALTER TABLE user_reports ADD COLUMN full_report JSONB;
            RAISE NOTICE 'Колонка full_report добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'created_at') THEN
            ALTER TABLE user_reports ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
            RAISE NOTICE 'Колонка created_at добавлена';
        END IF;
        
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'updated_at') THEN
            ALTER TABLE user_reports ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
            RAISE NOTICE 'Колонка updated_at добавлена';
        END IF;
        
        -- Создаем индексы если их нет
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE tablename = 'user_reports' AND indexname = 'idx_user_reports_user_id') THEN
            CREATE INDEX idx_user_reports_user_id ON user_reports(user_id);
            RAISE NOTICE 'Индекс idx_user_reports_user_id создан';
        END IF;
        
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE tablename = 'user_reports' AND indexname = 'idx_user_reports_created_at') THEN
            CREATE INDEX idx_user_reports_created_at ON user_reports(created_at);
            RAISE NOTICE 'Индекс idx_user_reports_created_at создан';
        END IF;
        
        IF NOT EXISTS (SELECT FROM pg_indexes WHERE tablename = 'user_reports' AND indexname = 'idx_user_reports_report_type') THEN
            CREATE INDEX idx_user_reports_report_type ON user_reports(report_type);
            RAISE NOTICE 'Индекс idx_user_reports_report_type создан';
        END IF;
        
        RAISE NOTICE 'Таблица user_reports обновлена';
    END IF;
END $$;

-- Показываем финальную структуру таблицы
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user_reports' 
ORDER BY ordinal_position; 
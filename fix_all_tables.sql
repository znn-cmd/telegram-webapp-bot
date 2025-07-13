-- Исправляем все необходимые таблицы

-- 1. Таблица user_reports
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_reports') THEN
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
        RAISE NOTICE 'Таблица user_reports создана';
    ELSE
        -- Добавляем недостающие колонки
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'user_id') THEN
            ALTER TABLE user_reports ADD COLUMN user_id INTEGER;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'report_type') THEN
            ALTER TABLE user_reports ADD COLUMN report_type VARCHAR(50);
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'title') THEN
            ALTER TABLE user_reports ADD COLUMN title VARCHAR(255);
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'description') THEN
            ALTER TABLE user_reports ADD COLUMN description TEXT;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'parameters') THEN
            ALTER TABLE user_reports ADD COLUMN parameters JSONB;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'address') THEN
            ALTER TABLE user_reports ADD COLUMN address VARCHAR(500);
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'latitude') THEN
            ALTER TABLE user_reports ADD COLUMN latitude NUMERIC;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'longitude') THEN
            ALTER TABLE user_reports ADD COLUMN longitude NUMERIC;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'bedrooms') THEN
            ALTER TABLE user_reports ADD COLUMN bedrooms INTEGER;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'price_range_min') THEN
            ALTER TABLE user_reports ADD COLUMN price_range_min NUMERIC;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'price_range_max') THEN
            ALTER TABLE user_reports ADD COLUMN price_range_max NUMERIC;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'full_report') THEN
            ALTER TABLE user_reports ADD COLUMN full_report JSONB;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'created_at') THEN
            ALTER TABLE user_reports ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'user_reports' AND column_name = 'updated_at') THEN
            ALTER TABLE user_reports ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
        END IF;
    END IF;
END $$;

-- 2. Таблица saved_objects
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'saved_objects') THEN
        CREATE TABLE saved_objects (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            object_data JSONB NOT NULL,
            saved_at TIMESTAMP DEFAULT NOW()
        );
        RAISE NOTICE 'Таблица saved_objects создана';
    ELSE
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'saved_objects' AND column_name = 'user_id') THEN
            ALTER TABLE saved_objects ADD COLUMN user_id INTEGER;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'saved_objects' AND column_name = 'object_data') THEN
            ALTER TABLE saved_objects ADD COLUMN object_data JSONB;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'saved_objects' AND column_name = 'saved_at') THEN
            ALTER TABLE saved_objects ADD COLUMN saved_at TIMESTAMP DEFAULT NOW();
        END IF;
    END IF;
END $$;

-- 3. Таблица client_contacts
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'client_contacts') THEN
        CREATE TABLE client_contacts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            realtor_telegram_id INTEGER,
            client_name VARCHAR(255) NOT NULL,
            client_telegram VARCHAR(100),
            client_username VARCHAR(100),
            report_address VARCHAR(500),
            last_report_pdf_url TEXT,
            sent_at TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW()
        );
        RAISE NOTICE 'Таблица client_contacts создана';
    ELSE
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'user_id') THEN
            ALTER TABLE client_contacts ADD COLUMN user_id INTEGER;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'realtor_telegram_id') THEN
            ALTER TABLE client_contacts ADD COLUMN realtor_telegram_id INTEGER;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'client_name') THEN
            ALTER TABLE client_contacts ADD COLUMN client_name VARCHAR(255);
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'client_telegram') THEN
            ALTER TABLE client_contacts ADD COLUMN client_telegram VARCHAR(100);
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'client_username') THEN
            ALTER TABLE client_contacts ADD COLUMN client_username VARCHAR(100);
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'report_address') THEN
            ALTER TABLE client_contacts ADD COLUMN report_address VARCHAR(500);
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'last_report_pdf_url') THEN
            ALTER TABLE client_contacts ADD COLUMN last_report_pdf_url TEXT;
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'sent_at') THEN
            ALTER TABLE client_contacts ADD COLUMN sent_at TIMESTAMP DEFAULT NOW();
        END IF;
        IF NOT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'client_contacts' AND column_name = 'created_at') THEN
            ALTER TABLE client_contacts ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
        END IF;
    END IF;
END $$;

-- Создаем индексы
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_created_at ON user_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_user_reports_report_type ON user_reports(report_type);

CREATE INDEX IF NOT EXISTS idx_saved_objects_user_id ON saved_objects(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_objects_saved_at ON saved_objects(saved_at);

CREATE INDEX IF NOT EXISTS idx_client_contacts_user_id ON client_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_client_contacts_realtor_id ON client_contacts(realtor_telegram_id);
CREATE INDEX IF NOT EXISTS idx_client_contacts_created_at ON client_contacts(created_at);

-- Показываем структуру всех таблиц
SELECT 'user_reports' as table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user_reports' 
ORDER BY ordinal_position;

SELECT 'saved_objects' as table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'saved_objects' 
ORDER BY ordinal_position;

SELECT 'client_contacts' as table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'client_contacts' 
ORDER BY ordinal_position; 
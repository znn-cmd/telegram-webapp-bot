-- Таблица: average_sqm_tracker
CREATE TABLE IF NOT EXISTS average_sqm_tracker (
    id SERIAL PRIMARY KEY,
    country VARCHAR(64),
    city VARCHAR(64),
    year INT,
    avg_price_per_sqm NUMERIC,
    property_type VARCHAR(32),
    source VARCHAR(128),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: purchase_price_tracker
CREATE TABLE IF NOT EXISTS purchase_price_tracker (
    id SERIAL PRIMARY KEY,
    country VARCHAR(64),
    city VARCHAR(64),
    year INT,
    avg_purchase_price NUMERIC,
    property_type VARCHAR(32),
    source VARCHAR(128),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: rent_price_tracker
CREATE TABLE IF NOT EXISTS rent_price_tracker (
    id SERIAL PRIMARY KEY,
    country VARCHAR(64),
    city VARCHAR(64),
    year INT,
    avg_rent_price NUMERIC,
    property_type VARCHAR(32),
    source VARCHAR(128),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: rental_yield_tracker
CREATE TABLE IF NOT EXISTS rental_yield_tracker (
    id SERIAL PRIMARY KEY,
    country VARCHAR(64),
    city VARCHAR(64),
    year INT,
    avg_rental_yield NUMERIC,
    property_type VARCHAR(32),
    source VARCHAR(128),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: rent_price_index
CREATE TABLE IF NOT EXISTS rent_price_index (
    id SERIAL PRIMARY KEY,
    country VARCHAR(64),
    city VARCHAR(64),
    year INT,
    rent_index NUMERIC,
    property_type VARCHAR(32),
    source VARCHAR(128),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: mortgage_rate_tracker
CREATE TABLE IF NOT EXISTS mortgage_rate_tracker (
    id SERIAL PRIMARY KEY,
    country VARCHAR(64),
    year INT,
    avg_mortgage_rate NUMERIC,
    source VARCHAR(128),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: global_house_price_index
CREATE TABLE IF NOT EXISTS global_house_price_index (
    id SERIAL PRIMARY KEY,
    country VARCHAR(64),
    year INT,
    house_price_index NUMERIC,
    source VARCHAR(128),
    updated_at TIMESTAMP DEFAULT NOW()
); 
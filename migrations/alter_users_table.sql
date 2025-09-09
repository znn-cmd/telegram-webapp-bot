-- Add new fields to users table
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS full_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS position VARCHAR(255),
    ADD COLUMN IF NOT EXISTS company_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS website_url VARCHAR(255),
    ADD COLUMN IF NOT EXISTS about_me TEXT,
    ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
    ADD COLUMN IF NOT EXISTS email VARCHAR(255),
    ADD COLUMN IF NOT EXISTS whatsapp_url VARCHAR(255),
    ADD COLUMN IF NOT EXISTS telegram_url VARCHAR(255),
    ADD COLUMN IF NOT EXISTS facebook_url VARCHAR(255),
    ADD COLUMN IF NOT EXISTS instagram_url VARCHAR(255),
    ADD COLUMN IF NOT EXISTS avatar_path VARCHAR(255);

-- Create directory for user avatars if it doesn't exist
-- Note: This needs to be executed in your application code, not in SQL
-- mkdir -p user/{telegram_id}

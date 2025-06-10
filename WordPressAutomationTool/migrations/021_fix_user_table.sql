
-- Fix user status field if missing
ALTER TABLE user ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';

-- Ensure login_attempts field exists
ALTER TABLE user ADD COLUMN IF NOT EXISTS login_attempts INTEGER DEFAULT 0;

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);

-- Fix any null password hashes (shouldn't happen but good to check)
UPDATE user SET password_hash = '' WHERE password_hash IS NULL;

-- Add security and tracking fields to user table
ALTER TABLE user ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE user ADD COLUMN last_login DATETIME;
ALTER TABLE user ADD COLUMN login_attempts INTEGER DEFAULT 0;

-- Add tracking fields to server_connection table
ALTER TABLE server_connection ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE server_connection ADD COLUMN last_verified DATETIME;
ALTER TABLE server_connection ADD COLUMN status VARCHAR(50) DEFAULT 'pending';
-- Create temporary tables without foreign key constraints
CREATE TABLE user_copy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    login_attempts INTEGER DEFAULT 0,
    is_admin BOOLEAN DEFAULT 0 NOT NULL
);

-- Copy data from old table to temporary table
INSERT INTO user_copy 
SELECT id, email, password_hash, created_at, last_login, COALESCE(login_attempts, 0), 0
FROM user;

-- Drop old table after dropping dependent tables
DROP TABLE IF EXISTS wordpress_installation;
DROP TABLE IF EXISTS subscription_plan;
DROP TABLE IF EXISTS server_connection;
DROP TABLE IF EXISTS user;

-- Rename temporary table to original name
ALTER TABLE user_copy RENAME TO user;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_user_created_at ON user(created_at);
CREATE INDEX IF NOT EXISTS idx_user_last_login ON user(last_login);
CREATE INDEX IF NOT EXISTS idx_user_is_admin ON user(is_admin);
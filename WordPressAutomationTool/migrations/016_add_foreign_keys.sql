-- Create server_connection table if it doesn't exist
CREATE TABLE IF NOT EXISTS server_connection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    domain_name TEXT NOT NULL,
    cpanel_username TEXT NOT NULL,
    cpanel_password TEXT NOT NULL,
    cpanel_api_key TEXT,
    softaculous_api_key TEXT,
    ssh_details TEXT,
    installation_method TEXT DEFAULT 'api',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_verified DATETIME,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(user_id) REFERENCES user(id)
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_server_connection_user_id ON server_connection(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_user_id ON subscription_plan(user_id);
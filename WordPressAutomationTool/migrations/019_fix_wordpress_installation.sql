-- Create temporary table with correct schema
CREATE TABLE wordpress_installation_copy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER,
    site_url TEXT NOT NULL,
    admin_username TEXT NOT NULL,
    admin_password TEXT NOT NULL,
    admin_email TEXT NOT NULL,
    site_title TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    installed_at DATETIME,
    category_id INTEGER,
    theme_id INTEGER,
    FOREIGN KEY(server_id) REFERENCES server_connection(id),
    FOREIGN KEY(category_id) REFERENCES website_category(id),
    FOREIGN KEY(theme_id) REFERENCES theme(id)
);

-- Copy data from old table if it exists
INSERT OR IGNORE INTO wordpress_installation_copy 
SELECT id, server_id, site_url, admin_username, admin_password, admin_email, site_title,
       status, created_at, installed_at, category_id, theme_id
FROM wordpress_installation;

-- Drop old table if it exists
DROP TABLE IF EXISTS wordpress_installation;

-- Rename new table
ALTER TABLE wordpress_installation_copy RENAME TO wordpress_installation;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_wordpress_installation_server_id ON wordpress_installation(server_id);
CREATE INDEX IF NOT EXISTS idx_wordpress_installation_category_id ON wordpress_installation(category_id);
CREATE INDEX IF NOT EXISTS idx_wordpress_installation_theme_id ON wordpress_installation(theme_id);
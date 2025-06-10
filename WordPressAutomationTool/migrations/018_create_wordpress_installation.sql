-- Drop existing table if it exists
DROP TABLE IF EXISTS wordpress_installation;

-- Create WordPress Installation Table
CREATE TABLE wordpress_installation (
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

-- Add indexes
CREATE INDEX idx_wordpress_installation_server_id ON wordpress_installation(server_id);
CREATE INDEX idx_wordpress_installation_category_id ON wordpress_installation(category_id);
CREATE INDEX idx_wordpress_installation_theme_id ON wordpress_installation(theme_id);
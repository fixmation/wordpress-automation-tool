-- Create a new table with the updated schema
CREATE TABLE wordpress_installation_copy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
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

-- Copy data from the old table to the new one
INSERT INTO wordpress_installation_copy 
SELECT id, server_id, site_url, admin_username, admin_password, admin_email, site_title, status, created_at, installed_at, NULL as category_id, NULL as theme_id
FROM wordpress_installation;

-- Delete the old table
DROP TABLE wordpress_installation;

-- Rename the new table to the original name
ALTER TABLE wordpress_installation_copy RENAME TO wordpress_installation;
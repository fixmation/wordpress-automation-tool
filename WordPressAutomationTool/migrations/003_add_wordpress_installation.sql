-- Create WordPress Installation Table
CREATE TABLE IF NOT EXISTS wordpress_installation (
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
    FOREIGN KEY(server_id) REFERENCES server_connection(id)
);
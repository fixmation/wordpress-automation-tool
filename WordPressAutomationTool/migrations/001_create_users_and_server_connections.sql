-- Create Users Table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Create Server Connections Table
CREATE TABLE IF NOT EXISTS server_connection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    domain_name TEXT NOT NULL,
    cpanel_username TEXT NOT NULL,
    cpanel_password TEXT NOT NULL,
    cpanel_api_key TEXT,
    ssh_details TEXT,
    FOREIGN KEY(user_id) REFERENCES user(id)
);
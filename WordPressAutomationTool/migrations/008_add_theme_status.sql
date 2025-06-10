-- Create a new table with the updated schema
CREATE TABLE theme_copy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    thumbnail_url TEXT NOT NULL,
    demo_url TEXT,
    category_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(category_id) REFERENCES website_category(id)
);

-- Copy data from the old table to the new one
INSERT INTO theme_copy 
SELECT id, name, description, thumbnail_url, demo_url, category_id, created_at, 'pending' as status
FROM theme;

-- Delete the old table
DROP TABLE theme;

-- Rename the new table to the original name
ALTER TABLE theme_copy RENAME TO theme;
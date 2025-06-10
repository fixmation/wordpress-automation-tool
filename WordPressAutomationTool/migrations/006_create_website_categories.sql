-- Create Website Categories Table
CREATE TABLE IF NOT EXISTS website_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert default categories
INSERT INTO website_category (name, description) VALUES
    ('eCommerce', 'Build an online store to sell products or services with features like shopping cart, payment processing, and inventory management'),
    ('Restaurant', 'Create a restaurant website with menu displays, online ordering, reservations, and location information'),
    ('Blog', 'Start a blog with a clean layout focused on content, categories, comments, and social sharing'),
    ('Portfolio', 'Showcase your work with a professional portfolio featuring galleries, project descriptions, and contact information'),
    ('Business', 'Present your business with a professional website including services, about us, testimonials, and contact forms'),
    ('News', 'Create a news website with article categories, featured stories, and multimedia content'),
    ('Social Network', 'Build a community website with user profiles, activity feeds, and member interactions'),
    ('Educational', 'Develop an educational website with course listings, learning resources, and student portals'),
    ('Real Estate', 'List properties with detailed information, photo galleries, and property search functionality'),
    ('Nonprofit', 'Create a nonprofit website with donation systems, event calendars, and volunteer signups');
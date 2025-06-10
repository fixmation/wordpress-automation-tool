-- Create Themes Table
CREATE TABLE IF NOT EXISTS theme (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    thumbnail_url TEXT NOT NULL,
    demo_url TEXT,
    category_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(category_id) REFERENCES website_category(id)
);

-- Insert default themes for each category
INSERT INTO theme (name, description, thumbnail_url, demo_url, category_id) VALUES
    -- eCommerce Themes
    ('ShopMaster', 'Professional eCommerce theme with product grid and clean design', 'https://example.com/shopmaster-thumb.jpg', 'https://example.com/shopmaster-demo', 1),
    ('WooWizard', 'Feature-rich WooCommerce theme with advanced product filters', 'https://example.com/woowizard-thumb.jpg', 'https://example.com/woowizard-demo', 1),

    -- Restaurant Themes
    ('FoodiePress', 'Modern restaurant theme with menu and reservation system', 'https://example.com/foodiepress-thumb.jpg', 'https://example.com/foodiepress-demo', 2),
    ('CafeStyle', 'Elegant restaurant theme with full-width images and menu showcase', 'https://example.com/cafestyle-thumb.jpg', 'https://example.com/cafestyle-demo', 2),

    -- Blog Themes
    ('MinimalBlog', 'Clean and minimalist blog theme with focus on content', 'https://example.com/minimalblog-thumb.jpg', 'https://example.com/minimalblog-demo', 3),
    ('ModernWriter', 'Contemporary blog theme with elegant typography', 'https://example.com/modernwriter-thumb.jpg', 'https://example.com/modernwriter-demo', 3),

    -- Portfolio Themes
    ('CreativeShowcase', 'Portfolio theme with grid and masonry layout', 'https://example.com/creativeshowcase-thumb.jpg', 'https://example.com/creativeshowcase-demo', 4),
    ('MinimalistPortfolio', 'Simple and clean portfolio theme for professionals', 'https://example.com/minimalistportfolio-thumb.jpg', 'https://example.com/minimalistportfolio-demo', 4),

    -- Business Themes
    ('CorporatePro', 'Professional business theme with corporate design', 'https://example.com/corporatepro-thumb.jpg', 'https://example.com/corporatepro-demo', 5),
    ('BusinessBoost', 'Modern business theme with service sections', 'https://example.com/businessboost-thumb.jpg', 'https://example.com/businessboost-demo', 5),

    -- News Themes
    ('NewsWire', 'Dynamic news theme with multiple layout options', 'https://example.com/newswire-thumb.jpg', 'https://example.com/newswire-demo', 6),
    ('MediaPress', 'Responsive news theme with video and article integration', 'https://example.com/mediapress-thumb.jpg', 'https://example.com/mediapress-demo', 6),

    -- Social Network Themes
    ('CommunityHub', 'Social network theme with user profile and activity feed', 'https://example.com/communityhub-thumb.jpg', 'https://example.com/communityhub-demo', 7),
    ('ConnectNow', 'Modern social networking theme with clean design', 'https://example.com/connectnow-thumb.jpg', 'https://example.com/connectnow-demo', 7),

    -- Educational Themes
    ('LearnMaster', 'Educational theme with course listings and learning resources', 'https://example.com/learnmaster-thumb.jpg', 'https://example.com/learnmaster-demo', 8),
    ('EduPro', 'Professional educational theme with student portal', 'https://example.com/edupro-thumb.jpg', 'https://example.com/edupro-demo', 8),

    -- Real Estate Themes
    ('PropertyPro', 'Real estate theme with advanced property search', 'https://example.com/propertypro-thumb.jpg', 'https://example.com/propertypro-demo', 9),
    ('RealtyHub', 'Comprehensive real estate theme with listing features', 'https://example.com/realtyhub-thumb.jpg', 'https://example.com/realtyhub-demo', 9),

    -- Nonprofit Themes
    ('CharityPress', 'Nonprofit theme with donation and event features', 'https://example.com/charitypress-thumb.jpg', 'https://example.com/charitypress-demo', 10),
    ('NonprofitConnect', 'Modern nonprofit theme with volunteer signup', 'https://example.com/nonprofitconnect-thumb.jpg', 'https://example.com/nonprofitconnect-demo', 10);
-- Create subscription_plan table if it doesn't exist
CREATE TABLE IF NOT EXISTS subscription_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    plan_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_subscription_user_id ON subscription_plan(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_status ON subscription_plan(status);
CREATE INDEX IF NOT EXISTS idx_subscription_created_at ON subscription_plan(created_at);
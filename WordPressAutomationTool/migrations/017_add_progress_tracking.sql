-- Create temporary table with updated schema
CREATE TABLE subscription_plan_copy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    plan_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    current_stage INTEGER,
    stage_data TEXT,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

-- Copy existing data
INSERT INTO subscription_plan_copy (
    id, user_id, stripe_customer_id, stripe_subscription_id, 
    plan_type, status, created_at, expires_at
)
SELECT 
    id, user_id, stripe_customer_id, stripe_subscription_id,
    plan_type, status, created_at, expires_at
FROM subscription_plan;

-- Drop old table
DROP TABLE subscription_plan;

-- Rename new table
ALTER TABLE subscription_plan_copy RENAME TO subscription_plan;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_subscription_current_stage ON subscription_plan(current_stage);
CREATE INDEX IF NOT EXISTS idx_subscription_user_id ON subscription_plan(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_status ON subscription_plan(status);
CREATE INDEX IF NOT EXISTS idx_subscription_created_at ON subscription_plan(created_at);
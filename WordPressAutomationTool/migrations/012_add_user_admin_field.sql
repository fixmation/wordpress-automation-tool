-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_user_created_at ON user(created_at);
CREATE INDEX IF NOT EXISTS idx_user_last_login ON user(last_login);
CREATE INDEX IF NOT EXISTS idx_subscription_status ON subscription_plan(status);
CREATE INDEX IF NOT EXISTS idx_subscription_created_at ON subscription_plan(created_at);
-- Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_subscription_user_id ON subscription_plan(user_id);
CREATE INDEX IF NOT EXISTS idx_server_connection_user_id ON server_connection(user_id);
CREATE INDEX IF NOT EXISTS idx_wordpress_installation_server_id ON wordpress_installation(server_id);
CREATE INDEX IF NOT EXISTS idx_subscription_created_at ON subscription_plan(created_at);
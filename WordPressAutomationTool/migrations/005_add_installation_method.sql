-- Add installation_method column to server_connection table
ALTER TABLE server_connection ADD COLUMN installation_method VARCHAR(50) DEFAULT 'api';
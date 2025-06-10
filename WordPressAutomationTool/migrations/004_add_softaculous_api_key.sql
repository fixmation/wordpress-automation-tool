-- Add Softaculous API key column to server_connection table
ALTER TABLE server_connection ADD COLUMN softaculous_api_key TEXT;
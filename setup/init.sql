DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_database WHERE datname = 'accounts_db'
    ) 
    THEN
        CREATE DATABASE accounts_db;
    END IF;
END
$$;
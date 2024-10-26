-- create role
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = '${POSTGRES_USER}'
    ) THEN
        CREATE ROLE "${POSTGRES_USER}" WITH LOGIN PASSWORD '${POSTGRES_PASSWORD}';
        RAISE NOTICE 'Role % created successfully', '${POSTGRES_USER}';
    ELSE
        RAISE NOTICE 'Role % already exists', '${POSTGRES_USER}';
    END IF;
END $$;

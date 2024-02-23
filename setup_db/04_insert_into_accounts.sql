-- Check if the accounts table is empty
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM accounts LIMIT 1
    )
    THEN
        -- Insert accounts data
        INSERT INTO accounts (first_name, surname, email, phone, birthday, gender)
        VALUES
            ('Alice', 'Smith', 'alice.smith@example.com', '001456789000', '1992-03-15', 'Female'),
            ('Bob', 'Johnson', 'bob.johnson@example.com', '972765432101', '1988-07-22', 'Male'),
            ('Charlie', 'Brown', 'charlie.brown@example.com', '001233445588', '1990-05-30', 'Male'),
            ('Diana', 'Williams', 'diana.williams@example.com', '972528877665', '1995-01-10', 'Female'),
            ('Ethan', 'Davis', 'ethan.davis@example.com', '972535432105', '1989-11-05', 'Male');
        RAISE NOTICE 'Accounts inserted successfully.';
    ELSE
        RAISE NOTICE 'Accounts table already contains data. No need to insert.';
    END IF;
END $$;

-- accounts table
CREATE TABLE IF NOT EXISTS accounts (
    account_id SERIAL PRIMARY KEY,
    first_name VARCHAR(20),
    surname VARCHAR(20),
    email VARCHAR(50),
    phone VARCHAR(15),
    birthday TIMESTAMP,
    gender VARCHAR(10)
);

-- messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(account_id),
    message VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- messages_predictions table
CREATE TABLE IF NOT EXISTS messages_predictions (
    prediction_id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(message_id) UNIQUE,
    score FLOAT,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

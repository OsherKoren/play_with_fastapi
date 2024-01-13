# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""This module sets up the database connection and defines the tables in the database"""


import os

from databases import Database
from dotenv import load_dotenv
from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, MetaData,
                        String, Table, create_engine, func)

load_dotenv()

def get_database_url():
    """
    Construct and return the PostgreSQL database URL based on environment variables.

    This function uses the following environment variables:
    - PS_HOST: PostgreSQL server host address (default is "localhost")
    - PS_USER: PostgreSQL username (required)
    - PS_PASSWORD: PostgreSQL password (required)
    - DB_NAME: PostgreSQL database name (required)
    - PS_PORT: PostgreSQL server port (required)

    If any of the required environment variables (PS_USER, PS_PASSWORD, DB_NAME, PS_PORT) is not set,
    a ValueError is raised.

    Example:
        To use this function, set the required environment variables and call the function:
        db_url = get_database_url()
        print(f"Database URL: {db_url}")
        Database URL: postgresql://your_username:your_password@localhost:5432/your_database_name

        Note: Ensure that you replace "your_username," "your_password," "your_database_name," and "your_port_number"
        with your actual PostgreSQL credentials.

    Returns:
        str: The constructed PostgreSQL database URL.

    Raises:
        ValueError: If any of the required environment variables is not set.
    """
    host = os.getenv("PS_HOST", "localhost")
    user = os.getenv("PS_USER")
    password = os.getenv("PS_PASSWORD")
    db_name = os.getenv("DB_NAME")
    port = os.getenv("PS_PORT")

    if None in (user, password, db_name, port):
        raise ValueError("Some required environment variables are not set.")

    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return db_url


db_url = get_database_url()

if db_url is None:
    raise ValueError("DATABASE_URL environment variable not set")


engine = create_engine(db_url)
metadata = MetaData()

accounts_table = Table(
    "accounts",
    metadata,
    Column("account_id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String(20)),
    Column("surname", String(20)),
    Column("email", String(50)),
    Column("phone", String(15)),
    Column("birthday", DateTime),
    Column("gender", String(10)),
)

messages_table = Table(
    "messages",
    metadata,
    Column("message_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "account_id", Integer, ForeignKey("accounts.account_id")
    ),  # ForeignKey reference to accounts
    Column("message", String(500)),
    Column("created_at", DateTime, default=func.now()),  # Automatic timestamp column
)

messages_predictions_table = Table(
    "messages_predictions",
    metadata,
    Column(
        "prediction_id", Integer, primary_key=True, autoincrement=True
    ),  # Unique ID for each prediction
    Column(
        "message_id", Integer, ForeignKey("messages.message_id"), unique=True
    ),  # ForeignKey reference to messages
    Column("score", Float),
    Column(
        "predicted_at", DateTime, default=func.now()
    ),  # Timestamp for when the prediction was made
)

database = Database(db_url)

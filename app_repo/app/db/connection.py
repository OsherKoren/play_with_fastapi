# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""This module sets up the database connection"""


import os

from databases import Database
from dotenv import load_dotenv

from logger import log


ENV_FILE = ".env.dev" if os.getenv("DEV_ENV") else ".env"
load_dotenv(ENV_FILE)


def get_database_url():
    """
    Construct and return the PostgreSQL database URL based on environment variables.

    This function uses the following environment variables:
    - PS_HOST: PostgreSQL server host address (default is "localhost")
    - PS_USER: PostgreSQL username (required)
    - PS_PASSWORD: PostgreSQL password (required)
    - DB_NAME: PostgreSQL database name (required)
    - PS_PORT: PostgreSQL server port (required)

    If any of the required environment variables (PS_USER, PS_PASSWORD, DB_NAME, PS_PORT)
     is not set, a ValueError is raised.

    Example:
        To use this function, set the required environment variables and call the function:
        db_url = get_database_url()
        print(f"Database URL: {db_url}")
        Database URL: postgresql://your_username:your_password@localhost:5432/your_database_name

        Note: Ensure that you replace "your_username," "your_password," "your_database_name,"
        and "your_port_number" with your actual PostgreSQL credentials.

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
        raise ValueError("Some required environment variables are not set.".center(40, "="))

    database_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    log.debug(f"Database URL:\n {database_url}")
    return database_url


db_url = get_database_url()
database = Database(db_url)


async def start_database():
    """
    Set up the database by creating tables and establishing a connection.

    Raises:
        Any exceptions raised during the database setup.
    """
    await database.connect()
    log.info(" Starting Up Database ".center(40, "="))


async def shutdown_database():
    """
    Tear down the database by disconnecting the connection.

    Raises:
        Any exceptions raised during the database teardown.
    """
    await database.disconnect()
    log.info(" Shutting Down Database ".center(40, "="))
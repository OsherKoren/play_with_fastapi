# !/usr/bin/env python

"""This module sets up the database connection"""


import os

from databases import Database
from dotenv import load_dotenv

from logger import log

ENV_FILE = os.getenv("ENV_FILE", ".env")
load_dotenv(ENV_FILE)


def get_database_url():
    """
    Construct and return the PostgreSQL database URL based on environment variables.

    This function uses the following environment variables:
    - PGUSER: PostgreSQL username (required)
    - PGPASSWORD: PostgreSQL password (required)
    - PGHOST: PostgreSQL server host address (default is "localhost")
    - PGPORT: PostgreSQL server port (required)
    - PGDATABASE: PostgreSQL database name (required)

    If any of the required environment variables (PGUSER, PGPASSWORD, PGHOST, PGPORT, PGDATABASE)
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
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    hostname = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT")
    db_name = os.getenv("PGDATABASE")

    if None in (user, password, port, db_name):
        log.debug(
            f"\nuser: {user}\npassword: {password}\nhostname: {hostname}\nport: {port}\ndb_name: {db_name}"
        )
        raise ValueError("Some required environment variables are not set.")

    database_url = f"postgresql://{user}:{password}@{hostname}:{port}/{db_name}"
    log.debug(f"Database URL:\n{database_url}")
    return database_url


DB_URL: str = get_database_url()
database = Database(DB_URL)


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
    log.info(" Shutting down database ".center(40, "="))

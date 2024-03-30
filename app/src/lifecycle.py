# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.db import connection as db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=unused-argument
    """
    Coroutine to manage the lifespan of the FastAPI application.

    This coroutine sets up the database and Kafka, yields to the application,
    and then tears down the Kafka and database on application shutdown.

    Args:
        app (FastAPI): The FastAPI application.

    Yields:
        None

    Raises:
        Any exceptions raised during the setup, application execution, or teardown phases.
    """
    await db_connection.start_database()
    try:
        yield
    finally:
        await db_connection.shutdown_database()

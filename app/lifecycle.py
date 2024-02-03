# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
import os
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import IncompatibleBrokerVersion, TopicAlreadyExistsError
from fastapi import FastAPI
from db.tables_metadata import database, engine, metadata

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


bootstrap_servers = "dev-kafka:29092" if os.getenv("DEV_ENV", False) else "kafka:9092"


async def setup_database():
    """
    Set up the database by creating tables and establishing a connection.

    Raises:
        Any exceptions raised during the database setup.
    """
    metadata.create_all(engine)
    await database.connect()
    logger.info("Starting up database ... ")


async def teardown_database():
    """
    Tear down the database by disconnecting the connection.

    Raises:
        Any exceptions raised during the database teardown.
    """
    await database.disconnect()
    logger.info("Shutting down database ... ")


async def setup_kafka():
    """
    Set up Kafka by creating the required topic.

    Raises:
        TopicAlreadyExistsError: If the Kafka topic already exists.
        IncompatibleBrokerVersion: If there's an issue with the Kafka broker version.
    """
    admin_client = AIOKafkaAdminClient(bootstrap_servers=bootstrap_servers)
    topic_name = "evt.user_message"
    topics = [NewTopic(topic_name, num_partitions=1, replication_factor=1)]

    try:
        await admin_client.create_topics(new_topics=topics, validate_only=False)
        logger.info(f"Topic {topic_name} created")
    except TopicAlreadyExistsError:
        logger.info(f"Topic {topic_name} already exists")
    except IncompatibleBrokerVersion as ex:
        logger.error(f"Failed to create topic {topic_name}: {ex}")


async def teardown_kafka():
    # Perform cleanup or shutdown actions related to Kafka if needed
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    await setup_database()
    await setup_kafka()
    try:
        yield
    finally:
        await teardown_kafka()
        await teardown_database()



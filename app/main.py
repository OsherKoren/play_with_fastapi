# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

import logging
from contextlib import asynccontextmanager
import asyncio
import os
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import IncompatibleBrokerVersion, TopicAlreadyExistsError
from fastapi import FastAPI

from api import messages
from db.tables_metadata import database, engine, metadata

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

metadata.create_all(engine)

bootstrap_servers = "dev-kafka:29092" if os.getenv("DEV_ENV", False) else "kafka:9092"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    print("Starting up database ... ")

    # Kafka topic creation using aiokafka
    admin_client = AIOKafkaAdminClient(
        loop=asyncio.get_event_loop(),
        bootstrap_servers=bootstrap_servers
    )
    topic_name = "evt.user_message"
    topics = [NewTopic(topic_name, num_partitions=1, replication_factor=1)]

    try:
        await admin_client.create_topics(new_topics=topics, validate_only=False)

        logger.info(f"Topic {topic_name} created")
    except TopicAlreadyExistsError as ex:
        # Check if the exception is 'Topic already exists'
        logger.info(f"Topic {topic_name} already exists")
    except IncompatibleBrokerVersion as ex:
        logger.error(f"Failed to create topic {topic_name}: {ex}")

    yield
    await database.disconnect()
    print("Shutting down ... ")

app = FastAPI(title="Message Prediction App", version="1.0", lifespan=lifespan)

app.include_router(messages.health_router, prefix='/api/v1', tags=["health"])
app.include_router(messages.router, prefix='/api/v1', tags=["messages"])

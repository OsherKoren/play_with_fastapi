# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

# from aiohttp import ClientSession
from contextlib import asynccontextmanager
import asyncio
import os
from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from fastapi import FastAPI

from api import messages
from db.tables_metadata import database, engine, metadata

metadata.create_all(engine)

bootstrap_servers = "dev-kafka:29092" if os.getenv("DEV_ENV", False) else "kafka:9092"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    print("Starting up database ... ")
    # Kafka topic creation
    admin_client = AdminClient({"bootstrap.servers": bootstrap_servers})
    topic_name = "message_score_topic"
    topics = [NewTopic(topic_name, 1, 1)]

    futures = admin_client.create_topics(topics, request_timeout=15.0)

    for topic, future in futures.items():
        try:
            future.result()  # Wait for operation to complete
            print(f"Topic {topic} created")
        except KafkaException as ex:
            # Check if the exception is 'Topic already exists'
            if ex.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS:
                print(f"Topic {topic} already exists")
            else:
                print(f"Failed to create topic {topic}: {ex}")
    yield
    await database.disconnect()
    print("Shutting down ... ")

app = FastAPI(title="Message Prediction App", version="1.0", lifespan=lifespan)

app.include_router(messages.health_router, prefix='/api/v1', tags=["health"])
app.include_router(messages.router, prefix='/api/v1', tags=["messages"])

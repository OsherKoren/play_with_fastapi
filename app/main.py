# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from fastapi import FastAPI

from app.api.messages import messages
from setup.db import database, engine, metadata

metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
    """
    Performs startup actions for the FastAPI application.

    This function is called when the FastAPI application starts. It connects to the database
    and tries to create a Kafka topic. If the topic already exists, it is ignored; otherwise,
    it creates the new topic.
    """
    await database.connect()
    # Kafka topic creation
    admin_client = AdminClient({"bootstrap.servers": "kafka:9092"})
    topic_name = "message_scores_topic"
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


@app.on_event("shutdown")
async def shutdown() -> None:
    """
    Performs shutdown actions for the FastAPI application.
    This function is called when the FastAPI application shuts down.
    It disconnects from the database.
    """
    await database.disconnect()


app.include_router(messages, tags=["messages"])

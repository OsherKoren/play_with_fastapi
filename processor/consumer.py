# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Consume Kafka messages"""

import json
import logging
import os
import time
from typing import Optional

from confluent_kafka import Consumer, KafkaError, KafkaException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


bootstrap_servers = "dev-kafka:29092" if os.getenv("DEV_ENV", False) else "kafka:9092"


async def set_consumer(retries: int = 3) -> Consumer:
    consumer = None

    async def _create_consumer():
        nonlocal consumer

        for i in range(1, retries + 1):
            try:
                consumer = Consumer({
                    "bootstrap.servers": bootstrap_servers,
                    "group.id": "department1",
                    "auto.offset.reset": "earliest",
                }
                )
                logger.info("Connected to Kafka")
                return consumer
            except KafkaException as err:
                logger.error("Failed to connect to Kafka: %s", err)
                if i <= retries:
                    logger.info("Retrying in 1 second... (Attempt %d of %d)", i, retries)
                    await asyncio.sleep(1)
                else:
                    raise ConnectionError(f"Failed to connect to Kafka after {retries} attempts.")

    try:
        yield await _create_producer()
    finally:
        if consumer:
            producer.close()
            logger.info("Consumer closed")


def consume_messages(consumer: Consumer) -> None:
    """
    Consumes messages from a Kafka topic.

    This function subscribes to a specified Kafka topic and continuously polls for messages.
    It logs each received message and handles errors and end-of-partition events.
    The function runs indefinitely until interrupted or an unrecoverable error occurs.

    Args:
        consumer (Consumer): A configured Kafka Consumer instance.
    """
    consumer.subscribe(["evt.user_message"])
    logger.info("Subscribing to topic: evt.user_message")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.debug("End of partition reached: %s", msg.error())
                    continue
                logger.error("Error in message consumption: %s", msg.error())
                break
            # Decode the message bytes into a string and then load it as JSON
            message_str = msg.value().decode("utf-8")
            message_dict = json.loads(message_str)
            logger.info("Received message: %s", message_dict)

    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()

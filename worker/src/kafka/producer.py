# !/usr/bin/env python

"""Kafka producer"""

import asyncio
import os

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from src.logger import log

BOOTSTRAP_SERVERS = "dev-kafka:29092" if os.getenv("DEV_ENV") else "kafka:9092"
KAFKA_PRODUCER: AIOKafkaProducer | None = None


# singleton pattern - Not needed if the connection is set in the src lifespan
def setup_producer() -> None:
    """
    Set up an AIOKafkaProducer instance.
    """
    global KAFKA_PRODUCER  # pylint: disable=global-statement

    if KAFKA_PRODUCER is None:
        KAFKA_PRODUCER = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
        log.info(" Instancing Kafka producer ".center(40, "="))


# pylint: disable=R0801
async def start_producer(retries: int = 3) -> None:
    """
    Starts the AIOKafkaProducer instance connection.

    Raises:
        KafkaConnectionError: If failed to connect to Kafka
        after the specified number of retry attempts.
    """
    setup_producer()

    assert KAFKA_PRODUCER
    for i in range(1, retries + 1):
        try:
            await KAFKA_PRODUCER.start()  # Start the producer
            log.info(" Connected to Kafka ".center(40, "="))
            return
        except KafkaConnectionError as err:
            log.error(f"Failed to connect to Kafka: {err}")
            if i <= retries:
                log.info(f"Retrying in 1 second... (Attempt {i} of {retries})")
                await asyncio.sleep(1)
            else:
                raise KafkaConnectionError(
                    f"Failed to connect to Kafka after {retries} attempts."
                ) from err


async def shutdown_producer() -> None:
    """
    Shut down by disconnecting the producer connection to the kafka broker.
    """
    if KAFKA_PRODUCER:
        await KAFKA_PRODUCER.stop()
        log.info(" Shutting down producer ".center(40, "="))

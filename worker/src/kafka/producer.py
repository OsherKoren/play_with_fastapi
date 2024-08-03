# !/usr/bin/env python

"""Kafka producer"""

import asyncio

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from src.kafka import constants
from src.logger import log

KAFKA_PRODUCER: AIOKafkaProducer | None = None


# singleton pattern - Not needed if the connection is set in the src lifespan
def setup_producer() -> None:
    """
    Set up an AIOKafkaProducer instance.

    Returns:
        AIOKafkaProducer: An instance of AIOKafkaProducer with the specified Kafka
        bootstrap servers.
    """
    global KAFKA_PRODUCER  # pylint: disable=global-statement

    if KAFKA_PRODUCER is None:
        KAFKA_PRODUCER = AIOKafkaProducer(
            bootstrap_servers=constants.BOOTSTRAP_SERVERS, api_version="2.8.1"
        )
        log.info(" Instancing Kafka producer ".center(40, "="))


# pylint: disable=R0801
async def start_producer() -> None:
    """
    Starts the AIOKafkaProducer instance connection.

    Raises:
        KafkaConnectionError: If failed to connect to Kafka
        after the specified number of retry attempts.
    """
    setup_producer()
    assert KAFKA_PRODUCER

    async def _connect_producer(trials: int = 3):
        try:
            await KAFKA_PRODUCER.start()  # Start the producer
            log.info(" Producer Connected to Kafka ".center(40, "="))
            return KAFKA_PRODUCER
        except KafkaConnectionError as err:
            log.error(f"Producer Failed to connect to Kafka: {err}")
            trials -= 1
            if trials > 0:
                log.info(f"Retrying in 1 second... (Attempts remaining: {trials})")
                await asyncio.sleep(1)
                await _connect_producer(trials)
            else:
                raise KafkaConnectionError(
                    f"Producer Failed to connect to Kafka after multiple attempts."
                ) from err

    await _connect_producer()


async def shutdown_producer() -> None:
    """
    Shut down by disconnecting the producer connection to the kafka broker.
    """
    if KAFKA_PRODUCER:
        await KAFKA_PRODUCER.stop()
        log.info(" Shutting down producer ".center(40, "="))

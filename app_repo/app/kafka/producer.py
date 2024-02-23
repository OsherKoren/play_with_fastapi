# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Kafka producer"""

import asyncio
import os
from typing import Optional

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

from logger import log

BOOTSTRAP_SERVERS: str = "dev-kafka:29092" if os.getenv("DEV_ENV") else "kafka:9092"
KAFKA_PRODUCER: Optional[AIOKafkaProducer] = None


# singleton pattern - Not needed if
# the connection function is set with fastapi Depends on the request
# or in fastapi lifespan
def setup_producer() -> None:
    """
    Set up an AIOKafkaProducer instance.

    Returns:
        AIOKafkaProducer: An instance of AIOKafkaProducer with the specified Kafka
        bootstrap servers.
    """
    global KAFKA_PRODUCER  # pylint: disable=global-statement

    if KAFKA_PRODUCER is None:
        KAFKA_PRODUCER = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
        log.info(" Instancing Kafka Producer ".center(40, "="))


async def get_producer() -> AIOKafkaProducer:
    """
    Creates and starts an AIOKafkaProducer instance.

    Returns:
        AIOKafkaProducer: An instance of AIOKafkaProducer connected to the specified Kafka
        bootstrap servers.

    Raises:
        KafkaConnectionError: If failed to connect to Kafka
        after the specified number of retry attempts.
    """
    setup_producer()
    assert KAFKA_PRODUCER

    async def _connect_producer():

        for i in range(1, 4):
            try:
                await KAFKA_PRODUCER.start()
                log.info(" Connected to Kafka ".center(40, "="))
                return KAFKA_PRODUCER
            except KafkaConnectionError as err:
                log.error(f"Failed to connect to Kafka: {err}")
                if i <= 3:
                    log.info(f"Retrying in 1 second... (Attempt {i} of 3")
                    await asyncio.sleep(1)
                else:
                    raise ConnectionError(
                        "Failed to connect to Kafka after 3 attempts."
                    ) from err

    try:
        yield await _connect_producer()
    finally:
        await KAFKA_PRODUCER.stop()
        log.info(" Producer Stopped ".center(40, "="))

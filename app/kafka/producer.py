# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Produce Kafka messages"""

import asyncio
import logging
import os

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bootstrap_servers = "dev-kafka:29092" if os.getenv("DEV_ENV", False) else "kafka:9092"


async def set_producer() -> AIOKafkaProducer:
    """
    Creates and starts an AIOKafkaProducer instance.

    Returns:
        AIOKafkaProducer: An instance of AIOKafkaProducer connected to the specified Kafka bootstrap servers.

    Raises:
        ConnectionError: If failed to connect to Kafka after the specified number of retry attempts.
    """
    producer = None

    async def _create_producer():
        nonlocal producer

        for i in range(1, 4):
            try:
                producer = AIOKafkaProducer(
                    loop=asyncio.get_event_loop(),
                    bootstrap_servers=bootstrap_servers
                )
                await producer.start()  # Start the producer
                logger.info("Connected to Kafka")
                return producer
            except KafkaError as err:
                logger.error("Failed to connect to Kafka: %s", err)
                if i <= 3:
                    logger.info("Retrying in 1 second... (Attempt %d of %d)", i, 3)
                    await asyncio.sleep(1)
                else:
                    raise ConnectionError(f"Failed to connect to Kafka after 3 attempts.")

    try:
        yield await _create_producer()
    finally:
        if producer:
            await producer.stop()
            logger.info("Producer stopped")

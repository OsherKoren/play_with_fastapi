# !/usr/bin/env python

"""kafka consumer module."""

import asyncio
import json
import os

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from src.db import db_manager
from src.kafka import constants, producer
from src.logger import log
from src.mock_ml import predict

KAFKA_CONSUMER: AIOKafkaConsumer | None = None


# singleton pattern - Not needed if the connection is set in the src lifespan
def setup_consumer() -> None:
    """
    Set up an AIOKafkaConsumer instance.
    """
    global KAFKA_CONSUMER  # pylint: disable=global-statement

    if KAFKA_CONSUMER is None:
        KAFKA_CONSUMER = AIOKafkaConsumer(
            "evt.userMessage",
            bootstrap_servers=constants.BOOTSTRAP_SERVERS,
            group_id="MlEngineersGroup",
            auto_offset_reset="latest",
            api_version="2.8.1",
            value_deserializer=lambda x: x.decode("utf-8"),
        )
        log.info(" Instancing Kafka Consumer ".center(40, "="))


# pylint: disable=R0801
async def start_consumer() -> None:
    """
    Starts an AIOKafkaConsumer instance connection to the kafka broker.

    retries (int): The number of retry attempts if connection to Kafka fails. Default is 3.

    Returns:
        AIOKafkaConsumer: An instance of AIOKafkaConsumer connected to the specified Kafka topic.

    Raises:
        ConnectionError: If failed to connect to Kafka after the specified number of retry attempts.
    """
    setup_consumer()
    assert KAFKA_CONSUMER

    async def _connect_consumer(trials: int = 3):
        try:
            await KAFKA_CONSUMER.start()
            log.info(" Consumer Connected to Kafka ".center(40, "="))
            return KAFKA_CONSUMER
        except KafkaConnectionError as err:
            log.error(f"Consumer Failed to connect to Kafka: {err}")
            trials -= 1
            if trials > 0:
                log.info(f"Retrying in 1 second... (Attempts remaining: {trials})")
                await asyncio.sleep(1)
                await _connect_consumer(trials)
            else:
                raise ConnectionError(
                    "Consumer Failed to connect to Kafka after multiple attempts."
                ) from err

    await _connect_consumer()


async def shutdown_consumer() -> None:
    """
    Shut down by disconnecting the consumer connection to the kafka broker.
    """
    if KAFKA_CONSUMER:
        await KAFKA_CONSUMER.stop()
        log.info(" Shutting Down Consumer ".center(40, "="))


async def consume_messages() -> None:
    """
    Consumes messages from a Kafka topic.

    This function subscribes to a specified Kafka topic and continuously polls for messages.
    It logs each received message and handles errors and end-of-partition events.
    The function runs indefinitely until interrupted or an unrecoverable error occurs.
    """

    assert KAFKA_CONSUMER

    async for msg in KAFKA_CONSUMER:
        log.info(
            f"Consume from topic: {msg.topic}\n"
            f"Partition: {msg.partition}\n"
            f"Offset: {msg.offset}\n"
            f"Key: {msg.key}\n"
            f"Value: {msg.value}\n"
            f"Timestamp: {msg.timestamp}\n"
        )
        # Decode the message bytes into a string and then load it as JSON
        message_dict = json.loads(msg.value)
        log.info(f"Received message: {message_dict}")

        score = predict.predict_score(message_dict.get("message"))

        message_dict["score"] = score
        message_serialized = json.dumps(message_dict, default=str).encode("utf-8")
        await producer.KAFKA_PRODUCER.send_and_wait(
            "evt.messageScore", message_serialized
        )
        log.info(f"Message sent to topic evt.messageScore: {message_dict}")

        message_id = message_dict.get("message_id")
        prediction_id = await db_manager.add_message_score(message_id, score)
        log.info(f"Database updated with prediction_id: {prediction_id}")


async def start_workers() -> None:
    """
    Starts the specified number of worker tasks to consume messages.

    """

    await start_consumer()
    num_workers = int(os.getenv("WORKERS", 2))
    tasks = [consume_messages() for _ in range(num_workers)]
    await asyncio.gather(*tasks)
    for worker_id, task in enumerate(tasks):
        log.info(f"Started worker {worker_id}")

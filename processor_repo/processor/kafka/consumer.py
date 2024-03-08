# !/usr/bin/env python

"""kafka consumer module."""

import asyncio
import json
import os

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from mock_ml import predict

from db import db_manager
from kafka import producer
from logger import log

BOOTSTRAP_SERVERS: str = "dev-kafka:29092" if os.getenv("DEV_ENV") else "kafka:9092"
KAFKA_CONSUMER: AIOKafkaConsumer | None = None


# singleton pattern - Not needed if the connection is set in the app lifespan
def setup_consumer() -> None:
    """
    Set up an AIOKafkaConsumer instance.
    """
    global KAFKA_CONSUMER  # pylint: disable=global-statement

    if KAFKA_CONSUMER is None:
        KAFKA_CONSUMER = AIOKafkaConsumer(
            "evt.user_message",
            bootstrap_servers=BOOTSTRAP_SERVERS,
            group_id="MlEngineersGroup",
            auto_offset_reset="earliest",
        )
        log.info(" Instancing Kafka Consumer ".center(40, "="))


# pylint: disable=R0801
async def start_consumer(retries: int = 3) -> None:
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
    for i in range(1, retries + 1):
        try:
            await KAFKA_CONSUMER.start()
            log.info(" Connected to Kafka ".center(40, "="))
            return
        except KafkaConnectionError as err:
            log.error(f"Failed to connect to Kafka: {err}")
            if i <= retries:
                log.info(f"Retrying in 1 second... (Attempt {i} of {retries}")
                await asyncio.sleep(1)
            else:
                raise ConnectionError(
                    f"Failed to connect to Kafka after {retries} attempts."
                ) from err


async def shutdown_consumer() -> None:
    """
    Shut down by disconnecting the consumer connection to the kafka broker.
    """
    if KAFKA_CONSUMER:
        await KAFKA_CONSUMER.stop()
        log.info(" Shutting Down Consumer ".center(40, "="))


async def get_consumer() -> AIOKafkaConsumer:
    """
    Creates and starts an AIOKafkaConsumer instance.

    Returns:
        AIOKafkaConsumer: An instance of AIOKafkaConsumer connected to the specified Kafka
        bootstrap servers.

    Raises:
        KafkaConnectionError: If failed to connect to Kafka
        after the specified number of retry attempts.
    """
    setup_consumer()

    assert KAFKA_CONSUMER

    async def _connect_consumer():

        for i in range(1, 4):
            try:
                await KAFKA_CONSUMER.start()
                log.info(" Connected to Kafka ".center(40, "="))
                return KAFKA_CONSUMER
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
        yield await _connect_consumer()
    finally:
        await KAFKA_CONSUMER.stop()
        log.info(" Producer Stopped ".center(40, "="))


async def consume_messages() -> None:
    """
    Consumes messages from a Kafka topic.

    This function subscribes to a specified Kafka topic and continuously polls for messages.
    It logs each received message and handles errors and end-of-partition events.
    The function runs indefinitely until interrupted or an unrecoverable error occurs.
    """

    assert KAFKA_CONSUMER

    while True:
        async for message in KAFKA_CONSUMER:
            log.info(f"Received from topic: {message.topic}")
            # Decode the message bytes into a string and then load it as JSON
            deserialize_message = message.value.decode("utf-8")
            message_dict = json.loads(deserialize_message)
            log.info(f"Received message: {message_dict}")

            score = predict.predict_score(message_dict.get("message"))

            message_dict["score"] = score
            message_serialized = json.dumps(message_dict, default=str).encode("utf-8")
            await producer.KAFKA_PRODUCER.send_and_wait(
                "evt.message_score", message_serialized
            )
            log.info(f"Message sent to topic evt.message_score: {message_dict}")

            message_id = message_dict.get("message_id")
            prediction_id = await db_manager.add_message_score(message_id, score)
            log.info(f"Database updated with prediction_id: {prediction_id}")

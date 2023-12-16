# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""This module mocks external user that consumes messages from Kafka"""
import json
import logging
import time

from confluent_kafka import Consumer, KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_consumer(retries: int = 5) -> Consumer:
    """
    Sets up and returns a Kafka consumer.

    This function attempts to create a Kafka consumer with specified configuration settings.
    If the initial connection attempt fails, it retries a specified number of times before
    giving up.

    Args:
        retries (int, optional): The number of attempts to make for connecting to Kafka.
                                 Defaults to 5.

    Returns:
        Consumer: A configured Kafka consumer instance.

    Raises:
        Exception: If the function fails to connect to Kafka after the specified number of retries.

    """
    for i in range(retries):
        try:
            _consumer = Consumer(
                {
                    "bootstrap.servers": "kafka:9092",
                    "group.id": "department1-consumer-group",
                    "auto.offset.reset": "earliest",
                }
            )
            logger.info("Connected to Kafka")
            return _consumer
        except ConnectionError as err:
            logger.error("Failed to connect to Kafka: %s", err)
            if i < retries - 1:
                logger.info("Retrying in 10 seconds... (Attempt %d/%d)", i + 2, retries)
                time.sleep(10)
    raise ConnectionError(f"Failed to connect to Kafka after {retries} retries")


def consume_messages(kafka_consumer: Consumer) -> None:
    """
    Consumes messages from a Kafka topic.

    This function subscribes to a specified Kafka topic and continuously polls for messages.
    It logs each received message and handles errors and end-of-partition events.
    The function runs indefinitely until interrupted or an unrecoverable error occurs.

    Args:
        kafka_consumer (Consumer): A configured Kafka Consumer instance.
    """
    kafka_consumer.subscribe(["message_scores_topic"])
    logger.info("Subscribing to topic: message_scores_topic")

    try:
        while True:
            msg = kafka_consumer.poll(1.0)
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
        kafka_consumer.close()


if __name__ == "__main__":
    consumer = set_consumer()
    consume_messages(consumer)

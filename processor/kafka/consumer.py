import asyncio
import json
import logging
import os

from aiokafka import AIOKafkaConsumer, ConsumerRebalanceListener
from aiokafka.errors import KafkaError

from mock_ml import predict
from db import db_manager
from db.tables_metadata import database, engine, metadata

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bootstrap_servers = "dev-kafka:29092" if os.getenv("DEV_ENV", False) else "kafka:9092"


async def startup_db():
    metadata.create_all(engine)
    await database.connect()


async def shutdown_db():
    await database.disconnect()


async def set_consumer(retries: int = 3) -> AIOKafkaConsumer:
    """
       Creates and starts an AIOKafkaConsumer instance.

       Args:
           retries (int): The number of retry attempts if connection to Kafka fails. Default is 3.

       Returns:
           AIOKafkaConsumer: An instance of AIOKafkaConsumer connected to the specified Kafka topic.

       Raises:
           ConnectionError: If failed to connect to Kafka after the specified number of retry attempts.
       """
    consumer = None

    async def _create_consumer():
        nonlocal consumer

        for i in range(1, retries + 1):
            try:
                consumer = AIOKafkaConsumer(
                    "evt.user_message",
                    bootstrap_servers=bootstrap_servers,
                    group_id="DataEngineersGroup",
                    auto_offset_reset="earliest",
                )
                await consumer.start()
                logger.info("Connected to Kafka")
                return consumer
            except KafkaError as err:
                logger.error("Failed to connect to Kafka: %s", err)
                if i <= retries:
                    logger.info("Retrying in 1 second... (Attempt %d of %d)", i, retries)
                    await asyncio.sleep(1)
                else:
                    raise ConnectionError(f"Failed to connect to Kafka after {retries} attempts.")

    try:
        yield await _create_consumer()
    finally:
        if consumer:
            await consumer.stop()
            logger.info("Consumer stopped")


async def consume_messages(consumer: AIOKafkaConsumer) -> None:
    """
    Consumes messages from a Kafka topic.

    This function subscribes to a specified Kafka topic and continuously polls for messages.
    It logs each received message and handles errors and end-of-partition events.
    The function runs indefinitely until interrupted or an unrecoverable error occurs.

    Args:
        consumer (AIOKafkaConsumer): A configured Kafka Consumer instance.
    """
    try:
        async for message in consumer:
            logger.info("Received from topic: %s", message.topic)
            # Decode the message bytes into a string and then load it as JSON
            message_str = message.value.decode("utf-8")
            message_dict = json.loads(message_str)
            logger.info("Received message: %s", message_dict)

            score = predict.predict_score(message)
            message_id = message_dict.get("message_id")
            prediction_id = await db_manager.add_message_score(message_id, score)

            logger.info("Predicted score: %s", score)
            logger.info("Database updated with prediction_id: %s", prediction_id)

    except KeyboardInterrupt:
        pass


async def listen_to_kafka():
    """
    Listens to Kafka messages.

    This function creates a Kafka consumer and consumes messages from the specified topic.
    """
    consumer_generator = set_consumer()
    async for consumer_instance in consumer_generator:
        await consume_messages(consumer_instance)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup_db())
    try:
        loop.run_until_complete(listen_to_kafka())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(shutdown_db())

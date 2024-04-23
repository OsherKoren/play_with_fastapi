# !/usr/bin/env python

"""Set up Kafka topics."""

from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import IncompatibleBrokerVersion, TopicAlreadyExistsError
from src.kafka import constants
from src.logger import log


async def setup_topics():
    """
    Set up Kafka by creating the required topic.

    Raises:
        TopicAlreadyExistsError: If the Kafka topic already exists.
        IncompatibleBrokerVersion: If there's an issue with the Kafka broker version.
    """
    admin_client = AIOKafkaAdminClient(bootstrap_servers=constants.BOOTSTRAP_SERVERS)
    topics = [
        NewTopic("evt.user_message", num_partitions=1, replication_factor=1),
        NewTopic("evt.message_score", num_partitions=1, replication_factor=1),
    ]
    try:
        futures = await admin_client.create_topics(
            new_topics=topics, timeout_ms=10, validate_only=False
        )
        for topic, f in futures.items():
            try:
                f.result()
                log.info(f"Topic {topic} Created")
            except TopicAlreadyExistsError as ex:
                log.info(f"Topic already exists {topic}, {ex}")
            except IncompatibleBrokerVersion as ex:
                log.error(f"Failed to create topic: {topic}, {ex}")

        log.info(f"Topics {topics} created")
    finally:
        await admin_client.close()

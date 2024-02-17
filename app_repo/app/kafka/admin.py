# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Set up Kafka topics."""
import os

from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import IncompatibleBrokerVersion, TopicAlreadyExistsError

from logger import log

BOOTSTRAP_SERVERS = "dev-kafka:29092" if os.getenv("DEV_ENV") else "kafka:9092"


async def setup_topics():
    """
    Set up Kafka by creating the required topic.

    Raises:
        TopicAlreadyExistsError: If the Kafka topic already exists.
        IncompatibleBrokerVersion: If there's an issue with the Kafka broker version.
    """
    admin_client = AIOKafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)
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

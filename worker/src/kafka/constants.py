# !/usr/bin/env python

"""Kafka constants."""
import os

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", "9092")
BOOTSTRAP_SERVERS: str = f"{KAFKA_HOST}:{KAFKA_PORT}"

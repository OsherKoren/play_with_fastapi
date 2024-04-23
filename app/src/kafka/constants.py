# !/usr/bin/env python

"""Kafka constants."""
import os

from dotenv import load_dotenv

ENV_FILE = ".env.dev" if os.getenv("DEV_ENV") else ".env"
load_dotenv(ENV_FILE)

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", "9092")
BOOTSTRAP_SERVERS: str = f"{KAFKA_HOST}:{KAFKA_PORT}"

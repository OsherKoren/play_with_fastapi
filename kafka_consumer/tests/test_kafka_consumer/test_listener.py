# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Tests for the Kafka consumer."""

import json
import logging
import pytest
from kafka_consumer import listener

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.parametrize("retries, expected_error", [
    (0, "Failed to connect to Kafka after 0 retries"),
    (3, "Failed to connect to Kafka after 3 retries"),
    (5, "Failed to connect to Kafka after 5 retries"),
])
def test_set_consumer_retries_failure(monkeypatch, caplog, retries, expected_error):
    # Test set_consumer with different retry scenarios
    with pytest.raises(ConnectionError, match=expected_error):
        set_consumer(retries=retries)

def test_consume_messages(mock_kafka_consumer, caplog):
    with logger as caplog:
        caplog.set_level(logging.INFO)

        # Test consume_messages with the mock_kafka_consumer fixture
        consume_messages(mock_kafka_consumer)

        # Add assertions based on your specific requirements
        assert "Subscribing to topic: message_scores_topic" in caplog.text
        assert "Received message:" in caplog.text
        assert "End of partition reached:" not in caplog.text
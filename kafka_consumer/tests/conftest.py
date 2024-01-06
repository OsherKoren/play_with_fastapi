# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""This module contains fixtures for the tests."""


import pytest


@pytest.fixture
def mock_kafka_consumer(monkeypatch):
    """Mocks the KafkaConsumer class."""
    class MockKafkaConsumer:
        def __init__(self, config):
            pass

        def subscribe(self, topics):
            pass

        def __iter__(self):
            return self

        def __next__(self):
            return None

    monkeypatch.setattr("kafka_consumer.listener.KafkaConsumer", MockKafkaConsumer)
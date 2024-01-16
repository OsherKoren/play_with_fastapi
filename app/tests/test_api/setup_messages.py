# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Setup for the Messages API endpoints tests"""

import pytest
from typing import List, Optional
from databases.interfaces import Record
from app.db import db_manager


all_messages_expected_response = [
    {
        "message_id": 1,
        "message": "Please stop sending me promotions emails.",
        "score": 0.5,
        "created_at": "2024-01-01 00:00:00",
        "account_id": 5,
    },
    {
        "message_id": 2,
        "message": "I am interested in receiving a loan, please contact me",
        "score": 0.9,
        "created_at": "2024-03-03 00:00:00",
        "account_id": 4,
    },
]

@pytest.fixture
def mock_all_messages(monkeypatch):
    """Mock all messages"""
    async def setup_get_all_messages() -> List[Record]:
        return all_messages_expected_response

    monkeypatch.setattr(
        "app.api.messages.db_manager.get_all_messages", setup_get_all_messages
    )


@pytest.fixture
def mock_message_2(monkeypatch):
    """Mock get message 2"""
    async def setup_message_2(*args, **kwargs) -> Optional[Record]:
        return {
                "message_id": 2,
                "message": "I am interested in receiving a loan, please contact me",
                "score": 0.9,
                "created_at": "2024-03-03 00:00:00",
                "account_id": 4,
            }
    monkeypatch.setattr(
        "app.api.messages.db_manager.get_message", setup_message_2
    )


@pytest.fixture
def mock_message_2_score(monkeypatch):
    """Mock get scores"""
    async def setup_get_message_score() -> List[Record]:
        return {
                "prediction_id": 2,
                "message_id": 2,
                "score": 0.9,
                "predicted_at": "2024-03-03 00:01:00",
        }
    monkeypatch.setattr(
        "app.api.messages.db_manager.get_message_score", setup_get_message_score
    )


# return [
#     {
#         "prediction_id": 1,
#         "message_id": 1,
#         "score": 0.5,
#         "predicted_at": "2024-01-01 00:01:00",
#     },
#     {
#         "prediction_id": 2,
#         "message_id": 2,
#         "score": 0.9,
#         "predicted_at": "2024-03-03 00:01:00",
#     }
# ]
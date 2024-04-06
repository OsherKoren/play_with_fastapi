# !/usr/bin/env python

"""Setup for the Messages API endpoints tests"""

import pytest


@pytest.fixture
def mock_all_messages(monkeypatch):
    """Mock all messages"""

    async def setup_all_messages():
        return [
            {
                "message_id": 1,
                "message": "Please stop sending me promotions emails.",
                "created_at": "2024-01-01 00:00:00",
                "account_id": 5,
                "account_first_name": "Ethan",
                "account_surname": "Davis",
                "account_email": "ethan.davis@example.com",
                "account_phone": "972535432105",
                "account_birthday": "1989-11-05",
                "account_gender": "Male",
            },
            {
                "message_id": 2,
                "message": "I am interested in receiving a loan, please contact me",
                "created_at": "2024-03-03 00:00:00",
                "account_id": 4,
                "account_first_name": "Diana",
                "account_surname": "Williams",
                "account_email": "diana.williams@example.com",
                "account_phone": "972528877665",
                "account_birthday": "1995-01-10",
                "account_gender": "Female",
            },
        ]

    monkeypatch.setattr(
        "src.api.messages.db_manager.get_all_messages", setup_all_messages
    )


@pytest.fixture
def mock_message_2(monkeypatch):
    """Mock message 2"""

    async def setup_message_2(*args, **kwargs):
        return (
            {
                "message_id": 2,
                "message": "I am interested in receiving a loan, please contact me",
                "created_at": "2024-03-03 00:00:00",
                "account_id": 4,
                "account_first_name": "Diana",
                "account_surname": "Williams",
                "account_email": "diana.williams@example.com",
                "account_phone": "972528877665",
                "account_birthday": "1995-01-10",
                "account_gender": "Female",
            },
        )

    monkeypatch.setattr("src.api.messages.db_manager.get_message", setup_message_2)


@pytest.fixture
def mock_messages_scores(monkeypatch):
    """Mock messages scores"""

    async def setup_messages_scores():
        return [
            {
                "message_id": 1,
                "message": "Please stop sending me promotions emails.",
                "created_at": "2024-01-01 00:00:00",
                "score": 0.5,
                "predicted_at": "2024-01-01 00:01:00",
                "account_id": 5,
                "account_first_name": "Ethan",
                "account_surname": "Davis",
                "account_email": "ethan.davis@example.com",
                "account_phone": "972535432105",
                "account_birthday": "1989-11-05",
                "account_gender": "Male",
            },
            {
                "message_id": 2,
                "message": "I am interested in receiving a loan, please contact me",
                "created_at": "2024-03-03 00:00:00",
                "score": 0.95,
                "predicted_at": "2024-03-03 00:01:00",
                "account_id": 4,
                "account_first_name": "Diana",
                "account_surname": "Williams",
                "account_email": "diana.williams@example.com",
                "account_phone": "972528877665",
                "account_birthday": "1995-01-10",
                "account_gender": "Female",
            },
        ]

    monkeypatch.setattr(
        "src.api.messages.db_manager.get_messages_scores", setup_messages_scores
    )


@pytest.fixture
def mock_message_2_score(monkeypatch):
    """Mock get message 2 score"""

    async def setup_message_score(*args, **kwargs):
        return {
            "message_id": 2,
            "message": "I am interested in receiving a loan, please contact me",
            "created_at": "2024-03-03 00:00:00",
            "score": 0.95,
            "predicted_at": "2024-03-03 00:01:00",
            "account_id": 4,
            "account_first_name": "Diana",
            "account_surname": "Williams",
            "account_email": "diana.williams@example.com",
            "account_phone": "972528877665",
            "account_birthday": "1995-01-10",
            "account_gender": "Female",
        }

    monkeypatch.setattr(
        "src.api.messages.db_manager.get_message_score", setup_message_score
    )


@pytest.fixture
def mock_filtered_scores(monkeypatch):
    """Mock filtered scores"""

    async def setup_filtered_scores(*args, **kwargs):
        return [
            {
                "message_id": 2,
                "message": "I am interested in receiving a loan, please contact me",
                "created_at": "2024-03-03 00:00:00",
                "score": 0.95,
                "predicted_at": "2024-03-03 00:01:00",
                "account_id": 4,
                "account_first_name": "Diana",
                "account_surname": "Williams",
                "account_email": "diana.williams@example.com",
                "account_phone": "972528877665",
                "account_birthday": "1995-01-10",
                "account_gender": "Female",
            },
        ]

    monkeypatch.setattr(
        "src.api.messages.db_manager.filter_messages_scores", setup_filtered_scores
    )

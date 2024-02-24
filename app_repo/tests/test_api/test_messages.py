# !/usr/bin/env python

"""Tests for the Messages API endpoints"""

import pytest

ROOT_ENDPOINT = "messages"
MSG_ENDPOINT = "messages/all"
MSG_2_ENDPOINT = "messages/2"
SCORES_ENDPOINT = "messages/scores"
MSG_2_SCORE_ENDPOINT = "messages/2/score"
FILTERED_SCORES_ENDPOINT = "messages/scores/0.9"


def test_root(test_app, base_url):
    """Test the get root endpoint"""
    response = test_app.get(f"{base_url}/{ROOT_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == "Messages Prediction Services"


@pytest.mark.anyio
async def test_root_async(async_test_app, base_url):
    """Test the get root endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{ROOT_ENDPOINT}/")
    assert response.status_code == 200
    assert response.json() == "Messages Prediction Services"


messages_expected_response = [
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


def test_get_messages(test_app, base_url, mock_all_messages):
    """Test the get all messages endpoint"""
    response = test_app.get(f"{base_url}/{MSG_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == messages_expected_response


@pytest.mark.anyio
async def test_get_messages_async(async_test_app, base_url, mock_all_messages):
    """Test the get all messages endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{MSG_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == messages_expected_response


message_expected_response = [
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
    }
]


# def test_get_message(test_app, base_url, mock_message_2):
#     """Test the get a message endpoint"""
#
#     response = test_app.get(f"{base_url}/{MSG_2_ENDPOINT}")
#     assert response.status_code == 200
#     assert response.json() == message_expected_response
#
#
# @pytest.mark.anyio
# async def test_get_message_async(async_test_app, base_url, mock_message_2):
#     """Test the get a message endpoint - async"""
#     response = await async_test_app.get(f"{base_url}/{MSG_2_ENDPOINT}")
#     assert response.status_code == 200
#     assert response.json() == message_expected_response


scores_expected_response = [
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


def test_get_scores(test_app, base_url, mock_messages_scores):
    """Test the get all scores endpoint"""
    response = test_app.get(f"{base_url}/{SCORES_ENDPOINT}")
    print(response.content)
    assert response.status_code == 200
    assert response.json() == scores_expected_response


@pytest.mark.anyio
async def test_get_scores_async(async_test_app, base_url, mock_messages_scores):
    """Test the get all scores endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{SCORES_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == scores_expected_response


message_2_score_expected_response = {
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


def test_get_message_score(test_app, base_url, mock_message_2_score):
    """Test the get a message score endpoint"""

    response = test_app.get(f"{base_url}/{MSG_2_SCORE_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == message_2_score_expected_response


@pytest.mark.anyio
async def test_get_message_score_async(async_test_app, base_url, mock_message_2_score):
    """Test the get a message endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{MSG_2_SCORE_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == message_2_score_expected_response


filtered_scores_expected_response = [
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


def test_get_filtered_scores(test_app, base_url, mock_filtered_scores):
    """Test the get filtered scores endpoint"""
    response = test_app.get(f"{base_url}/{FILTERED_SCORES_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == filtered_scores_expected_response


@pytest.mark.anyio
async def test_get_filtered_scores_async(
    async_test_app, base_url, mock_filtered_scores
):
    """Test the get filtered scores endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{FILTERED_SCORES_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == filtered_scores_expected_response

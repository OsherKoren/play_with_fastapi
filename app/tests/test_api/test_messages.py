# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Tests for the Messages API endpoints"""

import pytest


ROOT_ENDPOINT = "messages"
MSG_ENDPOINT = "messages/all"
MSG_2_ENDPOINT = "messages/2"
SCORES_ENDPOINT = "messages/scores/"
MSG_2_SCORE_ENDPOINT = "messages/2/score"


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

def test_get_messages(test_app, base_url, mock_all_messages):
    """Test the get all endpoint"""
    response = test_app.get(f"{base_url}/{MSG_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == all_messages_expected_response


@pytest.mark.anyio
async def test_get_all_async(async_test_app, base_url, mock_all_messages):
    """Test the get all endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{MSG_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == all_messages_expected_response


get_message_expected_response = {
            "message_id": 2,
            "message": "I am interested in receiving a loan, please contact me",
            "score": 0.9,
            "created_at": "2024-03-03 00:00:00",
            "account_id": 4,
        }


def test_get_message(test_app, base_url, mock_message_2):
    """Test the get a message endpoint"""

    response = test_app.get(f"{base_url}/{MSG_2_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == get_message_expected_response


@pytest.mark.anyio
async def test_get_message_async(async_test_app, base_url, mock_message_2):
    """Test the get a message endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{MSG_2_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == get_message_expected_response


get_message_2_score_expected_response = {
            "prediction_id": 5,
            "message_id": 2,
            "score": 0.9,
            "predicted_at": "2024-03-03 00:01:00",
        }


def test_get_message_score(test_app, base_url, mock_message_2_score):
    """Test the get a message score endpoint"""

    response = test_app.get(f"{base_url}/{MSG_2_SCORE_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == get_message_2_score_expected_response


@pytest.mark.anyio
async def test_get_message_score_async(async_test_app, base_url, mock_message_2_score):
    """Test the get a message endpoint - async"""
    response = await async_test_app.get(f"{base_url}/{MSG_2_SCORE_ENDPOINT}")
    assert response.status_code == 200
    assert response.json() == get_message_2_score_expected_response
#
#
# get_all_scores_expected_response =  [
#         {
#             "message_id": 1,
#             "message": "Please stop sending me promotions emails.",
#             "score": 0.5,
#             "created_at": "2024-01-01 00:00:00",
#             "account_id": 5,
#         },
#         {
#             "message_id": 2,
#             "message": "I am interested in receiving a loan, please contact me",
#             "score": 0.9,
#             "created_at": "2024-03-03 00:00:00",
#             "account_id": 4,
#         },
#     ]


# def test_get_scores(test_app, base_url, mock_scores):
#     """Test the get scores endpoint"""
#     endpoint = f"{base_url}/{SCORES_ENDPOINT}"
#     print(endpoint)
#     response = test_app.get(f"{base_url}/{SCORES_ENDPOINT}")
#     assert response.status_code == 200
#     assert response.json() == get_all_scores_expected_response
#
#
# @pytest.mark.anyio
# async def test_get_scores_async(async_test_app, base_url, mock_scores):
#     """Test the get scores endpoint - async"""
#     endpoint = f"{base_url}/{SCORES_ENDPOINT}"
#     print(endpoint)
#     response = await async_test_app.get(f"{base_url}/{SCORES_ENDPOINT}")
#     assert response.status_code == 200
#     assert response.json() == get_all_scores_expected_response

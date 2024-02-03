# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for API endpoints"""
import json
from datetime import datetime
import logging
import os
from typing import Annotated, Any, Dict, List, Union, Optional

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from . import schemas
from db import db_manager
from kafka import producer as kafka_producer

from mock_external import mock_authentication as authentication

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


router = APIRouter(prefix="/messages", tags=["messages"])
health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/", status_code=200)
async def health_check():
    """
    Health check endpoint to verify the status of the Messages Prediction Service.

    Returns:
        dict: A dictionary indicating the health status.
    """
    return {"status": "ok"}


@router.get("/", status_code=200)
async def root():
    """Root endpoint that welcomes users to the Messages Services."""
    return "Messages Prediction Services"


@router.get("/all", status_code=200)
async def get_messages():
    """Retrieve all messages."""
    return await db_manager.get_all_messages()


# @router.post("/score", status_code=201, response_model=schemas.MessageScore)
@router.post("/send",
             status_code=201,
             response_model=None,
             description="Post a message and store it in the database.",
             )
async def send_message(
    payload: schemas.MessageIn,
    # produce_message: Annotated[None, Depends(kafka_producer.produce_message)],
    account: dict = Depends(authentication.get_current_user),
    producer: AIOKafkaProducer = Depends(kafka_producer.set_producer),

        # kafka_producer: Annotated[MsgProducer, Depends(producer.produce_message)] = None),
) -> JSONResponse:
    """
    Store the user message in the database and send it to the Kafka topic.

    Args:
        payload (schemas.MessageIn): The message payload.
        account (dict): The user account information obtained from authentication.

    Returns:
        dict: A dictionary containing message details including the predicted score.
    """
    account_id = account["account_id"]
    message = payload.message

    message_id = await db_manager.add_message(account_id, message)
    created_at = datetime.now()

    kafka_message = {
        "message_id": message_id,
        "account_id": account_id,
        "message": message,
        "created_at": created_at,
    }
    # score = predict.predict_score(message)
    # await db_manager.add_message_score(message_id, score)
    #
    # response = {
    #     "message_id": message_id,
    #     "account_id": account_id,
    #     "message": message,
    #     "created_at": created_at,
    #     "score": score,
    # }
    message_serialized = json.dumps(kafka_message, default=str).encode("utf-8")
    try:
        await producer.send("evt.user_message", value=message_serialized)
        logger.info(f"Message sent to topic evt.user_message: {kafka_message}")
        # await kafka_producer.produce_message("evt.user_message", message_serialized)
    # producer.produce("message_score_topic", message_serialized)
    # producer.flush()

        job_id = f"{created_at.isoformat()}_{message_id}"
        return JSONResponse(content={"Message ID": message_id, "Job ID": job_id}, status_code=201)
    except ConnectionError as err:
        logger.error(f"ConnectionError: {err}")
        return JSONResponse(content={"Internal Server Error": "Failed to connect to Kafka"}, status_code=500)


@router.get("/scores", status_code=200)
async def get_scores():
    """Retrieve all scores."""
    return await db_manager.get_messages_scores()


# @router.get("/{msg_id}", status_code=200)
# async def get_message(msg_id: int):
#     """
#     Retrieve a specific message by its ID.
#
#     Args:
#         msg_id (int): The ID of the message to retrieve.
#
#     Returns:
#         dict: A dictionary containing the message details.
#     """
#     message = await db_manager.get_message(msg_id)
#     if not message:
#         return {"message": f"Message {msg_id} not found"}
#     return message


@router.get("/{msg_id}/score", status_code=200)
async def get_message_score(msg_id: int) -> Dict[str, Any]:
    """
    Retrieves the score of a specific message by its message ID.

    Args:
        msg_id (int): The ID of the message for which the score is to be retrieved.

    Returns:
        dict: A dictionary containing the message score details.
    """
    message_score = await db_manager.get_message_score(msg_id)
    if not message_score:
        return {"message": f"Message {msg_id} not found or no score available"}
    return dict(message_score)


@router.get("/scores/{threshold}", status_code=200)
async def get_filtered_scores(threshold: Annotated[float, Path(ge=0, le=1)]):
    """
    Retrieve scorers based on a specified threshold.

    Args:
        threshold (float): The score threshold to filter scores.

    Returns:
        dict: A dictionary containing filtered scores' details.
    """
    scores = await db_manager.filter_messages_scores(threshold)
    if not scores:
        return {"message": f"No score greater than {threshold} found"}
    return scores

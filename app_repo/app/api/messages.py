# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Module for API endpoints"""
import json
import logging
from datetime import datetime
from typing import Annotated, Any, Dict

import pydantic_core
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse

from db import db_manager
from kafka import producer
from mock_external import mock_authentication as authentication

from . import schemas
from logger import log


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


@router.post(
    "/send",
    status_code=201,
    response_model=None,
    description="Post a message and store it in the database.",
)
async def send_message(
    payload: schemas.MessageIn,
    account: dict = Depends(authentication.get_current_user),
    producer: AIOKafkaProducer = Depends(producer.get_producer)
) -> JSONResponse:
    """
    Store the user message in the database and send it to the Kafka topic.

    Args:
        payload (schemas.MessageIn): The message payload.
        account (dict): The user account information obtained from authentication.
        producer: AIOKafkaProducer: The Kafka producer instance connected to the broker.

    Returns:
        dict: A dictionary containing message details including the predicted score.
    """
    created_at = datetime.now()
    account_id = account["account_id"]
    message = payload.message

    message_id = await db_manager.add_message(account_id, message)

    kafka_message = {
        "message_id": message_id,
        "account_id": account_id,
        "message": message,
        "created_at": created_at,
    }

    message_serialized = json.dumps(kafka_message, default=pydantic_core.to_jsonable_python).encode("utf-8")
    try:
        await producer.send_and_wait("evt.user_message", value=message_serialized)
        log.info(f"Message sent to topic evt.user_message: {kafka_message}")

        job_id = f"{created_at.isoformat()}_{message_id}"
        return JSONResponse(
            content={"Message ID": message_id, "Job ID": job_id}, status_code=201
        )
    except ConnectionError as err:
        log.error(f"ConnectionError: {err}")
        return JSONResponse(
            content={"Internal Server Error": "Failed to connect to Kafka"},
            status_code=500,
        )


@router.get("/scores", status_code=200)
async def get_scores():
    """Retrieve all scores."""
    return await db_manager.get_messages_scores()


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

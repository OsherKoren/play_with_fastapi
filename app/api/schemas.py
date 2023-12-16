# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""This module is for setting and validating schemas for the API endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator


# pylint: disable=too-few-public-methods
class MessageIn(BaseModel):
    """
    Represents incoming message data.

    Attributes:
        message (str): The message content.
        email (EmailStr, optional): The email associated with the message (optional).
        phone (str, optional): The phone number associated with the message (optional).

    Methods:
        email_or_phone_valid(cls, values):
        Validates that at least one of email or phone is specified.
    """

    message: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def email_or_phone_valid(cls, values):
        """
        Validate that at least one of email or phone is specified.

        Args:
            values (dict): A dictionary of values containing 'email' and 'phone'.

        Raises:
            ValueError: If neither 'email' nor 'phone' is specified.
        """
        if "email" not in values and "phone" not in values:
            raise ValueError("At least one of email or phone must be specified")
        return values


# pylint: disable=too-few-public-methods
class MessageOut(MessageIn):
    """
    Represents outgoing message data with additional attributes.

    Attributes:
        message_id (int): The message ID.
        account_id (int): The account ID.
    """

    message_id: int
    account_id: int


# pylint: disable=too-few-public-methods
class MessageScore(BaseModel):
    """
    Represents a message's score data.

    Attributes:
        message_id (int): The message ID.
        account_id (int): The account ID.
        message (str): The message content.
        created_at (datetime): The timestamp when the message was created.
        score (float): The score associated with the message.

    Methods:
        score_valid(cls, value): Validates that the score is within the range [0, 1].
    """

    message_id: int
    account_id: int
    message: str
    created_at: datetime
    score: float

    @field_validator("score")
    @classmethod
    def score_valid(cls, value):
        """
        Validate that the score is within the range [0, 1].

        Args:
            value (float): The score value to validate.

        Raises:
            ValueError: If the score is not within the range [0, 1].
        """
        if not 0 <= value <= 1:
            raise ValueError("Score must be between 0 and 1")
        return value
